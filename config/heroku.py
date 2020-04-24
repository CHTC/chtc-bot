import os

from slackclient import SlackClient

from config.base import *

PRODUCTION = True

# Slack credentials
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_CLIENT = SlackClient(os.environ["SLACK_BOT_TOKEN"])
