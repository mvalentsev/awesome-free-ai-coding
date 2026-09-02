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

import json
import re
from dataclasses import dataclass, field
from typing import Callable, Mapping

import httpx

# Lives with the model layer, which is where the registry's own idea of "a host
# we already carry" belongs; re-exported here because every caller and test has
# always reached for it through this module.
from .models import domain_of  # noqa: F401

TIMEOUT = httpx.Timeout(30.0, connect=10.0)
UA = {"User-Agent": "freetier-radar/0.2"}

# The lists read on every run. Their opposite is sources.yaml: lists read once
# and put down, with the date and the reason. A candidate feed belongs in one
# file or the other, never both — freetier-check enforces exactly that.
CURATED_FEEDS = [
    # cheahjs/free-llm-api-resources was here until 2026-08-11, when the repo
    # turned out to be gone — GitHub 404s it, so raise_for_status dropped the
    # feed on every run and nobody noticed. The one list still carrying that
    # name (nherx/free-llm-api-resources) is a 6KB stub whose only links are
    # "Download Latest Release" and "Report Issues", so it is not a successor.
    "https://raw.githubusercontent.com/sourcegraph/awesome-code-ai/main/README.md",
    # A catalog rather than a page: one object per provider, endpoint and model
    # ids included, so a new gateway arrives here as a base URL to probe instead
    # of a sentence to interpret. Leads only, like the rest — it carried
    # "1M tokens/day" for Cerebras while cerebras.ai/pricing said $5 in credits.
    "https://raw.githubusercontent.com/vava-nessa/free-coding-models/main/sources.js",
    # Leads only: OmniRoute tracks free tiers aggressively but also ships spoofed
    # "no auth" channels for proprietary CLIs — claims still need official-page proof.
    # This was docs/getting-started/PROVIDERS-GUIDE.md until 2026-08-30, when both
    # files were measured against each other: the guide is a how-to that names one
    # provider id in 13161 characters, while FREE_TIERS.md is the file the project
    # edits when a free tier moves — 104 provider ids with a free type, a monthly
    # figure and a ToS flag each, of which 70 survive the 20000-character excerpt,
    # and the ones the cut loses are almost all already carried here. Its prose
    # half is the useful half twice over: it names what it has just REMOVED
    # (chutes, phind, kluster, aimlapi, yi) as well as what it has just added,
    # which is the half a list normally leaves out.
    "https://raw.githubusercontent.com/diegosouzapw/OmniRoute/main/docs/reference/FREE_TIERS.md",
    # A directory rather than a router: 30 providers in one table with a free-model
    # count and a "Credit Card?" column per row, regenerated daily from freellm.net.
    # The card column is the only machine-readable answer to that question anywhere
    # in these feeds. Leads only — the same table still lists GitHub Models, retired
    # 2026-07-30, and credits LLM7 with 15 free models when its catalog has none.
    "https://raw.githubusercontent.com/open-free-llm-api/awesome-freellm-apis/main/README.md",
    # A router's provider table: base URL, auth shape and a dated live-probe note
    # per gateway, written by someone who had to make each one answer. That makes
    # it the densest lead source here and the most opinionated — it carries
    # NavyAI and AINative next to SEA-LION, so the usual rule holds twice over:
    # leads only, official-page proof still required. Its verdicts are dated
    # opinions and two of them have now been wrong here: it says SambaNova's free
    # tier is "permanently gone" while docs.sambanova.ai still keys a Free Tier to
    # "no payment method linked with your account" (checked 2026-08-06 and again
    # 2026-08-14), and it credits AINative with "a recurring ~10M tokens/month free
    # allocation" that ainative.studio/pricing contradicts on its own page.
    "https://raw.githubusercontent.com/tashfeenahmed/freellmapi/main/server/src/providers/index.ts",
    # The only feed here that looks east: of the nine providers it carries that
    # nothing in this repository had a verdict on, seven appear in none of the
    # five feeds above — Intern AI, SenseNova, iFlytek Spark, Inception Labs and
    # three small Chinese resale gateways. Measured 2026-08-14 against all five.
    # Its own criterion is "limit request rate rather than token count", which is
    # why it surfaces recurring lanes rather than credit grants, and it accepts
    # OpenAI-format APIs only, so every row arrives with a base URL.
    # Leads only, and this one needs it twice over: its table is LLM-generated by
    # the maintainer's own admission, one row names a domain that has never
    # resolved (api.celebras.ai, a typo for Cerebras), and it lists gateways
    # serving gpt-5.x and claude-* "free" — one of which, G4F, is already
    # blocklisted here. It also credits Cerebras with a free lane at 30 RPM /
    # 900 RPH / 1440 RPD: neither figure occurs anywhere on
    # inference-docs.cerebras.ai/support/rate-limits, which on 2026-08-14 read
    # 5 RPM / 30K TPM for the same models and answered its own question with
    # "Is there a permanently free tier? No."
    "https://raw.githubusercontent.com/for-the-zero/Free-LLM-Collection/main/README.md",
    # Read once on 2026-08-14 and declined — sources.yaml carried the verdict, and
    # its reopen_if named the test it would have to pass: "its submissions start
    # surfacing providers the six curated feeds do not carry." On 2026-08-30 it
    # did. Its table had grown from 35 providers to 40 and one of the new rows is
    # Hetzner's Inference API, which appears in none of the six feeds above and in
    # no other list of the fourteen re-read that day. It keeps a "Credit Card?"
    # column and a base URL per row, so a lead arrives here already shaped like an
    # entry. Leads only, and this one has earned the warning: the Hetzner row it
    # was promoted for prints limits the vendor's own docs contradict — "3M input
    # / 60K output tokens per 60s" and a 24h row that does not exist, where
    # docs.hetzner.com reads 4M / 100k per 60s and 10 requests per 60s.
    "https://raw.githubusercontent.com/nejib1/Free-LLM/main/README.md",
]

