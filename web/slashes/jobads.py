from typing import Collection

import os.path
import html

import bs4
from flask import current_app, request

from ..executor import executor
from .. import http, slack, formatting, utils


def handle_jobads():
    channel = request.form.get("channel_id")
    attrs = html.unescape(request.form.get("text")).split(" ")
    user = request.form.get("user_id")

    executor.submit(
        attrs_reply, channel, user, attrs,
    )

    return (
        f"Looking for job ad attribute{formatting.plural(attrs)} {', '.join(formatting.bold(a) for a in attrs)}",
        200,
    )


ATTRS_URL = "https://htcondor.readthedocs.io/en/latest/classad-attributes/job-classad-attributes.html"


def attrs_reply(
    channel: str, user: str, attrs: Collection[str],
):
    response = http.cached_get_url(ATTRS_URL)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    descriptions = {attr: get_attrs_description(soup, attr) for attr in attrs}

    msg_lines = [
        f"<@{user}> asked for information on job ad attribute{formatting.plural(attrs)} {', '.join(formatting.bold(a) for a in attrs)}"
    ]

    good, bad = utils.partition(descriptions, key=lambda v: v is not None)

    if bad:
        p1 = "they were" if len(bad) > 1 else "it was"
        p2 = "don't" if len(bad) > 1 else "it doesn't"
        msg_lines.append(
            f"I couldn't find information on {', '.join(formatting.bold(k) for k, v in bad.items())}. Perhaps {p1} misspelled, or {p2} exist?"
        )
    msg_lines.extend(v + "\n" for v in good.values())

    msg = "\n".join(msg_lines)

    slack.post_message(channel=channel, text=msg)


def get_attrs_description(soup, attr):
    try:
        # This can't be the efficient way to do this.
        spans = soup.select("dt > code.docutils.literal.notranslate > span.pre")
        for span in spans:
            if span.text.lower() == attr.lower():
                description = span.parent.parent.find_next("dd")
                for converter in [
                    formatting.inplace_convert_em_to_underscores,
                    formatting.inplace_convert_inline_code_to_backticks,
                    formatting.inplace_convert_strong_to_stars,
                    lambda soup: formatting.inplace_convert_internal_links_to_links(
                        soup, os.path.dirname(ATTRS_URL), "doc"
                    ),
                ]:
                    converter(description)

                text_description = formatting.compress_whitespace(description.text)
                return f"{formatting.bold(span.text)}\n>{text_description}"
        return None

    except Exception as e:
        current_app.logger.exception(f"Error while trying to find job attr {attr}: {e}")
        return None
