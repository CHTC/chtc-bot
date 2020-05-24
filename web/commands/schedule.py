from typing import List

from flask import request
from flask import current_app

import bs4
import html
import datetime

from . import commands
from ..executor import executor
from .. import slack, formatting, http


# Although this command does scrape the web, since it replies privately,
# we don't want to include the ForgetfulDict anti-spam protections.
class ScheduleCommandHandler(commands.CommandHandler):
    def __init__(self):
        self.url = (
            "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl"
        )

    def handle(self):
        user = request.form.get("user_id")
        raw_args = request.form.get("text")
        args = (
            []
            if raw_args is None or len(raw_args) == 0
            else [arg.strip() for arg in html.unescape(raw_args).split(",")]
        )

        dayofweek = datetime.datetime.today().weekday()
        if dayofweek >= 5:
            slack.post_message(channel=user, text="It's not a weekday.")
            # FIXME: for testing.
            dayofweek = 4
            executor.submit(self.reply, user, args, dayofweek)
            return ":thinking_face: :calendar:"
        else:
            executor.submit(self.reply, user, args, dayofweek)
            return ":thinking_face: :calendar:"

    def reply(self, user: str, args: List[str], dayofweek):
        phrasing = {
            "Office": "working",
            "Travel": "travelling",
            "Vacation": "on vacation",
            "Furlough": "furloughed",
            "Sick": "out sick",
            "Office (Home)": "working",
            "Office (WFH)": "working",
        }
        users_by_status = self.get_users_by_status(args, dayofweek, self.get_soup())

        replies = []
        for status, users in users_by_status.items():
            count = len(users)
            ing = phrasing.get(status) if phrasing.get(status) is not None else status

            if count == 1:
                user, link = users[0]
                line = f"Only <{link}|{user}> is {formatting.bold(ing)}."
                replies.append(line)
            else:
                line = f"{count} people are {formatting.bold(ing)}: "
                for user, link in users:
                    line = f"{line}<{link}|{user}>, "
                replies.append(line[:-2])

        reply = "\n".join(replies)

        # Why does channel=user work in handle() but not here?
        slack.post_message(channel="#chtcbot-dev", text=reply)

    def get_soup(self):
        username = "condor-team"
        password = current_app.config["SCHEDULE_COMMAND_PASSWORD"]

        response = http.cached_get_url(self.url, auth=(username, password))
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        return soup

    def get_users_by_status(self, users: List[str], dayofweek: int, soup):
        calendar = soup.select("table.calmonth")[0]
        schedule = calendar.find_next("table")
        rows = schedule.find_all("tr")

        users_by_status = {}
        for row in rows[2:]:
            href = row.select("td > a")[0]
            user = href.text
            link = href["href"]

            if len(users) != 0 and user not in users:
                continue

            td = row.find_all("td")[dayofweek + 1]
            status = td.text.split("\n")[0]

            if users_by_status.get(status) is None:
                users_by_status[status] = []
            users_by_status[status].append((user, link))

        return users_by_status
