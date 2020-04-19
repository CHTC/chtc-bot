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