# A machine catalog rather than a list: 185 providers, one object per model with
# a published cost, maintained for the opencode/models.dev ecosystem. Read as a
# digest instead of a feed — see models_dev_digest.
MODELS_DEV_URL = "https://models.dev/api.json"
MODELS_DEV_MAX_PROVIDERS = 50
MODELS_DEV_CAVEAT = (
    "PROVIDERS ON models.dev PUBLISHING AT LEAST ONE MODEL AT COST 0, excluding every domain "
    "already carried in the registry. A zero in this catalog is a lead and not evidence of a "
    "free tier: it also reads zero when the usage is included in a paid subscription (which is "
    "what every *-coding-plan and *-token-plan row is) and when the vendor quotes a currency "
    "the catalog could not parse (kenari publishes IDR and reads 38/38 free). Confirm on the "
    "vendor's own page before proposing any of these."
)

# Every catalog entry pointing at one of these is a runtime the user hosts, and
# its models are priced 0 because there is no vendor in the transaction.
LOCAL_HOSTS = {"127.0.0.1", "localhost", "0.0.0.0", "[::1]", "::1"}

NOISE_DOMAINS = {
    "reddit.com", "x.com", "twitter.com", "facebook.com", "youtube.com",
    "medium.com", "linkedin.com", "instagram.com", "tiktok.com",
}

PAGE_TEXT_LIMIT = 5000
# Raised from 12000 on 2026-08-11. A code-shaped feed appends: the provider
# added last sits at the bottom of the file, so the cut was landing exactly on
# the newest leads — 12000 chars of freellmapi's table carried 16 of its 25
# gateways and dropped Requesty, NavyAI, NaraRouter and SEA-LION, the four worth
# reading. 20000 costs ~15K more characters across all four feeds together.
# It stays at 20000: the cut moved to both ends of the file instead (see
# _feed_excerpt), which covered the same blind spot without buying more prompt.
FEED_TEXT_LIMIT = 20000


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
    # Kept apart from `feeds` because it is not an excerpt of anything a human
    # wrote: it is our own reading of a machine catalog, and the prompt has to
    # say so or the scout will quote it as though the vendor did.
    digests: dict[str, str] = field(default_factory=dict)
    providers: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.hits or self.pages or self.feeds or self.digests)


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


