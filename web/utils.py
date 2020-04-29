from typing import (
    Union,
    Mapping,
    TypeVar,
    Optional,
    Callable,
    Tuple,
    Dict,
    Collection,
    List,
)
from collections.abc import MutableMapping

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

    def __contains__(self, key):
        now = time.monotonic()
        self._cleanup(now)
        return key in self._cache

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


def partition_collection(
    collection: V, key: Optional[Callable[[V], bool]] = None
) -> Tuple[List[V], List[V]]:
    """
    Partition the elements of a collection into two lists by evaluating a key
    function against their values. The first (second) list is the one where
    the key function returned ``True`` (``False``).

    Parameters
    ----------
    collection
        A collection to partition into two groups by the key function.
    key
        The function applied to each value in the collection to determine which
        group it should be in.

    Returns
    -------
    t, f
        Two mappings; one for the key-True items, and one for the key-False items.
    """
    if key is None:
        key = lambda _: _

    goodbad = {True: [], False: []}

    for v in collection:
        try:
            goodbad[key(v)].append(v)
        except KeyError as e:
            raise ValueError(
                "The partition key function must return a bool (True or False)"
            ) from e

    return goodbad[True], goodbad[False]


def partition_mapping(
    mapping: Mapping[K, V], key: Optional[Callable[[V], bool]] = None
) -> Tuple[Dict[K, V], Dict[K, V]]:
    """
    Partition the items of a mapping into two new mappings by evaluating a key
    function against their values. The first (second) mapping is the one where
    the key function returned ``True`` (``False``).

    Parameters
    ----------
    mapping
        A mapping to partition into two groups by the key function.
    key
        The function applied to each value in the mapping to determine which
        group it should be in.

    Returns
    -------
    t, f
        Two mappings; one for the key-True items, and one for the key-False items.
    """
    if key is None:
        key = lambda _: _

    goodbad = {True: {}, False: {}}

    for k, v in mapping.items():
        try:
            goodbad[key(v)][k] = v
        except KeyError as e:
            raise ValueError(
                "The partition key function must return a bool (True or False)"
            ) from e

    return goodbad[True], goodbad[False]
