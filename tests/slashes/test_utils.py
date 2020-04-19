import pytest

import bs4

from web.slashes import utils


@pytest.mark.parametrize(
    "converter, html, expected",
    [
        (
            utils.convert_em_to_underscores,
            "<em>this</em> <em>many_many</em> <em>condor_daemon_name</em>",
            "_this_ _many_many_ _condor_daemon_name_",
        ),
        (
            utils.convert_code_to_backticks,
            '<code class="docutils literal notranslate"><span class="pre">MASTER_NAME</span></code>',
            "`MASTER_NAME`",
        ),
        (
            utils.convert_strong_to_stars,
            "<strong>very powerful</strong>",
            "*very powerful*",
        ),
    ],
)
def test_convert_html_to_markdown(converter, html, expected):
    # This could include nested tags, but we're not testing BeautfulSoup here.
    soup = bs4.BeautifulSoup(html, "html.parser")
    converter(soup)
    assert soup.text == expected
