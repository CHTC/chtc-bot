from web import slack


def test_post_message_calls_client(config):
    slack.post_message(text="foo")

    config["SLACK_CLIENT"].chat_postMessage.assert_called_once_with(text="foo")


def test_user_info_calls_client(config):
    slack.user_info(user="foo")

    config["SLACK_CLIENT"].users_info.assert_called_once_with(user="foo")
