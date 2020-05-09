from typing import Tuple, List, Collection, Mapping, Any, Union

import re
import textwrap
import html

from flask import current_app, request

import htcondor
import classad

from ..executor import executor
from .. import slack, formatting

from . import commands


class ClassadEvalCommandHandler(commands.CommandHandler):
    def handle(self):
        channel = request.form.get("channel_id")
        user = request.form.get("user_id")
        text = html.unescape(request.form.get("text"))

        executor.submit(classad_eval_reply, channel, user, text)

        return f":thinking_face: :newspaper:", 200


def classad_eval_reply(channel: str, user: str, text: str):
    msg = generate_classad_eval_reply(user, text)

    slack.post_message(text=msg, channel=channel)


def generate_classad_eval_reply(user: str, text: str):
    try:
        ads_and_exprs = parse(text)
    except Exception as e:
        current_app.logger.exception(
            f"Failed to parse ad or expressions (raw: {text}): {e}"
        )
        return html.escape(f"Failed to parse ad or expressions: {e}", quote=False)

    try:
        results = evaluate(ads_and_exprs)
    except Exception as e:
        current_app.logger.exception(f"Failed to evaluate an expression: {e}")
        return html.escape(f"Failed to evaluate an expression: {e}", quote=False)

    msg_lines = [f"<@{user}> asked me to do ClassAd evaluation:"]

    ad_changed = False
    has_printed_an_expr = False
    last_ad = classad.ClassAd()
    for idx, result in enumerate(results):
        if isinstance(result, classad.ClassAd):
            ad_changed = True
            last_ad = result
        else:
            if ad_changed:
                msg_lines.append(f"Ad modified:" if has_printed_an_expr else "Ad:",)
                msg_lines.append(
                    "```" + "\n".join(textwrap.dedent(html.escape(str(last_ad), quote=False)).strip().splitlines()) + "```"
                )
                ad_changed = False

            expression, evaluated = result
            msg_lines.append(
                f"`{format_result(expression)}` :arrow_right: `{format_result(evaluated)}`"
            )
            has_printed_an_expr = True

    return "\n".join(filter(None, msg_lines))


RE_PARTS = re.compile(r"'(.*?)'")


def format_result(result: str):
    """Collapse newlines into spaces."""
    return html.escape(
        " ".join(s.strip() for s in str(result).splitlines()), quote=False
    )


def parse(text: str) -> List[Union[classad.ClassAd, classad.ExprTree]]:
    parts = RE_PARTS.findall(text)

    return [_parse_ad_or_expr(part) for part in parts]


def _parse_ad_or_expr(text: str) -> Union[classad.ClassAd, classad.ExprTree]:
    try:
        return _try_parse_ad(text)
    except SyntaxError:
        return classad.ExprTree(text)


def _try_parse_ad(text: str) -> classad.ClassAd:
    try:
        return classad.ClassAd(text)
    except SyntaxError:
        # it doesn't look like an ad... maybe they missed the wrapping braces?
        return classad.ClassAd(f"[{text}]")


def evaluate(
    ads_and_exprs,
) -> List[Union[classad.ClassAd, Tuple[classad.ExprTree, Any]]]:
    results = []
    base_ad = classad.ClassAd()
    for ad_or_expr in ads_and_exprs:
        if isinstance(ad_or_expr, classad.ClassAd):
            base_ad.update(ad_or_expr)

            new_ad = classad.ClassAd()
            new_ad.update(base_ad)
            results.append(new_ad)
        else:
            results.append((ad_or_expr, ad_or_expr.simplify(base_ad)))

    return results
