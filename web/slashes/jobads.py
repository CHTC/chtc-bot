from typing import Collection

import os.path
import html

import bs4
from flask import current_app, request

from ..executor import executor
from .. import http, slack, formatting, utils

from ..utils import ForgetfulDict

# ...
recently_linked_cache = ForgetfulDict(memory_time=300)


def handle_jobads():
    attrs = []
    skipped_attrs = []
    requested_attrs = html.unescape(request.form.get("text")).split(" ")

    for attr in requested_attrs:
        if attr not in recently_linked_cache:
            recently_linked_cache[attr] = True
            attrs.append(attr)
        else:
            skipped_attrs.append(attr)

    if len(attrs) == 0:
        return (
            f"Looked for job ad attribute{formatting.plural(skipped_attrs)} {', '.join(formatting.bold(k) for k in skipped_attrs)} recently, skipping",
            200,
        )

    user = request.form.get("user_id")
    channel = request.form.get("channel_id")

    executor.submit(
        attrs_reply, channel, user, attrs,
    )

    message = f"Looking for job ad attribute{formatting.plural(attrs)} {', '.join(formatting.bold(a) for a in attrs)}"
    if len(skipped_attrs) != 0:
        message += f", skipping recently-viewed job ad attributes{formatting.plural(skipped_attrs)} {', '.join(formatting.bold(k) for k in skipped_attrs)}"
    return (
        message,
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
                    formatting.inplace_convert_code_block_to_code_block,
                ]:
                    converter(description)

                text_description = formatting.compress_whitespace(description.text)
                return f"{formatting.bold(span.text)}\n>{text_description}"
        return None

    except Exception as e:
        current_app.logger.exception(f"Error while trying to find job attr {attr}: {e}")
        return None
