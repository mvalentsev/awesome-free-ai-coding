from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

import yaml
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

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


class FreePart(str, Enum):
    """What the free part of an offer is, which decides what its Models column
    may name (CONTRIBUTING, "A sum to spend names no model")."""
    # The vendor names models its free part serves in their own right: a free
    # lane, a zero price, a free quota per model, a free tier or trial that names
    # them — or caps it counts the same on every model it serves, which limit a
    # free tier rather than spend a sum. The column names them.
    MODELS = "models"
    # An amount the account spends across the catalog: a signup credit, a grant
    # of tokens every model draws on, an allowance at each model's own price. No
    # model is free by itself, so the column names none.
    SUM = "sum"
    # The vendor does not say which models the free part reaches — Copilot Free's
    # "auto model selection only". A family would be a claim it never makes.
    UNNAMED = "unnamed"


class Tier(str, Enum):
    FRONTIER = "frontier"
    STRONG = "strong"


class ProbeType(str, Enum):
    API_MODELS = "api-models"
    PAGE_KEYWORDS = "page-keywords"


def _squash(s: str) -> str:
    """Case and separators removed: vendors write "Qwen3 Coder" and "GLM-4.7
    Flash" for what the registry calls qwen3-coder and glm-4.7-flash."""
    return re.sub(r"[\s_-]+", "", s.lower())


def _id_squash(s: str) -> str:
    """_squash for a catalog id, where the dot goes too: Kenari lists the
    registry's glm-4.7-flash, step-3.7-flash and laguna-s-2.1 as
    glm-4-7-flash:free, step-3-7-flash:free and laguna-s-2-1:free. A page is
    prose and keeps its dots — "Qwen 3 6B" must not read as qwen3.6 — but an
    id is one token, and a version written with a hyphen is the same
    version."""
    return re.sub(r"[\s_.\-]+", "", s.lower())


def family_names(family: str, model_id: str) -> bool:
    """Whether a catalog id is one of a family's, the one way every part of the
    project decides it: the probe demanding a family back from a catalog, the
    render reading an id's tier, freetier-check and freetier-bars asking which
    ids a row's column already names. A substring of the squashed id, so
    `glm-5.3` also names a `glm-5.3-flash` id — give a family the most
    specific name the lane serves."""
    return _id_squash(family) in _id_squash(model_id)


def id_family(families: Iterable[str], model_id: str) -> str | None:
    """The family an id is, among a row's families: the most specific one that
    names it. A family names every id it is a substring of, so where a row
    carries glm-5 beside glm-5.2, coding-glm-5.2-free names both — and until
    2026-09-26 the glm-5 page offered it as a glm-5 id, and a catalog could go
    on vouching for glm-5 with it after glm-5's own id had left. Whose id it is
    — on a model page, for a tier, for the probe — is decided here."""
    named = [f for f in families if family_names(f, model_id)]
    return max(named, key=lambda f: len(_id_squash(f)), default=None)


class ModelFamily(BaseModel):
    family: str
    # A measurement, never a reputation (CONTRIBUTING, "tier: frontier is a
    # measurement"): how close the model this lane serves scores to the top of
    # the Artificial Analysis Intelligence Index, read by `freetier-tiers`. No
    # tier means not measured, or measured below the strong bar. Until
    # 2026-09-17 every family defaulted to `strong`, so Apertus 70B at 5 points
    # and GLM 5.3 Flash at 42 carried the same word.
    tier: Tier | None = None
    superseded_by: str | None = None
    # The Artificial Analysis model the tier was read from: the slug of its page
    # on artificialanalysis.ai/models/, for the variant the lane actually serves.
    aa_model: str | None = None

    @field_validator("family", "superseded_by", mode="before")
    @classmethod
    def _family_is_spelled_one_way(cls, value):
        """A family is matched against catalog ids with case and spacing
        ignored (`family_names`), so "GLM-5.4 Flash" and glm-5.4-flash are one
        family — and one page. It is kept in the registry's one spelling, lower
        case with a hyphen for a space, so a vendor's capitals in a proposal
        make a family rather than a refusal."""
        if isinstance(value, str):
            return re.sub(r"\s+", "-", value.strip().lower())
        return value

    @field_validator("family")
    @classmethod
    def _family_is_a_page_name(cls, value: str) -> str:
        """A family names a page of its own on the site (models/<family>/) and
        the file it is written to, so it is refused here, where the registry is
        read, rather than by the render halfway through a scheduled run."""
        if not re.fullmatch(r"[a-z0-9][a-z0-9.\-]*", value):
            raise ValueError(f"family {value!r} is not a page name — lower case, digits, dots "
                             "and hyphens, the way the registry spells every family")
        if value == "index":
            raise ValueError("family 'index' is not a page name — models/index.md is the index "
                             "of every model")
        return value

    @field_validator("aa_model")
    @classmethod
    def _aa_model_is_a_slug(cls, value: str | None) -> str | None:
        if value is not None and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", value):
            raise ValueError(f"aa_model {value!r} is not an Artificial Analysis model slug — "
                             "the last part of its artificialanalysis.ai/models/ URL")
        return value


