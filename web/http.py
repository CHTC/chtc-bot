import functools

import requests


@functools.lru_cache(2 ** 6)
def cached_get_url(url, *args, **kwargs):
    """
    This is a thin wrapper over requests.get(url, *args, **kwargs)
    with a small cache sitting in front of it.
    """
    r = requests.get(url, *args, **kwargs)

    # prefer the guessed encoding to the standard-defined encoding
    r.encoding = r.apparent_encoding

    return r
