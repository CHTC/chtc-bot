from .utils import run_in_thread


def handle_message_event(app, client, event_data):
    # skip edits
    if event_data["event"].get("subtype") == "message_changed":
        return

    # don't respond to our own messages
    if event_data["event"].get("user") == app.config["BOT_USER_ID"]:
        return

    # TODO: this is bad; we should spin up a thread pool and connect to here via a queue
    run_in_thread(lambda: _handle_message(app, client, event_data))


def _handle_message(app, client, event_data):
    message = event_data["event"]

    for handler in app.config["REGEX_HANDLERS"]:
        matches = handler.regex.findall(message["text"])
        matches = handler.filter_matches(message, matches)

        if len(matches) == 0:
            continue

        try:
            handler.handle_message(client, message, matches)
        except Exception as e:
            print(e)


def post_message(client, *args, **kwargs):
    client.api_call("chat.postMessage", *args, **kwargs)
