def plural(collection):
    """Return an 's' if the collection has any number of elements but 1."""
    return "" if len(collection) == 1 else "s"


def bold(text):
    """Wrap text in markdown bold text markers."""
    return f"*{text}*"


def italic(text):
    """Wrap text in markdown italic text markers."""
    return f"_{text}_"


def fixed(text):
    """Wrap text in markdown inline fixed text markers."""
    return f"`{text}`"


def fixed_block(text):
    """Wrap text in markdown block fixed text markers."""
    return f"```\n{text}\n```"


def link(url, text=None):
    """Construct a Slack-encoded link. If text is None, the raw URL is returned."""
    if text is not None:
        return f"<{url}|{text}>"
    else:
        return url


def compress_whitespace(text):
    """Convert all whitespaces into a single space between words."""
    return " ".join(text.split()).replace("<br />", "\n")


def inplace_convert_em_to_underscores(soup, selector="em"):
    for em in soup.find_all(selector):
        em.string = italic(em.string)
        em.unwrap()


def inplace_convert_inline_code_to_backticks(
    soup, selector="code.docutils.literal.notranslate > span.pre"
):
    for span in soup.select(selector):
        span.string = fixed(span.string)
        span.parent.unwrap()
        span.unwrap()


def inplace_convert_strong_to_stars(soup, selector="strong"):
    for em in soup.find_all(selector):
        em.string = bold(em.string)
        em.unwrap()


def inplace_convert_internal_links_to_links(soup, base_url, inner_span_classes):
    for span in soup.select(f"a.reference.internal > span.{inner_span_classes}"):
        href = span.parent.get("href")
        url = f"{base_url.rstrip('/')}{'/' if not href.startswith('#') else ''}{href}"
        span.string = link(url, span.string)
        span.parent.unwrap()
        span.unwrap()


def inplace_convert_code_block_to_code_block(
    soup, selector="div.highlight-default.notranslate > div.highlight > pre"
):
    codes = soup.select(selector)
    for code in codes:
        code.replace_with(f"```{code.text}```".replace("\n", "<br />"))
