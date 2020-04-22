import re
import os
import html

import bs4
from flask import current_app, request

from ..executor import executor
from .. import http, slack, formatting, utils


def handle_submits():
    channel = request.form.get("channel_id")
    submits = html.unescape(request.form.get("text")).split(" ")
    user = request.form.get("user_id")

    executor.submit(submits_reply, channel, user, submits)

    return (
        f"Looking for submit file command{formatting.plural(submits)} {', '.join(formatting.bold(s) for s in submits)}",
        200,
    )


SUBMITS_URL = "https://htcondor.readthedocs.io/en/latest/man-pages/condor_submit.html"


def submits_reply(
    channel, user, submits,
):
    response = http.cached_get_url(SUBMITS_URL)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    descriptions = {submit: get_submits_description(soup, submit) for submit in submits}

    msg_lines = [
        f"<@{user}> asked for information on submit file command{formatting.plural(submits)} {', '.join(formatting.bold(s) for s in submits)}"
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


def get_submits_description(soup, attr):
    try:
        start = soup.find("div", id="submit-description-file-commands")
        expr = re.compile(f"^{attr}( |$)", re.I)
        def text_matches(tag):
            return tag.name == "dt" and expr.search(tag.text)
        dts = start.find_all_next(text_matches);

        whole_description = None
        for dt in dts:
            description = dt.find_next("dd")

            for converter in [
                formatting.inplace_convert_em_to_underscores,
                formatting.inplace_convert_inline_code_to_backticks,
                formatting.inplace_convert_strong_to_stars,
                lambda soup: formatting.inplace_convert_internal_links_to_links(
                    soup, os.path.dirname(SUBMITS_URL), "std.std-ref"
                ),
                formatting.inplace_convert_code_block_to_code_block,
            ]:
                converter(description)

            for list in description.find_all("ol"):
                replacement = "<br>"
                for li in list.select("ol > li"):
                    replacement += f"\u2022 {li.text}<br>"
                list.replace_with(replacement)

            for list in description.find_all("ul"):
                replacement = "<br>"
                for li in list.select("ul > li"):
                    replacement += f"\u2022 {li.text}<br>"
                list.replace_with(replacement)

            text_description = formatting.compress_whitespace(description.text)
            text_description = text_description.replace( "<br>", "\n>" )

            result = f"{formatting.bold(dt.text)}\n>{text_description}"
            if whole_description is None:
                whole_description = result
            else:
                whole_description += f"\n{result}"

        return whole_description

    except Exception as e:
        current_app.logger.exception(f"Error while trying to find job attr {attr}: {e}")
        return None
