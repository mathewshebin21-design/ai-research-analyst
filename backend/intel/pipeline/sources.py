"""Source tiers and de-duplication."""

import hashlib
import re
from urllib.parse import urlsplit, urlunsplit

OFFICIAL = re.compile(
    r"(\.gov(\.[a-z]{2})?$|\.gov\.uk$|\.gouv\.[a-z]{2}$|\.europa\.eu$|\.int$|\.bund\.de$|"
    r"\.admin\.ch$|\.gc\.ca$|\.ac\.uk$|\.edu$|^(www\.)?(oecd\.org|worldbank\.org|imf\.org|un\.org|ons\.gov\.uk)$)"
)
MEDIA = re.compile(
    r"(medium\.com|substack\.com|blogspot\.|wordpress\.|linkedin\.com|reddit\.com|quora\.com|youtube\.com)"
)


def domain(url: str) -> str:
    host = urlsplit(url).hostname or ""
    return host.removeprefix("www.")


def tier_for(url: str) -> str:
    """A = official, statistical or academic; C = user-generated or blog platforms; B = everything else."""
    host = domain(url)
    if OFFICIAL.search(host):
        return "A"
    if MEDIA.search(host):
        return "C"
    return "B"


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = "&".join(p for p in parts.query.split("&") if p and not p.lower().startswith(("utm_", "ref=", "fbclid")))
    return urlunsplit((parts.scheme.lower(), (parts.hostname or "").lower(), parts.path.rstrip("/"), query, ""))


def content_hash(text: str) -> str:
    return hashlib.sha256(re.sub(r"\s+", " ", text).strip().lower().encode()).hexdigest()
