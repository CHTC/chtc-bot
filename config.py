import os
import re
import datetime

from web.events import linkers
from web.slashes.knobs import handle_knobs
from web.slashes.jobads import handle_jobads
from web.slashes.classad_eval import handle_classad_eval

FIVE_MINUTES = datetime.timedelta(minutes=5).total_seconds()


class Config:
    # Slack credentials
    SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
    SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

    # The user ID for this bot
    BOT_USER_ID = "U011WEDH24U"

    # The channel ID for the testing channel on the CHTC slack
    TESTING_CHANNEL = "G011PN92WTV"

    MESSAGE_HANDLERS = [
        linkers.FlightworthyTicketLinker(relink_timeout=FIVE_MINUTES),
        linkers.RTTicketLinker(relink_timeout=FIVE_MINUTES),
        linkers.TicketLinker(
            regex=re.compile(r"bot-issue#(\d+)", re.IGNORECASE),
            url="https://github.com/JoshKarpel/chtc-bot/issues/{}",
            prefix="bot",
            relink_timeout=FIVE_MINUTES,
        ),
        linkers.TicketLinker(
            regex=re.compile(r"bot-pr#(\d+)", re.IGNORECASE),
            url="https://github.com/JoshKarpel/chtc-bot/pull/{}",
            prefix="bot",
            relink_timeout=FIVE_MINUTES,
        ),
    ]

    SLASH_COMMANDS = {
        "knobs": handle_knobs,
        "classad_eval": handle_classad_eval,
        "jobads": handle_jobads,
    }


class HerokuConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    pass
