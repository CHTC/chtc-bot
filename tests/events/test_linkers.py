import pytest

import re

from web.events import linkers


def test_generic_ticket_linker_matches():
    linker = linkers.TicketLinker(
        regex=re.compile(r"bot#(\d+)", re.IGNORECASE),
        url="foobar/{}",
        prefix="bot",
        relink_timeout=300,
    )

    matches = linker.get_matches({"text": "bot#1234 bot#55678 help", "channel": "foo"})
    assert matches == ["1234", "55678"]


def test_generic_ticket_linker_message():
    linker = linkers.TicketLinker(
        regex=re.compile(r"bot#(\d+)", re.IGNORECASE),
        url="foobar/{}",
        prefix="bot",
        relink_timeout=300,
    )

    matches = linker.get_matches({"text": "bot#1234 bot#55678 help", "channel": "foo"})
    message = linker.generate_reply(matches)

    assert message == "<foobar/1234|bot#1234>\n<foobar/55678|bot#55678>"


@pytest.mark.parametrize(
    "linker, prefix",
    [
        (linkers.RTTicketLinker(relink_timeout=300), "rt"),
        (linkers.FlightworthyTicketLinker(relink_timeout=300), "gt"),
    ],
)
@pytest.mark.parametrize(
    "message, expected",
    [
        (
            "xt#0755 xt#0x755 xt#1 (xt#0755) (xt#0x755) (xt#2) xt#3, xt#4; xt#5. xt#6! xt#7",
            ("1", "2", "3", "4", "5", "6", "7"),
        ),
        ("xt#0755", ()),
        ("xt#0x755", ()),
        (
            "xt#1111 (xt#2222) xt#3333, xt#4444; xt#5555. xt#6666! xt#7777",
            ("1111", "2222", "3333", "4444", "5555", "6666", "7777"),
        ),
        (
            "xt#755x xt#755x! xt#8888 random other text *xt#9999* _xt#1010_",
            ("8888", "9999", "1010"),
        ),
    ],
)
def test_linker_matches(linker, prefix, message, expected):
    message = message.replace("xt", prefix)
    matches = linker.get_matches({"text": message, "channel": "foo"})
    assert len(matches) == len(expected)
    for (match, expect) in zip(matches, expected):
        assert match == expect


@pytest.mark.parametrize(
    "message, expected",
    [
        (
            {"text": "bot#1", "channel": "1234"},
            {"text": "<foobar/1|bot#1>", "channel": "1234", "thread_ts": None},
        ),
        (
            {"text": "bot#1", "channel": "1234", "thread_ts": "1.2"},
            {"text": "<foobar/1|bot#1>", "channel": "1234", "thread_ts": "1.2"},
        ),
    ],
)
def test_generic_linker_end_to_end(mocker, message, expected):
    mock = mocker.patch("web.slack.post_message")

    linker = linkers.TicketLinker(
        regex=re.compile(r"bot#(\d+)", re.IGNORECASE),
        url="foobar/{}",
        prefix="bot",
        relink_timeout=300,
    )

    linker.handle(message)

    assert mock.call_count == 1

    args, kwargs = mock.call_args

    assert kwargs == expected
