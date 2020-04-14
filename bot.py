from typing import List, MutableMapping

from pprint import pprint
import re
import threading
import os
import time

from flask import Flask

from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient

import requests
import bs4 as soup

app = Flask(__name__)


@app.route("/")
def index():
    return "I'm alive!"


SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_CLIENT = SlackClient(SLACK_BOT_TOKEN)


@slack_events_adapter.on("message")
def handle_message_event(event_data):
    pprint(event_data)

    # don't respond to our own messages
    if event_data["event"]["user"] == "U011WEDH24U":
        return

    # TODO: this is bad; we should spin up a thread pool and connect to here via a queue
    threading.Thread(target=lambda: _handle_message(event_data)).start()


def _handle_message(event_data):
    message = event_data["event"]

    for handler in REGEX_HANDLERS:
        matches = handler.regex.findall(message["text"])
        matches = handler.filter_matches(message, matches)

        if len(matches) == 0:
            continue

        try:
            handler.handle_message(SLACK_CLIENT, message, matches)
        except Exception as e:
            print(e)


# TODO: make this an actual metaclass
class RegexMessageHandler:
    def handle_message(self, client: SlackClient, message, matches: List[str]):
        raise NotImplementedError

    def filter_matches(self, message, matches: List[str]):
        return matches


class TicketLinker(RegexMessageHandler):
    def __init__(self, relink_timeout: int):
        self.relink_timeout = relink_timeout

        self.recently_linked_cache: MutableMapping[(str, str), float] = {}
        self.last_ticket_cleanup = time.monotonic()

    def filter_matches(self, message, matches: List[str]):
        now = time.monotonic()
        self._recently_linked_cleanup(now)
        return [
            match
            for match in matches
            if not self.recently_linked(message["channel"], match, now)
        ]

    def recently_linked(self, channel: str, ticket_id: str, now: float):
        key = (channel, ticket_id)
        if key in self.recently_linked_cache:
            return True
        else:
            self.recently_linked_cache[key] = now
            return False

    def _recently_linked_cleanup(self, now: float):
        """
        For a side-project, let's not think too hard.  Just purge our
        memory of old ticket IDs when we handle a new message, rather
        than on a timer in another thread.  Don't bother to scan the
        whole list on every message, though, just if it's been more
        than five seconds since the last clean-up.
        """
        if self.last_ticket_cleanup + self.relink_timeout > now:
            return

        self.recently_linked_cache = {
            _: last_linked
            for _, last_linked in self.recently_linked_cache.items()
            if not last_linked + self.relink_timeout < now
        }
        self.last_ticket_cleanup = now


class FlightworthyTicketLinker(TicketLinker):
    regex = re.compile(r"fw#(\d+)")

    def handle_message(self, client, message, matches: List[str]):
        msgs = []
        for ticket_id in matches:
            url = f"https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn={ticket_id}"

            response = requests.get(url)
            html = soup.BeautifulSoup(response.text, "html.parser")
            title = html.h2.string.split(": ")[-1]
            status = html.find("td", text="Status:").find_next("td").b.string

            msgs.append(f"<{url}|fw#{ticket_id}> | {title} [{status}]")
        msg = "\n".join(msgs)

        post_message(client, channel=message["channel"], text=msg)


class RTTicketLinker(TicketLinker):
    regex = re.compile(r"rt#(\d+)")

    def handle_message(self, client, message, matches):
        msgs = []
        for ticket_id in matches:
            url = f"https://crt.cs.wisc.edu/rt/Ticket/Display.html?id={ticket_id}"
            msgs.append(f"<{url}|rt#{ticket_id}>")
        msg = "\n".join(msgs)

        post_message(client, channel=message["channel"], text=msg)


def post_message(client, *args, **kwargs):
    client.api_call("chat.postMessage", *args, **kwargs)


# TODO: this makes me think we should have a config.py file where things like this list go
RELINK_TIMEOUT = 300
REGEX_HANDLERS = [
    FlightworthyTicketLinker(relink_timeout=RELINK_TIMEOUT),
    RTTicketLinker(relink_timeout=RELINK_TIMEOUT),
]


def startup():
    # TODO: discover channel by name
    post_message(SLACK_CLIENT, channel="G011PN92WTV", text="I'm alive!")
    print("I sent the I'm alive message")


if __name__ == "__main__":
    app.run(port=3000)
