from __future__ import annotations

import argparse
import asyncio
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path

import httpx

from .history import record_changes
from .models import (
    CHALLENGE_MARKERS, DEAD_MARKERS, Entry, Probe, ProbeType, load_registry, save_registry,
)

TIMEOUT = httpx.Timeout(20.0, connect=10.0)
UA = {"User-Agent": "freetier-radar/0.2"}
ATTEMPTS = 3
BACKOFF_SECONDS = 2.0
CONCURRENCY = 8
PROVISIONAL_PROMOTE_DAYS = 14


class ProbeStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"  # page reachable but the free offer is no longer evidenced
    INCONCLUSIVE = "inconclusive"  # could not check: blocked, down, network error
    STALE_MODELS = "stale-models"  # offer verified, but every listed family is superseded
    STALE_IDS = "stale-ids"  # offer and families verified, but api.model_ids has dead ids


@dataclass
class ProbeResult:
    status: ProbeStatus
    detail: str = ""


async def probe_entry(client: httpx.AsyncClient, entry: Entry,
                      attempts: int = ATTEMPTS, backoff: float = BACKOFF_SECONDS) -> ProbeResult:
    last = ""
    for i in range(attempts):
        if i:
            await asyncio.sleep(backoff * i)
        try:
            resp = await client.get(entry.probe.endpoint, timeout=TIMEOUT, follow_redirects=True)
        except httpx.HTTPError as exc:
            last = f"network error: {exc}"
            continue
        if resp.status_code in (401, 403, 429):
            return ProbeResult(ProbeStatus.INCONCLUSIVE, f"blocked: HTTP {resp.status_code}")
        if resp.status_code >= 500:
            last = f"HTTP {resp.status_code}"
            continue
        if resp.status_code >= 400:
            return ProbeResult(ProbeStatus.FAIL, f"page gone: HTTP {resp.status_code}")
        detail = check_content(resp, entry)
        if detail is None:
            # The offer is evidenced. Whether the models the README hangs off it
            # still are is a second question, and only a page-keywords probe
            # leaves it open — see unevidenced_families.
            unevidenced = unevidenced_families(resp, entry)
            if unevidenced:
                return ProbeResult(ProbeStatus.STALE_MODELS,
                                   "listed families the page does not name: "
                                   + ", ".join(unevidenced))
            # A third question about the same fetched bytes, and the last field
            # here that nothing read back. Only one of these two checks can fire
            # on any given entry: each is guarded on the probe type the other
            # cannot read.
            dead = dead_model_ids(resp, entry)
            if dead:
                return ProbeResult(ProbeStatus.STALE_IDS,
                                   "api.model_ids the catalog no longer answers for: "
                                   + "; ".join(dead))
            return ProbeResult(ProbeStatus.PASS)
        # Only asked once the content check has already failed. Plenty of live
        # pages carry a <noscript> asking for JavaScript while serving the offer
        # perfectly well above it — on those the keywords match and this never
        # runs. It is when they do NOT match that the wording matters: a bot wall
        # means we did not see the vendor's page, not that the offer is gone.
        challenge = challenge_marker_hit(resp.text)
        if challenge is not None:
            return ProbeResult(ProbeStatus.INCONCLUSIVE, f'bot challenge: page says "{challenge}"')
        return ProbeResult(ProbeStatus.FAIL, detail)
    return ProbeResult(ProbeStatus.INCONCLUSIVE, f"unreachable after {attempts} attempts: {last}")


def check_content(resp: httpx.Response, entry: Entry) -> str | None:
    """None = content confirms the entry; string = what is missing.

    Works on both sync and async httpx responses, so the scout reuses it to
    vet newly proposed entries before accepting them.
    """
    if entry.probe.type is ProbeType.API_MODELS:
        return _check_api_models(resp, entry)
    return _check_page_keywords(resp, entry)


