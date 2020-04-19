import re
import datetime

from web.events import linkers
from web.slashes.knobs import handle_knobs
from web.slashes.jobads import handle_jobads
from web.slashes.submits import handle_submits
from web.slashes.classad_eval import handle_classad_eval


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
    "knobs": handle_knobs,
    "classad_eval": handle_classad_eval,
    "jobads": handle_jobads,
    "submits": handle_submits,
}
