from flask import request
from flask import current_app

from . import slack


class RSSCommandHandler:
    def handle(self):
        secret = current_app.config["RSS_SHARED_SECRET"]
        if request.headers["x-shared-secret"] != secret:
            return ("invalid", 400)

        blob = request.json
        if blob is None:
            return "no JSON found", 400

        slack.post_message(channel="#chtcbot-dev", text=str(blob))
        return "", 200