def _model_id(model: dict) -> str:
    """What you put in the request body. OpenAI-shaped catalogs call the field
    `id`; the new-api family of gateways (TokenRouter and its kin) calls the
    same string `model_name`.

    `model_id` is read before `model_name` because a catalog that publishes both
    means the second one as a title — AIHubMix ships `"model_id":
    "coding-glm-5.1-free"` next to `"model_name": "Coding GLM 5.1 (free)"`, and
    a family matched against the title misses every hyphen."""
    for key in ("id", "model_id", "model_name"):
        value = model.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _number(value: object) -> float | None:
    """A price the vendor actually published. Booleans are numbers in Python and
    would read as a free 0/paid 1, so they are not."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _price_row(value: object) -> float | None:
    """One side of the price, however the vendor writes the row down. Most spell
    it as the bare number; Routeway wraps it in the unit it is quoted in —
    `{"unit": "1M tokens", "price_per_million_t": 0}`. Which unit that is does
    not matter to the only question asked here: is the row still a zero."""
    if isinstance(value, dict):
        for key in ("price_per_million_t", "price_per_million", "price", "amount", "value"):
            price = _number(value.get(key))
            if price is not None:
                return price
        return None
    return _number(value)


def _tiered_price_of(tiers: list) -> list[float] | None:
    """Requesty publishes one price row per usage tier, as a list of
    `{prompt_tokens_threshold, input_price, output_price}` rather than a single
    pricing object.

    Every tier is read, because the question is whether the row is a zero all
    the way up. A lane that costs nothing below a threshold and bills above it
    is a discount, not a free model, and taking only the first row — the
    cheapest one, since the list is ordered by threshold — would file it as
    free."""
    prices = []
    for tier in tiers:
        if not isinstance(tier, dict):
            return None
        for key in ("input_price", "output_price"):
            price = _price_row(tier.get(key))
            if price is not None:
                prices.append(price)
            elif key in tier:
                return None
    return prices or None


def _price_of(model: dict) -> list[float] | None:
    """What one plain completion costs, as the vendor publishes it, or None when
    it publishes nothing we understand. OpenRouter and BazaarLink name the rows
    prompt/completion, Vercel input/output, Requesty ships a tier per row; cache,
    image and request rows are ignored — a free lane is defined by the price of
    ordinary tokens."""
    pricing = model.get("pricing")
    if isinstance(pricing, list):
        return _tiered_price_of(pricing)
    if not isinstance(pricing, dict):
        return _multiplier_price_of(model)
    prices = []
    for key in ("prompt", "completion", "input", "output"):
        price = _price_row(pricing.get(key))
        if price is not None:
            prices.append(price)
        elif key in pricing:
            return None
    return prices or None


def _multiplier_price_of(model: dict) -> list[float] | None:
    """The new-api family publishes no pricing object. A row is billed either per
    request (`quota_type` 1, `model_price` in currency) or per token, where
    `model_ratio` multiplies a house unit and `completion_ratio` scales the
    output side of it. The unit cancels out for the only question asked here —
    is this row still a zero — so the multipliers are compared directly.

    `quota_type` is read loosely on purpose: a gateway that sends it as "1"
    would otherwise fall through to the token branch, where a per-request price
    sits next to a zero `model_ratio` and reads as free."""
    if _number(model.get("quota_type")) == 1:
        price = _number(model.get("model_price"))
        return [price] if price is not None else None
    ratio = _number(model.get("model_ratio"))
    if ratio is None:
        return None
    completion = _number(model.get("completion_ratio"))
    return [ratio, ratio * (completion if completion is not None else 1.0)]


def _is_withdrawn(model: dict) -> bool:
    """The vendor's own verdict that a row cannot be called right now.

    Of the catalogs probed here only Routeway publishes one — `available`, on all
    239 of its rows, false on exactly one, and that one a zero-priced `:free` id.
    That is the whole hole: the price stays 0 while the lane goes away, so a
    price-only check vouches for it forever.

    Read loosely, like `quota_type`: a gateway that stringifies the boolean would
    otherwise turn this into a check that can never fire. A missing or null field
    means the vendor said nothing, which is not a withdrawal.

    `outdated` is deliberately not read. The same catalog sets it on eight models
    that are `available: true` and callable — a model's age is is_model_stale's
    question, and answering it here would fail live entries over it.
    """
    value = model.get("available", True)
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value == 0
    if isinstance(value, str):
        return value.strip().lower() in ("false", "no", "off", "0")
    return False


def _price_note(model: dict) -> str:
    prices = _price_of(model)
    mid = _model_id(model) or "?"
    if prices is None:
        return f"{mid} publishes no price"
    return f"{mid} priced {'/'.join(f'{p:g}' for p in prices)}"


def _catalog_items(resp: httpx.Response) -> list[dict] | None:
    """Every model row of an OpenAI-shaped catalog, however the vendor wraps it,
    or None when the body is not JSON at all — the one case a caller has to tell
    apart from an empty catalog."""
    try:
        data = resp.json()
    except json.JSONDecodeError:
        return None
    rows = (data if isinstance(data, list)
            else data.get("data", []) if isinstance(data, dict) else [])
    return [m for m in rows if isinstance(m, dict)]


def _check_api_models(resp: httpx.Response, entry: Entry) -> str | None:
    items = _catalog_items(resp)
    if items is None:
        return "response is not JSON"
    if not any(_model_id(m) for m in items):
        return "no model ids in response"
    marker = entry.probe.free_marker.lower()
    missing, withdrawn, priced = [], [], []
    for family in entry.models:
        matches = [
            m for m in items
            if family.family.lower() in _model_id(m).lower()
            and (not marker or marker in _model_id(m).lower())
        ]
        if not matches:
            missing.append(family.family)
            continue
        # A row the vendor marks uncallable is not a free lane whatever its price
        # says, so it is dropped before the price is read below — otherwise a
        # withdrawn zero would go on vouching for a family whose only callable
        # row has started billing.
        live = [m for m in matches if not _is_withdrawn(m)]
        if not live:
            withdrawn.append(", ".join(_model_id(m) or family.family for m in matches[:3]))
            continue
        # Presence in the catalog is not the offer: an aggregator can leave a
        # free model's id exactly where it was and start charging for it, and a
        # substring check would keep passing forever. Where the vendor publishes
        # prices, the zero is the offer.
        if entry.probe.require_zero_price and not any(_is_free(m) for m in live):
            priced.append(", ".join(_price_note(m) for m in live[:3]))
    problems = []
    if missing:
        problems.append(f"missing families: {', '.join(missing)}")
    if withdrawn:
        problems.append(f"marked unavailable: {'; '.join(withdrawn)}")
    if priced:
        problems.append(f"no longer free: {'; '.join(priced)}")
    return " | ".join(problems) if problems else None


def _is_free(model: dict) -> bool:
    prices = _price_of(model)
    return prices is not None and all(p == 0 for p in prices)


def challenge_marker_hit(text: str) -> str | None:
    """The wording of a bot wall standing where the vendor's page should be."""
    lowered = text.lower()
    for marker in CHALLENGE_MARKERS:
        if marker in lowered:
            return marker
    return None


