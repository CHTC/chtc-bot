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

BOT_USER_ID = "U011WEDH24U"


@slack_events_adapter.on("message")
def handle_message_event(event_data):
    pprint(event_data)

    # skip edits
    if event_data["event"].get("subtype") == "message_changed":
        return

    # don't respond to our own messages
    if event_data["event"].get("user") == BOT_USER_ID:
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
        key = (channel, ticket_id.lower())
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

    def handle_message(self, client: SlackClient, message, matches: List[str]):
        msgs = []
        for ticket_id in matches:
            url = self.url.format(ticket_id)

            msg = f"<{url}|{self.prefix}#{ticket_id}>"

            summary = self.get_ticket_summary(url)
            if summary is not None:
                msg += f" | {summary}"

            msgs.append(msg)

        post_message(client, channel=message["channel"], text="\n".join(msgs))

    def get_ticket_summary(self, url: str):
        return None


# Message formatting: https://api.slack.com/reference/surfaces/formatting


class FlightworthyTicketLinker(TicketLinker):
    regex = re.compile(r"gt#(\d+)", re.I)
    url = "https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn={}"
    prefix = "GT"

    def get_ticket_summary(self, url: str):
        response = requests.get(url)
        html = soup.BeautifulSoup(response.text, "html.parser")

        title = html.h2.string.split(": ")[-1]
        status = html.find("td", text="Status:").find_next("td").b.string
        last_change = html.find("td", text=re.compile(r"Last\sChange:")).find_next("td").b.string

        return f"{title} [*{status}* at {last_change}]"


class RTTicketLinker(TicketLinker):
    regex = re.compile(r"rt#(\d+)", re.I)
    url = "https://crt.cs.wisc.edu/rt/Ticket/Display.html?id={}"
    prefix = "RT"


def post_message(client, *args, **kwargs):
    client.api_call("chat.postMessage", *args, **kwargs)


# TODO: this makes me think we should have a config.py file where things like this list go
RELINK_TIMEOUT = 300
REGEX_HANDLERS = [
    FlightworthyTicketLinker(relink_timeout=RELINK_TIMEOUT),
    RTTicketLinker(relink_timeout=RELINK_TIMEOUT),
]

TESTING_CHANNEL = "G011PN92WTV"


def startup():
    # TODO: discover channel by name
    post_message(SLACK_CLIENT, channel=TESTING_CHANNEL, text="I'm alive!")
    print("I sent the I'm alive message")


if __name__ == "__main__":
    app.run(port=3000)
