from bot import app, SLACK_CLIENT

if __name__ == "__main__":
    # TODO: discover channel by name
    SLACK_CLIENT.api_call(
        "chat.postMessage", channel = "G011PN92WTV", text = "I'm alive!",
    )
    app.run()
