from flask import current_app

from ..executor import executor

EVENT_HANDLERS = []


def event_handler(*args, **kwargs):
    def _(func):
        EVENT_HANDLERS.append((func, args, kwargs))
        return func

    return _


@event_handler("message")
def handle_message_event(event_data):
    # skip edits
    if event_data["event"].get("subtype") == "message_changed":
        return

    # don't respond to our own messages
    if event_data["event"].get("user") == current_app.config["BOT_USER_ID"]:
        return

    executor.submit(_handle_message, event_data)


def _handle_message(event_data):
    message = event_data["event"]

    for handler in current_app.config["MESSAGE_HANDLERS"]:
        try:
            handler.handle(current_app.config, message)
        except Exception as e:
            # TODO: logging
            pass
