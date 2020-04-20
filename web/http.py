import functools

import requests


@functools.lru_cache(2 ** 6)
def cached_get_url(url, *args, **kwargs):
    r = requests.get(url, *args, **kwargs)
    r.encoding = "utf-8"
    return r
