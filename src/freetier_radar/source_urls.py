"""Shared syntax checks for source links, with explicit allowed schemes."""
import re
from urllib.parse import urlparse


def valid_source_url(value: str, *, schemes: tuple[str, ...] = ('https',)) -> bool:
    if re.search(r'[\x00-\x20\x7f]', value):
        return False
    try:
        parsed = urlparse(value)
        parsed.port  # Reject malformed port numbers as well as malformed hosts.
        return (parsed.scheme in schemes and bool(parsed.hostname)
                and parsed.username is None and parsed.password is None)
    except ValueError:
        return False
