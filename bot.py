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

        now = time.monotonic()
        new_matches = [m for m in matches if not handler.recently_linked(m, now)]

        if len(new_matches) == 0:
            continue

        try:
            handler.handle_message(SLACK_CLIENT, message, new_matches)
        except Exception as e:
            print(e)


# TODO: make this an actual metaclass
class RegexMessageHandler:
    def handle_message(self, client, message, matches):
        raise NotImplementedError


class TicketLinker(RegexMessageHandler):
    def __init__(self, memory = 10):
        self.memory = memory

        self.tickets = dict()
        self.last_ticket_cleanup = time.monotonic()

    def recently_linked(self, ticket_id, now):
        # For a side-project, let's not think too hard.  Just purge our
        # memory of old ticket IDs when we handle a new message, rather
        # than on a timer in another thread.  Don't bother to scan the
        # whole list on every message, though, just if it's been more
        # than five seconds since the last clean-up.
        if self.last_ticket_cleanup + self.memory < now:
            for ticket_id, last_linked in self.tickets.items():
                print(ticket_id, last_linked)
                if last_linked + self.memory < now:
                    self.tickets.pop(ticket_id)
            self.last_ticket_cleanup = now

        print(self.tickets, now)
        if ticket_id in self.tickets:
            return now < self.tickets[ticket_id] + self.memory
        else:
            self.tickets[ticket_id] = now
            return False


class FlightworthyTicketLinker(TicketLinker):
    regex = re.compile(r"fw#(\d+)")

    def handle_message(self, client, message, matches):
        msgs = []
        for ticket_id in matches:
            url = f"https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn={ticket_id}"

            response = requests.get(url)
            html = soup.BeautifulSoup(response.text, "html.parser")
            title = html.h2.string.split(": ")[-1]
            status = html.find("td", text="Status:").find_next("td").b.string

            msgs.append(f"<{url}|fw#{ticket_id}> | {title} [{status}]")
        msg = "\n".join(msgs)

        client.api_call(
            "chat.postMessage", channel=message["channel"], text=msg,
        )


class RTTicketLinker(TicketLinker):
    regex = re.compile(r"rt#(\d+)")

    def handle_message(self, client, message, matches):
        msgs = []
        for ticket_id in matches:
            url = f"https://crt.cs.wisc.edu/rt/Ticket/Display.html?id={ticket_id}"
            msgs.append(f"<{url}|rt#{ticket_id}>")
        msg = "\n".join(msgs)

        client.api_call(
            "chat.postMessage", channel=message["channel"], text=msg,
        )


# TODO: this makes me think we should have a config.py file where things like this list go
REGEX_HANDLERS = [FlightworthyTicketLinker(), RTTicketLinker()]

def startup():
    # TODO: discover channel by name
    SLACK_CLIENT.api_call(
        "chat.postMessage", channel = "G011PN92WTV", text = "I'm alive!",
    )
    print("I sent the I'm alive message")

startup()

if __name__ == "__main__":
    app.run(port=3000)
