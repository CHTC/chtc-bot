import functools

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


class SlackUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), unique=True, nullable=False)

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id}, user_id={self.user_id})"

    @functools.cached_property
    def info(self) -> dict:
        """
        Get the Slack API user object for this user.

        See https://api.slack.com/types/user for details on the user object.
        This method returns the value of the "user" field from that object.
        """
        client = current_app.config["SLACK_CLIENT"]
        resp = client.api_call("users.info", user=self.user_id, include_locale=True)

        if not resp["ok"]:
            raise Exception(f"Failed to get info on {self} from the Slack API")

        return resp["user"]

    @classmethod
    def get_or_create(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()

        if user is not None:
            return user

        user = cls(user_id=user_id)
        db.session.add(user)
        db.session.commit()

        return user
