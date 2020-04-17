import pytest

import bs4

from web.slashes import knobs


def test_get_knob_description_returns_none_if_it_fails_to_find_the_knob():
    assert knobs.get_knob_description(bs4.BeautifulSoup("", features="html.parser"), "foo") is None
