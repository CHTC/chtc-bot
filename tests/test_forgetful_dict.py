import pytest

import time
import datetime

from web.utils import ForgetfulDict


def test_it_remembers():
    d = ForgetfulDict(memory_time=10)

    d["key"] = 5

    assert d["key"] == 5


def test_it_forgets_if_it_has_no_memory():
    d = ForgetfulDict(memory_time=0)

    d["key"] = 5

    with pytest.raises(KeyError):
        d["key"]


def test_it_forgets_with_short_memory():
    d = ForgetfulDict(memory_time=0.1)

    d["key"] = 5
    time.sleep(0.1)

    with pytest.raises(KeyError):
        d["key"]


def test_it_remembers_with_short_memory():
    d = ForgetfulDict(memory_time=0.2)

    d["key"] = 5
    time.sleep(0.1)

    assert d["key"] == 5


def test_constructor_converts_timedeltas():
    d = ForgetfulDict(memory_time=datetime.timedelta(seconds=1))

    assert d.memory_time == 1