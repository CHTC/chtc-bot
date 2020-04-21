from typing import Union, Mapping, TypeVar, Optional, Callable, Tuple, Dict

import collections

import time
import datetime


class ForgetfulDict:
    def __init__(self, *, memory_time: Union[datetime.timedelta, float]):
        if isinstance(memory_time, datetime.timedelta):
            memory_time = memory_time.total_seconds()
        self.memory_time = memory_time

        self._last_cleanup = time.monotonic()

        self._cache = dict()
        self._memory = dict()

    def __getitem__(self, key):
        now = time.monotonic()
        self._cleanup(now)
        return self._cache[key]

    def __setitem__(self, key, value):
        now = time.monotonic()
        self._cleanup(now)
        if key not in self._cache:
            self._memory[key] = now
        self._cache[key] = value

    def _cleanup(self, now: float):
        if self._last_cleanup + self.memory_time > now:
            return

        self._cache = {
            k: v
            for k, v in self._cache.items()
            if k in self._memory and now < self._memory[k] + self.memory_time
        }
        self._memory = {k: v for k, v in self._memory.items() if k in self._cache}

        self._last_cleanup = now


K = TypeVar("K")
V = TypeVar("V")


def partition(
    mapping: Mapping[K, V], key: Optional[Callable[[V], bool]] = None
) -> Tuple[Dict[K, V], Dict[K, V]]:
    if key is None:
        key = lambda _: _

    goodbad = {True: {}, False: {}}

    for k, v in mapping.items():
        try:
            goodbad[key(v)][k] = v
        except KeyError:
            raise ValueError("key function must return a bool (True or False)")

    return goodbad[True], goodbad[False]
