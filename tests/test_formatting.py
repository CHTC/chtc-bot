import pytest

from web import formatting


@pytest.mark.parametrize("input, expected", [("foo", "*foo*")])
def test_bold(input, expected):
    assert formatting.bold(input) == expected
