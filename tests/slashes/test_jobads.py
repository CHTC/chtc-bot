import pytest

import bs4

from web.slashes import jobads
import os.path


def test_get_attrs_description_returns_none_if_it_fails_to_find_the_knob():
    assert (
        jobads.get_attrs_description(
            bs4.BeautifulSoup("", features="html.parser"), "foo"
        )
        is None
    )
