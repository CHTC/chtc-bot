from typing import Union

import threading
import time
import datetime


def run_in_thread(func):
    """Run a zero-argument function asynchronously in a thread (use a lambda to capture local variables)."""
    threading.Thread(target=func).start()


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
