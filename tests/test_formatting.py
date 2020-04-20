import pytest

import bs4

import os

from web import formatting


@pytest.mark.parametrize("input, expected", [("foo", "*foo*")])
def test_bold(input, expected):
    assert formatting.bold(input) == expected


@pytest.mark.parametrize("input, expected", [("foo", "_foo_")])
def test_italic(input, expected):
    assert formatting.italic(input) == expected


@pytest.mark.parametrize("input, expected", [("foo", "`foo`")])
def test_fixed(input, expected):
    assert formatting.fixed(input) == expected


ATTRS_URL = "https://htcondor.readthedocs.io/en/latest/classad-attributes/job-classad-attributes.html"
KNOBS_URL = (
    "https://htcondor.readthedocs.io/en/latest/admin-manual/configuration-macros.html"
)


@pytest.mark.parametrize(
    "converter, html, expected",
    [
        (
            formatting.inplace_convert_em_to_underscores,
            "<em>this</em> <em>many_many</em> <em>condor_daemon_name</em>",
            "_this_ _many_many_ _condor_daemon_name_",
        ),
        (
            formatting.inplace_convert_code_to_backticks,
            '<code class="docutils literal notranslate"><span class="pre">MASTER_NAME</span></code>',
            "`MASTER_NAME`",
        ),
        (
            formatting.inplace_convert_strong_to_stars,
            "<strong>very powerful</strong>",
            "*very powerful*",
        ),
        (
            lambda soup: formatting.inplace_convert_internal_links_to_links(
                soup, KNOBS_URL, "std.std-ref"
            ),
            """<a class="reference internal" href="#condor-master-configuration-file-macros"><span class="std std-ref">condor_master Configuration File Macros</span></a>""",
            f"<{KNOBS_URL}#condor-master-configuration-file-macros|condor_master Configuration File Macros>",
        ),
        (
            lambda soup: formatting.inplace_convert_internal_links_to_links(
                soup, os.path.dirname(ATTRS_URL), "doc"
            ),
            """<a class="reference internal" href="../admin-manual/user-priorities-negotiation.html"><span class="doc">User Priorities and Negotiation</span></a>""",
            f"<{os.path.dirname(ATTRS_URL)}/../admin-manual/user-priorities-negotiation.html|User Priorities and Negotiation>",
        ),
        (
            formatting.inplace_convert_code_to_code,
            """<div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="o">&lt;</span><span class="n">name</span><span class="o">&gt;=&lt;</span><span class="n">value</span><span class="o">&gt;</span></pre></div>""",
            "```<name>=<value>```",
        ),
    ],
)
def test_convert_html_to_markdown(converter, html, expected):
    # This could include nested tags, but we're not testing BeautfulSoup here.
    soup = bs4.BeautifulSoup(html, "html.parser")
    converter(soup)
    assert soup.text == expected
