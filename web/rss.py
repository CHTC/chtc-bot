from flask import request

from . import slack


class RSSCommandHandler:
    def __init__(self):
        pass

    def handle(self):
        blob = request.json
        if blob is None:
            return "no JSON found", 400

        slack.post_message(channel="#chtcbot-dev", text=str(blob))
        return "", 200
