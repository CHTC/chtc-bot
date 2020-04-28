import pytest

import time
import textwrap

import bs4

from web.commands import scrapers


@pytest.fixture
def jch():
    return scrapers.JobAdsCommandHandler(rescrape_timeout=300)


def test_get_description_returns_none_if_it_fails_to_find_the_attr(jch):
    assert (
        jch.get_description(bs4.BeautifulSoup("", features="html.parser"), "foo")
        is None
    )


# This is a big blob of sample text taken from the HTCondor manual HTML.
# If that format ever changes, tests that depend on this will need to change as well!
ATTRS_HTML = textwrap.dedent(
    """
    <dt><code class="docutils literal notranslate"><span class="pre">AcctGroup</span></code></dt>
    <dd>The accounting group name, as set in the submit description file via
    the
    <strong>accounting_group</strong> <span class="target" id="index-5"></span> 
    command. This attribute is only present if an accounting group was
    requested by the submission. See the <a class="reference internal" href="../admin-manual/user-priorities-negotiation.html"><span class="doc">User Priorities and Negotiation</span></a> section
    for more information about accounting groups.
    <span class="target" id="index-6"></span> 
    <span class="target" id="index-7"></span> </dd>
    <dt><code class="docutils literal notranslate"><span class="pre">AcctGroupUser</span></code></dt>
    <dd>The user name associated with the accounting group. This attribute
    is only present if an accounting group was requested by the
    submission. <span class="target" id="index-8"></span> 
    <span class="target" id="index-9"></span> </dd>
    <dt><code class="docutils literal notranslate"><span class="pre">AllRemoteHosts</span></code></dt>
    <dd>String containing a comma-separated list of all the remote machines
    running a parallel or mpi universe job.
    <span class="target" id="index-10"></span> 
    <span class="target" id="index-11"></span> </dd>
    <dt><code class="docutils literal notranslate"><span class="pre">Args</span></code></dt>
    <dd>A string representing the command line arguments passed to the job,
    when those arguments are specified using the old syntax, as
    specified in
    the <a class="reference internal" href="../man-pages/condor_submit.html"><span class="doc">condor_submit</span></a> section.
    <span class="target" id="index-12"></span> 
    <span class="target" id="index-13"></span> </dd>
    <dt><code class="docutils literal notranslate"><span class="pre">Arguments</span></code></dt>
    <dd>A string representing the command line arguments passed to the job,
    when those arguments are specified using the new syntax, as
    specified in
    the <a class="reference internal" href="../man-pages/condor_submit.html"><span class="doc">condor_submit</span></a> section.
    <span class="target" id="index-14"></span> 
    <span class="target" id="index-15"></span> </dd>
    """
).strip()
ATTRS_SOUP = bs4.BeautifulSoup(ATTRS_HTML, "html.parser")


@pytest.mark.parametrize(
    "attr, expected",
    [
        (
            "AcctGroupUser",
            """
            *AcctGroupUser*
            >The user name associated with the accounting group. This attribute is only present if an accounting group was requested by the submission.
            """,
        ),
        ("NOPE", None),
    ],
)
def test_get_description(jch, attr, expected):
    # clean up the triple-quoted string
    expected = textwrap.dedent(expected).strip() if expected is not None else expected

    assert jch.get_description(ATTRS_SOUP, attr) == expected


@pytest.mark.parametrize("memory", [False, True])
@pytest.mark.parametrize("channel_id", ["1234", "4321"])
def test_handle_jobads_end_to_end(mocker, client, memory, channel_id):
    mock_get_url = mocker.patch("web.http.cached_get_url")
    mock_get_url.return_value.text = ATTRS_HTML

    mock = mocker.patch("web.slack.post_message")

    client.post(
        "/slash/jobads",
        data=dict(channel_id=channel_id, user_id="5678", text="AcctGroupUser"),
    )

    # let the executor run
    # Strictly speaking, this should (a) depend on the memory_time value
    # and (b) poll until the executor signals that it has run.
    time.sleep(0.1)

    if not memory:
        assert mock.call_count == 1
        channel = mock.call_args[1]["channel"]
        assert channel == channel_id
        msg = mock.call_args[1]["text"]

        # make a few assertions about the output message,
        # but without holding on too tight
        assert "<@5678>" in msg
        assert "AcctGroupUser" in msg
        assert "user name associated" in msg
        assert "AllRemoteHosts" not in msg
    else:
        assert mock.call_count == 0
