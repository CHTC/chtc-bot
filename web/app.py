from flask import Flask

from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter

from . import slash, slack


def create_app(config):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(f"config.{config.lower().capitalize()}Config")

    with app.app_context():
        app.config["SLACK_CLIENT"] = SlackClient(app.config["SLACK_BOT_TOKEN"])

        slack_events_adapter = SlackEventAdapter(
            app.config["SLACK_SIGNING_SECRET"], "/slack/events", app
        )
        slack_events_adapter.on("message")(slack.handle_message_event)

        app.register_blueprint(slash.slash_bp)

        return app
