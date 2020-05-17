import pytest

from web import rss

@pytest.mark.parametrize("input, expected, rssCH", [
        (
            { 'title': 'Check-in [59661]:   (By Tim Theisen )',
              'summary': '(<span class="ticket"><a href="https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn=7643" class="new" title="Get HTCondor to build on Modern Fedora without warnings">#7643</a></span>) Fix compiler warning where strncpy count depends on source <br>',
              'link': 'https://htcondor-wiki.cs.wisc.edu/index.cgi/chngview?cn=59661',
            },
            '<https://htcondor-wiki.cs.wisc.edu/index.cgi/chngview?cn=59661|Check-in [59661]:   (By Tim Theisen )>\n(<https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn=7643|#7643>) Fix compiler warning where strncpy count depends on source',
            rss.RSSCommandHandler()
        )
    ]
)
def test_rss_get_description(input, expected, rssCH):
    assert rssCH.get_description(input) == expected
