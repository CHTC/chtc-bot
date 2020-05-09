import pytest

import time

import htcondor
import classad

from web.commands import classad_eval


@pytest.mark.parametrize(
    "text, expected",
    [
        (
            "'[ foo = 5 ]' 'foo'",
            [classad.ClassAd({"foo": 5}), classad.ExprTree("foo")],
        ),
        (
            "'[ foo = \"bar\" ]' 'foo' 'bar'",
            [
                classad.ClassAd({"foo": "bar"}),
                classad.ExprTree("foo"),
                classad.ExprTree("bar"),
            ],
        ),
        (
            "'[ foo = bar ]' 'foo' 'bar'",
            [
                classad.ClassAd({"foo": classad.ExprTree("bar")}),
                classad.ExprTree("foo"),
                classad.ExprTree("bar"),
            ],
        ),
        ("'[]' '1 + 1'", [classad.ClassAd(), classad.ExprTree("1 + 1")]),
        ("'' '1 + 1'", [classad.ClassAd(), classad.ExprTree("1 + 1")]),
        (
            "'foo = 1' 'foo + 1'",
            [classad.ClassAd({"foo": 1}), classad.ExprTree("foo + 1")],
        ),
        (
            "'foo = 1; bar = 2' 'foo + 1'",
            [classad.ClassAd({"foo": 1, "bar": 2}), classad.ExprTree("foo + 1")],
        ),
        (
            "'[ foo = 1; bar = 2] ' 'foo + 1'",
            [classad.ClassAd({"foo": 1, "bar": 2}), classad.ExprTree("foo + 1")],
        ),
        (
            "'a = 1' 'b = 2' 'a > b'",
            [
                classad.ClassAd({"a": 1}),
                classad.ClassAd({"b": 2}),
                classad.ExprTree("a > b"),
            ],
        ),
    ],
)
def test_parsing(text, expected):
    parsed = classad_eval.parse(text)

    assert all(
        p.sameAs(e) if isinstance(e, classad.ExprTree) else ads_equal(p, e)
        for p, e in zip(parsed, expected)
    )


def ads_equal(a, b):
    return {k: str(v) for k, v in a.items()} == {k: str(v) for k, v in b.items()}


@pytest.mark.parametrize(
    "text", ["'[foo]'", "'[foo = 1]' '^'",],
)
def test_bad_parsing(text):
    with pytest.raises(SyntaxError):
        classad_eval.parse(text)


@pytest.mark.parametrize(
    "ads_and_exprs, expected",
    [
        (
            [classad.ClassAd({"foo": 5}), classad.ExprTree("foo")],
            [classad.ClassAd({"foo": 5}), (classad.ExprTree("foo"), 5),],
        )
    ],
)
def test_evaluating(ads_and_exprs, expected):
    evaluated = classad_eval.evaluate(ads_and_exprs)

    print(evaluated)

    for p, e in zip(evaluated, expected):
        if isinstance(e, classad.ClassAd):
            assert ads_equal(p, e)
        else:
            pk, pv = p
            ek, ev = e

            assert pk.sameAs(ek)
            assert pv == ev


@pytest.mark.parametrize(
    "text, in_msg",
    [
        ("'[foo = 5]' 'foo' 'bar' '1 + 1'", ["foo = 5", "undefined", "2"]),
        (
            "'foo = 5' 'foo - 1' 'bar = 1' 'foo + bar'",
            ["foo = 5", "Ad", "bar = 1", "Ad modified", "6", "4"],
        ),
        ("'* 123'", ["Failed"]),
    ],
)
def test_handle_classad_eval_end_to_end(mocker, client, text, in_msg):
    mock = mocker.patch("web.slack.post_message")

    client.post(
        "/slash/classad_eval", data=dict(channel_id="1234", user_id="5678", text=text),
    )

    # let the executor run
    time.sleep(0.1)

    assert mock.call_count == 1

    channel = mock.call_args[1]["channel"]

    assert channel == "1234"

    msg = mock.call_args[1]["text"]

    print(msg)

    # make a few assertions about the output message,
    # but without holding on too tight
    assert all(i in msg for i in in_msg)


# Upgrading to HTCondor 8.9.8 will get us access to GT#7607, which will
# cause certain problems with bad expression to go away (e.g., 'x = y'
# should not be parsed as 'x' and '123x' as '123').
