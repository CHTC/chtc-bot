from typing import Tuple, List, Collection, Mapping, Any

import re
import textwrap
import html

from flask import current_app, request

import htcondor
import classad

from ..executor import executor
from .. import slack, formatting


def handle_classad_eval():
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
        ad, exprs = parse(text)
    except Exception as e:
        current_app.logger.exception(
            f"Failed to parse ad or expressions (raw: {text}): {e}"
        )
        return f"Failed to parse ad or expressions: {e}"

    try:
        results = evaluate(ad, exprs)
    except Exception as e:
        current_app.logger.exception(
            f"Failed to evaluate an expression (ad: {repr(ad)}, expressions: {[exprs]}): {e}"
        )
        return f"Failed to evaluate an expression: {e}"

    prefix = f"<@{user}> asked me to evaluate {'a ' if len(exprs) == 1 else ''}ClassAd expression{formatting.plural(exprs)}"
    if len(ad) != 0:
        msg_lines = [
            f"{prefix} in the context of this ad:",
            "```",
            *textwrap.dedent(str(ad)).strip().splitlines(),
            "```",
            f"Expression{formatting.plural(results)}:",
        ]
    else:
        msg_lines = [f"{prefix}:"]

    msg_lines.extend(
        f"`{format_result(k)}` :arrow_right: `{format_result(v)}`"
        for k, v in results.items()
    )

    return "\n".join(filter(None, msg_lines))


RE_PARTS = re.compile(r"'(.*?)'")


def format_result(result: str):
    """Collapse newlines into spaces."""
    return html.escape(" ".join(s.strip() for s in str(result).splitlines()))


def parse(text: str) -> Tuple[classad.ClassAd, List[classad.ExprTree]]:
    parts = RE_PARTS.findall(text)

    ad = classad.parseOne(parts[0])
    exprs = [classad.ExprTree(s) for s in parts[1:]]

    return ad, exprs


def evaluate(
    ad: classad.ClassAd, exprs: Collection[classad.ExprTree]
) -> Mapping[classad.ExprTree, Any]:
    """Evaluate each expression in the context of the ad."""
    return {expr: expr.simplify(ad) for expr in exprs}