class Follow(BaseModel):
    """Where in a JSON index the page a probe reads is named today.

    ModelScope serves its docs under a dated release path —
    …/docdata/2026-9-10_15-4-CN/… — that the site replaces with each release,
    while the old paths go on answering: a keyword read at a pinned path keeps
    matching after the offer changed. The site names the current prefix in a
    JSON index (`Data.TargetPrefix` of main_doc_CN_prod), so the probe starts
    there and reads the page the index names."""
    field: str  # dotted path to the value in the index's JSON
    suffix: str = ""  # appended to that value

    @field_validator("field")
    @classmethod
    def _field_is_a_dotted_path(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z_][\w-]*(\.[A-Za-z_][\w-]*)*", value):
            raise ValueError(f"follow.field {value!r} is not a dotted path such as Data.TargetPrefix")
        return value

    @field_validator("suffix")
    @classmethod
    def _suffix_is_a_path(cls, value: str) -> str:
        if value and not value.startswith("/"):
            raise ValueError(f"follow.suffix {value!r} is joined to a URL, so it starts with /")
        return value


class Probe(BaseModel):
    type: ProbeType
    endpoint: str
    keywords: list[str] = []
    free_marker: str = ""
    dead_markers: list[str] = []  # entry-specific withdrawal wording, on top of DEAD_MARKERS
    # api-models: the matched id must still be free by the catalog's own account —
    # its free flag where it has one, else every price it publishes at zero
    require_zero_price: bool = False
    # page-keywords: a keyless JSON catalog to check api.model_ids against, for a
    # vendor that keeps its offer on one page and its ids at another url
    catalog: str | None = None
    # page-keywords: keywords the vendor serves only inside the page's machinery
    # — a framework state blob, an OpenAPI enum, an i18n bundle. `keywords` is
    # read against what the page renders, because an id left behind in a script
    # tag outlives the offer it was anchoring (Groq, 2026-09-08). Where the data
    # blob IS the evidence, say so here and the whole response is searched.
    machinery_keywords: list[str] = []
    # api-models: the key a vendor lists its free lane under, for a document
    # that publishes lanes side by side instead of flagging rows. Cline's
    # recommended-models answers `recommended`, `free`, `clinePass` and
    # `clineCloud` with no price anywhere, and one model can sit in two of them
    # — DeepSeek V4 Flash was in the free lane and in the $9.99 plan on
    # 2026-09-14 — so the lane is named rather than every array read. Unset,
    # the rows are the document itself or its `data`, as in an OpenAI catalog.
    lane: str | None = None
    # api-models: a keyless document in which the vendor marks which of the
    # catalog's models are free, for a catalog that publishes no price. NVIDIA's
    # /v1/models answered 82 ids on 2026-09-23 with nothing but the id and its
    # owner, while build.nvidia.com marked 39 endpoints "Free Endpoint", and
    # NGC's catalog search returns those marks for all of them in one call. The
    # probe joins the list onto the catalog and reads it as it reads a price
    # (see prober.join_free_list), so it takes require_zero_price with it.
    free_list: str | None = None
    # page-keywords: the endpoint is a JSON index that names the page to read,
    # for a vendor whose docs move to a new dated path each release (see Follow)
    follow: Follow | None = None

    @model_validator(mode="after")
    def _follow_reads_a_page(self) -> Probe:
        if self.follow is not None and self.type is not ProbeType.PAGE_KEYWORDS:
            raise ValueError(
                f"probe {self.endpoint}: follow names a page to read for keywords, so it "
                "belongs on a page-keywords probe")
        return self

    @model_validator(mode="after")
    def _lane_needs_a_catalog(self) -> Probe:
        """A lane is a key of the JSON document an api-models probe parses. A
        page-keywords probe reads the response as text, so the field would sit
        there changing nothing — which lane a model is in is exactly the
        question a substring cannot answer."""
        if self.lane is not None and self.type is not ProbeType.API_MODELS:
            raise ValueError(
                f"probe {self.endpoint}: lane is an api-models field — a page-keywords "
                "probe reads text, not the arrays of a JSON document")
        return self

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
    def _free_list_answers_the_price_question(self) -> Probe:
        """The list is read only where an api-models probe asks whether a row is
        free, which is what require_zero_price turns on: anywhere else it would
        be fetched, or not, and change nothing either way."""
        if self.free_list is None:
            return self
        if self.type is not ProbeType.API_MODELS or not self.require_zero_price:
            raise ValueError(
                f"probe {self.endpoint}: free_list stands in for the prices a catalog does "
                "not publish, so it needs an api-models probe with require_zero_price: true")
        if not self.free_list.startswith("https://"):
            raise ValueError(f"probe {self.endpoint}: free_list must be an https URL")
        return self

    @model_validator(mode="after")
    def _machinery_belongs_to_a_page(self) -> Probe:
        if self.type is not ProbeType.PAGE_KEYWORDS and self.machinery_keywords:
            raise ValueError(
                f"probe {self.endpoint}: machinery_keywords is a page-keywords field — "
                "a models API has no machinery to tell apart from its answer"
            )
        return self


# How long an `api.notice` holds a refused keyless lane off the failure count.
# Three FAILs archive a row in about ten days; a maintainer who has chosen to wait
# for a vendor's word needs longer than that, and a vendor that has said nothing
# for a month about breaking every other client has answered by its silence.
NOTICE_HOLD_DAYS = 30


