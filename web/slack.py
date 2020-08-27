from flask import current_app


def client():
    """
    Get the Slack client from the app config.
    """
    return current_app.config["SLACK_CLIENT"]


def post_message(*args, **kwargs):
    """
    Post a message to Slack.
    """
    return client().chat_postMessage(*args, **kwargs)


def upload_file(*args, **kwargs):
    return client().files_upload(*args, **kwargs)


def delete_file(*args, **kwargs):
    return client().files_delete(*args, **kwargs)


def user_info(*args, **kwargs):
    """
    Get info on a user.
    """
    return client().users_info(*args, **kwargs)


def notify_error(message):
    if current_app.config["PRODUCTION"]:
        post_message(
            text=message, channel=current_app.config["DEV_CHANNEL"],
        )
