import os
import re
import bs4
import html
from typing import List
from flask import current_app, request

from . import commands
from ..executor import executor
from ..utils import ForgetfulDict
from .. import http, slack, formatting, utils


class WebScrapingCommandHandler(commands.CommandHandler):
    def __init__(self, *, relink_timeout):
        super().__init__()

        self.recently_linked_cache = ForgetfulDict(memory_time=relink_timeout)

    def handle(self):
        channel = request.form.get("channel_id")

        args = []
        skipped_args = []
        requested_args = html.unescape(request.form.get("text")).split(" ")

        for arg in requested_args:
            if (arg.upper(), channel) not in self.recently_linked_cache:
                self.recently_linked_cache[(arg.upper(), channel)] = True
                args.append(arg)
            else:
                skipped_args.append(arg)

        if len(args) == 0:
            return (
                f"Looked for {self.word}{formatting.plural(skipped_args)}"
                + f" {', '.join(formatting.bold(k) for k in skipped_args)}"
                + f" recently, skippping",
                200,
            )

        user = request.form.get("user_id")
        executor.submit(self.reply, channel, user, args)

        message = f"Looking for {self.word}{formatting.plural(skipped_args)}"
        message += f" {', '.join(formatting.bold(k) for k in args)}"
        if len(skipped_args) != 0:
            message += f", skipping recently-viewed {self.word}"
            message += f"{formatting.plural(skipped_args)}"
            message += f" {', '.join(formatting.bold(k) for k in skipped_args)}"
        return (message, 200)

    def reply(self, channel, user, args: List[str]):
        response = http.cached_get_url(self.url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        lines = [
            f"<@{user}> asked for information on {self.word}"
            + f"{formatting.plural(args)}"
            + f" {', '.join(formatting.bold(k) for k in args)}"
        ]

        descriptions = {arg: self.get_description(soup, arg) for arg in args}
        good, bad = utils.partition(descriptions, key=lambda v: v is not None)

        if bad:
            p1 = "they were" if len(bad) > 1 else "it was"
            p2 = "don't" if len(bad) > 1 else "it doesn't"
            lines.append(
                f"I couldn't find information on"
                + f" {', '.join(formatting.bold(k) for k in bad.keys())}"
                + f".  Perhaps {p1} misspelled, or {p2} exist?"
            )

        lines.extend(v + "\n" for v in good.values())
        slack.post_message(channel=channel, text="\n".join(lines))


class KnobsCommandHandler(WebScrapingCommandHandler):
    def __init__(self, *, relink_timeout):
        super().__init__(relink_timeout=relink_timeout)

        # @JoshK: Should these be arguments to the superclass constructor?
        self.url = "https://htcondor.readthedocs.io/en/latest/admin-manual/configuration-macros.html"
        self.word = "knob"

    def get_description(self, page_soup, arg):
        try:
            header = page_soup.find("span", id=arg)

            description = header.parent.find_next("dd")
            for converter in [
                formatting.inplace_convert_em_to_underscores,
                formatting.inplace_convert_inline_code_to_backticks,
                formatting.inplace_convert_strong_to_stars,
                lambda soup: formatting.inplace_convert_internal_links_to_links(
                    soup, self.url, "std.std-ref"
                ),
                formatting.inplace_convert_code_block_to_code_block,
            ]:
                converter(description)

            text_description = formatting.compress_whitespace(description.text)
            return f"{formatting.bold(arg)}\n>{text_description}"
        except Exception as e:
            current_app.logger.exception(
                f"Error while trying to find {self.word} {arg}: {e}"
            )
            return None


class JobAdsCommandHandler(WebScrapingCommandHandler):
    def __init__(self, *, relink_timeout):
        super().__init__(relink_timeout=relink_timeout)

        # @JoshK: Should these be arguments to the superclass constructor?
        self.url = "https://htcondor.readthedocs.io/en/latest/classad-attributes/job-classad-attributes.html"
        self.word = "job ad attribute"

    def get_description(self, page_soup, arg):
        try:
            # This can't be the efficient way to do this.
            spans = page_soup.select(
                "dt > code.docutils.literal.notranslate > span.pre"
            )

            for span in spans:
                if span.text.lower() == arg.lower():
                    description = span.parent.parent.find_next("dd")
                    for converter in [
                        formatting.inplace_convert_em_to_underscores,
                        formatting.inplace_convert_inline_code_to_backticks,
                        formatting.inplace_convert_strong_to_stars,
                        lambda soup: formatting.inplace_convert_internal_links_to_links(
                            soup, os.path.dirname(self.url), "doc"
                        ),
                        formatting.inplace_convert_code_block_to_code_block,
                    ]:
                        converter(description)

                    text_description = formatting.compress_whitespace(description.text)
                    return f"{formatting.bold(span.text)}\n>{text_description}"
            return None
        except Exception as e:
            current_app.logger.exception(
                f"Error while trying to find {self.word} {arg}: {e}"
            )
            return None


class SubmitsCommandHandler(WebScrapingCommandHandler):
    def __init__(self, *, relink_timeout):
        super().__init__(relink_timeout=relink_timeout)

        # @JoshK: Should these be arguments to the superclass constructor?
        self.url = (
            "https://htcondor.readthedocs.io/en/latest/man-pages/condor_submit.html"
        )
        self.word = "submit file command"

    def get_description(self, page_soup, arg):
        try:
            start = page_soup.find("div", id="submit-description-file-commands")

            # No, we can't find_all_next("dt") and pass this regex to string,
            # because some of our dt tags have children, and "text" isn't a
            # keyword argument for some insane reason (it gets interpreted
            # as an attribute search).
            expr = re.compile(f"^{arg}( |$)", re.I)

            # ... lambda?
            def text_matches(tag):
                return tag.name == "dt" and expr.search(tag.text)

            dts = start.find_all_next(text_matches)

            whole_description = None
            for dt in dts:
                description = dt.find_next("dd")
                for converter in [
                    formatting.inplace_convert_em_to_underscores,
                    formatting.inplace_convert_inline_code_to_backticks,
                    formatting.inplace_convert_strong_to_stars,
                    lambda soup: formatting.inplace_convert_internal_links_to_links(
                        soup, os.path.dirname(self.url), "std.std-ref"
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
                text_description = text_description.replace("<br>", "\n>")

                result = f"{formatting.bold(dt.text)}\n>{text_description}"
                if whole_description is None:
                    whole_description = result
                else:
                    whole_description += f"\n{result}"

            return whole_description

        except Exception as e:
            current_app.logger.exception(
                f"Error while trying to find {self.word} {arg}: {e}"
            )
            return None
