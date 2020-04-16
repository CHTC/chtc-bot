from typing import List, MutableMapping

import re
import threading
import os
import time
import functools

from flask import Flask, request

from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient

import requests
import bs4

app = Flask(__name__)


@app.route("/")
def index():
    return "I'm alive!"


SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_CLIENT = SlackClient(SLACK_BOT_TOKEN)

BOT_USER_ID = "U011WEDH24U"


# TODO: replace this raw flask route decorator with our own abstraction... @slash('knobs')
@app.route("/slash/knobs", methods=["POST"])
def knobs():
    channel = request.form.get("channel_id")
    knobs = request.form.get("text").upper().split(" ")
    user = request.form.get("user_name")

    run_in_thread(lambda: handle_knobs(SLACK_CLIENT, channel, knobs, user))

    return f"Looking for knobs {', '.join(knobs)} ...", 200


KNOBS_URL = (
    "https://htcondor.readthedocs.io/en/latest/admin-manual/configuration-macros.html"
)


@functools.lru_cache(2 ** 6)
def get_url(url):
    return requests.get(url)


def handle_knobs(client, channel, knobs, user):
    response = get_url(KNOBS_URL)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    descriptions = {knob: get_knob_description(soup, knob) for knob in knobs}

    msg_lines = [f"{user} asked for information on knobs {', '.join(knobs)}"]
    if any(v is None for v in descriptions.values()):
        msg_lines.append(f"I could not find information on {', '.join(k for k, v in knobs)}. Perhaps they were misspelled, or don't exist?")
    msg_lines.extend(v + '\n' for v in knobs.values())

    msg = "\n".join(msg_lines)

    post_message(client, channel=channel, text=msg)


def get_knob_description(knobs_page_soup, knob):
    try:
        header = knobs_page_soup.find("span", id=knob)
        raw_description = header.parent.find_next("dd")
        description = raw_description.text.replace("\n", " ")

        return f"*{knob}*\n>{description}"
    except Exception:
        # TODO: add logging
        return None


@slack_events_adapter.on("message")
def handle_message_event(event_data):
    # skip edits
    if event_data["event"].get("subtype") == "message_changed":
        return

    # don't respond to our own messages
    if event_data["event"].get("user") == BOT_USER_ID:
        return

    # TODO: this is bad; we should spin up a thread pool and connect to here via a queue
    run_in_thread(lambda: _handle_message(event_data))


def run_in_thread(func):
    """Run a zero-argument function asynchronously in a thread (use a lambda to capture local variables)."""
    threading.Thread(target=func).start()


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
        response = get_url(url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        title = soup.h2.string.split(": ")[-1]
        status = self.find_info_table_element(soup, "Status:")
        last_change = self.find_info_table_element(soup, re.compile(r"Last\sChange:"))

        return f"{title} [*{status}* at {last_change}]"

    def find_info_table_element(self, soup, element):
        return soup.find("td", text=element).find_next("td").b.string


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


if __name__ == "__main__":
    app.run(port=3000)
