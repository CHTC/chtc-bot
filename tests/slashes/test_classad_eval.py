import pytest

import htcondor
import classad

from web.slashes import classad_eval


@pytest.mark.parametrize(
    "text, expected",
    [
        (
            "'[ foo = 5 ]' 'foo'",
            (classad.ClassAd({"foo": 5}), [classad.ExprTree("foo")]),
        ),
        (
            "'[ foo = \"bar\" ]' 'foo' 'bar'",
            (
                classad.ClassAd({"foo": "bar"}),
                [classad.ExprTree("foo"), classad.ExprTree("bar")],
            ),
        ),
        (
            "'[ foo = bar ]' 'foo' 'bar'",
            (
                classad.ClassAd({"foo": classad.ExprTree("bar")}),
                [classad.ExprTree("foo"), classad.ExprTree("bar")],
            ),
        ),
        ("'[ ]' '1 + 1'", (classad.ClassAd({}), [classad.ExprTree("1 + 1")])),
    ],
)
def test_parsing(text, expected):
    parsed_ad, parsed_exprs = classad_eval.parse(text)

    expected_ad, expected_exprs = expected

    assert {k: str(v) for k, v in parsed_ad.items()} == {
        k: str(v) for k, v in expected_ad.items()
    }
    assert all(p.sameAs(e) for p, e in zip(parsed_exprs, expected_exprs))


@pytest.mark.parametrize(
    "ad, exprs, expected",
    [
        (classad.ClassAd({"foo": 5}), [classad.ExprTree("foo")], [5]),
        (
            classad.ClassAd({"foo": 5, "bar": classad.ExprTree("foo + 1")}),
            [classad.ExprTree("foo"), classad.ExprTree("bar")],
            [5, 6],
        ),
    ],
)
def test_evaluating(ad, exprs, expected):
    assert list(classad_eval.evaluate(ad, exprs).values()) == expected
