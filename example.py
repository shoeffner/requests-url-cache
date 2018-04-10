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
