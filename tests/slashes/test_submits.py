import pytest

import time
import textwrap

import bs4

from web.slashes import submits


def test_get_submits_description_returns_none_if_it_fails_to_find_the_knob():
    assert (
        submits.get_submits_description(
            bs4.BeautifulSoup("", features="html.parser"), "foo"
        )
        is None
    )


# This is a big blob of sample text taken from the HTCondor manual HTML.
# If that format ever changes, tests that depend on this will need to change as well!
SUBMITS_HTML = textwrap.dedent(
    """
    <div class="section" id="submit-description-file-commands">
    <h2>Submit Description File Commands<a class="headerlink" href="#submit-description-file-commands" title="Permalink to this headline">¶</a></h2>
    <p><span class="target" id="index-12"></span> </p>
    <p>Note: more information on submitting HTCondor jobs can be found here:
    <a class="reference internal" href="../users-manual/submitting-a-job.html"><span class="doc">Submitting a Job</span></a>.</p>
    <p>As of version 8.5.6, the <em>condor_submit</em> language supports multi-line
    values in commands. The syntax is the same as the configuration language
    (see more details here:
    <a class="reference internal" href="../admin-manual/introduction-to-configuration.html#multi-line-values"><span class="std std-ref">Multi-Line Values</span></a>).</p>
    <p>Each submit description file describes one or more clusters of jobs to
    be placed in the HTCondor execution pool. All jobs in a cluster must
    share the same executable, but they may have different input and output
    files, and different program arguments. The submit description file is
    generally the last command-line argument to <em>condor_submit</em>. If the
    submit description file argument is omitted, <em>condor_submit</em> will read
    the submit description from standard input.</p>
    <p>The submit description file must contain at least one <em>executable</em>
    command and at least one <em>queue</em> command. All of the other commands have
    default actions.</p>
    <p><strong>Note that a submit file that contains more than one executable command
    will produce multiple clusters when submitted. This is not generally
    recommended, and is not allowed for submit files that are run as DAG node
    jobs by condor_dagman.</strong></p>
    <p>The commands which can appear in the submit description file are
    numerous. They are listed here in alphabetical order by category.</p>
    <p>BASIC COMMANDS <span class="target" id="index-13"></span> </p>
    <blockquote>
    <div><dl class="docutils">
    <dt>arguments = &lt;argument_list&gt;</dt>
    <dd><p class="first">List of arguments to be supplied to the executable as part of the
    command line.</p>
    <p>In the <strong>java</strong> universe, the first argument must be the name of the
    class containing <code class="docutils literal notranslate"><span class="pre">main</span></code>.</p>
    <p>There are two permissible formats for specifying arguments,
    identified as the old syntax and the new syntax. The old syntax
    supports white space characters within arguments only in special
    circumstances; when used, the command line arguments are represented
    in the job ClassAd attribute <code class="docutils literal notranslate"><span class="pre">Args</span></code>. The new syntax supports
    uniform quoting of white space characters within arguments; when
    used, the command line arguments are represented in the job ClassAd
    attribute <code class="docutils literal notranslate"><span class="pre">Arguments</span></code>.</p>
    <p><strong>Old Syntax</strong></p>
    <p>In the old syntax, individual command line arguments are delimited
    (separated) by space characters. To allow a double quote mark in an
    argument, it is escaped with a backslash; that is, the two character
    sequence &quot; becomes a single double quote mark within an argument.</p>
    <p>Further interpretation of the argument string differs depending on
    the operating system. On Windows, the entire argument string is
    passed verbatim (other than the backslash in front of double quote
    marks) to the Windows application. Most Windows applications will
    allow spaces within an argument value by surrounding the argument
    with double quotes marks. In all other cases, there is no further
    interpretation of the arguments.</p>
    <p>Example:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">arguments</span> <span class="o">=</span> <span class="n">one</span> \\<span class="s2">&quot;two</span><span class="se">\\&quot;</span><span class="s2"> &#39;three&#39;</span>
    </pre></div>
    </div>
    <p>Produces in Unix vanilla universe:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">argument</span> <span class="mi">1</span><span class="p">:</span> <span class="n">one</span>
    <span class="n">argument</span> <span class="mi">2</span><span class="p">:</span> <span class="s2">&quot;two&quot;</span>
    <span class="n">argument</span> <span class="mi">3</span><span class="p">:</span> <span class="s1">&#39;three&#39;</span>
    </pre></div>
    </div>
    <p><strong>New Syntax</strong></p>
    <p>Here are the rules for using the new syntax:</p>
    <ol class="arabic simple">
    <li>The entire string representing the command line arguments is
    surrounded by double quote marks. This permits the white space
    characters of spaces and tabs to potentially be embedded within a
    single argument. Putting the double quote mark within the
    arguments is accomplished by escaping it with another double
    quote mark.</li>
    <li>The white space characters of spaces or tabs delimit arguments.</li>
    <li>To embed white space characters of spaces or tabs within a single
    argument, surround the entire argument with single quote marks.</li>
    <li>To insert a literal single quote mark, escape it within an
    argument already delimited by single quote marks by adding
    another single quote mark.</li>
    </ol>
    <p>Example:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">arguments</span> <span class="o">=</span> <span class="s2">&quot;3 simple arguments&quot;</span>
    </pre></div>
    </div>
    <p>Produces:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">argument</span> <span class="mi">1</span><span class="p">:</span> <span class="mi">3</span>
    <span class="n">argument</span> <span class="mi">2</span><span class="p">:</span> <span class="n">simple</span>
    <span class="n">argument</span> <span class="mi">3</span><span class="p">:</span> <span class="n">arguments</span>
    </pre></div>
    </div>
    <p>Another example:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">arguments</span> <span class="o">=</span> <span class="s2">&quot;one &#39;two with spaces&#39; 3&quot;</span>
    </pre></div>
    </div>
    <p>Produces:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">argument</span> <span class="mi">1</span><span class="p">:</span> <span class="n">one</span>
    <span class="n">argument</span> <span class="mi">2</span><span class="p">:</span> <span class="n">two</span> <span class="k">with</span> <span class="n">spaces</span>
    <span class="n">argument</span> <span class="mi">3</span><span class="p">:</span> <span class="mi">3</span>
    </pre></div>
    </div>
    <p>And yet another example:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">arguments</span> <span class="o">=</span> <span class="s2">&quot;one &quot;&quot;two&quot;&quot; &#39;spacey &#39;&#39;quoted&#39;&#39; argument&#39;&quot;</span>
    </pre></div>
    </div>
    <p>Produces:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">argument</span> <span class="mi">1</span><span class="p">:</span> <span class="n">one</span>
    <span class="n">argument</span> <span class="mi">2</span><span class="p">:</span> <span class="s2">&quot;two&quot;</span>
    <span class="n">argument</span> <span class="mi">3</span><span class="p">:</span> <span class="n">spacey</span> <span class="s1">&#39;quoted&#39;</span> <span class="n">argument</span>
    </pre></div>
    </div>
    <p class="last">Notice that in the new syntax, the backslash has no special meaning.
    This is for the convenience of Windows users.
    <span class="target" id="index-14"></span> </p>
    </dd>
    <dt>environment = &lt;parameter_list&gt;</dt>
    <dd><p class="first">List of environment
    <span class="target" id="index-15"></span> variables.</p>
    <p>There are two different formats for specifying the environment
    variables: the old format and the new format. The old format is
    retained for backward-compatibility. It suffers from a
    platform-dependent syntax and the inability to insert some special
    characters into the environment.</p>
    <p>The new syntax for specifying environment values:</p>
    <ol class="arabic">
    <li><p class="first">Put double quote marks around the entire argument string. This
    distinguishes the new syntax from the old. The old syntax does
    not have double quote marks around it. Any literal double quote
    marks within the string must be escaped by repeating the double
    quote mark.</p>
    </li>
    <li><p class="first">Each environment entry has the form</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="o">&lt;</span><span class="n">name</span><span class="o">&gt;=&lt;</span><span class="n">value</span><span class="o">&gt;</span>
    </pre></div>
    </div>
    </li>
    <li><p class="first">Use white space (space or tab characters) to separate environment
    entries.</p>
    </li>
    <li><p class="first">To put any white space in an environment entry, surround the
    space and as much of the surrounding entry as desired with single
    quote marks.</p>
    </li>
    <li><p class="first">To insert a literal single quote mark, repeat the single quote
    mark anywhere inside of a section surrounded by single quote
    marks.</p>
    </li>
    </ol>
    <p>Example:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">environment</span> <span class="o">=</span> <span class="s2">&quot;one=1 two=&quot;&quot;2&quot;&quot; three=&#39;spacey &#39;&#39;quoted&#39;&#39; value&#39;&quot;</span>
    </pre></div>
    </div>
    <p>Produces the following environment entries:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">one</span><span class="o">=</span><span class="mi">1</span>
    <span class="n">two</span><span class="o">=</span><span class="s2">&quot;2&quot;</span>
    <span class="n">three</span><span class="o">=</span><span class="n">spacey</span> <span class="s1">&#39;quoted&#39;</span> <span class="n">value</span>
    </pre></div>
    </div>
    <p>Under the old syntax, there are no double quote marks surrounding
    the environment specification. Each environment entry remains of the
    form</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="o">&lt;</span><span class="n">name</span><span class="o">&gt;=&lt;</span><span class="n">value</span><span class="o">&gt;</span>
    </pre></div>
    </div>
    <p>Under Unix, list multiple environment entries by separating them
    with a semicolon (;). Under Windows, separate multiple entries with
    a vertical bar (|). There is no way to insert a literal semicolon
    under Unix or a literal vertical bar under Windows. Note that spaces
    are accepted, but rarely desired, characters within parameter names
    and values, because they are treated as literal characters, not
    separators or ignored white space. Place spaces within the parameter
    list only if required.</p>
    <p>A Unix example:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">environment</span> <span class="o">=</span> <span class="n">one</span><span class="o">=</span><span class="mi">1</span><span class="p">;</span><span class="n">two</span><span class="o">=</span><span class="mi">2</span><span class="p">;</span><span class="n">three</span><span class="o">=</span><span class="s2">&quot;quotes have no &#39;special&#39; meaning&quot;</span>
    </pre></div>
    </div>
    <p>This produces the following:</p>
    <div class="highlight-default notranslate"><div class="highlight"><pre><span></span><span class="n">one</span><span class="o">=</span><span class="mi">1</span>
    <span class="n">two</span><span class="o">=</span><span class="mi">2</span>
    <span class="n">three</span><span class="o">=</span><span class="s2">&quot;quotes have no &#39;special&#39; meaning&quot;</span>
    </pre></div>
    </div>
    <p class="last">If the environment is set with the
    <strong>environment</strong> <span class="target" id="index-16"></span> 
    command and <strong>getenv</strong> <span class="target" id="index-17"></span>  is
    also set to true, values specified with <strong>environment</strong> override
    values in the submitter’s environment (regardless of the order of
    the <strong>environment</strong> and <strong>getenv</strong> commands).
    <span class="target" id="index-18"></span> </p>
    </dd>
    <dt>error = &lt;pathname&gt;</dt>
    <dd>A path and file name used by HTCondor to capture any error messages
    the program would normally write to the screen (that is, this file
    becomes <code class="docutils literal notranslate"><span class="pre">stderr</span></code>). A path is given with respect to the file system
    of the machine on which the job is submitted. The file is written
    (by the job) in the remote scratch directory of the machine where
    the job is executed. When the job exits, the resulting file is
    transferred back to the machine where the job was submitted, and the
    path is utilized for file placement. If not specified, the default
    value of <code class="docutils literal notranslate"><span class="pre">/dev/null</span></code> is used for submission to a Unix machine. If
    not specified, error messages are ignored for submission to a
    Windows machine. More than one job should not use the same error
    file, since this will cause one job to overwrite the errors of
    another. If HTCondor detects that the error and output files for a
    job are the same, it will run the job such that the output and error
    data is merged. <span class="target" id="index-19"></span> </dd>
    <dt>executable = &lt;pathname&gt;</dt>
    <dd><p class="first">An optional path and a required file name of the executable file for
    this job cluster. Only one
    <strong>executable</strong> <span class="target" id="index-20"></span>  command
    within a submit description file is guaranteed to work properly.
    More than one often works.</p>
    <p class="last">If no path or a relative path is used, then the executable file is
    presumed to be relative to the current working directory of the user
    as the <em>condor_submit</em> command is issued.</p>
    </dd>
        """
).strip()
SUBMITS_SOUP = bs4.BeautifulSoup(SUBMITS_HTML, "html.parser")