def dead_marker_hit(text: str, probe: Probe) -> str | None:
    """The phrase a vendor uses to announce the offer is over, if the page has one."""
    for marker in (*DEAD_MARKERS, *probe.dead_markers):
        if marker.lower() in text:
            return marker
    return None


_SPACE_LOOKALIKES = str.maketrans(dict.fromkeys(
    "\u00a0\u202f\u2009\u2007\u2060", " "))


def _plain_spaces(text: str) -> str:
    """The typographic spaces a CMS puts between words a designer did not want
    broken across lines. They are invisible in a browser and in a copy-paste, so
    a keyword quoted off the page — "100 million free tokens" on Inception Labs'
    own page — simply never occurs in the bytes, and the probe reports a
    withdrawn offer over a non-breaking space."""
    return text.translate(_SPACE_LOOKALIKES)


def _check_page_keywords(resp: httpx.Response, entry: Entry) -> str | None:
    text = _plain_spaces(resp.text.lower())
    # An explicit withdrawal outranks the keywords: vendors leave the free tier
    # described on the page and add the bad news next to it.
    dead = dead_marker_hit(text, entry.probe)
    if dead is not None:
        return f'offer withdrawn: page says "{dead}"'
    missing = [k for k in entry.probe.keywords if k.lower() not in text]
    return f"missing keywords: {', '.join(missing)}" if missing else None


