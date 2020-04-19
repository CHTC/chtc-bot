from flask import current_app


def post_message(*args, client=None, **kwargs):
    if client is None:
        client = current_app.config["SLACK_CLIENT"]

    client.api_call("chat.postMessage", *args, **kwargs)
