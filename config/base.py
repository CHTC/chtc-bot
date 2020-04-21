import re
import datetime

import web.slashes as slashes
from web.events import linkers


DEBUG = False
TESTING = False

EXECUTOR_TYPE = "thread"
EXECUTOR_MAX_WORKERS = None  # let it decide
EXECUTOR_PROPAGATE_EXCEPTIONS = True

# The user ID for this bot
BOT_USER_ID = "U011WEDH24U"

# The channel ID for the testing channel on the CHTC slack
TESTING_CHANNEL = "G011PN92WTV"

FIVE_MINUTES = datetime.timedelta(minutes=5).total_seconds()

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
    "knobs": slashes.handle_knobs,
    "classad_eval": slashes.handle_classad_eval,
    "jobads": slashes.handle_jobads,
    "submits": slashes.handle_submits,
}