def unevidenced_families(resp: httpx.Response, entry: Entry) -> list[str]:
    """Families the README publishes that the probed page does not even name.

    `_check_api_models` demands every listed family back from the catalog, so on
    that half of the registry a model that quietly leaves takes its row with it.
    A page-keywords probe had no equivalent: its keywords anchor the OFFER, and
    nothing ever asked whether the models listed beside that offer are still
    there. Measured 2026-08-14 across every live page-keywords entry, a third of
    the published families appeared nowhere in the page their probe reads.

    Deliberately weak, in two ways that are both the point:

    It reads the same bytes the keywords do, so a name the vendor serves inside
    its page data counts. Whether the page names the model AS FREE is the
    stronger question, and the one an anchor keyword answers — novita's id sat
    next to a price for weeks before anyone noticed, and no presence check would
    have caught that.

    That weakness was measured the other way round on 2026-08-14, by byte
    location rather than presence: of the 32 live page-keywords entries, four
    match only in bytes a reader never sees, and every one of the four is
    deliberate — trae's `"name":"free"`, cursor's `"name":"hobby","price":"0"`,
    z.ai's ids glued to their price cells, and Upstage's own section heading
    inside a client-rendered payload. What the same pass did catch is the shape
    this docstring cannot: a family evidenced by an OpenAPI enum the page embeds
    (Groq's llama-4, absent from the Free Plan Limits table beside it) and one
    evidenced by an i18n bundle linking a 2025 blog post (Mistral). Both were
    fixed in the registry rather than here, because from this function the two
    cases are the same bytes.

    And it never fails an entry. Three failures archive a row, so a marketing
    page that drops a model name in a restyle would bury a live service inside a
    week; the rotating-lane rule (Kilo, TokenRouter) says the same thing from the
    other side. STALE_MODELS is what "the offer is alive, the Models column is
    not trustworthy" already means here, and it is what the scout's FIX_PROMPT
    already knows how to repair.
    """
    if entry.probe.type is not ProbeType.PAGE_KEYWORDS:
        return []
    squashed, text = _squash(resp.text), resp.text.lower()
    return [m.family for m in entry.models
            if _squash(m.family) not in squashed and not _named_in_parts(m.family, text)]


def dead_model_ids(resp: httpx.Response, entry: Entry) -> list[str]:
    """Ids in `api.model_ids` that the catalog no longer answers for.

    This is the last curated field here that nothing ever read back. It is not
    the Models column, so neither `_check_api_models` nor `unevidenced_families`
    looks at it, and it is not on any page, so no keyword anchors it — yet it is
    the field that fills `configs/litellm.yaml`, `configs/opencode.json` and
    `configs/free-llm.env.example`, which is what a reader actually pastes into
    a client. Three scout pull requests running dropped a family from `models[]`
    and left its id here — bazaarlink in #10, opencode and vercel-ai-gateway in
    #11, openrouter-free in #12 — and each time the configs went on handing out
    an id that 404s until somebody happened to look. Measured 2026-08-28 across
    the ten live api-models entries: 7 of their 72 ids were already dead, spread
    over two rows whose probes were passing that morning.

    Only an api-models entry can be asked, for the reason `unevidenced_families`
    is deliberately weak: a page-keywords probe reads prose, and a name missing
    from prose is not a withdrawal. Here the consequence would be worse — a
    deletion from a config file rather than a flag on a column.

    The match is exact, because `api.model_ids` holds what goes in the request
    body. `deepseek-ai/deepseek-v4-flash` and its live successor
    `deepseek-ai/deepseek-v4-flash-0731` are one model and two ids, and only the
    second one answers; a substring test would call the row healthy forever.
    That is also why a missing id is reported with any catalog id that extends
    it: NVIDIA re-versioned that row rather than dropping it, so the repair is a
    rename, and the two cases are indistinguishable without the hint.

    It never fails an entry and never repairs one. A free lane rotating its ids
    is this list doing its job — kilo-code's own note says so — so archiving a
    row over it would be the mistake `unevidenced_families` exists to avoid.
    And the repair is an exact string copied from a catalog, which is the last
    thing to let an LLM guess at: the scout is told to leave these rows for a
    human rather than sent off to fix them.
    """
    if entry.probe.type is not ProbeType.API_MODELS or entry.api is None:
        return []
    catalog: dict[str, dict] = {}
    for model in _catalog_items(resp) or []:
        mid = _model_id(model)
        if mid:
            catalog.setdefault(mid, model)
    dead = []
    for wanted in entry.api.model_ids:
        model = catalog.get(wanted)
        if model is None:
            dead.append(f"{wanted} is not in the catalog{_successor_hint(wanted, catalog)}")
        elif _is_withdrawn(model):
            dead.append(f"{wanted} is marked unavailable")
        elif entry.probe.require_zero_price and not _is_free(model):
            dead.append(_price_note(model))
    return dead


