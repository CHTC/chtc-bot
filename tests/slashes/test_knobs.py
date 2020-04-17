import pytest

import bs4

from web.slashes import knobs


def test_get_knob_description_returns_none_if_it_fails_to_find_the_knob():
    assert (
        knobs.get_knob_description(bs4.BeautifulSoup("", features="html.parser"), "foo")
        is None
    )


def test_convert_em_to_underscores():
    # This could include nested tags, but we're not testing BeautfulSoup here.
    test_input = "<em>this</em> <em>many_many</em> <em>condor_daemon_name</em>"
    soup = bs4.BeautifulSoup(test_input, "html.parser")
    knobs.convert_em_to_underscores(soup)
    test_output = soup.text
    assert test_output == "_this_ _many_many_ _condor_daemon_name_"
