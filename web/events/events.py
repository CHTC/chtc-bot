from .. import utils

EVENT_HANDLERS = []


def event_handler(*args, **kwargs):
    def _(func):
        EVENT_HANDLERS.append((func, args, kwargs))
        return func

    return _


@event_handler("message")
def handle_message_event(config, event_data):
    # skip edits
    if event_data["event"].get("subtype") == "message_changed":
        return

    # don't respond to our own messages
    if event_data["event"].get("user") == config["BOT_USER_ID"]:
        return

    # TODO: this is bad; we should spin up a thread pool and connect to here via a queue
    utils.run_in_thread(lambda: _handle_message(config, event_data))


def _handle_message(config, event_data):
    message = event_data["event"]

    for handler in config["MESSAGE_HANDLERS"]:
        try:
            handler.handle(config, message)
        except Exception as e:
            # TODO: logging
            pass
