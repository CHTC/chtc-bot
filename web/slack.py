def post_message(client, *args, **kwargs):
    client.api_call("chat.postMessage", *args, **kwargs)