@pytest.mark.parametrize(
    "submit, expected",
    [
        (
            "error",
            """
            *error = <pathname>*
            >A path and file name used by HTCondor to capture any error messages the program would normally write to the screen (that is, this file becomes `stderr`). A path is given with respect to the file system of the machine on which the job is submitted. The file is written (by the job) in the remote scratch directory of the machine where the job is executed. When the job exits, the resulting file is transferred back to the machine where the job was submitted, and the path is utilized for file placement. If not specified, the default value of `/dev/null` is used for submission to a Unix machine. If not specified, error messages are ignored for submission to a Windows machine. More than one job should not use the same error file, since this will cause one job to overwrite the errors of another. If HTCondor detects that the error and output files for a job are the same, it will run the job such that the output and error data is merged.
            """,
        ),
        ("NOPE", None),
    ],
)
def test_get_submits_description(submit, expected):
    # clean up the triple-quoted string
    expected = textwrap.dedent(expected).strip() if expected is not None else expected

    assert submits.get_submits_description(SUBMITS_SOUP, submit) == expected


@pytest.mark.parametrize(
    "memory", [ False, True ]
)
def test_handle_submits_end_to_end(mocker, client, memory):
    mock_get_url = mocker.patch("web.http.cached_get_url")
    mock_get_url.return_value.text = SUBMITS_HTML

    mock = mocker.patch("web.slack.post_message")

    client.post(
        "/slash/submits", data=dict(channel_id="1234", user_id="5678", text="error"),
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
        assert "error" in msg
        assert "the resulting file is transferred back" in msg
        assert "stream_error" not in msg
    else:
        assert mock.call_count == 0
