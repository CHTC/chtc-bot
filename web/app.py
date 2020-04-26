from pathlib import Path

from flask import Flask

from slackeventsapi import SlackEventAdapter

from . import events
from .executor import executor


def create_app(config):
    app = Flask("web")

    app.config.from_pyfile(
        (Path(__file__).parent.parent / "config" / config.lower()).with_suffix(".py")
    )

    with app.app_context():
        executor.init_app(app)

        # hook up the low-level raw event handlers; high-level config is done in base.py
        if app.config.get("SLACK_SIGNING_SECRET") is not None:
            # connect the events adapter to the flask app
            slack_events_adapter = SlackEventAdapter(
                app.config["SLACK_SIGNING_SECRET"], "/slack/events", app
            )

            # wire up individual event handlers
            for event_handler, args, kwargs in events.EVENT_HANDLERS:
                slack_events_adapter.on(*args, **kwargs)(event_handler)

        # add routes for slash commands as specified in base.py
        for command, command_handler in app.config["SLASH_COMMANDS"].items():
            app.add_url_rule(
                f"/slash/{command}",
                methods=["POST"],
                endpoint=command,
                view_func=command_handler,
            )

        return app
