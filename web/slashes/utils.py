import bs4


def convert_em_to_underscores(description):
    for em in description.find_all("em"):
        em.string = f"_{em.string}_"
        em.unwrap()


def convert_code_to_backticks(description):
    for span in description.select("code.docutils.literal.notranslate > span.pre"):
        span.string = f"`{span.string}`"
        span.parent.unwrap()
        span.unwrap()


def convert_strong_to_stars(description):
    for em in description.find_all("strong"):
        em.string = f"*{em.string}*"
        em.unwrap()
