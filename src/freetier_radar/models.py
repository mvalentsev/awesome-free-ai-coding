from __future__ import annotations

import re
from datetime import date
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

import yaml
from pydantic import BaseModel, model_validator

# Words every vendor keeps on the page long after the offer is gone. A probe
# built out of these alone verifies that the page loads, nothing more.
GENERIC_KEYWORDS = frozenset({
    "free", "free tier", "free plan", "free trial", "free credits", "credits",
    "api", "pricing", "price", "limits", "rate limits", "no credit card",
    "no credit card required", "sign up", "get started",
})

# The same words on their own. A phrase is only as specific as the words it is
# built from: "sign up for free and get started" is six words long and says
# exactly as little as "free". Used to judge phrases the frozen set above cannot
# enumerate — vendors word the same nothing in endless ways.
GENERIC_WORDS = frozenset({
    "a", "access", "an", "and", "any", "api", "apis", "are", "available", "card",
    "credit", "credits", "for", "free", "get", "getting", "in", "is", "it", "limit",
    "limits", "need", "needed", "no", "not", "now", "of", "on", "or", "our", "plan",
    "plans", "price", "prices", "pricing", "rate", "required", "sign", "signup",
    "start", "started", "the", "tier", "tiers", "to", "today", "trial", "trials",
    "up", "us", "usage", "use", "using", "with", "without", "you", "your",
})

# A phrase this long, carrying at least one word of its own, is a quote from the
# offer rather than a description of it: "light quota to code with agents" is
# reworded the day the plan changes. Four is where the vendor-neutral filler
# ("no credit card required") stops and the vendor's own sentence begins.
ANCHOR_PHRASE_WORDS = 4

# A model id, a JSON field, a path: kilo's `advanced_model_request_limit`,
# Mistral's `mistral-medium`, Trae's `"name":"free"`. Quotes count as boundary
# characters — a JSON key is exactly as anchoring as the id it holds.
_ID_LIKE = re.compile(r'[\w"][-_/:.][\w"]')


