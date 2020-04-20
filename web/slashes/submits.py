import bs4
from flask import current_app, request

from ..executor import executor
from .. import http, slack, formatting, html

import re
import os


def handle_submits():
    channel = request.form.get("channel_id")
    submits = html.unescape(request.form.get("text")).split(" ")
    user = request.form.get("user_id")

    executor.submit(submits_reply, channel, submits, user)

    return (
        f"Looking for submit file command{formatting.plural(submits)} {', '.join(formatting.bold(s) for s in submits)}",
        200,
    )


SUBMITS_URL = "https://htcondor.readthedocs.io/en/latest/man-pages/condor_submit.html"


def submits_reply(channel, submits, user):
    response = http.cached_get_url(SUBMITS_URL)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    descriptions = {submit: get_submits_description(soup, submit) for submit in submits}

    msg_lines = [
        f"<@{user}> asked for information on submit file command{formatting.plural(submits)} {', '.join(formatting.bold(s) for s in submits)}"
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

    slack.post_message(channel=channel, text=msg)


def get_submits_description(soup, attr):
    try:
        start = soup.find("div", id="submit-description-file-commands")
        dts = start.find_all_next("dt", string=re.compile(f"^{attr} ", re.I))

        for dt in dts:
            description = dt.find_next("dd")
            for converter in [
                formatting.inplace_convert_em_to_underscores,
                formatting.inplace_convert_code_to_backticks,
                formatting.inplace_convert_strong_to_stars,
                lambda soup: formatting.inplace_convert_internal_links_to_links(
                    soup, os.path.dirname(SUBMITS_URL), "std.std-ref"
                ),
                formatting.inplace_convert_code_to_code,
            ]:
                converter(description)

            text_description = formatting.compress_whitespace(description.text)
            return f"{formatting.bold(dt.text)}\n>{text_description}"
        return None

    except Exception as e:
        current_app.logger.exception(f"Error while trying to find job attr {attr}: {e}")
        return None
