import bs4
from flask import request, current_app

import os.path

from .. import http, slack, formatting, html, utils


def handle_jobads():
    channel = request.form.get("channel_id")
    attrs = html.unescape(request.form.get("text")).split(" ")
    user = request.form.get("user_id")

    client = current_app.config["SLACK_CLIENT"]

    utils.run_in_thread(lambda: attrs_reply(client, channel, attrs, user))

    return (
        f"Looking for job ad attribute{formatting.plural(attrs)} {', '.join(formatting.bold(a) for a in attrs)}",
        200,
    )


ATTRS_URL = "https://htcondor.readthedocs.io/en/latest/classad-attributes/job-classad-attributes.html"


def attrs_reply(client, channel, attrs, user):
    response = http.cached_get_url(ATTRS_URL)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    descriptions = {attr: get_attrs_description(soup, attr) for attr in attrs}

    msg_lines = [
        f"<@{user}> asked for information on job ad attribute{formatting.plural(attrs)} {', '.join(formatting.bold(a) for a in attrs)}"
    ]

    # TODO: this is clunky, we should make a function for this kind of grouping
    good = {k: v for k, v in descriptions.items() if v is not None}
    bad = {k: v for k, v in descriptions.items() if v is None}

    if bad:
        p1 = "they were" if len(bad) > 1 else "it was"
        p2 = "don't" if len(bad) > 1 else "it doesn't"
        msg_lines.append(
            f"I couldn't find information on {', '.join(formatting.bold(k) for k, v in bad.items())}. Perhaps {p1} misspelled, or {p2} exist?"
        )
    msg_lines.extend(v + "\n" for v in good.values())

    msg = "\n".join(msg_lines)

    slack.post_message(client, channel=channel, text=msg)


def get_attrs_description(soup, attr):
    try:
        # This can't be the efficient way to do this.
        spans = soup.select("dt > code.docutils.literal.notranslate > span.pre")
        for span in spans:
            if span.text.lower() == attr.lower():
                description = span.parent.parent.find_next("dd")
                for converter in [
                    formatting.inplace_convert_em_to_underscores,
                    formatting.inplace_convert_code_to_backticks,
                    formatting.inplace_convert_strong_to_stars,
                    lambda soup: formatting.inplace_convert_internal_links_to_links(
                        soup, os.path.dirname(ATTRS_URL), "doc"
                    ),
                ]:
                    converter(description)

                text_description = description.text.replace("\n", " ")
                return f"{formatting.bold(span.text)}\n>{text_description}"
        return None

    except Exception as e:
        # TODO: add logging
        return None
