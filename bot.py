from pprint import pprint
import re
import threading
import os

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
slack_client = SlackClient(SLACK_BOT_TOKEN)


@slack_events_adapter.on("message")
def handle_message(event_data):
    pprint(event_data)

    # don't respond to our own messages
    if event_data["event"]["user"] == "U011WEDH24U":
        return

    # TODO: this is bad; we should spin up a thread pool and connect to here via a queue
    threading.Thread(target=lambda: _handle_message(event_data)).start()


FW_TICKET_RE = re.compile(r"fw#(\d+)")
RT_TICKET_RE = re.compile(r"rt#(\d+)")


def _handle_message(event_data):
    try:
        message = event_data["event"]

        matches = FW_TICKET_RE.findall(message["text"])
        for ticket_id in matches:
            url = f"https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn={ticket_id}"

            response = requests.get(url)
            html = soup.BeautifulSoup(response.text, "html.parser")
            title = html.h2.string.split(": ")[-1]
            status = html.find("td", text="Status:").find_next("td").b.string

            slack_client.api_call(
                "chat.postMessage",
                channel=message["channel"],
                text=f"<{url}|fw#{ticket_id}> | {title} [{status}]",
            )

        matches = RT_TICKET_RE.findall(message["text"])
        for ticket_id in matches:
            url = f"https://crt.cs.wisc.edu/rt/Ticket/Display.html?id={ticket_id}"

            slack_client.api_call(
                "chat.postMessage",
                channel=message["channel"],
                text=f"<{url}|rt#{ticket_id}>",
            )

    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    app.run(port=3000)
