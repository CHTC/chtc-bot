import pytest

import bs4

from web.slashes import knobs


def test_get_knob_description_returns_none_if_it_fails_to_find_the_knob():
    assert (
        knobs.get_knob_description(bs4.BeautifulSoup("", features="html.parser"), "foo")
        is None
    )


@pytest.mark.parametrize(
    "converter, html, expected",
    [
        (
            knobs.convert_em_to_underscores,
            "<em>this</em> <em>many_many</em> <em>condor_daemon_name</em>",
            "_this_ _many_many_ _condor_daemon_name_",
        ),
        (
            knobs.convert_code_to_backticks,
            '<code class="docutils literal notranslate"><span class="pre">MASTER_NAME</span></code>',
            "`MASTER_NAME`",
        ),
    ],
)
def test_convert_html_to_markdown(converter, html, expected):
    # This could include nested tags, but we're not testing BeautfulSoup here.
    soup = bs4.BeautifulSoup(html, "html.parser")
    converter(soup)
    assert soup.text == expected
