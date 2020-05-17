import os

from slackclient import SlackClient

from config.base import *

PRODUCTION = True

# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
SQLALCHEMY_RECORD_QUERIES = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# Slack credentials
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_CLIENT = SlackClient(os.environ["SLACK_BOT_TOKEN"])
