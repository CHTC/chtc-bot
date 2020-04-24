import html

import bs4
from flask import current_app, request

from ..executor import executor
from .. import http, slack, formatting, utils

from ..utils import ForgetfulDict

# ...
recently_linked_cache = ForgetfulDict(memory_time=300)

def handle_knobs():
    knobs = []
    requested_knobs = html.unescape(request.form.get("text")).upper().split(" ")
    for knob in requested_knobs:
        if knob not in recently_linked_cache:
            recently_linked_cache[knob] = True
            knobs.append(knob)

    user = request.form.get("user_id")
    channel = request.form.get("channel_id")
    executor.submit(knobs_reply, channel, user, knobs)

    return (
        f"Looking for knob{formatting.plural(knobs)} {', '.join(formatting.bold(k) for k in knobs)}",
        200,
    )


KNOBS_URL = (
    "https://htcondor.readthedocs.io/en/latest/admin-manual/configuration-macros.html"
)


def knobs_reply(channel, user, knobs):
    response = http.cached_get_url(KNOBS_URL)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    descriptions = {knob: get_knob_description(soup, knob) for knob in knobs}

    msg_lines = [
        f"<@{user}> asked for information on knob{formatting.plural(knobs)} {', '.join(formatting.bold(k) for k in knobs)}"
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


def get_knob_description(knobs_page_soup, knob):
    try:
        header = knobs_page_soup.find("span", id=knob)
        description = header.parent.find_next("dd")
        for converter in [
            formatting.inplace_convert_em_to_underscores,
            formatting.inplace_convert_inline_code_to_backticks,
            formatting.inplace_convert_strong_to_stars,
            lambda soup: formatting.inplace_convert_internal_links_to_links(
                soup, KNOBS_URL, "std.std-ref"
            ),
            formatting.inplace_convert_code_block_to_code_block,
        ]:
            converter(description)
        text_description = formatting.compress_whitespace(description.text)

        return f"{formatting.bold(knob)}\n>{text_description}"
    except Exception as e:
        current_app.logger.exception(f"Error while trying to find knob {knob}: {e}")
        return None