def normalize_keyword(keyword: str) -> str:
    """Punctuation-free lowercase form, so `Free-Tier`, `"free tier"` and
    `free tier.` all read as the same generic phrase."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]+", " ", keyword.lower())).strip()


def is_anchor(keyword: str) -> bool:
    """Does this keyword die together with the free offer?

    Three ways it can, checked after the generic phrases are ruled out so that
    dressing one up ("free-tier", `"free"`) does not sneak it past:

    - a number — a quota, a price, a version: `$0.10, subject to change`,
      `anonymous users get one request every 15 seconds`;
    - an id-shaped token — a model id or a JSON field the vendor's own API uses;
    - a phrase of ANCHOR_PHRASE_WORDS or more with at least one word that is not
      pricing-page filler.

    What this rejects is what a page keeps for months after the tier is
    withdrawn: `hobby`, `free quota`, `monthly credits`, `no signup`.
    """
    normalized = normalize_keyword(keyword)
    if not normalized or normalized in GENERIC_KEYWORDS:
        return False
    if any(ch.isdigit() for ch in keyword):
        return True
    if _ID_LIKE.search(keyword):
        return True
    words = normalized.split()
    return (len(words) >= ANCHOR_PHRASE_WORDS
            and any(w not in GENERIC_WORDS for w in words))

# How a vendor words a withdrawal. Missing keywords catch an offer that quietly
# vanished from the page; these catch the opposite case — the page still lists
# the free tier and announces, a paragraph below, that it is over. Every phrase
# names the free offer itself, so a page retiring some unrelated product does
# not fail a live entry.
DEAD_MARKERS = (
    "no longer free",
    "no longer available for free",
    "free tier has ended",
    "free trial has ended",
    "free plan has ended",
    "free access has ended",
    "free api service has ended",
    "free tier has been discontinued",
    "free plan has been discontinued",
    "free tier is being discontinued",
    "discontinuing the free",
    "discontinued the free",
    "sunsetting the free",
    "we are retiring the free",
    "end of the free tier",
)

# A bot wall answering HTTP 200. Cloudflare, Vercel's Security Checkpoint and
# their kin serve a challenge page in place of the vendor's own; it carries none
# of the probe keywords, so without this the check reads as "the free offer is
# gone" and three runs later archives a service that never stopped working.
# cto.new taught the mirror image — a probe that passes on the runner and
# nowhere else — so a challenge is not a pass either: it is not an answer at all,
# which is what INCONCLUSIVE is for.
CHALLENGE_MARKERS = (
    "enable javascript to continue",
    "enable javascript and cookies to continue",
    "please enable javascript to view",
    "please turn javascript on",
    "vercel security checkpoint",
    "checking your browser",
    "verifying you are human",
    "verify you are human",
    "just a moment...</title>",
    "cf-browser-verification",
    "cf_chl_opt",
    "__cf_chl",
    "ddos protection by cloudflare",
    "attention required! | cloudflare",
)


class Category(str, Enum):
    AGENT_CLI = "agent-cli"
    API_FREE_TIER = "api-free-tier"
    TRIAL = "trial"
    AGGREGATOR = "aggregator"


class Tier(str, Enum):
    FRONTIER = "frontier"
    STRONG = "strong"


class ProbeType(str, Enum):
    API_MODELS = "api-models"
    PAGE_KEYWORDS = "page-keywords"


class ModelFamily(BaseModel):
    family: str
    tier: Tier = Tier.STRONG
    released: str = ""
    superseded_by: str | None = None


class Probe(BaseModel):
    type: ProbeType
    endpoint: str
    keywords: list[str] = []
    free_marker: str = ""
    dead_markers: list[str] = []  # entry-specific withdrawal wording, on top of DEAD_MARKERS
    require_zero_price: bool = False  # api-models: the matched id must still be priced 0

    @model_validator(mode="after")
    def _zero_price_needs_a_price_list(self) -> Probe:
        """Only a models API publishes prices. Set on a page-keywords probe the
        flag would silently do nothing, which is the worst outcome for a check
        whose whole job is to notice a free model quietly acquiring a price."""
        if self.require_zero_price and self.type is not ProbeType.API_MODELS:
            raise ValueError(
                f"probe {self.endpoint}: require_zero_price needs an api-models probe"
            )
        return self

    @model_validator(mode="after")
    def _keywords_must_anchor(self) -> Probe:
        """A page-keywords probe needs at least one keyword that dies with the
        offer — the free model's id, its quota figure, or the vendor's own
        sentence about it. Generic words alone keep passing for months after a
        free tier is withdrawn.

        The first version of this rule only rejected keywords listed verbatim in
        GENERIC_KEYWORDS, which let `hobby`, `free quota`, `no signup` and
        `monthly credits` through — words that sit on a pricing page whatever
        the page is currently offering. is_anchor() asks the question the list
        cannot: would this string still be there once the free tier is gone?
        """
        if self.type is ProbeType.PAGE_KEYWORDS:
            if not any(is_anchor(k) for k in self.keywords):
                raise ValueError(
                    f"probe {self.endpoint}: none of the keywords {self.keywords} anchors on "
                    "the offer — use a free model id, a quota or price figure, or a phrase "
                    "of four or more words quoted from the page"
                )
        return self


class ApiInfo(BaseModel):
    """Connection details a developer pastes into an agent/SDK config."""
    base_url: str | None = None
    key_url: str | None = None
    auth: str = "api-key"  # "api-key" | "none"
    openai_compatible: bool = True
    model_ids: list[str] = []  # exact callable ids for generated configs
    note: str = ""


class Entry(BaseModel):
    id: str
    name: str
    category: Category
    url: str
    source_urls: list[str] = []
    card_required: bool = False
    offering: str
    limits: str = ""
    models: list[ModelFamily] = []
    api: ApiInfo | None = None
    probe: Probe
    first_seen: date
    last_verified: date
    retired_on: date | None = None  # vendor-announced shutdown; archives the row on that day
    probe_failures: int = 0
    provisional: bool = False
    rank: int = 100  # sort key within a category: lower renders higher


def live_families(entry: Entry) -> list[str]:
    """The model families this entry actually publishes.

    Superseded ones are a note to a reviewer — "bump this row to the generation
    the free tier serves" — and the README hides them. Anything that reports on
    what the list says must hide them too, or it announces a change no reader
    can see.
    """
    return [m.family for m in entry.models if m.superseded_by is None]


def domain_of(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def known_domains(entries: list[Entry]) -> set[str]:
    """Every host the registry already reaches an entry at.

    All three matter, which is what makes this a function rather than a set
    comprehension at the call site: NVIDIA is listed at build.nvidia.com,
    documented at docs.api.nvidia.com and served at integrate.api.nvidia.com,
    and a set built from the url alone reported our own entry back to us as an
    undiscovered provider.
    """
    domains = {domain_of(e.url) for e in entries}
    domains |= {domain_of(u) for e in entries for u in e.source_urls}
    domains |= {domain_of(e.api.base_url) for e in entries if e.api and e.api.base_url}
    return {d for d in domains if d}


ARCHIVE_AFTER_DAYS = 60


def is_archived(entry: Entry, today: date) -> bool:
    """Liveness comes from probes, staleness and vendor-announced retirement —
    never from model generations. A provider whose catalog moves on is still
    free, so a superseded family means "bump the row", not "bury the entry".

    Lives with the model rather than with the renderer because it answers a
    question about the entry, not about the README: the scout needs it too, to
    keep from proposing work on entries the registry has already buried.
    """
    if entry.retired_on and today >= entry.retired_on:
        return True
    if entry.probe_failures >= 3:
        return True
    if (today - entry.last_verified).days > ARCHIVE_AFTER_DAYS:
        return True
    return False


# ---- the files this repository curates by hand ----------------------------
# All four loaders live here rather than in scout.py, where the first three
# grew: they are read by the scout, by the renderer and by freetier-check, and
# a validator that had to import the scout would drag an LLM client and an HTTP
# stack in behind it. A missing file always means "empty", never an error — each
# of these is optional to a caller that has no opinion about it.

def load_blocklist(path: Path) -> dict[str, str]:
    """domain -> reason; missing file means an empty blocklist."""
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return {str(d["domain"]).lower(): str(d.get("reason", ""))
            for d in data if isinstance(d, dict) and d.get("domain")}


def is_blocked(domain: str, blocklist: dict[str, str]) -> bool:
    return any(domain == b or domain.endswith("." + b) for b in blocklist)


def load_dismissed(path: Path) -> set[tuple[str, str, str]]:
    """(entry id, family, newer family) triples a human has already rejected.

    Since supersede became proposal-only the registry never records a decision
    about a bump, so every run re-proposes the ones a reviewer threw out — z.a
    i's free glm-4.7-flash "superseded by" the paid glm-5.2 came back in each PR.
    This file is that memory: the proposal is a suggestion, and a suggestion
    declined stays declined until a human removes the line.
    """
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = data.get("dismissed") if isinstance(data, dict) else data
    return {
        (str(d["entry"]), str(d["family"]), str(d["superseded_by"]))
        for d in (items or [])
        if isinstance(d, dict) and d.get("entry") and d.get("family") and d.get("superseded_by")
    }


class Watched(BaseModel):
    """A service that belongs on neither list yet: legitimate, but with no free
    tier a developer can reach today.

    The registry had two states and needed three. `blocklist.yaml` is a verdict
    on the *service* — BYOK-only, pooled piracy, hostile to agents — and it is
    meant to be permanent, so putting a legitimate vendor there buries it on the
    day it opens a free lane. Leaving it in neither file is what actually
    happened to tokenrouter.io and LLM7: nothing recorded the decision, so the
    scout re-proposed them and a reviewer re-derived the same "no" from scratch.

    This is a verdict on the *offer, on a date*. `checked_on` is what makes it
    different from a quiet blocklist — it expires. `reopen_if` names the evidence
    that would change the answer, so the next look starts from the last one
    instead of from zero.
    """
    # A list, unlike blocklist.yaml's single domain, because a watched service is
    # routinely reachable under more than one of them and a proposal may arrive
    # under either: ModelScope answers on both .cn and .ai, and suppressing one
    # spelling while the other sails through is the same as not suppressing.
    domains: list[str]
    name: str
    checked_on: date
    reason: str
    reopen_if: str = ""

    @model_validator(mode="after")
    def _needs_a_domain(self) -> Watched:
        if not self.domains:
            raise ValueError(f"watchlist entry {self.name}: needs at least one domain")
        return self


# How long a "no free tier today" verdict is worth trusting. Long enough that a
# lead does not churn through every twice-weekly run, short enough that a tier
# opened in the meantime is noticed within a quarter. Past this the entry stops
# suppressing proposals and is reported as due for a re-check instead.
WATCH_RECHECK_DAYS = 90


def load_watchlist(path: Path) -> list[Watched]:
    """Missing file means an empty watchlist — the file is optional the way
    blocklist.yaml is."""
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = data.get("watched") if isinstance(data, dict) else data
    return [Watched.model_validate(w) for w in (items or [])]


def is_watch_current(watched: Watched, today: date) -> bool:
    """Is this verdict still young enough to answer for the service?"""
    return (today - watched.checked_on).days <= WATCH_RECHECK_DAYS


def watch_match(domain: str, watchlist: list[Watched], today: date) -> Watched | None:
    """The current verdict covering this domain, if there is one.

    Suffix-matched like the blocklist, so `siliconflow.com` also covers
    `api.siliconflow.com`. An expired verdict deliberately matches nothing: that
    is the whole difference between watching a service and burying it.
    """
    for w in watchlist:
        if not is_watch_current(w, today):
            continue
        for raw in w.domains:
            d = raw.lower()
            if domain == d or domain.endswith("." + d):
                return w
    return None


def load_registry(path: Path) -> list[Entry]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [Entry.model_validate(e) for e in data["entries"]]


def save_registry(path: Path, entries: list[Entry]) -> None:
    payload = {"entries": [e.model_dump(mode="json", exclude_none=True) for e in entries]}
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
