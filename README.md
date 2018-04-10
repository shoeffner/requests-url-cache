# requests-url-cache

[![Build Status](https://semaphoreci.com/api/v1/shoeffner/requests-url-cache/branches/master/badge.svg)](https://semaphoreci.com/shoeffner/requests-url-cache)

```python
import time

import requests
import requests_cache

from requests_url_cache import PerURLCacheSession, register_url

requests_cache.install_cache('test', backend='sqlite', session_factory=PerURLCacheSession)

def p(response, should_be=False):
    print('Request to', response.url, 'was',
          'cached;' if response.from_cache else 'not cached;',
          'should be',
          'cached' if should_be else 'not cached')

# Normal caching forever
p(requests.get('https://httpbin.org/get'))
p(requests.get('https://httpbin.org/get'), True)

# Disable caching for /anything
p(requests.get('https://httpbin.org/anything', expire_after=-1))
p(requests.get('https://httpbin.org/anything'))
p(requests.get('https://httpbin.org/anything'))

# It still works for /get
p(requests.get('https://httpbin.org/get'), True)

# Register get for an expiration of 1 second
register_url('https://httpbin.org/get', 1)
# Registration causes a reset, thus get is queried again...
p(requests.get('https://httpbin.org/get'))
# ... but cached for 1 second
p(requests.get('https://httpbin.org/get'), True)
# After > 1 second ...
time.sleep(1)
p(requests.get('https://httpbin.org/get'))
```

This drop-in module allows to utilize
[requests-cache](https://github.com/reclosedev/requests-cache) caching based on
urls and individual requests.

This is still not tested thoroughly and there might be some gotchas, but the
basic functionality is there.

## Install

```bash
pipenv install -e git+https://github.com/shoeffner/requests-url-cache#egg=requests-url-cache
# or
pip install -e git+https://github.com/shoeffner/requests-url-cache#egg=requests-url-cache
```

## Usage

To use the URL-based caching, it is enough to set the `session_factory` in the `requests_cache.install_cache` call:

```python
import requests_cache

from requests_url_cache import PerURLCacheSession

requests_cache.install_cache('test', backend='sqlite', session_factory=PerURLCacheSession)
```

Now all requests support the `expire_after` keyword argument, which takes an expiration time in seconds:

```python
requests.get('https://httpbin.org/get', expire_after=10)
```

To register URLs without actually making requests, it is possible to use the
`register_url` function, it takes a URL and an expire_after time in seconds.

```python
from requests_url_cache import register_url

register_url('https://httpbin.org/get', 10)
```

It is also possible to remove old cache entries based on their individual
caching preferences by simply calling
`requests_cache.core.remove_expired_responses()`. (This should work without the
explicit call to `core`, but I oddly didn't get it to work and didn't bother.)


## Contributing

I'm happy to see your ideas, suggestions, pull requests, ...


## Other

This little plugin is inspired by
https://github.com/reclosedev/requests-cache/issues/108. If it ever gets a
proper solution built into the library, it becomes obsolete.