class Notice(BaseModel):
    """The list owning up, in its own voice, to a lane that does not work as
    published while it waits for the vendor to say why.

    opencode Zen began refusing every client but OpenCode itself on 2026-09-17
    with `403 FreeTierError`, and OpenCode said nothing: no docs change, no
    answer on the issues. The row could not honestly go on printing its curl as
    the page's first command without a word, and removing a lane on a change the
    vendor may yet walk back was a call the maintainer chose to wait on. This is
    that word — dated, because it must be able to go stale, and linked to where
    the problem is followed."""
    since: date
    text: str
    url: str | None = None

    @field_validator("text")
    @classmethod
    def _text_says_something(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("notice text is empty — say what a reader will run into")
        return value.strip()

    @field_validator("url")
    @classmethod
    def _url_is_https(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith("https://"):
            raise ValueError("notice url must be an https URL — a reader clicks it from the README")
        return value


def notice_holds(notice: Notice | None, today: date) -> bool:
    """Whether a notice still holds a refused lane's row off the failure count."""
    return notice is not None and (today - notice.since).days <= NOTICE_HOLD_DAYS


class FreeSince(BaseModel):
    """A record older than this registry's own first read that shows an id
    free: a Wayback snapshot of the vendor's free list, the vendor's own
    snapshot of its lane. freetier-bars counts the two-week bar from the
    earliest day it knows, and until 2026-09-25 it knew only the registry's
    history and NVIDIA's free list, so the bars such a record set lived in a
    maintainer's notes — Cline's DeepSeek V4.1 Flash in its lane since 09-14,
    Alibaba's since 09-14 by Wayback, both dated 10-09 by the report."""
    id: str
    on: date
    source: str  # the record itself, one a reader can open

    @field_validator("source")
    @classmethod
    def _source_is_a_page(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError(f"free_since source {value!r} is not an https URL — name the record "
                             "that shows the id free: a Wayback snapshot, the vendor's own snapshot")
        return value


def _dated_ids_are_listed(field: str, model_ids: list[str], free_since: list[FreeSince]) -> None:
    unlisted = [s.id for s in free_since if s.id not in model_ids]
    if unlisted:
        raise ValueError(f"{field}.free_since dates {', '.join(unlisted)}, which {field}.model_ids "
                         "does not list — a date for an id the lane does not carry dates nothing")


# How a lane lets a client in: no key at all, the key the vendor prints for
# anyone, or the reader's own — `ApiInfo.key_kind`, the one place that decides.
KEY_KINDS = ("none", "public", "own")
# What a lane can ask every request to carry besides its key — `ApiInfo.asks`.
# Each page and config that says how to connect keys its words by these names,
# and the render's tests refuse a table without one, so a new ask cannot reach
# some pages and not others.
ASKS = ("user-agent", "session-header")


class ApiInfo(BaseModel):
    """Connection details a developer pastes into an agent/SDK config."""
    base_url: str | None = None
    key_url: str | None = None
    auth: str = "api-key"  # "api-key" | "none"
    openai_compatible: bool = True
    model_ids: list[str] = []  # exact callable ids for generated configs
    # Zero-priced ids the catalog carries that are deliberately not in
    # model_ids — an image generator, a row whose own description says it was
    # removed, a lane the row does not track — with the reason in `note`. The probe reports every
    # free id it finds outside model_ids, and this is where a decision about
    # one of them is recorded so it is not reported again. Written only where
    # set: every api block already carries model_ids and note, and this list
    # means something only on the rows whose catalog prices are read.
    ignored_ids: list[str] = Field(default_factory=list, exclude_if=lambda ids: not ids)
    # Ids in model_ids that no Models-column family will name, on purpose: a
    # router, a stealth codename, a model its own developer advises against
    # agentic coding — with the reason in `note`. Every other id a free lane
    # has carried for two weeks is owed a family, and freetier-bars says so;
    # this is where a decision not to give one is recorded.
    no_family_ids: list[str] = Field(default_factory=list, exclude_if=lambda ids: not ids)
    # Ids in model_ids that an older record than this registry shows free, with
    # the day and the record, so freetier-bars counts their bar from there.
    free_since: list[FreeSince] = Field(default_factory=list, exclude_if=lambda v: not v)
    # The base of the vendor's Anthropic-format Messages API — the value Claude
    # Code's ANTHROPIC_BASE_URL takes, the client appending /v1/messages itself.
    # Set only where the vendor documents the route, never from a 401 alone:
    # a gateway's auth wall answers 401 on any path. The probe then POSTs to it
    # keyless on every run, and a 404 is reported beside a dead model id — the
    # same kind of fact, a connection detail this list publishes and the world
    # stopped backing.
    anthropic_base_url: str | None = None
    # The header in which the vendor wants a stable id for each conversation.
    # opencode Zen has answered a free id without x-opencode-session with 400
    # MissingSessionID since 2026-09-07, and the rule OpenCode's team gives
    # other clients is "any stable UUID per conversation". A LiteLLM entry is
    # written once and cannot mint one, and OpenCode sends such a header only
    # for its own built-in provider, so a row that sets this stays out of
    # litellm.yaml and opencode.json; every place that tells a reader how to
    # connect names the header, and the keyless probe and the README's
    # quickstart curl send a fresh id.
    session_header: str | None = None
    # The vendor asks every client to name itself in the User-Agent. OpenCode's
    # client rules read "Identify itself with its own user agent, such as
    # my-coding-agent/1.0, rather than a generic SDK or HTTP-library name" beside
    # the session id, and curl left to itself sends curl/8.x — so the README's
    # command names itself, and every place that tells a reader how to connect
    # says their client must too. Written only where set.
    client_user_agent: bool = Field(default=False, exclude_if=lambda v: not v)
    # A key the vendor itself prints for anyone to call its lane with — LLM
    # Tech's quickstart publishes "a shared free trial key" so that anyone can
    # "try before you talk to anyone". A reader needs no account, so the row
    # counts with the keyless ones wherever the list answers "no account at
    # all", the env example carries the key filled in, and every run calls the
    # lane with it the way it calls a keyless lane without one. It is the
    # vendor's key only as long as the vendor's own page prints it: `key_url`
    # names that page and the run reads it back. A key anyone else hands out —
    # leaked, pooled, passed around — is key sharing, which does not qualify.
    public_key: str | None = None
    # A keyless lane that refuses any call carrying an Authorization header
    # while it answers a bare one. LiteLLM sends a bearer token on every call —
    # `api_key: none` goes out as "Bearer none", an empty key is refused before
    # the call, and OVHcloud answers an empty header value with 400 — so a lane
    # that sets this is left out of litellm.yaml; opencode's
    # @ai-sdk/openai-compatible adds the header only when given a key, and keeps
    # the lane. Measured 2026-09-21: OVHcloud's anonymous lane and VLM Run's
    # answered "Bearer none" with 403, Kilo's with 401 "Your authentication token
    # is invalid". The keyless probe asks again every run and says when it
    # changes, both ways. Written only where set.
    refuses_bearer: bool = Field(default=False, exclude_if=lambda v: not v)
    note: str = ""
    # A lane that does not work as published right now, owned up to while the
    # list waits for the vendor (see Notice). Rendered under the README's
    # quickstart curl, in the connection table, on the provider page and in
    # llms.txt; on a keyless row it also holds a refusal off the failure count
    # for NOTICE_HOLD_DAYS, and the run asks for it to come down the day the
    # lane answers again.
    notice: Notice | None = None

    @property
    def key_kind(self) -> str:
        """How a client is let in, decided once for every page, config and probe
        that says it or acts on it — one of KEY_KINDS. A key the vendor prints
        for anyone rides on a keyed lane, so it is its own kind: no account,
        and still a key on every request."""
        if self.auth == "none":
            return "none"
        return "public" if self.public_key is not None else "own"

    def asks(self) -> list[tuple[str, str]]:
        """What the lane asks every request to carry besides its key, as (name,
        value) by the names in ASKS, in the order the pages list them."""
        out = []
        if self.client_user_agent:
            out.append(("user-agent", ""))
        if self.session_header:
            out.append(("session-header", self.session_header))
        return out

    @model_validator(mode="after")
    def _client_user_agent_needs_an_endpoint(self) -> ApiInfo:
        if self.client_user_agent and not self.base_url:
            raise ValueError("client_user_agent says how to call base_url, and there is no base_url")
        return self

    @model_validator(mode="after")
    def _public_key_is_the_vendor_s_for_a_keyed_lane(self) -> ApiInfo:
        """The key is sent as a bearer token on a lane that wants one; the page
        that prints it is what makes it the vendor's; and the run calls the lane
        with it on the first of model_ids."""
        if self.public_key is None:
            return self
        if not self.public_key or re.search(r"\s", self.public_key):
            raise ValueError("public_key is empty or holds whitespace — it is sent as a bearer token")
        if self.auth == "none":
            raise ValueError("public_key is the key a keyed lane is called with, and auth is none")
        if not self.base_url:
            raise ValueError("public_key says how to call base_url, and there is no base_url")
        if not self.key_url:
            raise ValueError("public_key needs key_url, the vendor's page that prints it")
        if not self.model_ids:
            raise ValueError("public_key is checked by a call on the first of model_ids, "
                             "and there is none")
        return self

    @model_validator(mode="after")
    def _refuses_bearer_is_a_keyless_lane_s(self) -> ApiInfo:
        if self.refuses_bearer and self.auth != "none":
            raise ValueError("refuses_bearer is said of a keyless lane, and auth is not none — "
                             "a keyed lane is always called with a bearer token")
        return self

    @model_validator(mode="after")
    def _notice_needs_an_endpoint(self) -> ApiInfo:
        if self.notice and not self.base_url:
            raise ValueError("notice speaks about calling base_url, and there is no base_url")
        return self

    @model_validator(mode="after")
    def _free_since_dates_listed_ids(self) -> ApiInfo:
        _dated_ids_are_listed("api", self.model_ids, self.free_since)
        return self

    @field_validator("session_header")
    @classmethod
    def _session_header_is_a_header_name(cls, value: str | None) -> str | None:
        if value is not None and not re.fullmatch(r"[A-Za-z0-9!#$%&'*+.^_`|~-]+", value):
            raise ValueError(f"session_header {value!r} is not an HTTP header name")
        return value

    @model_validator(mode="after")
    def _session_header_needs_an_endpoint(self) -> ApiInfo:
        if self.session_header and not self.base_url:
            raise ValueError("session_header says how to call base_url, and there is no base_url")
        return self

    @field_validator("anthropic_base_url")
    @classmethod
    def _anthropic_base_is_a_base(cls, value: str | None) -> str | None:
        """Claude Code appends /v1/messages; a value that already carries the
        route would be sent to /v1/messages/v1/messages, and a trailing slash
        would double the one the client adds."""
        if value is None:
            return value
        value = value.rstrip("/")
        if not value.startswith("https://"):
            raise ValueError("anthropic_base_url must be an https URL")
        if value.endswith("/messages"):
            raise ValueError(
                "anthropic_base_url is the base Claude Code appends /v1/messages to — "
                "drop the route from it")
        return value


class ClientLane(BaseModel):
    """The ids of a free lane served only inside the vendor's own client.

    Cline's free models are picked in Cline's own model picker — "Free model
    usage is not supported through the Cline API. Free models are only
    available in the Cline IDE Extension and CLI" — so the row has no endpoint
    to paste and no `api` block, and until 2026-09-25 nothing recorded which
    ids its lane carried. Nine ids came or went between 2026-09-10 and 09-25 by
    the vendor's own snapshots of the lane: no run said so, and freetier-bars
    could not date one of them. The ids are recorded here, held to the lane on
    every run in both directions as `api.model_ids` are held to a catalog, and
    dated from this list's history for the two-week bar. Nothing a reader
    pastes is written from them: there is nothing to connect to."""
    model_ids: list[str]
    # Ids the lane carries that no Models-column family will name, on purpose —
    # a stealth codename, a router — with the reason in `note`, as
    # `api.no_family_ids`. A lane no config is written from needs no second
    # list for ids left out of it: every id it carries is listed here.
    no_family_ids: list[str] = Field(default_factory=list, exclude_if=lambda ids: not ids)
    # As `api.free_since`: the vendor's own snapshots of its lane date an id
    # before this list's history does.
    free_since: list[FreeSince] = Field(default_factory=list, exclude_if=lambda v: not v)
    note: str = Field(default="", exclude_if=lambda v: not v)

    @field_validator("model_ids")
    @classmethod
    def _a_lane_records_ids(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("client_lane.model_ids is empty — a lane with no ids records nothing, "
                             "so drop the block")
        return value

    @model_validator(mode="after")
    def _free_since_dates_listed_ids(self) -> ClientLane:
        _dated_ids_are_listed("client_lane", self.model_ids, self.free_since)
        return self


@dataclass(frozen=True)
class LaneIds:
    """Where a row records the ids of its free lane, read the one way the probe,
    freetier-check and freetier-bars read it: `api` for a lane an API serves,
    `client_lane` for one served only inside the vendor's own client."""
    field: str
    model_ids: list[str]
    ignored_ids: list[str]
    no_family_ids: list[str]
    free_since: list[FreeSince]


def lane_ids(entry: Entry) -> LaneIds | None:
    if entry.api is not None:
        return LaneIds("api", entry.api.model_ids, entry.api.ignored_ids, entry.api.no_family_ids,
                       entry.api.free_since)
    if entry.client_lane is not None:
        return LaneIds("client_lane", entry.client_lane.model_ids, [],
                       entry.client_lane.no_family_ids, entry.client_lane.free_since)
    return None


class DataUse(BaseModel):
    """What the vendor says it does with what a reader sends on the free offer —
    prompts, code, conversations — in its own words, on a page anyone can open.

    A free tier's price is often paid in data, and the vendors say so where they
    split tiers: the Gemini API's free tier lists "Content used to improve our
    products" and its paid tier "Content not used to improve our products".
    `trains` is `yes` (it may train or improve models on it), `opt-out` (it does
    until the reader turns it off) or `no` (it says it does not). A row whose
    vendor says nothing either way carries none. The README marks yes and
    opt-out with one glyph beside the name; the row's page quotes the sentence,
    and the run reads `url` back for it.
    """
    trains: Literal["yes", "opt-out", "no"]
    quote: str  # verbatim; the page prints it inside quotation marks
    url: str

    @field_validator("quote")
    @classmethod
    def _quote_is_a_sentence(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("data_use.quote is empty — the vendor's own words go here")
        if '"' in value or "“" in value or "”" in value:
            raise ValueError("data_use.quote holds quotation marks — it is printed inside a pair "
                             "of its own")
        return value.strip()

    @field_validator("url")
    @classmethod
    def _url_is_https(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("data_use.url must be an https URL")
        return value


class Delisting(BaseModel):
    """A row a reviewer took off the list, kept in the registry as the record of
    what the list published.

    Before 2026-09-17 a row came off by being deleted: twelve of them — Cerebras,
    Novita, LongCat and Kenari among them — left nothing on the page but a
    "Delisted" line with a dash where the reason goes, while the Archive promised
    that a dead tier is never silently forgotten. A row now leaves through the
    Archive and nowhere else, with the day and the reason; `freetier-check`, the
    probe run and the render all refuse a registry that has lost a row.
    """
    on: date
    reason: str  # what the Archive prints beside the row; the long account is the verdict's

    @field_validator("reason")
    @classmethod
    def _says_why(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("delisted.reason is empty — say why the row left the list")
        return value


class Entry(BaseModel):
    id: str
    name: str
    category: Category
    url: str
    source_urls: list[str] = []
    card_required: bool = False
    offering: str
    limits: str = ""
    # Which kind of free this is; freetier-check refuses a live row without it.
    free_part: FreePart | None = None
    models: list[ModelFamily] = []
    api: ApiInfo | None = None
    client_lane: ClientLane | None = None
    data_use: DataUse | None = None
    probe: Probe
    first_seen: date
    last_verified: date
    retired_on: date | None = None  # vendor-announced shutdown; archives the row on that day
    delisted: Delisting | None = None  # taken off the list by a reviewer; archives the row
    # The row that holds this same service, where two rows named one: the id of
    # the row that keeps the offer, the evidence and the history, and the reason
    # this one is listed nowhere a reader counts services.
    duplicate_of: str | None = None
    probe_failures: int = 0
    provisional: bool = False
    rank: int = 100  # sort key within a category: lower renders higher

    @model_validator(mode="after")
    def _keywords_must_anchor(self) -> Entry:
        """A page-keywords probe needs at least one keyword that dies with the
        offer — the free model's id, its quota figure, or the vendor's own
        sentence about it. Generic words alone keep passing for months after a
        free tier is withdrawn.

        The first version of this rule only rejected keywords listed verbatim in
        GENERIC_KEYWORDS, which let `hobby`, `free quota`, `no signup` and
        `monthly credits` through — words that sit on a pricing page whatever
        the page is currently offering. is_anchor() asks the question the list
        cannot: would this string still be there once the free tier is gone?

        A delisted row is exempt. No probe reads it again, and it keeps the probe
        it was published with as part of the record — on the list's first day
        that was the bare word "free", which is how aider and Puter got listed.
        """
        probe = self.probe
        if self.delisted is None and probe.type is ProbeType.PAGE_KEYWORDS:
            every = [*probe.keywords, *probe.machinery_keywords]
            if not any(is_anchor(k) for k in every):
                raise ValueError(
                    f"probe {probe.endpoint}: none of the keywords {every} anchors on "
                    "the offer — use a free model id, a quota or price figure, or a phrase "
                    "of four or more words quoted from the page"
                )
        return self

    @model_validator(mode="after")
    def _only_a_free_part_of_models_names_models(self) -> Entry:
        """The Models column lists models the vendor serves free in their own
        right. A sum to spend makes none of them free by itself, and a free part
        the vendor names no model for makes no claim a family could repeat.

        Until 2026-09-25 this was a sentence in CONTRIBUTING, applied by reading
        rows: the pass that emptied Cloudflare's, Upstage's and Dahl's columns
        said they were the only ones, and Inception, Sail Research and Sarvam
        went on naming the models their credit is spent on."""
        if self.models and self.free_part is FreePart.SUM:
            raise ValueError(
                f"{self.id}: free_part is sum — a sum to spend names no model, since no model is "
                "free by itself; empty models[] and keep a few of the vendor's exact ids in "
                "api.model_ids")
        if self.models and self.free_part is FreePart.UNNAMED:
            raise ValueError(
                f"{self.id}: free_part is unnamed — the vendor names no model its free part "
                "reaches, so a family would be a claim it never makes; empty models[], or set "
                "free_part: models where it names them")
        return self

    @model_validator(mode="after")
    def _a_probe_that_reads_free_models_reads_a_free_part_of_models(self) -> Entry:
        """A probe that reads each model's own free mark — a zero price, a free
        marker, a lane key, a free list — or a lane served inside the vendor's
        client is reading free models, whatever else the row offers: Vercel's $5
        a month sits beside three models it prices at zero, and those three are
        its column."""
        p = self.probe
        reads_free = self.client_lane is not None or (
            p.type is ProbeType.API_MODELS
            and bool(p.require_zero_price or p.free_marker or p.lane or p.free_list))
        if reads_free and self.free_part in (FreePart.SUM, FreePart.UNNAMED):
            raise ValueError(
                f"{self.id}: the probe reads free models — each model's own free mark, or the "
                f"lane the vendor's client serves — so free_part is models, not "
                f"{self.free_part.value}")
        return self

    @model_validator(mode="after")
    def _a_fold_is_a_reviewers_decision_about_another_row(self) -> Entry:
        """`duplicate_of` is for two rows that named one service.

        The list ran with two for two months: `mimocode`, a placeholder from
        the first day's seed — "Coding agent with free tier", limits "TBD by
        scout", at mimocode.ai, a domain that has never resolved — and
        `mimo-code`, Xiaomi's agent, added that evening with its README, its
        models and its shutdown date. Xiaomi's own README prints the name as
        one word, so the Archive showed one project twice, two lines apart.

        A row is never deleted, so the fold is recorded rather than applied:
        the duplicate keeps its id, since the id is its page's URL, and names
        the row that holds the service. That is a reviewer's reading of two
        rows, not a probe result, so the row carries the `delisted` that says
        so — and a row folded into itself would be a page pointing at itself.
        """
        if self.duplicate_of is None:
            return self
        if self.duplicate_of == self.id:
            raise ValueError(f"{self.id}: duplicate_of names the row itself — it names the "
                             "other row, the one that holds the service")
        if self.delisted is None:
            raise ValueError(
                f"{self.id}: a row folded into {self.duplicate_of} leaves the list by a "
                "reviewer's hand — give it `delisted` with the reason, or drop duplicate_of")
        return self

    @model_validator(mode="after")
    def _ignored_ids_need_a_price_list(self) -> Entry:
        """`api.ignored_ids` is read where the probe compares a catalog's
        zero-priced rows with `api.model_ids` — an api-models probe with
        require_zero_price set — and nowhere else. Anywhere else it would sit
        in the registry recording a decision nothing acts on, the silence
        _zero_price_needs_a_price_list refuses for the same reason. And an id
        in both lists is two decisions about one id."""
        if self.api is None or not self.api.ignored_ids:
            return self
        if not (self.probe.type is ProbeType.API_MODELS and self.probe.require_zero_price):
            raise ValueError(
                f"{self.id}: api.ignored_ids needs an api-models probe with "
                "require_zero_price — nothing reads it anywhere else")
        both = sorted(set(self.api.ignored_ids) & set(self.api.model_ids))
        if both:
            raise ValueError(
                f"{self.id}: {', '.join(both)} cannot sit in both api.model_ids and "
                "api.ignored_ids")
        return self

    @model_validator(mode="after")
    def _a_client_lane_is_a_lane_its_probe_reads(self) -> Entry:
        """`client_lane` records a lane no API serves, and its ids are held to what
        the probe reads, in both directions — so the probe must be able to tell
        the free lane from the rest of what it reads: the key the vendor lists
        it under (`probe.lane`), or prices it reads at zero. On a page, or on a
        catalog it cannot read free off, the list would be checked by nothing.
        And a lane an API serves keeps its ids in `api.model_ids`, which the
        configs are written from: two lists of one lane drift apart."""
        if self.client_lane is None:
            return self
        if self.api is not None:
            raise ValueError(
                f"{self.id}: a lane an API serves keeps its ids in api.model_ids — "
                "client_lane is for a lane served only inside the vendor's own client")
        probe = self.probe
        if probe.type is not ProbeType.API_MODELS or not (probe.lane or probe.require_zero_price):
            raise ValueError(
                f"{self.id}: client_lane.model_ids are held to the lane an api-models probe "
                "reads — name it in probe.lane, or read prices with require_zero_price")
        return self

    @model_validator(mode="after")
    def _catalog_needs_ids_to_check(self) -> Entry:
        """`probe.catalog` is read once, to check `api.model_ids` on a row whose
        probe reads prose. An api-models probe already reads its endpoint as
        the catalog, so a second one there is two answers to one question; and
        a page row with no ids has nothing for the catalog to check. Either way
        the field would sit in the registry doing nothing."""
        if self.probe.catalog is None:
            return self
        if self.probe.type is not ProbeType.PAGE_KEYWORDS:
            raise ValueError(
                f"{self.id}: probe.catalog belongs on a page-keywords probe — an "
                "api-models probe reads its endpoint as the catalog")
        if self.api is None or not self.api.model_ids:
            raise ValueError(
                f"{self.id}: probe.catalog has nothing to check without api.model_ids")
        return self


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


# Hosts that serve anyone's repository, where the path names the publisher and
# the host names nobody. Each maps to the host its owners are counted under, so
# a raw file and the repository it came from are the same owner.
SHARED_HOSTS = {
    "github.com": "github.com",
    "raw.githubusercontent.com": "github.com",
    "gist.github.com": "github.com",
    "huggingface.co": "huggingface.co",
}
# On huggingface.co these lead the path and the owner follows them.
_HF_KINDS = {"spaces", "datasets", "models"}


def site_of(url: str) -> str:
    """Who publishes a URL: its host, or on a shared host, host and owner."""
    host = domain_of(url)
    if host not in SHARED_HOSTS:
        return host
    parts = [p for p in urlparse(url).path.lower().split("/") if p]
    if host == "huggingface.co" and parts and parts[0] in _HF_KINDS:
        parts = parts[1:]
    return f"{SHARED_HOSTS[host]}/{parts[0]}" if parts else host


def is_covered(url: str, known: set[str]) -> bool:
    """Whether a URL belongs to a vendor `known` already names.

    A host is covered by itself, by any host it is a subdomain of and by any it
    is the parent of: api.z.ai and nvidia.com are Z.ai and NVIDIA, both of which
    the scout proposed back on 2026-09-14 while their rows were listed at z.ai
    and build.nvidia.com. A sibling is not covered — docs.api.nvidia.com is not
    integrate.api.nvidia.com — and on a shared host only the same owner is,
    since github.com is the parent of docs.github.com and of every repository.
    """
    site = site_of(url)
    if site in known:
        return True
    host = domain_of(url)
    if not host or host in SHARED_HOSTS:
        return False
    return any(host.endswith("." + k) or k.endswith("." + host)
               for k in known if "/" not in k)


def known_domains(entries: list[Entry]) -> set[str]:
    """Every site the registry already reaches an entry at — a host, or an
    owner on a shared host (see `site_of`).

    All three matter, which is what makes this a function rather than a set
    comprehension at the call site: NVIDIA is listed at build.nvidia.com,
    documented at docs.api.nvidia.com and served at integrate.api.nvidia.com,
    and a set built from the url alone reported our own entry back to us as an
    undiscovered provider.

    A delisted row reaches nothing: it is the record of a row, and the verdict
    that took it off lives in the watchlist or the blocklist, which answer for
    the vendor — the watchlist's expiring so that the question comes back.
    """
    entries = [e for e in entries if e.delisted is None]
    urls = [e.url for e in entries] + [u for e in entries for u in e.source_urls]
    urls += [e.api.base_url for e in entries if e.api and e.api.base_url]
    return {s for s in map(site_of, urls) if s}


ARCHIVE_AFTER_DAYS = 60
# The weekdays the scheduled run probes every row on, numbered the way the cron
# in .github/workflows/update.yml numbers them (0 is Sunday). Every page that
# says how often a row is checked reads the phrase from here, and freetier-check
# holds the workflow's cron and the hand-written files to it: "twice a week" was
# typed into two dozen places, each of which would have gone on saying it the
# day the cron moved.
PROBE_WEEKDAYS = (1, 4)
_TIMES_A_WEEK = {1: "once a week", 2: "twice a week", 3: "three times a week",
                 4: "four times a week", 5: "five times a week", 6: "six times a week",
                 7: "every day"}


def probe_frequency(weekdays: tuple[int, ...] = PROBE_WEEKDAYS) -> str:
    """How often the list says a row is checked, in the words its pages use."""
    return _TIMES_A_WEEK[len(set(weekdays))]


# Consecutive FAILs before a row is buried. Two is a vendor reshuffling a
# page between Monday and Thursday; three is the offer being gone. The
# provider page quotes it, so the countdown a reader is shown and the rule
# that ends it are the same number.
ARCHIVE_AFTER_FAILURES = 3


def is_archived(entry: Entry, today: date) -> bool:
    """Liveness comes from probes, staleness, vendor-announced retirement and a
    reviewer's delisting — never from model generations. A provider whose catalog
    moves on is still free, so a superseded family means "bump the row", not
    "bury the entry".

    Lives with the model rather than with the renderer because it answers a
    question about the entry, not about the README: the scout needs it too, to
    keep from proposing work on entries the registry has already buried.
    """
    if is_archived_for_good(entry, today):
        return True
    if entry.probe_failures >= ARCHIVE_AFTER_FAILURES:
        return True
    if (today - entry.last_verified).days > ARCHIVE_AFTER_DAYS:
        return True
    return False


def folded_into(entries: list[Entry], entry: Entry) -> Entry | None:
    """The row this one was folded into, where the registry holds it.

    None for a row of its own, and None for a fold whose target the registry
    has lost — the renderer then has a page to build either way, and
    `freetier-check` is where a dangling fold is reported."""
    if entry.duplicate_of is None:
        return None
    return next((e for e in entries if e.id == entry.duplicate_of), None)


def is_archived_for_good(entry: Entry, today: date) -> bool:
    """Archived by a date or by a reviewer rather than by the probe — so no probe
    result can bring the row back, and none is asked for. A row the probe
    archived stays probed, and the first pass restores it."""
    if entry.delisted is not None:
        return True
    return entry.retired_on is not None and today >= entry.retired_on


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
    on the *service* — pooled piracy, spoofed clients, hostile to agents, a
    product that is gone — and it is meant to be permanent, so putting a
    legitimate vendor there buries it on the day it opens a free lane. BYOK-only
    was on that list once and is the proof: Cline sat on the blocklist as a tool
    with no bundled usage for two months while its own provider handed out free
    models, because a permanent verdict is never read again. Leaving it in
    neither file is what actually happened to tokenrouter.io and LLM7: nothing
    recorded the decision, so the scout re-proposed them and a reviewer
    re-derived the same "no" from scratch.

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


class Source(BaseModel):
    """A list, catalog or directory read as a possible feed and not adopted.

    `Watched` records a verdict on a service; this is the same record one level
    up, on the thing that *proposes* services. CURATED_FEEDS in discovery.py is
    the positive half — the lists the scout reads every run — and nothing
    held the negative half, so the cost of opening a list that carries no
    provider data was paid again every time the link resurfaced. Three lists
    went through that in a single week and left no trace in the repository:
    the reasoning existed only in whichever conversation happened to have it.

    A verdict on a SOURCE, on a DATE, for the same reason `Watched` is: a
    directory can start carrying endpoints long after someone first opened it.
    """
    url: str
    name: str
    checked_on: date
    reason: str
    reopen_if: str = ""


# Deliberately longer than WATCH_RECHECK_DAYS. A vendor can open a free tier in
# any given week, so 90 days is the most a "nothing free here" verdict is worth
# trusting — but a directory rarely changes what kind of directory it is, and
# re-reading one every quarter would spend a session to re-learn the same thing.
# Twice a year is often enough to catch a list that grew into a feed.
SOURCE_RECHECK_DAYS = 180


def load_sources(path: Path) -> list[Source]:
    """Missing file means nothing has been declined yet."""
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = data.get("read") if isinstance(data, dict) else data
    return [Source.model_validate(s) for s in (items or [])]


def is_source_current(source: Source, today: date) -> bool:
    """Past this the verdict is not wrong, only old enough to be worth asking
    again — which is all this file ever claims."""
    return (today - source.checked_on).days <= SOURCE_RECHECK_DAYS


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
