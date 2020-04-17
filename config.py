import os

from web.events import linkers
from web.slashes.knobs import handle_knobs


class Config:
    # Slack credentials
    SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
    SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

    # The user ID for this bot
    BOT_USER_ID = "U011WEDH24U"

    # The channel ID for the testing channel on the CHTC slack
    TESTING_CHANNEL = "G011PN92WTV"

    MESSAGE_HANDLERS = [
        linkers.FlightworthyTicketLinker(relink_timeout=300),
        linkers.RTTicketLinker(relink_timeout=300),
    ]

    SLASH_COMMANDS = {"knobs": handle_knobs}


class HerokuConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    pass