def _successor_hint(wanted: str, catalog: dict[str, dict]) -> str:
    """The catalog ids that extend a missing one, when a vendor re-versioned the
    row instead of withdrawing it. Only a prefix counts, which is what keeps the
    hint honest in the opposite case: Routeway's `llama-3.1-8b-instruct:free`
    left its free lane while `llama-3.1-8b-instruct` went on being metered, and
    naming the metered twin as the successor is exactly the confusion
    `require_zero_price` was added to stop."""
    heirs = sorted(mid for mid in catalog if mid != wanted and mid.startswith(wanted))
    return f" (catalog carries {', '.join(heirs[:2])})" if heirs else ""


def _squash(s: str) -> str:
    """Case and separators removed: vendors write "Qwen3 Coder" and "GLM-4.7
    Flash" for what the registry calls qwen3-coder and glm-4.7-flash."""
    return re.sub(r"[\s_-]+", "", s.lower())


# How far apart the parts of a family name may sit and still be one name. Wide
# enough for the words a vendor folds in ("Claude Sonnet & Opus 4.6" spends 24),
# narrow enough that a price list mentioning claude in one row and 4.6 in
# another does not vouch for a model nobody offers.
NAME_SPREAD = 48


def _named_in_parts(family: str, text: str) -> bool:
    """Antigravity enumerates its free agent models as "Claude Sonnet & Opus
    4.6": two models sharing one version number, and neither of them a substring
    of the page. A warning that fires on entries that are correct is a warning
    that gets ignored, so a family also counts as named when its parts appear in
    order and close together.

    Each part must start where a name starts. Without that, the version half of
    a family name matches inside a *different* version and the check vouches for
    a model nobody offers: kiro.dev/pricing, which serves Sonnet 4.5 free and
    sells 4.6, named opus-5 for this function through the "5" in "Opus 4.5",
    and glm-5 through a "GLM" in a country-support FAQ and a "5" in the minified
    markup after it. Anchoring on the left is enough — anchoring on the right
    too would unname minimax-2.1, which that same page writes at the end of a
    sentence as "MiniMax 2.1.". Measured against every live page-keywords entry
    on 2026-08-14: no family this repository publishes changes verdict.

    The letter in front of a version number is the vendor's, and it moves. On
    2026-08-20 the same Kiro page restyled the free-tier footnote it had written
    as "DeepSeek v3.2 and MiniMax 2.1." into "DeepSeek 3.2, and MiniMax M2.1" —
    same two models, same sentence, same free tier, and both families unnamed
    for this function. That is not a Models column going stale, it is a caption
    being retyped, and it reached a scout PR proposing to delete two models the
    vendor still hands out for free. So a version part is matched through
    _version_pattern, which lets that prefix letter differ on either side.
    Measured the same way on 2026-08-20, across all 18 live page-keywords
    entries that publish a family: kiro is the only verdict that moves, and it
    moves to none.
    """
    parts = [p for p in re.split(r"[\s_-]+", family.lower()) if p]
    if len(parts) < 2:
        return False
    spread = r"[^\n]{0,%d}?" % NAME_SPREAD
    anchored = (r"(?<![\w.])" + (_version_pattern(p) or re.escape(p)) for p in parts)
    return re.search(spread.join(anchored), text) is not None


# A generation number the vendor may or may not put a letter in front of:
# "v3.2", "3.2" and "M2.1" are one part each, and the letter is the vendor's.
# The dot is required. A bare number carries no letter here, because a hashed
# "h5" in minified markup would then name glm-5 for any page that says GLM
# nearby — the exact failure the left anchor in _named_in_parts exists to stop,
# walked back in through the number.
DOTTED_VERSION = re.compile(r"[a-z]?(\d+(?:\.\d+)+)")


def _version_pattern(part: str) -> str | None:
    """How a dotted version part may be spelled, or None for any other part.

    Three vendors write one generation three ways — "v3.2", "3.2", "M2.1" — and
    the registry has to write it once, so the prefix letter is optional on both
    sides. Nothing else about the part is relaxed: "2.1" still has to start
    where a name starts, and still has to sit within NAME_SPREAD of the part
    before it.
    """
    match = DOTTED_VERSION.fullmatch(part)
    return None if match is None else r"[a-z]?" + re.escape(match.group(1))


def is_model_stale(entry: Entry) -> bool:
    """Every listed family bumped to a newer generation. The entry is alive —
    a supersede mark never archives — but the README has no free model left to
    name for it, so the families need refreshing."""
    return bool(entry.models) and all(m.superseded_by for m in entry.models)


