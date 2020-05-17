from flask import request

from . import slack

class RSSCommandHandler:
    def __init__(self):
        pass

    def handle(self):
        blob = request.get_json()
        if blob is None:
            return None

        slack.post_message(channel="#chtcbot-dev", text=str(blob))
        return None
