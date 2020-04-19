HTML_UNESCAPES = {
    "&gt;": ">",
    "&lt;": "<",
    "&amp;": "&",
}


def unescape(text):
    for from_, to_ in HTML_UNESCAPES.items():
        text = text.replace(from_, to_)

    return text
