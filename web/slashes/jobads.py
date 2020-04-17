import bs4
from flask import request, current_app

from .. import http, slack, utils
from ..formatting import plural, bold


def handle_jobads():
    channel = request.form.get("channel_id")
    attrs = request.form.get("text").upper().split(" ")
    user = request.form.get("user_id")

    client = current_app.config["SLACK_CLIENT"]

    utils.run_in_thread(lambda: jobads_reply(client, channel, attrs, user))

    return f"Looking for job ad attribute{plural(attrs)} {', '.join(bold(a) for a in attrs)}", 200


ATTRS_URL = (
    "https://htcondor.readthedocs.io/en/latest/classad-attributes/job-classad-attributes.html"
)


def attrs_reply(client, channel, attrs, user):
    response = http.cached_get_url(ATTRS_URL)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    descriptions = {attr: get_attrs_description(soup, attr) for attr in attrs}

    msg_lines = [
        f"<@{user}> asked for information on job ad attribute{plural(attrs)} {', '.join(bold(a) for a in attrs)}"
    ]

    # TODO: this is clunky, we should make a function for this kind of grouping
    good = {k: v for k, v in descriptions.items() if v is not None}
    bad = {k: v for k, v in descriptions.items() if v is None}

    if bad:
        p1 = "they were" if len(bad) > 1 else "it was"
        p2 = "don't" if len(bad) > 1 else "it doesn't"
        msg_lines.append(
            f"I couldn't find information on {', '.join(bold(k) for k, v in bad.items())}. Perhaps {p1} misspelled, or {p2} exist?"
        )
    msg_lines.extend(v + "\n" for v in good.values())

    msg = "\n".join(msg_lines)

    slack.post_message(client, channel=channel, text=msg)


def get_attrs_description(soup, attr):
    try:
        # This can't be the efficient way to do this.
        spans = soup.select("dt > code.docutils.literal.notranslate > span.pre")
        description = spans.find(string=attr)

        for converter in [
            convert_code_to_backticks,
            convert_code_to_backticks,
            convert_strong_to_stars,
            convert_links_to_links,
        ]:
            converter(description)
        text_description = description.text.replace("\n", " ")

        return f"{bold(attr)}\n>{text_description}"
    except Exception as e:
        # TODO: add logging
        return None
