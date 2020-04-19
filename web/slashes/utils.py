import bs4
from . import knobs

def convert_em_to_underscores(description):
    for em in description.find_all("em"):
        em.string = f"_{em.string}_"
        em.unwrap()


def convert_code_to_backticks(description):
    for span in description.select("code.docutils.literal.notranslate > span.pre"):
        span.string = f"`{span.string}`"
        span.parent.unwrap()
        span.unwrap()


# My code-reuse detector is going off.
def convert_strong_to_stars(description):
    for em in description.find_all("strong"):
        em.string = f"*{em.string}*"
        em.unwrap()


def convert_links_to_links(description):
    for span in description.select("a.reference.internal > span.std.std-ref"):
        href = span.parent.get("href")
        url = f"{knobs.KNOBS_URL}{href}"
        span.string = f"<{url}|{span.string}>"
        span.parent.unwrap()
        span.unwrap()
