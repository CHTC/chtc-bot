import pytest

from web.app import create_app


@pytest.fixture(scope="function", autouse=True)
def app(mocker):
    """This fixture provides access to the Flask application."""
    app = create_app("testing")

    # add a mock slack client
    app.config["SLACK_CLIENT"] = mocker.Mock()

    return app
