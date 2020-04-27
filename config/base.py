import re
import datetime

from web.events import linkers
from web.slashes import scrapers
from web.slashes import classad_eval


DEBUG = False
TESTING = False
PRODUCTION = False

EXECUTOR_TYPE = "thread"
EXECUTOR_MAX_WORKERS = None  # let it decide
EXECUTOR_PROPAGATE_EXCEPTIONS = True

# The user ID for this bot
BOT_USER_ID = "U011WEDH24U"

# The channel ID for the dev channel on the CHTC slack
DEV_CHANNEL = "G011PN92WTV"

five_minutes = datetime.timedelta(minutes=5).total_seconds()

MESSAGE_HANDLERS = [
    linkers.FlightworthyTicketLinker(relink_timeout=five_minutes),
    linkers.RTTicketLinker(relink_timeout=five_minutes),
    linkers.TicketLinker(
        regex=re.compile(r"bot-issue#(\d+)", re.IGNORECASE),
        url="https://github.com/JoshKarpel/chtc-bot/issues/{}",
        prefix="bot",
        relink_timeout=five_minutes,
    ),
    linkers.TicketLinker(
        regex=re.compile(r"bot-pr#(\d+)", re.IGNORECASE),
        url="https://github.com/JoshKarpel/chtc-bot/pull/{}",
        prefix="bot",
        relink_timeout=five_minutes,
    ),
]


SLASH_COMMANDS = {
    "knobs": scrapers.KnobsCommandHandler(relink_timeout=five_minutes),
    "jobads": scrapers.JobAdsCommandHandler(relink_timeout=five_minutes),
    "submits": scrapers.SubmitsCommandHandler(relink_timeout=five_minutes),
    "classad_eval": classad_eval.ClassadEvalCommandHandler(),
}
