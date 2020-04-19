from web import slack


def test_post_message_calls_client(config):
    slack.post_message(text="foo")

    config["SLACK_CLIENT"].api_call.assert_called_once_with(
        "chat.postMessage", text="foo"
    )
