import html
import shlex
import subprocess

from flask import current_app, request

from .. import formatting, slack
from ..executor import executor
from . import commands


class CondorStatusCommandHandler(commands.CommandHandler):
    def handle(self):
        channel = request.form.get("channel_id")
        user = request.form.get("user_id")
        text = html.unescape(request.form.get("text"))

        executor.submit(condor_status_reply, channel, user, text)

        return f":thinking_face: :card_file_box:", 200


def condor_status_reply(channel: str, user: str, text: str):
    msg = generate_condor_status_reply(user, text)

    slack.post_message(text=msg, channel=channel)


def generate_condor_status_reply(user: str, text: str):
    args = ["condor_status", "-pool", current_app.config["POOL"], *shlex.split(text)]

    fmt_args = formatting.fixed(shlex.join(args))
    current_app.logger.debug(f"About to run: {fmt_args}")

    cmd = subprocess.run(args, text=True, env={}, capture_output=True)

    if cmd.returncode != 0:
        current_app.logger.error(f"Error while trying to run {shlex.join(args)}:\n{cmd.stderr}")
        return f"Error while trying to run {fmt_args} for {user}: {formatting.fixed(cmd.stderr.splitlines()[0])}"

    return f"<@{user}> asked me to run {fmt_args}:\n{formatting.fixed_block(cmd.stdout.rstrip())}"
