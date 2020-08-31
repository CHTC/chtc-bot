import datetime
import threading
import time

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


def list_files(*args, **kwargs):
    return client().files_list(*args, **kwargs)


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


def delete_uploaded_files(delay=datetime.timedelta(hours=6).total_seconds()):
    """
    Wait a certain amount of time,
    then delete all Slack files created by the bot before the wait started.

    Doing it this way also ensures that any leaked files get deleted the next
    time this function is run.
    """
    # make sure this gets run in a thread outside the thread pool
    threading.Thread(
        target=_delete_uploaded_files, args=(delay, current_app.config["BOT_USER_ID"])
    ).start()


def _delete_uploaded_files(delay, bot_user_id):
    start = time.time()

    time.sleep(delay)

    for file in list_files(user=bot_user_id)["files"]:
        if start >= file["created"]:
            delete_file(file=file["id"])
