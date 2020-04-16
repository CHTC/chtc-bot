import pytest

from web.utils import ForgetfulDict


def test_it_remembers():
    d = ForgetfulDict(memory=10)

    d["key"] = 5

    assert d["key"] == 5


def test_it_forgets():
    d = ForgetfulDict(memory=-1)

    d["key"] = 5

    with pytest.raises(KeyError):
        d["key"]
