from bot import app, SLACK_CLIENT

# TODO: discover channel by name
SLACK_CLIENT.api_call(
    "chat.postMessage", channel = "G011PN92WTV", text = "I'm alive!",
)
print("I sent the I'm alive message")

if __name__ == "__main__":
    app.run()
