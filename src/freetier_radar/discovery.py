"""Multi-source web discovery: search providers and keyless feeds feeding the scout.

Sources, each optional and independent:
- Tavily search                 (needs TAVILY_API_KEY)
- Hacker News via Algolia       (keyless)
- GitHub repository search      (keyless; GITHUB_TOKEN raises rate limits)
- Curated awesome-list feeds    (keyless raw markdown)

A source that has no key or errors out contributes nothing instead of failing
the run, so the scout always gets the best evidence available.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Mapping
from urllib.parse import urlparse

import httpx

TIMEOUT = httpx.Timeout(30.0, connect=10.0)
UA = {"User-Agent": "freetier-radar/0.2"}

CURATED_FEEDS = [
    "https://raw.githubusercontent.com/cheahjs/free-llm-api-resources/main/README.md",
    "https://raw.githubusercontent.com/sourcegraph/awesome-code-ai/main/README.md",
    # Leads only: OmniRoute tracks free tiers aggressively but also ships spoofed
    # "no auth" channels for proprietary CLIs — claims still need official-page proof.
    "https://raw.githubusercontent.com/diegosouzapw/OmniRoute/main/docs/getting-started/PROVIDERS-GUIDE.md",
]

NOISE_DOMAINS = {
    "reddit.com", "x.com", "twitter.com", "facebook.com", "youtube.com",
    "medium.com", "linkedin.com", "instagram.com", "tiktok.com",
}

PAGE_TEXT_LIMIT = 5000
FEED_TEXT_LIMIT = 12000


@dataclass
class Hit:
    url: str
    title: str
    snippet: str
    source: str


@dataclass
class Evidence:
    hits: list[Hit] = field(default_factory=list)
    pages: dict[str, str] = field(default_factory=dict)
    feeds: dict[str, str] = field(default_factory=dict)
    providers: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.hits or self.pages or self.feeds)


def domain_of(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def tavily_search(client: httpx.Client, key: str, query: str, count: int = 6) -> list[Hit]:
    r = client.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {key}"},
        json={"query": query, "max_results": count},
    )
    r.raise_for_status()
    return [
        Hit(it["url"], it.get("title", ""), (it.get("content") or "")[:400], "tavily")
        for it in r.json().get("results", [])
        if it.get("url")
    ]


def hn_search(client: httpx.Client, query: str, count: int = 8) -> list[Hit]:
    r = client.get(
        "https://hn.algolia.com/api/v1/search",
        params={"query": query, "tags": "story", "hitsPerPage": count},
    )
    r.raise_for_status()
    hits = []
    for h in r.json().get("hits", []):
        url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
        hits.append(Hit(url, h.get("title", ""), "", "hn"))
    return hits


def github_search(client: httpx.Client, query: str, token: str | None = None,
                  count: int = 8, min_stars: int = 20) -> list[Hit]:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = client.get(
        "https://api.github.com/search/repositories",
        params={"q": query, "sort": "updated", "per_page": count},
        headers=headers,
    )
    r.raise_for_status()
    return [
        Hit(it["html_url"], it.get("full_name", ""), (it.get("description") or "")[:400], "github")
        for it in r.json().get("items", [])
        if it.get("stargazers_count", 0) >= min_stars
    ]


def fetch_page_texts(urls: list[str], client: httpx.Client | None = None,
                     limit: int = PAGE_TEXT_LIMIT) -> dict[str, str]:
    """GET each URL, strip tags, collapse whitespace. Failures become empty strings."""
    own = client is None
    client = client or httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers=UA)
    out: dict[str, str] = {}
    try:
        for u in urls:
            try:
                r = client.get(u)
                text = re.sub(r"<[^>]+>", " ", r.text)
                out[u] = re.sub(r"\s+", " ", text)[:limit]
            except httpx.HTTPError:
                out[u] = ""
    finally:
        if own:
            client.close()
    return out


def _searchers(client: httpx.Client, env: Mapping[str, str]) -> list[tuple[str, Callable[[str], list[Hit]]]]:
    searchers: list[tuple[str, Callable[[str], list[Hit]]]] = []
    if env.get("TAVILY_API_KEY"):
        searchers.append(("tavily", lambda q: tavily_search(client, env["TAVILY_API_KEY"], q)))
    searchers.append(("hn", lambda q: hn_search(client, q)))
    searchers.append(("github", lambda q: github_search(client, q, env.get("GITHUB_TOKEN"))))
    return searchers


def gather_evidence(queries: list[str], known_domains: set[str], env: Mapping[str, str],
                    http: httpx.Client | None = None, max_pages: int = 10) -> Evidence:
    """Run every available source over the queries and assemble deduplicated evidence."""
    ev = Evidence()
    own = http is None
    client = http or httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers=UA)
    try:
        for name, search in _searchers(client, env):
            found = False
            for q in queries:
                try:
                    hits = search(q)
                except httpx.HTTPError:
                    continue
                found = found or bool(hits)
                ev.hits.extend(hits)
            if found:
                ev.providers.append(name)

        seen: set[str] = set()
        kept: list[Hit] = []
        for h in ev.hits:
            d = domain_of(h.url)
            if h.url in seen or d in NOISE_DOMAINS or d in known_domains:
                continue
            seen.add(h.url)
            kept.append(h)
        ev.hits = kept

        ev.pages = fetch_page_texts([h.url for h in kept[:max_pages]], client)

        for feed in CURATED_FEEDS:
            try:
                r = client.get(feed)
                r.raise_for_status()
                ev.feeds[feed] = r.text[:FEED_TEXT_LIMIT]
            except httpx.HTTPError:
                continue
        if ev.feeds:
            ev.providers.append("curated-feeds")
    finally:
        if own:
            client.close()
    return ev


def format_evidence(ev: Evidence, max_hits: int = 40) -> str:
    lines = ["SEARCH HITS:"]
    for h in ev.hits[:max_hits]:
        lines.append(f"- [{h.source}] {h.title} — {h.url} :: {h.snippet}")
    for url, text in ev.pages.items():
        if text:
            lines.append(f"\nPAGE {url}:\n{text}")
    for url, text in ev.feeds.items():
        lines.append(f"\nCURATED FEED {url} (excerpt):\n{text}")
    return "\n".join(lines)
