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

        slack_events_adapter = SlackEventAdapter(
            app.config["SLACK_SIGNING_SECRET"], "/slack/events", app
        )
        for handler, args, kwargs in events.EVENT_HANDLERS:
            slack_events_adapter.on(*args, **kwargs)(
                lambda event: handler(app, client, event)
            )

        app.register_blueprint(slashes.slash_bp)

        return app
