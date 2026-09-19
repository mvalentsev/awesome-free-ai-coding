from __future__ import annotations

import re
from datetime import date
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

import yaml
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


class Tier(str, Enum):
    FRONTIER = "frontier"
    STRONG = "strong"


class ProbeType(str, Enum):
    API_MODELS = "api-models"
    PAGE_KEYWORDS = "page-keywords"


class ModelFamily(BaseModel):
    family: str
    # A measurement, never a reputation (CONTRIBUTING, "tier: frontier is a
    # measurement"): how close the model this lane serves scores to the top of
    # the Artificial Analysis Intelligence Index, read by `freetier-tiers`. No
    # tier means not measured, or measured below the strong bar. Until
    # 2026-09-17 every family defaulted to `strong`, so Apertus 70B at 5 points
    # and GLM 5.3 Flash at 42 carried the same word.
    tier: Tier | None = None
    released: str = ""
    superseded_by: str | None = None
    # The Artificial Analysis model the tier was read from: the slug of its page
    # on artificialanalysis.ai/models/, for the variant the lane actually serves.
    aa_model: str | None = None

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
    note: str = ""
    # A lane that does not work as published right now, owned up to while the
    # list waits for the vendor (see Notice). Rendered under the README's
    # quickstart curl, in the connection table, on the provider page and in
    # llms.txt; on a keyless row it also holds a refusal off the failure count
    # for NOTICE_HOLD_DAYS, and the run asks for it to come down the day the
    # lane answers again.
    notice: Notice | None = None

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
    def _notice_needs_an_endpoint(self) -> ApiInfo:
        if self.notice and not self.base_url:
            raise ValueError("notice speaks about calling base_url, and there is no base_url")
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
    models: list[ModelFamily] = []
    api: ApiInfo | None = None
    probe: Probe
    first_seen: date
    last_verified: date
    retired_on: date | None = None  # vendor-announced shutdown; archives the row on that day
    delisted: Delisting | None = None  # taken off the list by a reviewer; archives the row
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
