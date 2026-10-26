"""What the hand-written files say about the code and the data, held to them.

The pages are generated and state every rule from the constant that applies
it; CONTRIBUTING.md, the site's config, the social preview's source and
browse.html are written by hand and cannot. So each sentence that states a figure the code applies is
listed here with the constant it states, how often the files in SCHEDULED say
the list is checked is held to models.PROBE_WEEKDAYS (and so is the workflow's
cron), and `freetier-check` refuses the sentence — or the constant — the day
the two part. A claim whose sentence was reworded is reported too, since a
claim that matches nothing checks nothing.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, get_args

import yaml

from .announce import MAX_AGE_DAYS, POSTS_PER_RUN
from .bars import BAR_DAYS
from .gate import EARNED
from .history import EventType
from .layout import MAP, Kind
from .models import ApiInfo, Category, ClientLane, FreeAccess, ModelBinding, OPENCODE_OUTPUT_FIELD, OPENCODE_LEGACY_OUTPUT_FIELD, Probe, SessionEligibility
from .page_dates import MODIFIED
from .models import (ANCHOR_PHRASE_WORDS, ARCHIVE_AFTER_DAYS, ARCHIVE_AFTER_FAILURES,
                     CODEX_LITELLM_PROFILE, NOTICE_HOLD_DAYS,
                     PROBE_WEEKDAYS, SOURCE_RECHECK_DAYS, TIMES_A_WEEK, WATCH_RECHECK_DAYS,
                     load_registry, probe_frequency)
from .prober import ROUTE_GONE, KEYLESS_IDS_TRIED, PROVISIONAL_PROMOTE_DAYS, UA
from .quotes import MIN_WORDS
from .render import (CATEGORY_TITLES, CODEX_SINCE, LITELLM_BRIDGE_SINCE, MODEL_PAGE_ROWS,
                     PAGES_URL, QUICKSTART_USER_AGENT, README_MODELS, README_PICKS,
                     README_STARTERS, README_STRONG, _site_client_configs)
from .tiers import FRONTIER_WITHIN, STRONG_WITHIN
from .validate import PROSE_LIMITS
# The render's own words for a figure (see words.py).
from .words import number as _word, ordinal as _ordinal, series as _series, weeks as _weeks
from .borders import SHARED
from .countries import country_name
from .quotas import UNKNOWN_RECHECK_DAYS, UsageQuota
from .quality import (CRITERIA, ELIGIBILITY_FIELDS, ELIGIBILITY_MAX_AGE_DAYS,
                      CONFLICT_STATES, WITHDRAWAL_VERDICTS)

__all__ = ["Claim", "CLAIMS", "SCHEDULED", "check_claims"]

@dataclass(frozen=True)
class Claim:
    """A sentence in a hand-written file, found by `pattern`, whose groups — or
    what `read` takes out of the match — state the values `truth` returns."""
    file: str
    pattern: str
    truth: Callable[[Path], tuple[str, ...]]
    source: str
    read: Callable[[re.Match], tuple[str, ...]] = re.Match.groups


def _no_row_sets(field: str) -> Callable[[Path], tuple[str, ...]]:
    """The truth of "No row sets the field today": "No" while no row sets
    `field`, else the ids of the rows that do."""
    def truth(root: Path) -> tuple[str, ...]:
        rows = [e.id for e in load_registry(root / "registry.yaml")
                if e.api and getattr(e.api, field)]
        return ("No",) if not rows else (", ".join(rows),)
    return truth


def _keys(found: re.Match) -> tuple[str, ...]:
    """The keys of a JavaScript object literal, in the order written."""
    return tuple(re.findall(r'"([a-z-]+)":', found.group(1)))


def _ordered_keys(found: re.Match) -> tuple[str, ...]:
    try:
        pairs = json.loads('{' + found.group(1) + '}', object_pairs_hook=list)
    except json.JSONDecodeError:
        return ('invalid category order',)
    return tuple(f'{key}:{value}' for key, value in pairs)


def _ci_pythons(root: Path) -> tuple[str, str]:
    """The oldest and the newest Python CI runs the suite on."""
    ci = yaml.safe_load((root / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    pythons = sorted(ci["jobs"]["test"]["strategy"]["matrix"]["python"],
                     key=lambda v: tuple(map(int, v.split("."))))
    return pythons[0], pythons[-1]


def _cron_day(workflow: str) -> Callable[[Path], tuple[str, ...]]:
    """The weekday a workflow's one cron line names."""
    def truth(root: Path) -> tuple[str, ...]:
        data = yaml.safe_load((root / workflow).read_text(encoding="utf-8"))
        trigger = data.get("on", data.get(True)) or {}
        days = {str(entry["cron"]).split()[4] for entry in trigger.get("schedule") or []}
        names = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
        return tuple(names[int(d) % 7] if d.isdigit() else d for d in sorted(days))
    return truth


