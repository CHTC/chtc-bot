import pytest

import time
import textwrap

import bs4

@pytest.fixture
def kch():
    from web.slashes import commands

    return commands.KnobsCommandHandler(relink_timeout=300)


def test_get_description_returns_none_if_it_fails_to_find_the_knob(kch):
    assert (
        kch.get_description(
            bs4.BeautifulSoup("", features="html.parser"), "foo"
        )
        is None
    )


# This is a big blob of sample text taken from the HTCondor manual HTML.
# If that format ever changes, tests that depend on this will need to change as well!
KNOB_HTML = textwrap.dedent(
    """
    <dt><span class="macro-def target" id="CREATE_CORE_FILES">CREATE_CORE_FILES</span></dt>
    <dd>Defines whether or not HTCondor daemons are to create a core file in
    the <code class="docutils literal notranslate"><span class="pre">LOG</span></code> <span class="target" id="index-18"></span>  directory if something really bad
    happens. It is used to set the resource limit for the size of a core
    file. If not defined, it leaves in place whatever limit was in
    effect when the HTCondor daemons (normally the <em>condor_master</em>)
    were started. This allows HTCondor to inherit the default system
    core file generation behavior at start up. For Unix operating
    systems, this behavior can be inherited from the parent shell, or
    specified in a shell script that starts HTCondor. If this parameter
    is set and <code class="docutils literal notranslate"><span class="pre">True</span></code>, the limit is increased to the maximum. If it is
    set to <code class="docutils literal notranslate"><span class="pre">False</span></code>, the limit is set at 0 (which means that no core
    files are created). Core files greatly help the HTCondor developers
    debug any problems you might be having. By using the parameter, you
    do not have to worry about tracking down where in your boot scripts
    you need to set the core limit before starting HTCondor. You set the
    parameter to whatever behavior you want HTCondor to enforce. This
    parameter defaults to undefined to allow the initial operating
    system default value to take precedence, and is commented out in the
    default configuration file.</dd>
    <dt><span class="macro-def target" id="CKPT_PROBE">CKPT_PROBE</span></dt>
    <dd>Defines the path and executable name of the helper process HTCondor
    will use to determine information for the <code class="docutils literal notranslate"><span class="pre">CheckpointPlatform</span></code>
    attribute in the machine’s ClassAd. The default value is
    <code class="docutils literal notranslate"><span class="pre">$(LIBEXEC)/condor_ckpt_probe</span></code>.</dd>
    <dt><span class="macro-def target" id="ABORT_ON_EXCEPTION">ABORT_ON_EXCEPTION</span></dt>
    <dd>When HTCondor programs detect a fatal internal exception, they
    normally log an error message and exit. If you have turned on
    <code class="docutils literal notranslate"><span class="pre">CREATE_CORE_FILES</span></code> <span class="target" id="index-19"></span> , in some
    cases you may also want to turn on <code class="docutils literal notranslate"><span class="pre">ABORT_ON_EXCEPTION</span></code>
    <span class="target" id="index-20"></span>  so that core files are generated
    when an exception occurs. Set the following to True if that is what
    you want.</dd>
    <dt><span class="macro-def target" id="Q_QUERY_TIMEOUT">Q_QUERY_TIMEOUT</span></dt>
    <dd>Defines the timeout (in seconds) that <em>condor_q</em> uses when trying
    to connect to the <em>condor_schedd</em>. Defaults to 20 seconds.</dd>
    """
).strip()
KNOB_SOUP = bs4.BeautifulSoup(KNOB_HTML, "html.parser")


@pytest.mark.parametrize(
    "knob, expected",
    [
        (
            "CKPT_PROBE",
            """
            *CKPT_PROBE*
            >Defines the path and executable name of the helper process HTCondor will use to determine information for the `CheckpointPlatform` attribute in the machine’s ClassAd. The default value is `$(LIBEXEC)/condor_ckpt_probe`.
            """,
        ),
        ("NOPE", None),
    ],
)
def test_get_knob_description(kch, knob, expected):
    # clean up the triple-quoted string
    expected = textwrap.dedent(expected).strip() if expected is not None else expected

    assert kch.get_description(KNOB_SOUP, knob) == expected


@pytest.mark.parametrize("memory", [False, True])
def test_handle_knobs_end_to_end(mocker, client, memory):
    mock_get_url = mocker.patch("web.http.cached_get_url")
    mock_get_url.return_value.text = KNOB_HTML

    mock = mocker.patch("web.slack.post_message")

    client.post(
        "/slash/knobs", data=dict(channel_id="1234", user_id="5678", text="CKPT_PROBE"),
    )

    # let the executor run
    # Strictly speaking, this should (a) depend on the memory_time value
    # and (b) poll until the executor signals that it has run.
    time.sleep(0.1)

    if not memory:
        assert mock.call_count == 1
        channel = mock.call_args[1]["channel"]
        assert channel == "1234"
        msg = mock.call_args[1]["text"]

        # make a few assertions about the output message,
        # but without holding on too tight
        assert "<@5678>" in msg
        assert "CKPT_PROBE" in msg
        assert "helper process HTCondor" in msg
        assert "Q_QUERY_TIMEOUT" not in msg
    else:
        assert mock.call_count == 0
