"""Multi-source web discovery: search providers and keyless feeds feeding the scout.

Sources, each optional and independent:
- Tavily search                 (needs TAVILY_API_KEY)
- Hacker News via Algolia       (keyless)
- GitHub repository search      (keyless; GITHUB_TOKEN raises rate limits)
- Curated awesome-list feeds    (keyless raw files on GitHub)
- models.dev catalog digest     (keyless)

A source that has no key or errors out contributes nothing instead of failing
the run, so the scout always gets the best evidence available. Entry point:
`gather_evidence`, rendered for the prompt by `format_evidence`.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Callable, Mapping
from urllib.parse import urlparse

import httpx

# Defined in models.py; scout and the tests import domain_of from here.
from .models import domain_of, is_covered  # noqa: F401

TIMEOUT = httpx.Timeout(30.0, connect=10.0)
UA = {"User-Agent": "freetier-radar/0.2"}

# The lists read on every run. Their opposite is sources.yaml: lists read once
# and put down, with the date and the reason. A candidate feed belongs in one
# file or the other, never both — freetier-check enforces that.
# A feed on GitHub is read at HEAD, the branch its repository calls its own,
# never at a branch named here: a project can move its work to another branch
# and leave the named one standing, answering 200 with an old file (see
# test_every_github_feed_is_read_at_the_branch_its_repository_works_on). A
# fragment names the section of the file that is the list — see _section_bounds.
CURATED_FEEDS = [
    # One entry per provider with its free tier in a phrase and its sign-up URL,
    # generated from the project's own catalog (sources.js) by its own script,
    # and what the catalog has removed and why. Leads only, like the rest.
    "https://raw.githubusercontent.com/vava-nessa/free-coding-models/HEAD/docs/providers.md",
    # Leads only: OmniRoute tracks free tiers aggressively but also ships spoofed
    # "no auth" channels for proprietary CLIs — claims still need official-page proof.
    # FREE_TIERS.md is the file the project edits when a free tier moves: a row per
    # provider with a free type, a monthly figure and a ToS flag, and notes on what
    # it has just removed as well as added. Read from its per-provider table up to
    # the glossary; the head is methodology.
    "https://raw.githubusercontent.com/diegosouzapw/OmniRoute/HEAD/docs/reference/FREE_TIERS.md#per-provider-free-tier:glossary",
    # A directory rather than a router: one table of providers with a free-model
    # count and a "Credit Card?" column per row, regenerated daily from freellm.net.
    # Leads only. Read from its provider directory up to its per-model catalog: the
    # directory and its base-URL table sit between a pitch and that catalog.
    "https://raw.githubusercontent.com/open-free-llm-api/awesome-freellm-apis/HEAD/README.md#provider-directory:best-free-models",
    # A router's own list of the providers it takes keys for: one line each with a
    # label that says what the free offer is ("daily free-model quota", "shared
    # monthly credits", "$5 monthly with payment method") and the page that issues
    # the key. Leads only, and opinionated: read a lead against the page where the
    # plan is sold, not the docs about it.
    "https://raw.githubusercontent.com/tashfeenahmed/freellmapi/HEAD/client/src/components/keys/shared.tsx",
    # It looks east: Chinese providers such as Intern AI, SenseNova and iFlytek
    # Spark. Its criterion is "limit request rate rather than token count", so it
    # surfaces recurring lanes rather than credit grants, and it takes
    # OpenAI-format APIs only, so every row arrives with a base URL. Leads only,
    # twice over: the maintainer says the table is LLM-generated, and it lists
    # gateways serving gpt-5.x and claude-* "free", G4F (blocklisted here) among them.
    "https://raw.githubusercontent.com/for-the-zero/Free-LLM-Collection/HEAD/README.md",
    # A "Credit Card?" column and a base URL per row, so a lead arrives already
    # shaped like an entry. Leads only: its limits can contradict the vendor's own
    # docs. Read from its provider directory up to its guides, which takes in the
    # directory and its base-URL table.
    "https://raw.githubusercontent.com/nejib1/Free-LLM/HEAD/README.md#provider-directory:guides",
]

# A machine catalog rather than a list: one object per model with a published
# cost, maintained for the opencode/models.dev ecosystem. Read as a digest
# instead of a feed — see models_dev_digest.
MODELS_DEV_URL = "https://models.dev/api.json"
MODELS_DEV_MAX_PROVIDERS = 50
MODELS_DEV_CAVEAT = (
    "PROVIDERS ON models.dev PUBLISHING AT LEAST ONE MODEL AT COST 0, excluding every domain "
    "the registry, the watchlist or the blocklist already answers. A zero in this catalog is a "
    "lead and not evidence of a "
    "free tier: it also reads zero when the usage is included in a paid subscription (which is "
    "what every *-coding-plan and *-token-plan row is) and when the vendor quotes a currency "
    "the catalog could not parse (kenari publishes IDR and reads 38/38 free). Confirm on the "
    "vendor's own page before proposing any of these."
)

# Every catalog entry pointing at one of these is a runtime the user hosts, and
# its models are priced 0 because there is no vendor in the transaction.
LOCAL_HOSTS = {"127.0.0.1", "localhost", "0.0.0.0", "[::1]", "::1"}

# A catalog entry whose only URL is a package page or a repository names a
# client, not a vendor: nothing on these hosts can be matched to a registry
# domain or probed as an offer.
CODE_HOSTS = {"github.com", "npmjs.com", "pypi.org"}

NOISE_DOMAINS = {
    "reddit.com", "x.com", "twitter.com", "facebook.com", "youtube.com",
    "medium.com", "linkedin.com", "instagram.com", "tiktok.com",
}

PAGE_TEXT_LIMIT = 5000
# The characters of a feed's section that reach the prompt; a longer section
# loses its middle (see _feed_excerpt).
FEED_TEXT_LIMIT = 20000
# Past this share of a feed's section falling in the elided middle, the run says
# so: a list that grows keeps its head and tail and loses its middle unseen.
FEED_ELIDED_WARN = 0.25


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
    # One line per curated feed that is failing the scout, for the run's log and
    # status file — never for the prompt. See `_read_feed`.
    feed_warnings: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.hits or self.pages or self.feeds or self.digests)

    def describe_providers(self) -> str:
        """Every source that answered, a search with the hits it kept: a source
        is listed when it answers, before the filter decides what to keep, so
        its name alone does not say the model got anything from it."""
        kept: dict[str, int] = {}
        for h in self.hits:
            kept[h.source] = kept.get(h.source, 0) + 1
        searches = set(SEARCH_SOURCES)
        return ", ".join(
            f"{p} ({kept.get(p, 0)} hit{'' if kept.get(p, 0) == 1 else 's'} kept)"
            if p in searches else p
            for p in self.providers)


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

    Three quarters from the head and one from the tail, since an append-shaped
    file keeps its newest leads at the bottom. The middle is what goes, and the
    cut is marked so the scout does not read the excerpt as one continuous
    document.
    """
    if len(text) <= limit:
        return text
    head = int(limit * 0.75)
    return f"{text[:head]}\n… {len(text) - limit} characters elided …\n{text[head - limit:]}"


