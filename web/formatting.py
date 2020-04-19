def plural(collection):
    return "" if len(collection) == 1 else "s"


def bold(text):
    return f"*{text}*"


def italic(text):
    return f"_{text}_"


def fixed(text):
    return f"`{text}`"


def link(url, text=None):
    if text is not None:
        return f"<{url}|{text}>"
    else:
        return url


def inplace_convert_em_to_underscores(soup):
    for em in soup.find_all("em"):
        em.string = italic(em.string)
        em.unwrap()


def inplace_convert_code_to_backticks(soup):
    for span in soup.select("code.docutils.literal.notranslate > span.pre"):
        span.string = fixed(span.string)
        span.parent.unwrap()
        span.unwrap()


def inplace_convert_strong_to_stars(soup):
    for em in soup.find_all("strong"):
        em.string = bold(em.string)
        em.unwrap()


def inplace_convert_internal_links_to_links(soup, base_url, inner_span_classes):
    for span in soup.select(f"a.reference.internal > span.{inner_span_classes}"):
        href = span.parent.get("href")
        url = f"{base_url.rstrip('/')}{'/' if not href.startswith('#') else ''}{href}"
        span.string = link(url, span.string)
        span.parent.unwrap()
        span.unwrap()
