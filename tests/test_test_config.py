def test_that_test_config_was_loaded(config):
    assert config["TESTING"] is True


def test_that_slack_client_is_a_mock(config):
    assert hasattr(config["SLACK_CLIENT"], "assert_called")
