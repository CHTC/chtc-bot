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
        (
            knobs.convert_strong_to_stars,
            "<strong>very powerful</strong>",
            "*very powerful*",
        ),
        (
            knobs.convert_links_to_links,
            """<a class="reference internal" href="#condor-master-configuration-file-macros"><span class="std std-ref">condor_master Configuration File Macros</span></a>""",
            f"<{knobs.KNOBS_URL}#condor-master-configuration-file-macros|condor_master Configuration File Macros>",
        ),
    ],
)
def test_convert_html_to_markdown(converter, html, expected):
    # This could include nested tags, but we're not testing BeautfulSoup here.
    soup = bs4.BeautifulSoup(html, "html.parser")
    converter(soup)
    assert soup.text == expected