def _slug(heading: str) -> str:
    """A Markdown heading the way GitHub anchors it: lowercase, punctuation
    dropped, spaces as hyphens."""
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", heading.lower()).strip())


def _section_bounds(text: str, url: str) -> tuple[int, int] | None:
    """Where the section a feed's fragment names begins and ends: the whole file
    for a feed without a fragment, None for one whose start heading the file no
    longer carries (`_read_feed` then reads the whole file and says so).

    A fragment is how a feed says which section is the list when both ends of a
    long file are prose; the fetch drops it and `_source_key` ignores it. A
    heading is matched as a prefix of its GitHub anchor, so a date the project
    appends to the title does not break the match. `#from:until` also names
    where the list ends: the first heading after the start whose anchor begins
    with `until` (an anchor carries no colon, so the pair cannot be read as one
    heading). An end the file no longer carries reads on to the end of the file,
    which the elision warning then measures."""
    fragment = urlparse(url).fragment.lower()
    if not fragment:
        return 0, len(text)
    begin, _, until = fragment.partition(":")
    headings = [(m.start(), _slug(m.group(1)))
                for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, re.M)]
    start = next((pos for pos, slug in headings if slug.startswith(begin)), None)
    if start is None:
        return None
    end = next((pos for pos, slug in headings
                if until and pos > start and slug.startswith(until)), len(text))
    return start, end


def _feed_name(url: str) -> str:
    """A feed as a warning names it: owner/repo/path on GitHub, host/path elsewhere."""
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    if parsed.netloc == "raw.githubusercontent.com" and len(parts) > 3:
        return "/".join(parts[:2] + parts[3:])
    return parsed.netloc + parsed.path


def _read_feed(client: httpx.Client, feed: str, env: Mapping[str, str]) -> tuple[str | None, list[str]]:
    """The excerpt of one curated feed the scout reads, and what is wrong with it:
    a feed that could not be read, a start heading gone, more than
    FEED_ELIDED_WARN of its section elided, or an archived repository. None of
    these fails the run; each is a line in the log saying what to do about it."""
    name = _feed_name(feed)
    try:
        r = client.get(feed)
        r.raise_for_status()
    except httpx.HTTPError as exc:
        failure = (f"HTTP {exc.response.status_code}" if isinstance(exc, httpx.HTTPStatusError)
                   else type(exc).__name__)
        return None, [f"{name}: not read — {failure}"]
    warnings = []
    bounds = _section_bounds(r.text, feed)
    if bounds is None:
        begin = urlparse(feed).fragment.partition(":")[0]
        warnings.append(f"{name}: no heading matches #{begin} any more, "
                        "so the whole file was read")
    section = r.text if bounds is None else r.text[bounds[0]:bounds[1]]
    elided = len(section) - FEED_TEXT_LIMIT
    if elided > FEED_ELIDED_WARN * len(section):
        warnings.append(f"{name}: {elided:,} of its {len(section):,} characters "
                        f"({100 * elided // len(section)}%) never reach the scout — point the "
                        "feed at the part that is the list")
    archived = _archived_repo(client, feed, env)
    if archived:
        warnings.append(archived)
    return _feed_excerpt(section, FEED_TEXT_LIMIT), warnings


