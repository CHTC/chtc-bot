import functools

import requests


@functools.lru_cache(2 ** 6)
def cached_get_url(url, *args, **kwargs):
    return requests.get(url, *args, **kwargs)