def _page_recovery_limits() -> tuple[str, ...]:
    from .page_reader import RECOVERY_SECONDS, RECOVERY_REDIRECTS, RECOVERY_BYTES
    return tuple(str(v) for v in (RECOVERY_SECONDS, RECOVERY_REDIRECTS, RECOVERY_BYTES // (1024 * 1024)))


def _site_url() -> tuple[str, str]:
    """PAGES_URL as Jekyll's `url` and `baseurl`."""
    host, base = PAGES_URL.rsplit("/", 1)
    return host, "/" + base


def _review_push_base(root: Path) -> tuple[str, ...]:
    from .review import PUSH_BASE_FLAG
    return (PUSH_BASE_FLAG,)


def _review_producer_workflows(root: Path) -> tuple[str, ...]:
    from .review import PRODUCER_WORKFLOWS
    return tuple(PRODUCER_WORKFLOWS)


def _page_catalog_views(root: Path) -> tuple[str, ...]:
    from .models import _row_payload
    rows = [e for e in load_registry(root / "registry.yaml") if e.page_catalog]
    if rows and all(e.models == e.page_catalog.published()
                    and e.newcomers == e.page_catalog.waiting()
                    and not {"models", "newcomers"} & _row_payload(e).keys() for e in rows):
        return ("models", "newcomers")
    return ("invalid canonical catalog",)


CLAIMS: tuple[Claim, ...] = (
    Claim("CONTRIBUTING.md", r'history ends in `(removed)` appends `(restored)`',
          lambda root: (EventType.REMOVED.value, EventType.RESTORED.value),
          "history.diff_state and record_changes; legacy return preserves arrival and append-only prefix in tests/test_history.py"),
    Claim("CONTRIBUTING.md", r'`payment_kind` accepts `(top-up)`, `(card verification)`, or `(charge)`',
          lambda root: get_args(FreeAccess.model_fields['payment_kind'].annotation),
          "models.FreeAccess; shared payment inheritance and rendering in tests/test_free_access.py"),
    Claim("CONTRIBUTING.md", r"Every page under both carries `(last_modified_at)`",
          lambda root: (MODIFIED,),
          "page_dates.PageDates.stamp; tests/test_page_dates.py checks substantive changes, stable repeats, archives and legacy Git provenance"),
    Claim("CONTRIBUTING.md", r"`(agent-cli)` contains coding tools with ongoing Free usage",
          lambda root: (Category.AGENT_CLI.value,),
          "models.Category; category is canonical registry data; review every advertised free mode on the current primary plan and usage sources"),
    Claim("CONTRIBUTING.md", r"`(trial)` contains offers funded only\s+by a finite introductory grant or trial",
          lambda root: (Category.TRIAL.value,),
          "models.Category; recurring Free plans are distinct from optional paid-plan trials and finite signup grants"),
    Claim("CONTRIBUTING.md", r"Set `read: (catalog)` to bind identity text to that exact ID",
          lambda root: tuple(value for value in ModelBinding.model_fields['read'].annotation.__args__ if value == 'catalog'),
          "quotes.model_binding_changes; exact-ID identity, other-row quote and duplicate-row HTTP controls in tests/test_model_bindings.py"),
    Claim("CONTRIBUTING.md", r"`api\.(model_bindings)\[ID\]` or `client_lane\.(model_bindings)\[ID\]`",
          lambda root: tuple("model_bindings" for kind in (ApiInfo, ClientLane) if "model_bindings" in kind.model_fields),
          "models.entry_id_family; tests/test_model_bindings.py covers HTTP identity drift, distinct gateways, model pages and expiry"),
    Claim("CONTRIBUTING.md", r"last-offer checks in `(historical_checks)`",
          lambda root: ("historical_checks",),
          "review.sources; same changed HTTP quota fails an active row and remains a visible historical mismatch for a delisted row"),
    Claim("CONTRIBUTING.md", r"`probe\.(model_prices)` binds",
          lambda root: tuple(k for k in ("model_prices",) if k in Probe.model_fields),
          "models.ModelPriceTable and prober.unevidenced_families; paid-input/free-output HTTP-boundary regression"),
    Claim("CONTRIBUTING.md", r"`probe\.(model_plan)` binds",
          lambda root: tuple(k for k in ("model_plan",) if k in Probe.model_fields),
          "models.ModelPlanTable and prober._table_models; Free/Enterprise, missing/duplicate table and duplicate-model HTTP controls"),
    Claim("CONTRIBUTING.md", r"An OpenCode request budget can instead be chosen in `api\.(opencode_output_tokens)\[ID\]`",
          lambda root: tuple(k for k in ("opencode_output_tokens",) if k in ApiInfo.model_fields),
          "models.ApiInfo; client request budgets, distinct from model_limits, in tests/test_models.py"),
    Claim("CONTRIBUTING.md", r"It writes `(max_completion_tokens)` into that model.s request options",
          lambda root: (OPENCODE_OUTPUT_FIELD,),
          "render.build_opencode_config; conformance.check_opencode_output_budget and the real freetier-review client recorder"),
    Claim("CONTRIBUTING.md", r"and gives `(max_tokens)` the same budget for older clients",
          lambda root: (OPENCODE_LEGACY_OUTPUT_FIELD,),
          "render.build_opencode_config; OpenCode1.19.0 real HTTP/request-budget and completed native session control"),
    Claim("CONTRIBUTING.md", r'these `criteria`: `(existing_behavior)`, `(reuse)`,\s+`(copy)`, `(user_path)`, `(regression)`, `(diff)`, `(eligibility)`',
          lambda root: CRITERIA,
          "quality.CRITERIA; judgment and normal pre-push regressions in tests/test_quality.py"),
    Claim("CONTRIBUTING.md", r'current `(plan)`, `(payment)`,\s+`(regions)`, `(limits)`, `(deadline)`, and `(conflicts)`',
          lambda root: ELIGIBILITY_FIELDS, "quality.validate_judgment; tests/test_quality.py"),
    Claim("CONTRIBUTING.md", r'records older than\s+(one) day cannot authorize a new push',
          lambda root: (_word(ELIGIBILITY_MAX_AGE_DAYS),), "quality.fresh_eligibility; tests/test_quality.py"),
    Claim("CONTRIBUTING.md", r'`conflict_status` as `(none)`, `(resolved)`,\s+or `(unresolved)`',
          lambda root: CONFLICT_STATES,
          "quality.validate_judgment; unresolved withdrawal and ordinary disclosure controls in tests/test_quality.py"),
    Claim("CONTRIBUTING.md", r'Each mode must be\s+`(ended)` or `(ineligible)`',
          lambda root: WITHDRAWAL_VERDICTS,
          "quality.validate_judgment; available recurring mode blocks archival in tests/test_quality.py"),
    Claim("CONTRIBUTING.md", r'inputs: `(provider_ids)` selects',
          lambda root: tuple(k for k in (yaml.safe_load((root / '.github/workflows/update.yml').read_text()).get('on')
              or yaml.safe_load((root / '.github/workflows/update.yml').read_text()).get(True))['workflow_dispatch']['inputs']
              if k == 'provider_ids'),
          "update.yml; exact workflow arguments, injection controls and isolated HTTP verification in tests/test_targeted_verification.py and tests/test_prober.py"),
    Claim("CONTRIBUTING.md", r'an exact model/plan `(table)` binding, the free cell.s `(value)`, and a `(plan_price)`',
          lambda root: tuple(field for field in ('table', 'value', 'plan_price')
                             if field in SessionEligibility.model_fields),
          "models.SessionEligibility and scoped HTTP/paid-plan regressions in tests/test_eligibility.py"),
    Claim("browse.html", r'function noAccount\(e\) \{ return e\.(no_account) === true; \}',
          lambda root: ('no_account',),
          "render.build_index publishes render.needs_no_account; actual browser parity in tests/test_evidence_contracts.py"),
    Claim("browse.html", r'dataUseWords = data\.(data_use_words);',
          lambda root: ('data_use_words',),
          "render.build_index publishes DATA_USE_WORDS; reviewed-copy propagation in tests/test_browse.py"),
    Claim("browse.html", r'(?s)<select id="client"[^>]*>(.*?)</select>',
          lambda root: tuple(_site_client_configs([], date.min)),
          "render._site_client_configs; exact eligibility, unsupported native-only lanes and selected-client controls in tests/test_browse.py",
          read=lambda match: tuple(re.findall(r'<option value="([^"]+)"', match[1]))),
    Claim("browse.html", r'configClients = data\.(client_configs) \|\| \{\};',
          lambda root: ('client_configs',),
          "render.build_index derives membership from generated writers; tests/test_site.py and tests/test_browse.py"),
    Claim("browse.html", r'return lane \? lane\.(model_ids) \|\| \[\] : \[\];',
          lambda root: tuple(field for field in ('model_ids',)
                             if all(field in kind.model_fields for kind in (ApiInfo, ClientLane))),
          "models.ApiInfo and ClientLane; current versus ignored exact-ID regression in tests/test_browse.py"),
    Claim("browse.html", r'e\.access_labels\.(ids) && e\.access_labels\.ids\[id\]',
          lambda root: ('ids',),
          "render._index_access_labels uses models.id_access/access_words; full deadline and inherited-payment controls in tests/test_browse.py"),
    Claim("CONTRIBUTING.md", r"last-offer checks in `(historical_checks)`,\s+including source-read failures under `(sources)`",
          lambda root: ("historical_checks", "sources"),
          "review.sources; historical/shared/explicit HTTP-boundary controls in tests/test_review.py"),
    Claim("CONTRIBUTING.md", r"`quotas` stores `(amount)`, `(unit)`, `(period)` and `(scope)`",
          lambda root: tuple(field for field in ("amount", "unit", "period", "scope")
                             if field in UsageQuota.model_fields),
          "quotas.UsageQuota; HTTP-boundary and source-binding regressions in tests/test_quotas.py"),
    Claim("CONTRIBUTING.md", r"dated manual review after (\d+) days",
          lambda root: (str(UNKNOWN_RECHECK_DAYS),),
          "quotas.UNKNOWN_RECHECK_DAYS and quota_moved; expiry regression in tests/test_quotas.py"),
    Claim("CONTRIBUTING.md", r"probe requests a fresh review\s+after (\d+) days",
          lambda root: (str(UNKNOWN_RECHECK_DAYS),),
          "page_catalog.check_page_catalog and UNKNOWN_RECHECK_DAYS; Markdown HTTP-boundary expiry regression"),
    Claim("CONTRIBUTING.md", r"Read modes are `(page)`,\s+`(catalog)`, `(constant)`, `(table)`, and `(catalog-field)`",
          lambda root: get_args(UsageQuota.model_fields['read'].annotation),
          "quotas.UsageQuota and quota_changes; HTTP-boundary regressions in tests/test_quotas.py"),
    Claim("CONTRIBUTING.md", r"An unpublished `(amount)` or `(period)` stays null",
          lambda root: tuple(field for field in ('amount','period')
                             if type(None) in get_args(UsageQuota.model_fields[field].annotation)),
          "quotas.UsageQuota; nullable-window regression in tests/test_quotas.py"),
    Claim("CONTRIBUTING.md", r"`page_catalog` derives `(models)` and `(newcomers)`",
          _page_catalog_views, "models.PageCatalog, Entry and _row_payload; tests/test_page_catalog.py"),
    Claim("CONTRIBUTING.md", r"`prepare (--push-base) <commit>` records the commit immediately before the final",
          _review_push_base, "review.PUSH_BASE_FLAG and prepare; push-range regressions in tests/test_review.py"),
    Claim("CONTRIBUTING.md", r"For a bot (verification) or (expiry) commit, add `prepare --verification-run",
          _review_producer_workflows,
          "review.PRODUCER_WORKFLOWS and prepare; matching main-writer receipt regressions in tests/test_review.py"),
    Claim("CONTRIBUTING.md", r"and it\s+expires after (\d+) days, at which point the scout",
          lambda root: (str(WATCH_RECHECK_DAYS),), "models.WATCH_RECHECK_DAYS"),
    Claim("CONTRIBUTING.md", r"Those verdicts expire after (\d+)\s+days",
          lambda root: (str(SOURCE_RECHECK_DAYS),), "models.SOURCE_RECHECK_DAYS"),
    Claim("CONTRIBUTING.md",
          r"after (\w+) failed\s+probes in a row, or after (\d+) days without a passing probe",
          lambda root: (_word(ARCHIVE_AFTER_FAILURES), str(ARCHIVE_AFTER_DAYS)),
          "models.ARCHIVE_AFTER_FAILURES and ARCHIVE_AFTER_DAYS"),
    Claim("CONTRIBUTING.md",
          r"scores within (\d+) points of the top\s+of the index, counting current models only,"
          r"\s+`strong` within (\d+)",
          lambda root: (f"{FRONTIER_WITHIN:g}", f"{STRONG_WITHIN:g}"),
          "tiers.FRONTIER_WITHIN and STRONG_WITHIN"),
    Claim("CONTRIBUTING.md", r"vendor output in backticks, (\d+) characters\s+at most",
          lambda root: (str(PROSE_LIMITS["api.notice"]),), "validate.PROSE_LIMITS['api.notice']"),
    Claim("CONTRIBUTING.md", r"holds a refusal off the failure count for (\d+) days from `since`",
          lambda root: (str(NOTICE_HOLD_DAYS),), "models.NOTICE_HOLD_DAYS"),
    Claim("CONTRIBUTING.md", r"only events from the last (\d+) days, at most (\w+) per channel",
          lambda root: (str(MAX_AGE_DAYS), _word(POSTS_PER_RUN)),
          "announce.MAX_AGE_DAYS and POSTS_PER_RUN"),
    Claim("CONTRIBUTING.md",
          r"`freetier-check` holds `offering` to ([\d,]+) characters, `limits` to ([\d,]+) and"
          r"\s+`api.note` to ([\d,]+)",
          lambda root: tuple(f"{PROSE_LIMITS[f]:,}" for f in ("offering", "limits", "api.note")),
          "validate.PROSE_LIMITS"),
    Claim("CONTRIBUTING.md", r"The first (\w+) no-card agents are also the top of the README",
          lambda root: (_word(README_STARTERS),), "render.README_STARTERS"),
    Claim("CONTRIBUTING.md", r"read (\w+) names deep per section",
          lambda root: (_word(README_PICKS),), "render.README_PICKS"),
    Claim("CONTRIBUTING.md", r"An undated model on a rotating lane waits (\w+ weeks|a week)",
          lambda root: (_weeks(BAR_DAYS),), "bars.BAR_DAYS"),
    Claim("CONTRIBUTING.md", r"and joins `models\[\]` (\w+ weeks|a week) later",
          lambda root: (_weeks(BAR_DAYS),), "bars.BAR_DAYS"),
    Claim("CONTRIBUTING.md", r"`offering`, the first (\w+)\s+model families and the date",
          lambda root: (_word(README_MODELS),), "render.README_MODELS"),
    Claim("CONTRIBUTING.md", r"every family past the (\w+), one click from their count",
          lambda root: (_ordinal(README_MODELS),), "render.README_MODELS"),
    Claim("CONTRIBUTING.md", r"the most widely served first and at most (\w+);",
          lambda root: (_word(README_STRONG),), "render.README_STRONG"),
    Claim("CONTRIBUTING.md", r"a page for every model (\w+) rows or more serve",
          lambda root: (_word(MODEL_PAGE_ROWS),), "render.MODEL_PAGE_ROWS"),
    Claim("CONTRIBUTING.md", r"sends the check on to the next id, up to\s+(\w+),",
          lambda root: (_word(KEYLESS_IDS_TRIED),), "prober.KEYLESS_IDS_TRIED"),
    Claim("CONTRIBUTING.md", r"recovery, with a (\d+)-second budget,\s+up to (\d+) redirects and an (\d+) MiB body limit",
          lambda root: _page_recovery_limits(), "page_reader recovery limits"),
    Claim("CONTRIBUTING.md", r"always calls under this\s+project's own `([^`]+)`",
          lambda root: (UA["User-Agent"],), "prober.UA"),
    Claim("CONTRIBUTING.md", r"sends `User-Agent: ([^`]+)`",
          lambda root: (QUICKSTART_USER_AGENT,), "render.QUICKSTART_USER_AGENT"),
    Claim("CONTRIBUTING.md", r"\| a sentence of (\d+)\+ words quoted from the page \|",
          lambda root: (str(ANCHOR_PHRASE_WORDS),), "models.ANCHOR_PHRASE_WORDS"),
    Claim("CONTRIBUTING.md", r"reports every quote of (\w+) words or more",
          lambda root: (_word(MIN_WORDS),), "quotes.MIN_WORDS"),
    Claim("CONTRIBUTING.md", r"is a route, a (\d+), (\d+) or (\d+)\s+is reported",
          lambda root: tuple(str(c) for c in ROUTE_GONE), "prober.ROUTE_GONE"),
    Claim("CONTRIBUTING.md", r"beside the (\w+) configs it describes",
          lambda root: (_word(len([n for n in MAP if n.kind is Kind.GENERATED
                                   and n.path.startswith("configs/")
                                   and n.path != "configs/README.md"])),),
          "the configs layout.MAP marks generated"),
    Claim("CONTRIBUTING.md",
          r"a hand edit of `(\w+)`,\s+`(\w+)`, `(\w+)` or `(\w+)`, which only the run's probe",
          lambda root: tuple(sorted(EARNED)), "gate.EARNED",
          read=lambda found: tuple(sorted(found.groups()))),
    Claim("CONTRIBUTING.md", r"Anthropic check's way: a (\d+), (\d+) or (\d+) is",
          lambda root: tuple(str(c) for c in ROUTE_GONE), "prober.ROUTE_GONE"),
    Claim("CONTRIBUTING.md", r"cannot take is `(\w+)`, the LiteLLM profile's name",
          lambda root: (CODEX_LITELLM_PROFILE,), "models.CODEX_LITELLM_PROFILE"),
    Claim("CONTRIBUTING.md", r"the header asks for\s+LiteLLM (\d+\.\d+) or later",
          lambda root: (LITELLM_BRIDGE_SINCE,), "render.LITELLM_BRIDGE_SINCE"),
    Claim("CONTRIBUTING.md", r"since\s+Codex CLI (\d+\.\d+)",
          lambda root: (CODEX_SINCE,), "render.CODEX_SINCE"),
    Claim("CONTRIBUTING.md", r"Python (\d+\.\d+) to (\d+\.\d+), httpx",
          _ci_pythons, "the oldest and the newest Python in .github/workflows/ci.yml"),
    Claim("CONTRIBUTING.md", r"`conformance` workflow runs them every (\w+)",
          _cron_day(".github/workflows/conformance.yml"),
          ".github/workflows/conformance.yml's cron"),
    Claim("CONTRIBUTING.md", r"(No) row sets\s+the field today",
          _no_row_sets("session_header"), "the rows that set api.session_header"),
    Claim("CONTRIBUTING.md", r"countries under comprehensive US embargo — ([^—]+?)\s+—",
          lambda root: (_series(sorted(country_name(c) for c in SHARED)),), "borders.SHARED",
          read=lambda found: (" ".join(found.group(1).split()),)),
    Claim("browse.html", r"listed for less than (\w+ weeks|a week)",
          lambda root: (_weeks(PROVISIONAL_PROMOTE_DAYS),),
          "prober.PROVISIONAL_PROMOTE_DAYS"),
    Claim("browse.html", r'<link rel="canonical" href="([^"]+)/browse\.html">',
          lambda root: (PAGES_URL,), "render.PAGES_URL"),
    Claim("browse.html", r"var ORDER = \{([^}]*)\}",
          lambda root: tuple(f'{c.value}:{index}' for index, c in enumerate(CATEGORY_TITLES)),
          "render.CATEGORY_TITLES order; divergence controls in tests/test_claims.py",
          read=_ordered_keys),
    Claim("browse.html", r"var LABEL = \{([^}]*)\}",
          lambda root: tuple(c.value for c in CATEGORY_TITLES), "render.CATEGORY_TITLES",
          read=_keys),
    Claim("_config.yml", r"(?m)^url: (\S+)\nbaseurl: (\S+)$",
          lambda root: _site_url(), "render.PAGES_URL"),
)


# The hand-written files that say how often the list is checked.
SCHEDULED = ("CONTRIBUTING.md", "_config.yml", "browse.html", "assets/social-preview.svg")
_FREQUENCY = re.compile(r"\b(?:" + "|".join(map(re.escape, TIMES_A_WEEK.values())) + r")\b")


def _line(text: str, at: int) -> int:
    return text.count("\n", 0, at) + 1


def _cron_weekdays(root: Path) -> tuple[int, ...] | None:
    workflow = yaml.safe_load((root / ".github/workflows/update.yml").read_text(encoding="utf-8"))
    # PyYAML reads a bare `on:` as the boolean true.
    trigger = workflow.get("on", workflow.get(True)) or {}
    days: set[int] = set()
    for entry in trigger.get("schedule") or []:
        field = str(entry["cron"]).split()[4]
        if field == "*":
            days |= set(range(7))
        else:
            days |= {int(d) % 7 for d in field.split(",")}
    return tuple(sorted(days)) or None


def check_claims(root: Path, claims: tuple[Claim, ...] = CLAIMS,
                 scheduled: tuple[str, ...] = SCHEDULED) -> list[str]:
    problems = []
    for claim in claims:
        text = (root / claim.file).read_text(encoding="utf-8")
        found = re.search(claim.pattern, text)
        if found is None:
            problems.append(f"{claim.file} no longer has the sentence stating {claim.source} "
                            f"(claims.CLAIMS: `{claim.pattern}`) — point the claim at the sentence "
                            "that states it now")
            continue
        truth = claim.truth(root)
        if claim.read(found) != truth:
            said = " ".join(found.group(0).split())
            problems.append(f"{claim.file}:{_line(text, found.start())} says `{said}` and "
                            f"{claim.source} says {', '.join(truth)} — change the sentence or the "
                            "constant, never one of them alone")
    expected = probe_frequency(PROBE_WEEKDAYS)
    for name in scheduled:
        text = (root / name).read_text(encoding="utf-8")
        for m in _FREQUENCY.finditer(text):
            if m.group(0) != expected:
                problems.append(f"{name}:{_line(text, m.start())} says `{m.group(0)}` and the "
                                f"scheduled run probes {expected} (models.PROBE_WEEKDAYS)")
    cron = _cron_weekdays(root)
    if cron is not None and set(cron) != set(PROBE_WEEKDAYS):
        problems.append(
            f".github/workflows/update.yml runs on weekdays {','.join(map(str, cron))} and "
            f"models.PROBE_WEEKDAYS says {','.join(map(str, PROBE_WEEKDAYS))} — the pages would "
            f"say {expected}")
    return problems
