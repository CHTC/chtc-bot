import pytest


from web.app import create_app


@pytest.fixture(scope="function")
def app(mocker):
    """This fixture provides access to the Flask application."""
    app = create_app("testing")

    # add a mock slack client
    app.config["SLACK_CLIENT"] = mocker.Mock()

    return app


@pytest.fixture(scope="function")
def config(app):
    """This fixture provides access to the application config."""
    return app.config


@pytest.fixture(scope="function")
def client(config):
    """
    This fixtures provides access to a "Slack client" that is actually a Mock.

    See https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
    """
    return config["SLACK_CLIENT"]
