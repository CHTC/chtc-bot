import functools

from flask import Flask

from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter

from . import slashes, events


def create_app(config):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(f"config.{config.lower().capitalize()}Config")

    with app.app_context():
        client = SlackClient(app.config["SLACK_BOT_TOKEN"])
        app.config["SLACK_CLIENT"] = client

        # hook up the low-level raw event handlers; high-level config is done in config.py
        slack_events_adapter = SlackEventAdapter(
            app.config["SLACK_SIGNING_SECRET"], "/slack/events", app
        )
        for event_handler, args, kwargs in events.EVENT_HANDLERS:
            slack_events_adapter.on(*args, **kwargs)(
                functools.partial(event_handler, app, client)
            )

        # add routes for slash commands as specified in config.py
        for command, command_handler in app.config["SLASH_COMMANDS"].items():
            app.route(f"/slash/{command}", methods=["POST"])(command_handler)

        return app
