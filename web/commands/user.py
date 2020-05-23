from pprint import pformat

from flask import request

from . import commands
from ..executor import executor
from ..model import SlackUser
from .. import slack, formatting


class UserCommandHandler(commands.CommandHandler):
    def handle(self):
        user_id = request.form.get("user_id")

        executor.submit(self.reply_with_user_info, user_id)

        return ":point_left: :eyes:"

    def reply_with_user_info(self, user_id: str):
        user = SlackUser.get_or_create(user_id)

        parts = [
            f"Your CHTC Bot user ID is {formatting.fixed(user.id)}.",
            f"Your Slack user ID is {formatting.fixed(user.user_id)}.",
            formatting.fixed_block(pformat(user.info)),
        ]

        text = "\n".join(parts)

        slack.post_message(channel=user_id, text=text)
