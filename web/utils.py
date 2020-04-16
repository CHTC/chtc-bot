import threading
import time
import functools

import requests


@functools.lru_cache(2 ** 6)
def get_url(url):
    return requests.get(url)


def run_in_thread(func):
    """Run a zero-argument function asynchronously in a thread (use a lambda to capture local variables)."""
    threading.Thread(target=func).start()


class ForgetfulDict:
    def __init__(self, *, memory: float):
        self.timeout = memory
        self.last_cleanup = time.monotonic()
        self.cache = dict()
        self.memory = dict()

    def __getitem__(self, key):
        now = time.monotonic()
        self._cleanup(now)
        return self.cache[key]

    def __setitem__(self, key, value):
        now = time.monotonic()
        self._cleanup(now)
        if key not in self.cache:
            self.memory[key] = now
        self.cache[key] = value

    def _cleanup(self, now: float):
        if self.last_cleanup + self.timeout > now:
            return

        self.cache = {
            k: v
            for k, v in self.cache.items()
            if k in self.memory and now < self.memory[k] + self.timeout
        }
        self.memory = {k: v for k, v in self.memory.items() if k in self.cache}

        self.last_cleanup = now


if __name__ == "__main__":
    test = ForgetfulDict(memory=0.1)
    test["foo"] = "bar"
    try:
        x = test["bar"]
        print("Test 1 FAILURE")
        exit(1)
    except KeyError:
        print("Test 1 OK")
    if test["foo"] != "bar":
        print("Test 2 FAILURE\n")
    else:
        print("Test 2 OK")

    time.sleep(0.2)

    try:
        x = test["bar"]
        print("Test 3 FAILURE")
        exit(1)
    except KeyError:
        print("Test 3 OK")
    try:
        x = test["foo"]
        print("Test 4 FAILURE")
        exit(1)
    except KeyError:
        print("Test 4 OK")

    exit(0)
