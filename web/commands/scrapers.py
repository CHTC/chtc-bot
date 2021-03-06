import abc
import html
import os
import re
from typing import List

import bs4
from flask import current_app, request

from .. import formatting, http, slack, utils
from ..executor import executor
from ..utils import ForgetfulDict
from . import commands


def hard_shorten(text, limit):
    while text[limit] != " ":
        limit -= 1
    return text[0:limit]


class WebScrapingCommandHandler(commands.CommandHandler):
    def __init__(self, *, rescrape_timeout, url, word):
        self.url = url
        self.word = word

        self.recently_scraped = ForgetfulDict(memory_time=rescrape_timeout)

    def handle(self):
        channel = request.form.get("channel_id")

        requested_args = html.unescape(request.form.get("text")).split(" ")
        skipped_args, args = self.seen_and_unseen(requested_args, channel)

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
            message += formatting.plural(skipped_args)
            message += f" {', '.join(formatting.bold(k) for k in skipped_args)}"
        return (message, 200)

    def reply(self, channel, user, args: List[str]):
        soup = self.soup_line()

        lines = [
            f"<@{user}> asked for information on {self.word}"
            + f"{formatting.plural(args)}"
            + f" {', '.join(formatting.bold(k) for k in args)}"
        ]

        descriptions = {arg: self.get_description(soup, arg) for arg in args}
        good, bad = utils.partition_mapping(descriptions, key=lambda v: v is not None)

        if bad:
            p1 = "they were" if len(bad) > 1 else "it was"
            p2 = "don't" if len(bad) > 1 else "it doesn't"
            lines.append(
                f"I couldn't find information on"
                + f" {', '.join(formatting.bold(k) for k in bad.keys())}"
                + f".  Perhaps {p1} misspelled, or {p2} exist?"
            )

        if len(good) == 0:
            slack.post_message(channel=channel, text="\n".join(lines))

        for arg, (description, anchor) in good.items():
            full_url = f"{self.url}#{anchor}"
            if len(description) < 512:
                text = f"{lines[0]}\n{description}"
            else:
                short = hard_shorten(description, 512)
                text = f"{lines[0]}\n{short} ... [<{full_url}|the rest>]\n"
            slack.post_message(channel=channel, text=text)

    def seen_and_unseen(self, requested_args, channel):
        seen, unseen = utils.partition_collection(
            requested_args,
            key=lambda arg: not self.recently_scraped.set(
                (arg.upper(), channel), None, update_existing=False
            ),
        )

        return seen, unseen

    def soup_line(self):
        response = http.cached_get_url(self.url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        return soup

    @abc.abstractmethod
    def get_description(self, page_soup: bs4.BeautifulSoup, arg: str):
        raise NotImplementedError


class KnobsCommandHandler(WebScrapingCommandHandler):
    def __init__(self, *, rescrape_timeout):
        super().__init__(
            rescrape_timeout=rescrape_timeout,
            url="https://htcondor.readthedocs.io/en/latest/admin-manual/configuration-macros.html",
            word="knob",
        )

    def get_description(self, page_soup: bs4.BeautifulSoup, arg: str):
        try:
            header = page_soup.find("span", id=arg)

            anchor = header["id"]
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

            text_description = format_lists_and_paragraphs(description)
            return f"{formatting.bold(arg)}\n>{text_description}", anchor
        except Exception as e:
            current_app.logger.exception(f"Error while trying to find {self.word} {arg}: {e}")
            return None


class JobAdsCommandHandler(WebScrapingCommandHandler):
    def __init__(self, *, rescrape_timeout):
        super().__init__(
            rescrape_timeout=rescrape_timeout,
            url="https://htcondor.readthedocs.io/en/latest/classad-attributes/job-classad-attributes.html",
            word="job ad attribute",
        )

    def get_description(self, page_soup: bs4.BeautifulSoup, arg: str):
        try:
            # This can't be the efficient way to do this.
            spans = page_soup.select("dt > code.docutils.literal.notranslate > span.pre")

            for span in spans:
                if span.text.lower() == arg.lower():
                    anchor = span.find_previous("span", class_="target")["id"]
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

                    text_description = format_lists_and_paragraphs(description)
                    return f"{formatting.bold(span.text)}\n>{text_description}", anchor
            return None
        except Exception as e:
            current_app.logger.exception(f"Error while trying to find {self.word} {arg}: {e}")
            return None


def hard_wrap_line(line, spaces):
    rv = ""
    length = 0
    for word in line.split():
        if length > 80:
            rv += f"<br>{spaces}"
            length = 0
        length += len(word.replace("<space>", " ")) + 1
        rv += f"{word} "
    return rv[0:-1]


def hard_wrap(text, spaces):
    rv = ""
    lines = text.split("<br>")
    for line in lines:
        rv += hard_wrap_line(line, spaces) + "<br>"
    return rv[0:-4]


# BeautifulSoup assumes that you always want to be able to traverse the whole
# soup from any tag in it, so you have to do your own recursion if you care
# about tag boundaries.
#
# If we find an example of a list nested under an ordered list item, we can
# convert depth to the spaces string used to do word-wrapping.
def replace_lists_in(description, depth=0, ordered=False):
    try:
        children = description.children
    except AttributeError:
        return

    number = 1
    for child in children:
        if child.name == "ul":
            replace_lists_in(child, depth + 1)

            child.replace_with(f"<br>{child.text}")
        elif child.name == "ol":
            replace_lists_in(child, depth + 1, True)

            child.replace_with(f"<br>{child.text}")
        else:
            replace_lists_in(child, depth)

        if child.name == "li":
            indent = "<space><space><space><space>"

            spaces = ""
            for i in range(0, depth):
                spaces += indent

            bullet = "\u2022"
            if ordered:
                indent += "<space>"
                bullet = f"{number}."
                number += 1

            hw = hard_wrap(child.text, f"{spaces}{indent}")
            child.replace_with(f"{spaces}{bullet} {hw}<br>")


def preserve_paragraph_breaks_in(description):
    for p in description.find_all("p"):
        p.replace_with(f"<br>{p.text}<br>")


def format_lists_and_paragraphs(description):
    replace_lists_in(description)
    preserve_paragraph_breaks_in(description)

    text_description = formatting.compress_whitespace(description.text)
    # When a list is the last tag in a list item, we insert one
    # <br> for end of the last item in the last and another for
    # end of the containing list item.  Merge them together.
    text_description = text_description.replace("<br><br>", "<br>")
    text_description = text_description.replace("<br>", "\n>")
    text_description = text_description.replace("<space>", " ")

    if text_description.endswith("\n>"):
        text_description = text_description[0:-1]
    if text_description.startswith("\n"):
        text_description = text_description[2:]

    return text_description


class SubmitsCommandHandler(WebScrapingCommandHandler):
    def __init__(self, *, rescrape_timeout):
        super().__init__(
            rescrape_timeout=rescrape_timeout,
            url="https://htcondor.readthedocs.io/en/latest/man-pages/condor_submit.html",
            word="submit file command",
        )

    def get_description(self, page_soup: bs4.BeautifulSoup, arg: str):
        try:
            start = page_soup.find("div", id="submit-description-file-commands")

            # No, we can't find_all_next("dt") and pass this regex to string,
            # because some of our dt tags have children, and "text" isn't a
            # keyword argument for some insane reason (it gets interpreted
            # as an attribute search).
            expr = re.compile(f"^{arg}( |$)", re.I)

            def text_matches(tag):
                return tag.name == "dt" and expr.search(tag.text)

            dts = start.find_all_next(text_matches)

            # We'll assume that all of the subsequent descriptions are
            # immediately subsequent and that the first anchor is the
            # correct one to use if the description is shortened.
            anchor = None
            descriptions = []
            for dt in dts:
                if anchor is None:
                    anchor = dt.find_previous("span", class_="target")["id"]
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

                text_description = format_lists_and_paragraphs(description)
                result = f"{formatting.bold(dt.text)}\n>{text_description}"
                descriptions.append(result)

            if len(descriptions) == 0:
                return None
            elif len(descriptions) == 1:
                return (descriptions[0], anchor)
            else:
                return ("\n".join(descriptions), anchor)

        except Exception as e:
            current_app.logger.exception(f"Error while trying to find {self.word} {arg}: {e}")
            return None
