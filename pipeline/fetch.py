"""Fetch a whitelisted page and reduce it to readable text.

Split the same way the lunchUncle tools are: an impure fetch function that does
the network call, and pure functions that shape the result. Only the pure parts
are tested.
"""

import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

from .whitelist import check

USER_AGENT = "dialect-money/0.1 (coursework; contact via repo)"
TIMEOUT_S = 30

# Tags whose text content is never page content.
SKIP_TAGS = {"script", "style", "noscript", "nav", "header", "footer", "svg"}

# Tags that should produce a line break in the extracted text.
BLOCK_TAGS = {
    "p", "div", "section", "article", "br", "li", "tr",
    "h1", "h2", "h3", "h4", "h5", "h6",
}


class _TextExtractor(HTMLParser):
    """Collect visible text, preserving rough block structure."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self._skip_depth += 1
        elif tag in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._parts.append(data)

    def text(self):
        return "".join(self._parts)


def extract_text(html):
    """Reduce an HTML document to visible text. Pure."""
    parser = _TextExtractor()
    parser.feed(html)
    return collapse(parser.text())


def collapse(text):
    """Normalise whitespace: trim lines, drop blanks, collapse runs. Pure."""
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def fetch_page(url):
    """Fetch a whitelisted URL and return {url, fetched_at, text}.

    Raises NotWhitelisted before any network call is made.
    """
    check(url)

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(charset, errors="replace")

    return {
        "url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "text": extract_text(html),
    }
