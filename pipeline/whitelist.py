"""Source whitelist.

The problem statement's guardrail: the crawler reads whitelisted sources only,
never the open web. This is enforced here, in one place, and every fetch goes
through it. A URL that is not on the list is a hard failure, not a warning.
"""

from urllib.parse import urlparse

# Authoritative Singapore money guidance. Subdomains of these are allowed.
ALLOWED_HOSTS = (
    "cpf.gov.sg",
    "mas.gov.sg",
    "moneysense.gov.sg",
    "iras.gov.sg",
    "mof.gov.sg",
    "gov.sg",
)


class NotWhitelisted(Exception):
    """Raised when a URL is outside the approved source list."""


def check(url):
    """Return the parsed URL if its host is whitelisted, else raise.

    Matches the host exactly or as a subdomain, so "www.moneysense.gov.sg"
    passes via "moneysense.gov.sg" but "moneysense.gov.sg.evil.com" does not.
    """
    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise NotWhitelisted(f"Refusing non-HTTPS URL: {url}")

    host = (parsed.hostname or "").lower()
    for allowed in ALLOWED_HOSTS:
        if host == allowed or host.endswith("." + allowed):
            return parsed

    raise NotWhitelisted(
        f"{host or url!r} is not a whitelisted source. Allowed: {', '.join(ALLOWED_HOSTS)}"
    )


def is_allowed(url):
    """Boolean form of check(), for filtering."""
    try:
        check(url)
        return True
    except NotWhitelisted:
        return False
