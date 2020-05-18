from pprint import pformat

from flask import request

from . import commands
from ..executor import executor
from ..model import SlackUser
from .. import slack, formatting


class UserCommandHandler(commands.CommandHandler):
    def handle(self):
        user_id = request.form.get("user_id")

        executor.submit(self.reply, user_id)

        return ":eyes: :point_down:"

    def reply(self, user_id):
        user = SlackUser.get_or_create(user_id)

        parts = [
            f"Your CHTC Bot user ID is {formatting.fixed(user.id)}",
            formatting.fixed_block(pformat(user.info)),
        ]

        text = "\n".join(parts)

        slack.post_message(channel=user_id, text=text)
