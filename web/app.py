from pathlib import Path

from flask import Flask
from slackeventsapi import SlackEventAdapter

from . import events


def create_app(config):
    app = Flask("web")

    app.config.from_pyfile(
        (Path(__file__).parent.parent / "config" / config.lower()).with_suffix(".py")
    )

    with app.app_context():
        from .executor import executor
        from .model import db, migrate

        executor.init_app(app)

        if app.config.get("SQLALCHEMY_DATABASE_URI") is not None:
            db.init_app(app)
            migrate.init_app(app, db)

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
                view_func=command_handler.handle,
            )

        # Turn off until we do something vaguely secure here or are
        # actively working on this again.
        for url, methods, api, api_handler in app.config["APIS"]:
            app.add_url_rule(url, methods=methods, endpoint=api, view_func=api_handler.handle)

        return app
