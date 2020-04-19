import pytest

from web import html


@pytest.mark.parametrize(
    "input, expected", [("MAX_&lt;SUBSYS&gt;_LOG", "MAX_<SUBSYS>_LOG")]
)
def test_unescape(input, expected):
    assert html.unescape(input) == expected
