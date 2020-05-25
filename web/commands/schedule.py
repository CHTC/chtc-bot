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

        tz = datetime.timezone(-datetime.timedelta(hours=5))
        dayofweek = datetime.datetime.now(tz=tz).weekday()
        if dayofweek >= 5:
            return ":confused: :calendar: It's not a weekday, there's no schedule."
        else:
            executor.submit(self.reply, user, args, dayofweek)
            return ":thinking_face: :calendar:"

    def reply(self, reply_to: str, args: List[str], dayofweek):
        users_by_status = self.get_users_by_status(args, dayofweek, self.get_soup())

        replies = []
        for status, users in users_by_status.items():
            count = len(users)
            if count == 1:
                user, link, hours = users[0]
                line = f"<{link}|{user}> is {formatting.bold(status)}."
                replies.append(line)
            else:
                line = f"{count} people are {formatting.bold(status)}: "
                for user, link, hours in users:
                    if user == users[-1][0]:
                        line = f"{line}and <{link}|{user}>."
                    else:
                        line = f"{line}<{link}|{user}>, "
                replies.append(line)
        reply = "\n".join(replies)

        slack.post_message(channel=reply_to, text=reply)

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

        phrasing = {
            "Office": "working",
            "Travel": "travelling",
            "Vacation": "on vacation",
            "Furlough": "furloughed",
            "Sick": "out sick",
            "Sick:4": "out sick (half day)",
            "Office (Home)": "working",
            "Office (WFH)": "working",
        }

        users_by_status = {}
        for row in rows[2:]:
            href = row.select("td > a")[0]
            user = href.text
            link = href["href"]

            if len(users) != 0 and user not in users:
                continue

            td = row.find_all("td")[dayofweek + 1]
            fields = td.text.split("\n")
            status = fields[0]
            hours = fields[1] if len(fields) > 1 and len(fields[1]) > 0 else None
            status = (
                phrasing.get(status) if phrasing.get(status) is not None else status
            )

            if users_by_status.get(status) is None:
                users_by_status[status] = []
            users_by_status[status].append((user, link, hours))

        return users_by_status
