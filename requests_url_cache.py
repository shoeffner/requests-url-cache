from datetime import timedelta, datetime
import requests_cache

__version__ = '0.9.0'

class RequestRegistry(dict):
    """A dictionary to store cache times."""

    def __setitem__(self, key, value):
        """Sets the value of the dictionary.

        None, 'default' and timedelta values are simply set, other values are
        assumed to be seconds to be used to create a timedelta instance to store.

        If a value was set for that key before and it changed, the key
        is added to PerURLCacheSession.changed_for.

        While this should be used with request cache_keys as created by the
        CacheSession, the PerURLCacheSession takes care of converting url entries
        to cache_keys, allowing to just store urls using register_url.

        Args:
            key: The key to cache.
            value: The expiration: None for never, 'default' to inherit the
                   caches default, or a number in seconds or timedelta.
        """
        if value is not None and value != 'default' and not isinstance(value, timedelta):
            value = timedelta(seconds=value)

        try:
            old_value = super().__getitem__(key)
        except KeyError:
            old_value = None

        if old_value != value:
            PerURLCacheSession.changed_for.add(key)

        super().__setitem__(key, value)


def register_url(key, expire_after):
    """Registers a URL with the request registry.

    Args:
        key: The url or cache key to register.
        expire_after: The expiry time in seconds (or a timedelta instance)
    """
    PerURLCacheSession.registry[key] = expire_after


class PerURLCacheSession(requests_cache.CachedSession):
    """A Session to be used with requests-cache as a custom session
    factory.

    It uses the RequestRegistry stored in registry to determine
    if a url has a custom cache time or uses the cache's default time.
    """
    registry = RequestRegistry()
    changed_for = set()

    def send(self, request, **kwargs):
        """Performs the super()'s send method with the same arguments, but
        adjusts the _cache_expire_after times before the call (and resets it
        after).

        This method checks the registry for the requested URL and retrieves the
        associated time.

        Args:
            request: The request to be made by requests.
            kwargs: Arguments to be passed to the session's send method.

        See also:
            https://github.com/reclosedev/requests-cache/blob/5fe2bc23ba29c2aeeb55be15458f6443264db3a2/requests_cache/core.py#L81-L119
        """
        cache_key = self.cache.create_key(request)

        # Register by requests keyword
        if self.expire_after != 'default':
            register_url(cache_key, self.expire_after)

        expire_after = PerURLCacheSession.registry.get(request.url, 'default')
        expire_after = PerURLCacheSession.registry.get(cache_key, expire_after)

        # Clear from cache on change
        if request.url in PerURLCacheSession.changed_for:
            self.cache.delete(cache_key)
            register_url(cache_key, expire_after)
            for k in [request.url, cache_key]:
                try:
                    PerURLCacheSession.changed_for.remove(k)
                except KeyError:
                    pass
        elif cache_key in PerURLCacheSession.changed_for:
            self.cache.delete(cache_key)
            PerURLCacheSession.changed_for.remove(cache_key)

        if expire_after == 'default':
            return super().send(request, **kwargs)

        old, self._cache_expire_after = self._cache_expire_after, expire_after
        try:
            return super().send(request, **kwargs)
        finally:
            self._cache_expire_after = old

    def request(self, method, url, **kwargs):
        """Adds an additional keyword argument to requests.request calls:
            expire_after.

        This keyword is used to set the expiry time for that request, and can
        be omitted on subsequent calls. Subsequent calls with different
        times invalidate the cache, calls with the same time don't.
        """
        try:
            self.expire_after = kwargs.pop('expire_after', 'default')
        except KeyError:
            self.expire_after = 'default'
        try:
            return super().request(method, url, **kwargs)
        finally:
            self.expire_after = 'default'

    def remove_expired_responses(self):
        """Removes expired responses, taking into account individual request
        expiry times."""
        now = datetime.utcnow()

        keys_to_delete = set()
        for key in self.cache.responses:

            # get cache entry or continue
            try:
                response, created = self.cache.responses[key]
            except KeyError:
                continue

            # delete by custom expiry and continue
            try:
                expiry = PerURLCacheSession.registry[key]
                if now - expiry > created:
                    keys_to_delete.add(key)
                continue
            except KeyError:
                pass

            # delete by default expiry, if it's not None
            if self._cache_expire_after and now - self._cache_expire_after > created:
                keys_to_delete.add(key)

        for key in keys_to_delete:
            self.cache.delete(key)
