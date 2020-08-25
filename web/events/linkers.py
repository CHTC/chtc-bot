import re
import time
from typing import List, MutableMapping

import bs4

from .. import formatting, http, slack
from .handlers import RegexMessageHandler


class TicketLinker(RegexMessageHandler):
    def __init__(self, *, regex, url, prefix, relink_timeout: float):
        super().__init__(regex=regex)

        self.url = url
        self.prefix = prefix

        self.relink_timeout = relink_timeout

        self.recently_linked_cache: MutableMapping[(str, str), float] = {}
        self.last_ticket_cleanup = time.monotonic()

    def filter_matches(self, message, matches: List[str]):
        now = time.monotonic()
        self._recently_linked_cleanup(now)
        return [
            match for match in matches if not self.recently_linked(message["channel"], match, now)
        ]

    def recently_linked(self, channel: str, ticket_id: str, now: float):
        key = (channel, ticket_id.lower())
        if key in self.recently_linked_cache:
            return True
        else:
            self.recently_linked_cache[key] = now
            return False

    def _recently_linked_cleanup(self, now: float):
        """
        For a side-project, let's not think too hard.  Just purge our
        memory of old ticket IDs when we handle a new message, rather
        than on a timer in another thread.  Don't bother to scan the
        whole list on every message, though, just if it's been more
        than five seconds since the last clean-up.
        """
        if self.last_ticket_cleanup + self.relink_timeout > now:
            return

        self.recently_linked_cache = {
            _: last_linked
            for _, last_linked in self.recently_linked_cache.items()
            if not last_linked + self.relink_timeout < now
        }
        self.last_ticket_cleanup = now

    def handle_message(self, message, matches: List[str]):
        msg = self.generate_reply(matches)

        # respond in the same channel the message was sent in
        channel = message["channel"]

        # if the message was in a thread, respond in that thread
        thread_ts = message.get("thread_ts")

        slack.post_message(text=msg, channel=channel, thread_ts=thread_ts)

    def generate_reply(self, matches):
        msgs = []
        for ticket_id in matches:
            url = self.url.format(ticket_id)

            msg = formatting.link(url, f"{self.prefix}#{ticket_id}")

            summary = self.get_ticket_summary(url)
            if summary is not None:
                msg += f" | {summary}"

            msgs.append(msg)

        return "\n".join(msgs)

    def get_ticket_summary(self, url: str):
        return None


class FlightworthyTicketLinker(TicketLinker):
    def __init__(self, *, relink_timeout):
        super().__init__(
            relink_timeout=relink_timeout,
            regex=re.compile(r"gt#([1-9]\d*)[^ A-Za-z]*(?: |$)", re.I),
            url="https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn={}",
            prefix="GT",
        )

    def get_ticket_summary(self, url: str):
        response = http.cached_get_url(url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        title = soup.h2.string.split(": ")[-1]
        status = self.find_info_table_element(soup, "Status:")
        last_change = self.find_info_table_element(soup, re.compile(r"Last\sChange:"))

        return f"{title} [{formatting.bold(status)} at {last_change}]"

    def find_info_table_element(self, soup, element):
        return soup.find("td", text=element).find_next("td").b.string


class RTTicketLinker(TicketLinker):
    def __init__(self, *, relink_timeout):
        super().__init__(
            relink_timeout=relink_timeout,
            regex=re.compile(r"rt#([1-9]\d*)[^ A-Za-z]*(?: |$)", re.I),
            url="https://crt.cs.wisc.edu/rt/Ticket/Display.html?id={}",
            prefix="RT",
        )
