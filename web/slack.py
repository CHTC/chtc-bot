from flask import current_app


def post_message(*args, **kwargs):
    """
    Post a message to Slack.
    """
    client = current_app.config["SLACK_CLIENT"]

    client.api_call("chat.postMessage", *args, **kwargs)


def notify_error(message):
    if current_app.config["PRODUCTION"]:
        post_message(
            text=message, channel=current_app.config["DEV_CHANNEL"],
        )
