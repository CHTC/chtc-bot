import pytest

import bs4

from web.slashes import jobads


def test_get_attrs_description_returns_none_if_it_fails_to_find_the_knob():
    assert (
        jobads.get_attrs_description(
            bs4.BeautifulSoup("", features="html.parser"), "foo"
        )
        is None
    )


@pytest.mark.parametrize(
    "converter, html, expected",
    [
        (
            jobads.convert_links_to_links,
            """<a class="reference internal" href="../admin-manual/user-priorities-negotiation.html"><span class="doc">User Priorities and Negotiation</span></a>""",
            f"<{jobads.ATTRS_URL}../admin-manual/user-priorities-negotiation.html|User Priorities and Negotiation>",
        ),
    ],
)
def test_convert_html_to_markdown(converter, html, expected):
    # This could include nested tags, but we're not testing BeautfulSoup here.
    soup = bs4.BeautifulSoup(html, "html.parser")
    converter(soup)
    assert soup.text == expected
