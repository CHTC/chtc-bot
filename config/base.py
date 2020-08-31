import datetime
import re

import web.commands as commands
import web.events as events
from web import rss

DEBUG = False
TESTING = False
PRODUCTION = False

# Database configuration
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/dev.db"
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

EXECUTOR_TYPE = "thread"
EXECUTOR_MAX_WORKERS = None  # let it decide
EXECUTOR_PROPAGATE_EXCEPTIONS = True

# The user ID for this bot
BOT_USER_ID = "U011WEDH24U"

# The channel ID for the dev channel on the CHTC slack
DEV_CHANNEL = "G011PN92WTV"

five_minutes = datetime.timedelta(minutes=5).total_seconds()

MESSAGE_HANDLERS = [
    events.FlightworthyTicketLinker(relink_timeout=five_minutes),
    events.RTTicketLinker(relink_timeout=five_minutes),
    events.TicketLinker(
        regex=re.compile(r"bot-issue#(\d+)", re.IGNORECASE),
        url="https://github.com/JoshKarpel/chtc-bot/issues/{}",
        prefix="bot",
        relink_timeout=five_minutes,
    ),
    events.TicketLinker(
        regex=re.compile(r"bot-pr#(\d+)", re.IGNORECASE),
        url="https://github.com/JoshKarpel/chtc-bot/pull/{}",
        prefix="bot",
        relink_timeout=five_minutes,
    ),
]


SLASH_COMMANDS = {
    "knobs": commands.KnobsCommandHandler(rescrape_timeout=five_minutes),
    "jobads": commands.JobAdsCommandHandler(rescrape_timeout=five_minutes),
    "submits": commands.SubmitsCommandHandler(rescrape_timeout=five_minutes),
    "classad_eval": commands.ClassadEvalCommandHandler(),
    "user": commands.UserCommandHandler(),
    "schedule": commands.ScheduleCommandHandler(),
    "condor_status": commands.CondorStatusCommandHandler(),
}


APIS = [["/rss", ["POST"], "rss", rss.RSSCommandHandler()]]