def _feed_excerpt(text: str, limit: int = FEED_TEXT_LIMIT) -> str:
    """A window on a feed too long to send whole, taken from both of its ends.

    Head-first was already known to cut the newest leads off an append-shaped
    file, which is why the limit was raised on 2026-08-11. Measuring the feeds
    again on 2026-08-14 showed the head is not simply the better half either:
    free-coding-models keeps its provider-to-endpoint map in the last 5005
    characters of `sources.js`, so reading 20000 from the top named 9 of its 20
    providers and not one endpoint. Both ends of the same budget name all 20
    with their endpoints, and the only other oversized feed lost no row it had
    under the old cut.

    The middle is what goes, and on these files the middle is per-model rows for
    providers both ends already name. The cut is marked rather than silent: a
    feed that reads as one continuous document invites the scout to conclude
    things about a list it has only seen the ends of.
    """
    if len(text) <= limit:
        return text
    head = int(limit * 0.75)
    return f"{text[:head]}\n… {len(text) - limit} characters elided …\n{text[head - limit:]}"


def _timeout_within(left: float | None) -> httpx.Timeout:
    """No single request may outlive the budget it is spending. The cap only ever
    shrinks the module's own timeouts, so a wide budget changes nothing."""
    if left is None:
        return TIMEOUT
    return httpx.Timeout(min(TIMEOUT.read, left), connect=min(TIMEOUT.connect, left))


# What a reader never sees and a model should not be fed: the site's menus and
# footer, stylesheets, the JavaScript-required notice, and scripts — except
# JSON-LD, which is page content in a structured coat (Freebuff publishes its
# FAQ there and nowhere else). Measured 2026-09-02 over the 45 live rows' first
# source urls: script blocks were a median 30% of the raw HTML and 98% of the
# worst page, and PAGE_TEXT_LIMIT was being spent on them and on the menus —
# the retirement sweep's one signal was the word "Deprecations" in
# ai.google.dev's sidebar, while three mentions in body text sat past the cap.
_NOISE_BLOCK = re.compile(r"<(script|style|nav|footer|noscript)\b[^>]*>.*?</\1\s*>", re.S | re.I)
_LD_JSON = re.compile(r"""type\s*=\s*["']?application/ld\+json""", re.I)


def page_text(html: str) -> str:
    """The page as prose: noise blocks dropped, tags stripped, whitespace
    collapsed. What the scout reads and what a quote is verified against, so
    the two never disagree about what was on the page."""
    def drop(match: re.Match) -> str:
        block = match.group(0)
        opening = block[:block.find(">") + 1]
        if match.group(1).lower() == "script" and _LD_JSON.search(opening):
            return block
        return " "
    text = re.sub(r"<[^>]+>", " ", _NOISE_BLOCK.sub(drop, html))
    return re.sub(r"\s+", " ", text)


def fetch_page_texts(urls: list[str], client: httpx.Client | None = None,
                     limit: int = PAGE_TEXT_LIMIT,
                     time_left: Callable[[], float] | None = None) -> dict[str, str]:
    """GET each URL, strip tags, collapse whitespace. Failures become empty strings.

    `time_left` returns the seconds the run has left (`Deadline.remaining`). Given
    one, the loop stops rather than starting a fetch it cannot afford: ten
    arbitrary hosts at 30 seconds of read timeout each is five minutes of run
    riding on strangers' uptime. A URL left unfetched is simply absent from the
    result — every caller already reads it with `.get(url, "")`, and claiming an
    empty page would be claiming we looked.
    """
    own = client is None
    client = client or httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers=UA)
    out: dict[str, str] = {}
    try:
        for u in urls:
            left = time_left() if time_left is not None else None
            if left is not None and left <= 0:
                break
            try:
                r = client.get(u, timeout=_timeout_within(left))
                # A catalog answers JSON, and JSON is not HTML: a "<" in one
                # model's description is where the tag stripper would start
                # eating, and Pollinations' 20-kilobyte catalog came back as
                # 286 characters.
                is_json = "json" in r.headers.get("content-type", "").lower()
                text = re.sub(r"\s+", " ", r.text) if is_json else page_text(r.text)
                out[u] = text[:limit]
            except httpx.HTTPError:
                out[u] = ""
    finally:
        if own:
            client.close()
    return out


