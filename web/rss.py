import bs4

from flask import request, current_app

from . import formatting
from . import slack


class RSSCommandHandler:
    def handle(self):
        secret = current_app.config["RSS_SHARED_SECRET"]
        if request.headers.get("x-shared-secret") != secret:
            return "invalid", 400

        blob = request.json
        if blob is None:
            return "no JSON found", 400

        for entry in blob:
            # slack.post_message(channel="#chtcbot-dev", text=entry)
            text = self.get_description(entry)
            if text is not None:
                # Don't forget to add the 'bot to the channel if you
                # change this!
                slack.post_message(channel="#birdwatcher", text=text)

        return "", 200

    def get_description(self, entry):
        link = entry.get("link")
        title = entry.get("title")
        # OK, WT_A_F: this is 'description' in the RSS feed and when
        # parsed by feedreader in the Lambda function!
        description = entry.get("summary")
        if link is None or title is None or description is None:
            return None

        soup = bs4.BeautifulSoup(description, "html.parser")
        formatting.inplace_convert_em_to_underscores(soup, selector="i")
        formatting.inplace_convert_external_links_to_links(soup)
        text_description = formatting.compress_whitespace(soup.text)

        text = f"<{link}|{title}>\n{text_description}"
        return text