def _archived_repo(client: httpx.Client, feed: str, env: Mapping[str, str]) -> str | None:
    """A warning if a GitHub feed's repository is archived. Best effort: an API
    that does not answer is not the feed's fault and says nothing."""
    parsed = urlparse(feed)
    parts = [p for p in parsed.path.split("/") if p]
    if parsed.netloc != "raw.githubusercontent.com" or len(parts) < 2:
        return None
    repo = f"{parts[0]}/{parts[1]}"
    headers = {"Accept": "application/vnd.github+json"}
    if env.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {env['GITHUB_TOKEN']}"
    try:
        r = client.get(f"https://api.github.com/repos/{repo}", headers=headers)
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, ValueError):
        return None
    if not isinstance(data, dict) or not data.get("archived"):
        return None
    pushed = str(data.get("pushed_at") or "")[:10] or "on an unknown date"
    return (f"{repo}: archived on GitHub, last pushed {pushed} — its list no longer "
            "changes; put it down in sources.yaml")


def _timeout_within(left: float | None) -> httpx.Timeout:
    """No single request may outlive the budget it is spending. The cap only ever
    shrinks the module's own timeouts, so a wide budget changes nothing."""
    if left is None:
        return TIMEOUT
    return httpx.Timeout(min(TIMEOUT.read, left), connect=min(TIMEOUT.connect, left))


# What a reader never sees and a model should not be fed: the site's menus and
# footer, stylesheets, the JavaScript-required notice, and scripts — except
# JSON-LD, which is page content in a structured coat (Freebuff publishes its
# FAQ there and nowhere else). Left in, they spend PAGE_TEXT_LIMIT before the
# body text, and a sidebar word can trip the retirement sweep.
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
    one, the loop stops rather than starting a fetch it cannot afford, and each
    fetch's timeout is capped by what is left. A URL left unfetched is absent
    from the result — callers read it with `.get(url, "")` — since an empty
    string would claim the page was read.
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
                # A catalog answers JSON, which the tag stripper would eat from
                # the first "<" in a model's description on.
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

    Not a feed: the whole catalog is megabytes of prices and cannot go in a
    prompt. What survives is the one question this project asks — which vendor
    publishes a row at zero — as a line per provider with the endpoint to
    probe, most zero-cost rows first, capped at `max_providers`. A zero is a
    lead and never evidence, which MODELS_DEV_CAVEAT says to the model.
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
        if not host or host in LOCAL_HOSTS or host in CODE_HOSTS:
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


# The names _searchers gives its sources, which are also every Hit.source.
SEARCH_SOURCES = ("tavily", "hn", "github")


def _searchers(client: httpx.Client, env: Mapping[str, str]) -> list[tuple[str, Callable[[str], list[Hit]]]]:
    searchers: list[tuple[str, Callable[[str], list[Hit]]]] = []
    if env.get("TAVILY_API_KEY"):
        searchers.append(("tavily", lambda q: tavily_search(client, env["TAVILY_API_KEY"], q)))
    searchers.append(("hn", lambda q: hn_search(client, q)))
    searchers.append(("github", lambda q: github_search(client, q, env.get("GITHUB_TOKEN"))))
    return searchers


def gather_evidence(queries: list[str], known_domains: set[str], env: Mapping[str, str],
                    http: httpx.Client | None = None, max_pages: int = 10,
                    time_left: Callable[[], float] | None = None,
                    answered_domains: set[str] | frozenset[str] = frozenset()) -> Evidence:
    """Run every available source over the queries and assemble deduplicated evidence.

    `known_domains` is the registry's: a hit or a digest line about a listed
    vendor is noise. `answered_domains` is the watchlist's current verdicts and
    the blocklist, and they leave only the models.dev digest — a zero there is a
    lead, and these are leads a human already followed to a written answer.
    Search hits about the same vendors stay in, because a `reopen_if` waits on
    exactly that kind of fresh evidence.

    `time_left` returns the seconds this phase may still spend (see
    `scout.Deadline.share`). Running out is not an error: what has been gathered
    is returned and the scout reasons over that. The clock is read between
    calls, so the phase can overrun by at most the one request already in flight.
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
            if h.url in seen or d in NOISE_DOMAINS or is_covered(h.url, known_domains):
                continue
            seen.add(h.url)
            kept.append(h)
        ev.hits = kept

        ev.pages = fetch_page_texts([h.url for h in kept[:max_pages]], client,
                                    time_left=time_left)

        for feed in CURATED_FEEDS:
            if spent():
                break
            excerpt, warnings = _read_feed(client, feed, env)
            ev.feed_warnings.extend(warnings)
            if excerpt is not None:
                ev.feeds[feed] = excerpt
        if ev.feeds:
            ev.providers.append("curated-feeds")

        if not spent():
            digest = models_dev_digest(client, known_domains | set(answered_domains))
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
