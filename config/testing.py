from config.base import *

DEBUG = True
TESTING = True

# Database configuration
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test.db"

# a mock SLACK_CLIENT is added in tests/conftest.py::app