def apply_results(entries: list[Entry], results: dict[str, ProbeResult],
                  today: date) -> list[tuple[Entry, ProbeResult]]:
    """PASS verifies and resets failures; FAIL increments them; INCONCLUSIVE
    touches nothing — the staleness rule archives entries that stay unverifiable.
    A provisional entry that keeps passing probes for PROVISIONAL_PROMOTE_DAYS
    after first_seen is promoted to a regular entry. An entry past its
    vendor-announced retirement date is left alone entirely.
    Returns (entry, result) pairs needing scout attention: FAIL, INCONCLUSIVE,
    passing entries whose model families are all superseded, and passing entries
    flagged for their Models column or their `api.model_ids`."""
    needs_attention = []
    for e in entries:
        result = results.get(e.id)
        if result is None:
            continue
        # The vendor's own shutdown date has passed: the entry is archived and
        # its endpoint is meant to be dead. Re-verifying it would keep moving
        # last_verified forward on a service that is gone, and flagging it sends
        # the scout off to "fix" the probe — which is how GitHub Models' HTTP
        # 410 crashed the 2026-08-03 run.
        if e.retired_on is not None and today >= e.retired_on:
            continue
        # STALE_MODELS and STALE_IDS are passes with a note: the probe reached
        # the page and the offer was evidenced there, so the liveness
        # bookkeeping is the same one a PASS gets. Letting last_verified freeze
        # instead would archive the row by staleness in ARCHIVE_AFTER_DAYS over
        # a question about its Models column or its config ids — which is the
        # opposite of what either flag is for.
        if result.status in (ProbeStatus.PASS, ProbeStatus.STALE_MODELS, ProbeStatus.STALE_IDS):
            e.last_verified = today
            e.probe_failures = 0
            if e.provisional and (today - e.first_seen).days >= PROVISIONAL_PROMOTE_DAYS:
                e.provisional = False
            if result.status is not ProbeStatus.PASS:
                needs_attention.append((e, result))
            elif is_model_stale(e):
                needs_attention.append((e, ProbeResult(
                    ProbeStatus.STALE_MODELS,
                    "every listed family is marked superseded — refresh models to the "
                    "generation the free tier actually serves")))
        else:
            if result.status is ProbeStatus.FAIL:
                e.probe_failures += 1
            needs_attention.append((e, result))
    return needs_attention


async def _amain(registry_path: Path, failures_dir: Path, dry_run: bool = False) -> None:
    entries = load_registry(registry_path)
    sem = asyncio.Semaphore(CONCURRENCY)

    async def bounded(entry: Entry) -> ProbeResult:
        async with sem:
            return await probe_entry(client, entry)

    async with httpx.AsyncClient(headers=UA) as client:
        outcomes = await asyncio.gather(*(bounded(e) for e in entries))
    results = {e.id: r for e, r in zip(entries, outcomes)}
    flagged = apply_results(entries, results, date.today())
    if dry_run:
        # Verification dates are earned in CI, where the probes run from a known
        # address. A local check is for reading, not for recording.
        print("dry run: registry left untouched")
    else:
        save_registry(registry_path, entries)
        # After the save, and against the history rather than against the
        # entries as they were loaded: an entry archived by staleness alone
        # changes no field of the registry, and an entry added by hand since the
        # last run changed none of them during this one.
        recorded = record_changes(registry_path, registry_path.parent / "history.jsonl",
                                  date.today(), datetime.now(timezone.utc))
        for ev in recorded:
            print(f"history: {ev.event.value} {ev.id}")
    failures_dir.mkdir(parents=True, exist_ok=True)
    payload = [
        {"id": e.id, "status": r.status.value, "detail": r.detail}
        for e, r in flagged
    ]
    (failures_dir / "failures.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"probed {len(entries)} entries, {len(flagged)} need attention")
    # failures.json never leaves the runner, so the count alone was the whole
    # public account of a probe that fails from CI and passes from a laptop —
    # the one class of failure that cannot be reproduced locally.
    for row in payload:
        print(f"  {row['id']}: {row['status']} — {row['detail'] or 'no detail'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--failures", type=Path, default=Path("failures"))
    parser.add_argument("--dry-run", action="store_true",
                        help="probe everything and report, but write no verification dates")
    args = parser.parse_args()
    asyncio.run(_amain(args.registry, args.failures, args.dry_run))