def models_dev_digest(client: httpx.Client, known_domains: set[str],
                      url: str = MODELS_DEV_URL,
                      max_providers: int = MODELS_DEV_MAX_PROVIDERS) -> str:
    """Providers on models.dev carrying at least one zero-cost row, minus the ones
    already answered by the curated files.

    Not a feed: 3.7 MB and 185 providers cannot go in a prompt, and would be
    mostly prices for models nobody here is looking for. What survives the read
    is the one question this project asks — which vendor publishes a row at
    zero — as a line per provider with the endpoint to probe. Measured
    2026-08-14: 46 unknown providers, 6075 characters.

    A zero here is a lead and never evidence, which the digest says out loud
    because two failure modes were verified the day it was written and neither
    is visible in the number itself.
    """
    try:
        r = client.get(url)
        r.raise_for_status()
        catalog = r.json()
    except (httpx.HTTPError, json.JSONDecodeError):
        return ""
    if not isinstance(catalog, dict):
        return ""

    rows = []
    for pid, p in catalog.items():
        if not isinstance(p, dict):
            continue
        models = p.get("models")
        if not isinstance(models, dict):
            continue
        free = [m for m in models.values() if isinstance(m, dict) and _is_zero_cost(m)]
        if not free:
            continue
        endpoint = p.get("api") or p.get("doc") or ""
        host = domain_of(endpoint).split(":")[0]
        if not host or host in LOCAL_HOSTS:
            continue
        if any(host == k or host.endswith("." + k) for k in known_domains if k):
            continue
        ids = ", ".join(str(m.get("id") or "?") for m in free[:3])
        rows.append((len(free), f"- {pid} ({p.get('name') or pid}) api {p.get('api') or '—'} "
                                f"doc {p.get('doc') or '—'} — {len(free)}/{len(models)} "
                                f"rows at cost 0: {ids}"))
    if not rows:
        return ""

    rows.sort(key=lambda r: -r[0])
    lines = [MODELS_DEV_CAVEAT] + [line for _, line in rows[:max_providers]]
    if len(rows) > max_providers:
        lines.append(f"- ... {len(rows) - max_providers} further providers with a zero-cost "
                     f"row omitted from this digest.")
    return "\n".join(lines)


def _is_zero_cost(model: dict) -> bool:
    cost = model.get("cost")
    if not isinstance(cost, dict):
        return False
    return cost.get("input") == 0 and cost.get("output") == 0


def _searchers(client: httpx.Client, env: Mapping[str, str]) -> list[tuple[str, Callable[[str], list[Hit]]]]:
    searchers: list[tuple[str, Callable[[str], list[Hit]]]] = []
    if env.get("TAVILY_API_KEY"):
        searchers.append(("tavily", lambda q: tavily_search(client, env["TAVILY_API_KEY"], q)))
    searchers.append(("hn", lambda q: hn_search(client, q)))
    searchers.append(("github", lambda q: github_search(client, q, env.get("GITHUB_TOKEN"))))
    return searchers


def gather_evidence(queries: list[str], known_domains: set[str], env: Mapping[str, str],
                    http: httpx.Client | None = None, max_pages: int = 10,
                    time_left: Callable[[], float] | None = None) -> Evidence:
    """Run every available source over the queries and assemble deduplicated evidence.

    `time_left` returns the seconds this phase may still spend. It exists because
    the phase runs before the first LLM call and used to be bounded only by the
    per-request timeouts: a typical run gathers everything in ~20 seconds, but
    three searchers over five queries plus ten pages plus the feeds can hold the
    line open for the better part of an hour, and the run's whole budget with it.
    Every phase after this one would then report "skipped" while the workflow
    reported success — nothing found, nothing wrong, nothing to see.

    Running out is not an error: what has been gathered is returned and the scout
    reasons over that. The clock is read between calls, so the phase can overrun
    by at most the one request already in flight.
    """
    ev = Evidence()
    own = http is None
    client = http or httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers=UA)

    def spent() -> bool:
        return time_left is not None and time_left() <= 0

    try:
        for name, search in _searchers(client, env):
            found = False
            for q in queries:
                if spent():
                    break
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

        ev.pages = fetch_page_texts([h.url for h in kept[:max_pages]], client,
                                    time_left=time_left)

        for feed in CURATED_FEEDS:
            if spent():
                break
            try:
                r = client.get(feed)
                r.raise_for_status()
                ev.feeds[feed] = _feed_excerpt(r.text, FEED_TEXT_LIMIT)
            except httpx.HTTPError:
                continue
        if ev.feeds:
            ev.providers.append("curated-feeds")

        if not spent():
            digest = models_dev_digest(client, known_domains)
            if digest:
                ev.digests[MODELS_DEV_URL] = digest
                ev.providers.append("models.dev")
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
    for url, text in ev.digests.items():
        lines.append(f"\nDERIVED FROM {url} — our own reading of that catalog, not its words:\n{text}")
    return "\n".join(lines)
