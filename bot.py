from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
import re

from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient

import requests
import bs4 as soup

FW_TICKET_RE = re.compile(r"fw#(\d+)")

if __name__ == "__main__":
    SLACK_SIGNING_SECRET = None
    slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, endpoint = "/slack/events")

    # Create a SlackClient for your bot to use for Web API requests
    SLACK_BOT_TOKEN = None
    slack_client = SlackClient(SLACK_BOT_TOKEN)

    with ThreadPoolExecutor() as pool:
        # Example responder to greetings
        @slack_events_adapter.on("message")
        def handle_message(event_data):
            pprint(event_data)
            if event_data['event']['user'] == "U011WEDH24U":
                return

            pool.submit(_handle_message, event_data)


        def _handle_message(event_data):
            try:
                message = event_data["event"]
                matches = FW_TICKET_RE.findall(message['text'])
                for ticket_id in matches:
                    url = f"https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn={ticket_id}"
                    response = requests.get(url)
                    print(response)
                    html = soup.BeautifulSoup(response.text, 'html.parser')
                    print('parsed')
                    title = html.h2.string.split(": ")[-1]
                    print(title)

                    status = html.find('td', text = 'Status:').find_next('td').b.string

                    slack_client.api_call(
                        "chat.postMessage",
                        channel = message['channel'],
                        text = f"{url} | {title} [{status}]",
                    )
                    print('done')
            except Exception as e:
                print(e)
                raise e


        # Start the server on port 3000
        slack_events_adapter.start(port = 3000)
