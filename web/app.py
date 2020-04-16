from flask import Flask

from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter

from . import slash, slack


def create_app(config):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(f"config.{config.lower().capitalize()}Config")

    with app.app_context():
        client = SlackClient(app.config["SLACK_BOT_TOKEN"])
        app.config["SLACK_CLIENT"] = client

        slack_events_adapter = SlackEventAdapter(
            app.config["SLACK_SIGNING_SECRET"], "/slack/events", app
        )
        slack_events_adapter.on("message")(
            lambda event: slack.handle_message_event(app, client, event)
        )

        app.register_blueprint(slash.slash_bp)

        return app
