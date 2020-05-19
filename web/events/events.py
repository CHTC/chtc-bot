import traceback

from flask import current_app

from ..executor import executor
from .. import slack


EVENT_HANDLERS = []


def event_handler(*args, **kwargs):
    def _(func):
        EVENT_HANDLERS.append((func, args, kwargs))
        return func

    return _


@event_handler("message")
def handle_message_event(event_data):
    """
    This is the raw incoming event handler; it will be passed a Slack API event
    as a Python dictionary parsed from JSON.
    """
    subtype = event_data["event"].get("subtype")

    # skip edits
    if subtype == "message_changed":
        return

    # skip deletes
    if subtype == "message_deleted":
        return

    # don't respond to our own messages
    if event_data["event"].get("user") == current_app.config["BOT_USER_ID"]:
        return

    executor.submit(_handle_message, event_data)


def _handle_message(event_data):
    message = event_data["event"]

    for handler in current_app.config["MESSAGE_HANDLERS"]:
        try:
            handler.handle(message)
        except Exception as e:
            current_app.logger.exception(f"Uncaught exception in {handler}: {e}")

            executor.submit(
                slack.notify_error,
                f"Uncaught exception in `{handler}`: `{e}`\n```\n{traceback.format_exc()}\n```",
            )

            pass
