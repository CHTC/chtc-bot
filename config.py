import os


class Config:
    # Slack credentials
    SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
    SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

    # The user ID for this bot
    BOT_USER_ID = "U011WEDH24U"

    # The channel ID for the testing channel on the CHTC slack
    TESTING_CHANNEL = "G011PN92WTV"


class HerokuConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    pass
