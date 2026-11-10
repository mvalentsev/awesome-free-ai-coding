"""What the hand-written files say about the code and the data, held to them.

The pages state every rule from its constant. CONTRIBUTING.md also generates
registered rule values; other handwritten assertions remain independently
checked. Each sentence that states a figure the code applies is
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
from .models import ApiInfo, ArchiveReview, Category, ClientLane, FreeAccess, RemainingFree, ModelBinding, ModelFamily, ModelLimits, ModelTableExclusion, Newcomer, OPENCODE_OUTPUT_FIELD, OPENCODE_LEGACY_OUTPUT_FIELD, Probe, SessionEligibility, utc_today
from .page_dates import MODIFIED
from .models import (ANCHOR_PHRASE_WORDS, ARCHIVE_AFTER_DAYS, ARCHIVE_AFTER_FAILURES,
                     CODEX_LITELLM_PROFILE, NOTICE_HOLD_DAYS,
                     PROBE_WEEKDAYS, SOURCE_RECHECK_DAYS, TIMES_A_WEEK, WATCH_RECHECK_DAYS,
                     load_registry, probe_frequency)
from .prober import ROUTE_GONE, KEYLESS_IDS_TRIED, PROVISIONAL_PROMOTE_DAYS, ProbeStatus, UA
from .quotes import MIN_WORDS
from .render import (CATEGORY_TITLES, CODEX_SINCE, LITELLM_BRIDGE_SINCE, MODEL_PAGE_ROWS, MODEL_ORDER_FIELDS, MODEL_SORT,
                     PAGES_URL, QUICKSTART_USER_AGENT, README_MODELS, README_PICKS,
                     README_STARTERS, README_COMPARISON, _site_client_configs)
from .tiers import FRONTIER_WITHIN, INDEX_VERSION, STRONG_WITHIN
from .pictures import _chart_ticks, _style
from .validate import PROSE_LIMITS
# The render's own words for a figure (see words.py).
from .words import number as _word, ordinal as _ordinal, series as _series, weeks as _weeks
from .borders import SHARED
from .countries import country_name
from .quotas import UNKNOWN_RECHECK_DAYS, UsageQuota
from .quality import (CRITERIA, ELIGIBILITY_FIELDS, ELIGIBILITY_MAX_AGE_DAYS,
                      CONFLICT_STATES, WITHDRAWAL_VERDICTS)
from .review_leads import LEAD_VERDICTS

__all__ = ["Claim", "CLAIMS", "SCHEDULED", "check_claims", "render_claims"]

@dataclass(frozen=True)
class Claim:
    """A sentence in a hand-written file, found by `pattern`, whose groups — or
    what `read` takes out of the match — state the values `truth` returns."""
    file: str
    pattern: str
    truth: Callable[[Path], tuple[str, ...]]
    source: str
    read: Callable[[re.Match], tuple[str, ...]] = re.Match.groups
    generated: bool = False


def _no_row_sets(field: str) -> Callable[[Path], tuple[str, ...]]:
    """The truth of "No row sets the field today": "No" while no row sets
    `field`, else the ids of the rows that do."""
    def truth(root: Path) -> tuple[str, ...]:
        rows = [e.id for e in load_registry(root / "registry.yaml")
                if e.api and getattr(e.api, field)]
        return ("No",) if not rows else (", ".join(rows),)
    return truth


def _browser_coverage_purposes(root: Path) -> tuple[str, ...]:
    from .review_browser import COVERAGE_PURPOSES
    return tuple(purpose.rsplit('-', 1)[-1] for purpose in COVERAGE_PURPOSES)


def _internal_browser_policy(root: Path) -> tuple[str, ...]:
    from .review_browser import browser_scope
    internal = browser_scope(['CONTRIBUTING.md', 'src/freetier_radar/prober.py'])
    layout = browser_scope(['_layouts/default.html'])
    return ('no browser cases',) if internal == (False, False) and layout == (True, True) else ()


def _pending_quota_policy(root: Path) -> tuple[str, ...]:
    from .models import Entry
    row = Entry.model_validate({
        'id': 'claim', 'name': 'Claim', 'category': 'agent-cli',
        'url': 'https://vendor.example', 'offering': 'Free models', 'free_part': 'models',
        'first_seen': '2026-07-19', 'last_verified': '2026-07-19',
        'newcomers': [{'family': 'next-model', 'on': '2026-07-19', 'source': 'https://vendor.example/models'}],
        'quotas': [{'amount': 100, 'unit': 'requests', 'period': 'day', 'scope': 'account-model',
                    'families': ['next-model'], 'source': 'https://vendor.example/models',
                    'quote': 'Next Model allows 100 requests per day.'}],
        'probe': {'type': 'page-keywords', 'endpoint': 'https://vendor.example/models',
                  'keywords': ['Next Model allows 100 requests per day.']}})
    return ('pending',) if not row.models and row.quotas[0].families == [row.newcomers[0].family] else ()


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


def _archive_review_limits(root: Path) -> tuple[str, ...]:
    from .archive_review import ARCHIVE_RECHECK_DAYS, ARCHIVE_REVIEW_SECONDS
    return (str(ARCHIVE_RECHECK_DAYS), str(ARCHIVE_REVIEW_SECONDS))


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


def _bot_conformance_dispatch(root: Path) -> tuple[str, ...]:
    for filename, job, condition in (
            ('update.yml', 'update', "!inputs.dry_run && steps.commit.outputs.pushed == 'true'"),
            ('expire.yml', 'expire', "steps.publish.outputs.changed == 'true'")):
        data = yaml.safe_load((root / '.github/workflows' / filename).read_text())
        steps = [step for step in data['jobs'][job]['steps']
                 if 'freetier-conformance dispatch' in step.get('run', '')]
        if (len(steps) != 1 or condition not in steps[0].get('if', '')
                or steps[0].get('continue-on-error')
                or steps[0].get('env', {}).get('GH_TOKEN') != '${{ github.token }}'
                or data.get('permissions', {}).get('actions') != 'write'):
            return ()
    data = yaml.safe_load((root / '.github/workflows/conformance.yml').read_text())
    trigger = data.get('on', data.get(True))
    if 'expected_sha' not in (trigger.get('workflow_dispatch') or {}).get('inputs', {}):
        return ()
    guards = [step for step in data['jobs']['conformance']['steps']
              if step.get('name') == 'Require the requested commit']
    if (len(guards) != 1 or guards[0].get('env') != {
            'EXPECTED_SHA': '${{ inputs.expected_sha }}', 'ACTUAL_SHA': '${{ github.sha }}'}):
        return ()
    return ('verification', 'expiry')


def _unpriced_catalog_tier(root: Path) -> tuple[str, ...]:
    from .prober import _is_free
    if (_is_free({'tier': 'free'})
            and not _is_free({'tier': 'free', 'pricing': {'prompt': 1, 'completion': 1}})
            and not _is_free({'tier': 'free', 'pricing': {'prompt': 'unknown'}})
            and not _is_free({'tier': 'paid'})):
        return ('free',)
    return ()


def _page_catalog_views(root: Path) -> tuple[str, ...]:
    from .models import _row_payload
    rows = [e for e in load_registry(root / "registry.yaml") if e.page_catalog]
    if rows and all(e.models == e.page_catalog.published()
                    and e.newcomers == e.page_catalog.waiting()
                    and not {"models", "newcomers"} & _row_payload(e).keys() for e in rows):
        return ("models", "newcomers")
    return ("invalid canonical catalog",)


def _catalog_arrival_spelling(root: Path) -> tuple[str, ...]:
    import httpx
    from .models import Entry
    from .prober import unlisted_free_ids
    entry = Entry.model_validate({
        'id': 'claim', 'name': 'Claim', 'category': 'api-free-tier',
        'url': 'https://vendor.example', 'source_urls': ['https://vendor.example/models'],
        'offering': 'Free coding models', 'first_seen': '2026-07-19', 'last_verified': '2026-07-19',
        'api': {'base_url': 'https://vendor.example/v1', 'model_ids': ['known:free']},
        'probe': {'type': 'api-models', 'endpoint': 'https://vendor.example/models',
                  'free_marker': ':free', 'require_zero_price': True}})
    response = httpx.Response(200, json={'data': [
        {'id': 'new-free', 'isFree': True, 'pricing': {'input': 0, 'output': 0}},
        {'id': 'paid', 'isFree': False, 'pricing': {'input': 0, 'output': 0}}]})
    return ('probe.free_marker',) if unlisted_free_ids(response, entry) == ['new-free'] else ()


def _catalog_chat_operations(root: Path) -> tuple[str, ...]:
    import httpx
    from .models import Entry
    from .prober import dead_model_ids
    entry = Entry.model_validate({
        'id': 'claim', 'name': 'Claim', 'category': 'trial',
        'url': 'https://vendor.example', 'offering': 'A shared token balance',
        'first_seen': '2026-07-19', 'last_verified': '2026-07-19', 'free_part': 'sum',
        'api': {'base_url': 'https://vendor.example/v1', 'model_ids': ['candidate']},
        'probe': {'type': 'page-keywords', 'endpoint': 'https://vendor.example/pricing',
                  'keywords': ['100 million free tokens']}})
    def notes(paths):
        row = {'id': 'candidate', **({'supported_endpoints': paths} if paths is not None else {})}
        return dead_model_ids(httpx.Response(200, json={'data': [row]}), entry)
    return ('Chat Completions',) if (notes(['decisions']) and not notes(['chat.completions'])
                                     and not notes(None)) else ()


def _page_family_text(root: Path) -> tuple[str, ...]:
    import httpx
    from .models import Entry
    from .prober import unevidenced_families
    entry = Entry.model_validate({
        'id': 'claim', 'name': 'Claim', 'category': 'api-free-tier',
        'url': 'https://vendor.example', 'offering': 'Free models',
        'first_seen': '2026-07-19', 'last_verified': '2026-07-19',
        'models': [{'family': 'science-flash'}],
        'probe': {'type': 'page-keywords', 'endpoint': 'https://vendor.example/pricing',
                  'keywords': ['100 free requests per day']}})
    bodies = ['<script>science-flash</script>', '<template>science-flash</template>',
              '<!-- science-flash -->', '<p>science-flash</p>']
    missing = [bool(unevidenced_families(httpx.Response(200, text=b), entry)) for b in bodies]
    return ('inert templates', 'machinery_keywords', 'comments') if missing == [True, True, True, False] else ()


def _unscored_tier_policy(root: Path) -> tuple[str, ...]:
    from .models import Entry
    from .tiers import Scored, review
    entry = Entry.model_validate({
        'id': 'claim', 'name': 'Claim', 'category': 'api-free-tier',
        'url': 'https://vendor.example', 'offering': 'Free models',
        'first_seen': '2026-07-19', 'last_verified': '2026-07-19',
        'models': [{'family': family, 'aa_model': family, 'tier': 'strong'}
                   for family in ('known', 'missing')],
        'probe': {'type': 'page-keywords', 'endpoint': 'https://vendor.example/pricing',
                  'keywords': ['100 free requests per day']}})
    _, marks = review([entry], {
        'top': Scored('top', 'Top', 50, False, False),
        'known': Scored('known', 'Known', None, False, False)})
    known, missing = (next(m for m in marks if m.family == f) for f in ('known', 'missing'))
    return ('clears' if known.moved and known.measured is None else 'invalid',
            'preserves' if missing.unknown and not missing.moved else 'invalid')


def _automatic_aa_hold(root: Path) -> tuple[str, ...]:
    from .models import Entry
    from .tiers import Scored, review, unmeasured
    def row(held=False, explicit=False):
        return Entry.model_validate({
            'id': 'claim', 'name': 'Claim', 'category': 'api-free-tier',
            'url': 'https://vendor.example', 'offering': 'Free models',
            'first_seen': '2026-11-03', 'last_verified': '2026-11-03',
            'models': [{'family': 'reviewed-model', 'aa_auto': not held,
                        **({'aa_model': 'reviewed-model'} if explicit else {})}],
            'probe': {'type': 'page-keywords', 'endpoint': 'https://vendor.example/pricing',
                      'keywords': ['100 free requests per day']}})
    board = {'top': Scored('top', 'Top', 50, False, False),
             'reviewed-model': Scored('reviewed-model', 'Model (Xhigh)', 40, False, False)}
    ordinary = unmeasured([row()], board)
    held = unmeasured([row(held=True), row()], board)
    _, explicit = review([row(held=True, explicit=True)], board)
    return ('hold' if ordinary and not held else 'invalid',
            'measured' if explicit[0].score == board['reviewed-model'] else 'invalid')


def _checkpoint_review_policy(root: Path) -> tuple[str, ...]:
    from .models import Entry
    from .tiers import Scored, checkpoint_reviews
    row = Entry.model_validate({
        'id': 'claim', 'name': 'Claim', 'category': 'api-free-tier',
        'url': 'https://vendor.example', 'offering': 'Free models',
        'provisional': False,
        'first_seen': '2026-07-19', 'last_verified': utc_today(),
        'models': [{'family': 'reviewed-model', 'aa_model': 'reviewed-model'}],
        'probe': {'type': 'page-keywords', 'endpoint': 'https://vendor.example/pricing',
                  'keywords': ['100 free requests per day']}})
    findings = checkpoint_reviews([row], {
        'top': Scored('top', 'Top', 50, False, False),
        'reviewed-model': Scored('reviewed-model', 'Old model', None, True, False),
        'reviewed-model-1017': Scored('reviewed-model-1017', 'Dated model', 40, False, False)})
    return ('report' if findings and findings[0][1][0].slug == 'reviewed-model-1017' else 'invalid',
            'not made' if row.models[0].aa_model == 'reviewed-model' else 'invalid')


def _review_link_formats(root: Path) -> tuple[str, ...]:
    from .review_leads import collect_leads
    source = 'https://vendor.example/pricing'
    examples = {
        'HTML': '<a href="/library">Model comparisons directory</a>',
        'inline Markdown': '[Model comparisons directory](/library)',
        'reference Markdown': '[Model comparisons directory][models]\n\n[models]: /library',
    }
    return tuple(name for name, body in examples.items()
                 if [r['url'] for r in collect_leads({source: body}, {'vendor.example'})]
                 == ['https://vendor.example/library'])


def _source_detail_policy(root: Path) -> tuple[str, ...]:
    import ast
    tree = ast.parse((root / 'src/freetier_radar/review.py').read_text())
    source = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef)
                  and node.name == 'sources')
    calls = {node.func.id for node in ast.walk(source)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    return ('rechecks' if {'quota_review_changes', 'border_changes'} <= calls else 'omits',)


def _prose_access_fields(root: Path) -> tuple[str, ...]:
    from .models import Entry, ProseModelAccess
    return tuple(name for name in ('model_access', 'quote', 'deadline_quote', 'until', 'expired_models')
                 if name in (Entry.model_fields if name in ('model_access', 'expired_models')
                             else ProseModelAccess.model_fields))


def _empty_app_policy(root: Path) -> tuple[str, ...]:
    import httpx
    from .prober import page_response_ok
    shell = '<html><head><title>Free offer</title><script type="module" src="/app.js"></script></head><body><div id="root"><template>Free offer</template></div></body></html>'
    response = httpx.Response(200, text=shell, headers={'content-type': 'text/html'})
    return ('unreadable' if not page_response_ok(response) else 'readable',)


def _native_audio_policy(root: Path) -> tuple[str, ...]:
    from .prober import _is_free
    models = [{'types': kind, 'pricing': {'input': 0, 'output': 0},
               'pricing_source': 'billing_config',
               'pricing_lines': [{'billable': billable, 'cost_usd': 1}]}
              for kind, billable in (('stt', 'audio_input_seconds'), ('t2a', 'audio_generation'))]
    return ('mandatory billing lines' if all(not _is_free(model) for model in models) else 'ignored billing lines',)


def _review_lead_scope(root: Path) -> tuple[str, ...]:
    from .review_leads import collect_leads
    examples = (
        ('other products', 'https://vendor.example/product',
         'https://vendor.example/another-product', {'https://vendor.example/product'}, True),
        ('other repositories', 'https://github.com/owner/one',
         'https://github.com/owner/two', {'https://github.com/owner/one'}, True),
        ('operator blocks', 'https://directory.example/list',
         'https://api.blocked.example/v1', {'blocked.example'}, False),
        ('Query parameters', 'https://vendor.example/list',
         'https://vendor.example/models?product=second', {'https://vendor.example/models?product=first'}, True),
    )
    return tuple(name for name, source, target, known, expected in examples
                 if [r['url'] for r in collect_leads({source: f'<a href="{target}">Read</a>'}, known)]
                 == ([target] if expected else []))


def _utc_date_deadline(root: Path) -> tuple[str, ...]:
    day = date(2026, 11, 30)
    access = FreeAccess(source='https://vendor.example/promo', until=day)
    end = access.ends_at
    return ('inclusive' if (end.date() - day).days == 1 else 'invalid',
            end.tzname(), end.strftime('%H:%M'))


CLAIMS: tuple[Claim, ...] = (
    Claim("assets/README.md", r"radar beam uses (CSS) animation",
          lambda root: ('CSS',) if 'animation:turn' in _style() else (),
          "pictures._style; animation and reduced-motion controls in tests/test_pictures.py"),
    Claim("assets/README.md", r"the beam stays (still)",
          lambda root: ('still',) if re.search(
              r'@media \(prefers-reduced-motion: reduce\).*?\.turning \{ animation: none \}', _style()) else (),
          "pictures._style; actual generated SVG reduced-motion control in tests/test_pictures.py"),
    Claim(".github/workflows/indexnow.yml", r"(freetier-render) generates this projection",
          lambda root: next(node.written_by for node in MAP if node.path == ".github/workflows/indexnow.yml"),
          "layout.MAP and render.render_indexnow_filter; independent new-file/job-preservation controls in tests/test_layout.py"),
    Claim("CONTRIBUTING.md", r"each changed page's (content) once\. Shared (layout),",
          _browser_coverage_purposes,
          "review_browser.browser_plan; per-content and bounded-representative regression in tests/test_review.py"),
    Claim("CONTRIBUTING.md", r"Internal changes with no browser-facing output add (no browser cases)",
          _internal_browser_policy,
          "review_browser.browser_scope and browser_plan; internal-change, shared-layout and complete execution-data regressions in tests/test_review.py"),
    Claim("CONTRIBUTING.md", r"A page-only model's quota can name a (pending) family in `newcomers` without",
          _pending_quota_policy,
          "models.Entry._quota_catalog_is_bound_to_the_lane; canonical pending quota, Limits scope and unknown-family controls in tests/test_prose_promotions.py"),
    Claim("CONTRIBUTING.md", r"Pages model orders are `(score)`, `(name)` or `(providers)`",
          lambda root: tuple(option["id"] for option in MODEL_SORT["options"]),
          "render.MODEL_SORT and model-sort.js; ordering and browser history/filter controls"),
    Claim("CONTRIBUTING.md", r"An automatic free router declares its upstream catalog in `(api.free_routers)`",
          lambda root: ('api.free_routers',) if 'free_routers' in ApiInfo.model_fields else (),
          "models.ApiInfo and ModelFamily.router; owning/upstream HTTP eligibility, scoped labels, expiry and measured-pool controls in tests/test_free_routers.py"),
    Claim("assets/model-sort.js", r'if \(mode === "(score)"\) return items.slice\(\);',
          lambda root: (MODEL_SORT["default"],),
          "render.MODEL_SORT; generated score order preserved by model-sort.js and tests/test_search_contract.py"),
    Claim("CONTRIBUTING.md", r"Matching Intelligence Index (score)s come first, highest first;"
          r"\s+unavailable scores use the retained (tier), then natural model-(name) order",
          lambda root: MODEL_ORDER_FIELDS, "render.MODEL_ORDER_FIELDS and shared display ordering; tests/test_render.py"),
    Claim('CONTRIBUTING.md',
          r'For a prose-based tool without callable IDs, `(model_access)` on the entry uses\s+'
          r'the exact family, an eligibility `(quote)` and a `(deadline_quote)` beside `(until)`\.\s+'
          r'The same source checks, model labels and expiry writer apply\. Ended families\s+'
          r'remain in `(expired_models)`;',
          _prose_access_fields,
          'models.Entry and ProseModelAccess; HTTP Free-plan/deadline, writer-clock and scoped-quota controls in tests/test_prose_promotions.py'),
    Claim('CONTRIBUTING.md',
          r'The sources phase (rechecks) quota review deadlines and recorded territory lists',
          _source_detail_policy,
          'review.sources uses quotas.quota_review_changes and prober.border_changes; HTTP expiry and region controls in tests/test_review.py'),
    Claim('CONTRIBUTING.md',
          r'An HTML response with an empty app mount and a client bootstrap is (unreadable)',
          _empty_app_policy,
          'prober.page_response_ok and page_reader.empty_app_page; metadata-only and rendered HTTP controls across readers in tests/test_page_http_policy.py'),
    Claim('CONTRIBUTING.md',
          r'Native speech transcription and audio generation use (mandatory billing lines)',
          _native_audio_policy,
          'prober._additional_prices; native audio zero/paid/unreadable and optional text input controls in tests/test_catalog_billing.py'),
    Claim('CONTRIBUTING.md',
          r'Unavailable pinned measurements (report) current\s+dated checkpoint candidates for review; automatic substitutions are (not made)',
          _checkpoint_review_policy,
          'tiers.checkpoint_reviews and HTTP writer regressions for deprecated/null records, pinned efforts, archived rows and different-generation controls in tests/test_tiers.py'),
    Claim('CONTRIBUTING.md',
          r'Date-only `until` values are (inclusive) (UTC) dates: the writer expires\s+them at (00:00) UTC on the following day',
          _utc_date_deadline,
          'models.FreeAccess.ends_at and expire_entries; real writer date-preservation, inclusive-day expiry and timestamp controls in tests/test_free_access.py'),
    Claim('CONTRIBUTING.md',
          r'Exact URL decisions preserve links to (other products) and (other repositories);\s+(operator blocks) retain their domain scope\. (Query parameters) remain part of the link identity',
          _review_lead_scope,
          'review_leads.answered_sites and collect_leads; committed-decision HTTP product, supporting-host, repository, alias, navigation and blocklist controls in tests/test_review.py'),
    Claim('CONTRIBUTING.md',
          r'links to comparisons and source directories from\s+(HTML), (inline Markdown) and (reference Markdown)',
          _review_link_formats,
          'review_leads.collect_leads; HTTP source-boundary formats and navigation controls in tests/test_review.py, provenance and hidden-content controls in tests/test_review_leads.py'),
    Claim('CONTRIBUTING.md',
          r'Set `aa_auto: false` to (hold) automatic binding for\s+a family while its available benchmark variant is under review; explicit\s+reviewed bindings remain (measured)',
          _automatic_aa_hold,
          'models.ModelFamily.aa_auto and tiers.unmeasured; repeated HTTP writer, bare-peer and explicit reviewed binding controls in tests/test_tiers.py'),
    Claim("CONTRIBUTING.md", r'Its verdict is `(canonical)`, `(task)`, or `(irrelevant)`',
          lambda _: LEAD_VERDICTS,
          "review.sources and review_leads.validate_dispositions; captured comparison, missing decision, canonical pointer and unresolved task controls in tests/test_review.py, tests/test_review_leads.py and tests/test_quality.py"),
    Claim("CONTRIBUTING.md",
          r'An explicit `null` score in\s+a readable current leaderboard (clears) the old tier; a missing model or unreadable\s+source (preserves) it for review',
          _unscored_tier_policy,
          "tiers.review; full-table HTTP null/zero/missing/malformed/duplicate controls and unreadable-source preservation in tests/test_tiers.py"),
    Claim("CONTRIBUTING.md", r'`remaining_free` records a separately continuing mode with its `(source)`, `(quote)`,\s+`(free_part)` \(`sum` or `unnamed`\) and optional payment `(access)`',
          lambda root: tuple(RemainingFree.model_fields),
          "models.RemainingFree and expire_entries; HTTP current/changed/unreadable offer controls and exact payment-preserving expiry in tests/test_remaining_free.py"),
    Claim("CONTRIBUTING.md", r'`(model_bindings)` names the model and `quotas\[\]\.(model_ids)` binds its',
          lambda root: tuple(k for cls, k in ((ClientLane, 'model_bindings'), (UsageQuota, 'model_ids'))
                             if k in cls.model_fields),
          "models.Entry._a_client_lane_is_a_lane_its_probe_reads; HTTP identity/allowance failures, unbound-wallet controls and shared expiry in tests/test_page_client_lane.py"),
    Claim("CONTRIBUTING.md", r'Model names in scripts and (inert templates) need explicit `(machinery_keywords)`; (comments) cannot keep\s+a family listed',
          _page_family_text,
          "prober.unevidenced_families; HTTP machinery/comment regression and rendered-text control in tests/test_page_family_machinery.py"),
    Claim("CONTRIBUTING.md", r'An explicit catalog operation list must include `(Chat Completions)`',
          _catalog_chat_operations,
          "prober.dead_model_ids; actual page/catalog HTTP boundary and valid/absent metadata controls in tests/test_catalog_operations.py"),
    Claim("CONTRIBUTING.md", r'Discovery checks every available catalog row marked or priced free, even when\s+its ID does not match `(probe.free_marker)`',
          _catalog_arrival_spelling,
          "prober.unlisted_free_ids; HTTP alternate-suffix and paid/unavailable controls in tests/test_model_table_inventory.py and tests/test_prober.py"),
    Claim("CONTRIBUTING.md", r'`models\[\]\.(table_name)` binds',
          lambda root: tuple(k for k in ModelFamily.model_fields if k == 'table_name'),
          "models.ModelFamily; exact decorated-table-row and new-variant HTTP controls in tests/test_model_table_inventory.py"),
    Claim("CONTRIBUTING.md", r'`probe.model_exclusions` records `(name)`, `(source)`, `(quote)` and `(reviewed_on)`',
          lambda root: tuple(ModelTableExclusion.model_fields),
          "models.ModelTableExclusion and HTTP inventory/exclusion controls in tests/test_model_table_inventory.py"),
    Claim("CONTRIBUTING.md", r'exclusion\s+needs another manual review after (\d+) days',
          lambda root: (str(UNKNOWN_RECHECK_DAYS),),
          "prober.model_table_findings; dated source and exclusion controls in tests/test_model_table_inventory.py", generated=True),
    Claim("CONTRIBUTING.md", r'`newcomers\[\]\.(table_name)` binds',
          lambda root: tuple(k for k in Newcomer.model_fields if k == 'table_name'),
          "models.Newcomer; exact eligible row-label check in prober.model_table_findings"),
    Claim("CONTRIBUTING.md", r'`archive_review` pairs\s+`(checked_on)` with `(sources)`',
          lambda root: tuple(ArchiveReview.model_fields),
          "models.ArchiveReview; canonical current-source and date controls in tests/test_archive_review.py"),
    Claim("CONTRIBUTING.md", r'(?s)manual review is at least (\d+) days old, through `freetier-archive-review`.*?Source collection has a\s+(\d+)-second budget',
          _archive_review_limits,
          "archive_review.due_entries and collect; scheduled HTTP and exclusion controls in tests/test_archive_review.py", generated=True),
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
    Claim("CONTRIBUTING.md", r"`source` and `quote` in `api\.(opencode_output_sources)\[ID\]`",
          lambda root: tuple(k for k in ("opencode_output_sources",) if k in ApiInfo.model_fields),
          "models.ApiInfo and client_limits.model_limit_changes; documented parameter and changed-source HTTP controls in tests/test_nested_catalog.py"),
    Claim("CONTRIBUTING.md", r"By default, `read: (catalog)` compares the limits",
          lambda root: (ModelLimits.model_fields['read'].default,),
          "prober.stale_ids; catalog cap drift and unavailable/noninteger metadata HTTP controls in tests/test_prober.py"),
    Claim("CONTRIBUTING.md", r"set `read: (opencode-config)` and\s+`(source_provider)`",
          lambda root: (next(v for v in get_args(ModelLimits.model_fields['read'].annotation) if v != 'catalog'),
                        next(k for k in ModelLimits.model_fields if k == 'source_provider')),
          "client_limits.model_limit_changes and prober.probe_entry; exact provider/model, ambiguity, changed/unreadable source HTTP controls in tests/test_client_limits.py"),
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
          "quotas.UNKNOWN_RECHECK_DAYS and quota_moved; expiry regression in tests/test_quotas.py", generated=True),
    Claim("CONTRIBUTING.md", r"probe requests a fresh review\s+after (\d+) days",
          lambda root: (str(UNKNOWN_RECHECK_DAYS),),
          "page_catalog.check_page_catalog and UNKNOWN_RECHECK_DAYS; Markdown HTTP-boundary expiry regression", generated=True),
    Claim("CONTRIBUTING.md", r"Read modes are `(page)`,\s+`(catalog)`, `(constant)`, `(table)`, `(catalog-field)`, and `(script-field)`",
          lambda root: get_args(UsageQuota.model_fields['read'].annotation),
          "quotas.UsageQuota and quota_changes; HTTP-boundary regressions in tests/test_quotas.py"),
    Claim("CONTRIBUTING.md", r"semantics require a dated review every (\d+) days",
          lambda root: (str(UNKNOWN_RECHECK_DAYS),),
          "quotas.quota_moved; JSON plan-field review expiry regression in tests/test_quotas.py", generated=True),
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
          lambda root: (str(WATCH_RECHECK_DAYS),), "models.WATCH_RECHECK_DAYS", generated=True),
    Claim("CONTRIBUTING.md", r"Those verdicts expire after (\d+)\s+days",
          lambda root: (str(SOURCE_RECHECK_DAYS),), "models.SOURCE_RECHECK_DAYS", generated=True),
    Claim("CONTRIBUTING.md",
          r"after (\w+) failed\s+probes in a row, or after (\d+) days without a passing probe",
          lambda root: (_word(ARCHIVE_AFTER_FAILURES), str(ARCHIVE_AFTER_DAYS)),
          "models.ARCHIVE_AFTER_FAILURES and ARCHIVE_AFTER_DAYS", generated=True),
    Claim("CONTRIBUTING.md",
          r"scores within (\d+) points of the top\s+of the index, counting current models only,"
          r"\s+`strong` within (\d+)",
          lambda root: (f"{FRONTIER_WITHIN:g}", f"{STRONG_WITHIN:g}"),
          "tiers.FRONTIER_WITHIN and STRONG_WITHIN", generated=True),
    Claim("CONTRIBUTING.md", r"index version `([\d.]+)`; a missing",
          lambda root: (INDEX_VERSION,), "tiers.INDEX_VERSION and HTTP writer revision regressions", generated=True),
    Claim("CONTRIBUTING.md", r"The comparison axis starts at (\d+) and scales to the free models",
          lambda root: (f"{_chart_ticks(33.6)[0]:g}",),
          "pictures._chart_ticks; zero baseline, real score ratios and common-width axis controls in tests/test_pictures.py"),
    Claim("CONTRIBUTING.md", r"vendor output in backticks, (\d+) characters\s+at most",
          lambda root: (str(PROSE_LIMITS["api.notice"]),), "validate.PROSE_LIMITS['api.notice']", generated=True),
    Claim("CONTRIBUTING.md", r"holds a refusal off the failure count for (\d+) days from `since`",
          lambda root: (str(NOTICE_HOLD_DAYS),), "models.NOTICE_HOLD_DAYS", generated=True),
    Claim("CONTRIBUTING.md", r"only events from the last (\d+) days, at most (\w+) per channel",
          lambda root: (str(MAX_AGE_DAYS), _word(POSTS_PER_RUN)),
          "announce.MAX_AGE_DAYS and POSTS_PER_RUN", generated=True),
    Claim("CONTRIBUTING.md",
          r"`freetier-check` holds `offering` to ([\d,]+) characters, `limits` to ([\d,]+) and"
          r"\s+`api.note` to ([\d,]+)",
          lambda root: tuple(f"{PROSE_LIMITS[f]:,}" for f in ("offering", "limits", "api.note")),
          "validate.PROSE_LIMITS", generated=True),
    Claim("CONTRIBUTING.md", r"The first (\w+) no-card agents are also the top of the README",
          lambda root: (_word(README_STARTERS),), "render.README_STARTERS", generated=True),
    Claim("CONTRIBUTING.md", r"read (\w+) names deep per section",
          lambda root: (_word(README_PICKS),), "render.README_PICKS", generated=True),
    Claim("CONTRIBUTING.md", r"An undated model on a rotating lane waits (\w+ weeks|a week)",
          lambda root: (_weeks(BAR_DAYS),), "bars.BAR_DAYS", generated=True),
    Claim("CONTRIBUTING.md", r"and joins `models\[\]` (\w+ weeks|a week) later",
          lambda root: (_weeks(BAR_DAYS),), "bars.BAR_DAYS", generated=True),
    Claim("CONTRIBUTING.md", r"The report counts (\w+ weeks|a week)\s+from that date",
          lambda root: (_weeks(BAR_DAYS),), "bars.BAR_DAYS", generated=True),
    Claim("CONTRIBUTING.md", r"`offering`, the first (\w+)\s+model families and the date",
          lambda root: (_word(README_MODELS),), "render.README_MODELS", generated=True),
    Claim("CONTRIBUTING.md", r"every family past the (\w+), one click from their count",
          lambda root: (_ordinal(README_MODELS),), "render.README_MODELS", generated=True),
    Claim("CONTRIBUTING.md", r"The comparison shows at most (\w+) families;",
          lambda root: (_word(README_COMPARISON),), "render.README_COMPARISON", generated=True),
    Claim("CONTRIBUTING.md", r"a page for every model (\w+) rows or more serve",
          lambda root: (_word(MODEL_PAGE_ROWS),), "render.MODEL_PAGE_ROWS", generated=True),
    Claim("CONTRIBUTING.md", r"sends the check on to the next id, up to\s+(\w+),",
          lambda root: (_word(KEYLESS_IDS_TRIED),), "prober.KEYLESS_IDS_TRIED", generated=True),
    Claim("CONTRIBUTING.md", r"A later id answering is reported as `([^`]+)`\s+naming both results",
          lambda root: (ProbeStatus.STALE_IDS.value,),
          "prober.keyless_lane_verdict and HTTP alternate-completion notice regression in tests/test_prober.py"),
    Claim("CONTRIBUTING.md", r"recovery, with a (\d+)-second budget,\s+up to (\d+) redirects and an (\d+) MiB body limit",
          lambda root: _page_recovery_limits(), "page_reader recovery limits", generated=True),
    Claim("CONTRIBUTING.md", r"always calls under this\s+project's own `([^`]+)`",
          lambda root: (UA["User-Agent"],), "prober.UA", generated=True),
    Claim("CONTRIBUTING.md", r"sends `User-Agent: ([^`]+)`",
          lambda root: (QUICKSTART_USER_AGENT,), "render.QUICKSTART_USER_AGENT", generated=True),
    Claim("CONTRIBUTING.md", r"\| a sentence of (\d+)\+ words quoted from the page \|",
          lambda root: (str(ANCHOR_PHRASE_WORDS),), "models.ANCHOR_PHRASE_WORDS", generated=True),
    Claim("CONTRIBUTING.md", r"reports every quote of (\w+) words or more",
          lambda root: (_word(MIN_WORDS),), "quotes.MIN_WORDS", generated=True),
    Claim("CONTRIBUTING.md", r"is a route, a (\d+), (\d+) or (\d+)\s+is reported",
          lambda root: tuple(str(c) for c in ROUTE_GONE), "prober.ROUTE_GONE", generated=True),
    Claim("CONTRIBUTING.md", r"beside the (\w+) configs it describes",
          lambda root: (_word(len([n for n in MAP if n.kind is Kind.GENERATED
                                   and n.path.startswith("configs/")
                                   and n.path != "configs/README.md"])),),
          "the configs layout.MAP marks generated", generated=True),
    Claim("CONTRIBUTING.md",
          r"a hand edit of `(\w+)`,\s+`(\w+)`, `(\w+)` or `(\w+)`, which only the run's probe",
          lambda root: tuple(sorted(EARNED)), "gate.EARNED",
          read=lambda found: tuple(sorted(found.groups()))),
    Claim("CONTRIBUTING.md", r"Anthropic check's way: a (\d+), (\d+) or (\d+) is",
          lambda root: tuple(str(c) for c in ROUTE_GONE), "prober.ROUTE_GONE", generated=True),
    Claim("CONTRIBUTING.md", r"cannot take is `(\w+)`, the LiteLLM profile's name",
          lambda root: (CODEX_LITELLM_PROFILE,), "models.CODEX_LITELLM_PROFILE"),
    Claim("CONTRIBUTING.md", r"the header asks for\s+LiteLLM (\d+\.\d+) or later",
          lambda root: (LITELLM_BRIDGE_SINCE,), "render.LITELLM_BRIDGE_SINCE", generated=True),
    Claim("CONTRIBUTING.md", r"since\s+Codex CLI (\d+\.\d+)",
          lambda root: (CODEX_SINCE,), "render.CODEX_SINCE", generated=True),
    Claim("CONTRIBUTING.md", r"Python (\d+\.\d+) to (\d+\.\d+), httpx",
          _ci_pythons, "the oldest and the newest Python in .github/workflows/ci.yml", generated=True),
    Claim("CONTRIBUTING.md", r"`conformance` workflow runs them every (\w+)",
          _cron_day(".github/workflows/conformance.yml"),
          ".github/workflows/conformance.yml's cron", generated=True),
    Claim("CONTRIBUTING.md", r"The (verification) and (expiry) writers explicitly dispatch this workflow",
          _bot_conformance_dispatch,
          "conformance.dispatch and both bot writers; path, dispatch and exact-commit controls in tests/test_conformance_dispatch.py"),
    Claim("CONTRIBUTING.md", r"An unpriced catalog may use `tier: (free)`",
          _unpriced_catalog_tier,
          "prober._is_free; current HTTP and stale-price controls in tests/test_prober.py"),
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


def render_claims(text: str, file: str, root: Path) -> str:
    """Generate opted-in values while preserving each registered sentence.

    Missing/reworded assertions still fail check_claims; this writer cannot
    invent prose, rewrite external quotes or renew dated vendor evidence.
    """
    for claim in CLAIMS:
        if claim.file != file or not claim.generated:
            continue
        matches = list(re.finditer(claim.pattern, text))
        if not matches:
            continue
        values = claim.truth(root)
        if claim.read is not re.Match.groups or any(len(values) != len(m.groups()) for m in matches):
            raise ValueError(f"{claim.source}: generated claims need one value per plain group")
        for found in reversed(matches):
            for group, value in reversed(list(enumerate(values, 1))):
                start, end = found.span(group)
                text = text[:start] + value + text[end:]
    return text


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
    files = {file: (root / file).read_text(encoding="utf-8")
             for file in {c.file for c in claims} | set(scheduled)}
    for claim in claims:
        text = files[claim.file]
        matches = list(re.finditer(claim.pattern, text))
        if not matches:
            problems.append(f"{claim.file} no longer has the sentence stating {claim.source} "
                            f"(claims.CLAIMS: `{claim.pattern}`) — point the claim at the sentence "
                            "that states it now")
            continue
        truth = claim.truth(root)
        for found in matches:
            if claim.read(found) != truth:
                said = " ".join(found.group(0).split())
                problems.append(f"{claim.file}:{_line(text, found.start())} says `{said}` and "
                                f"{claim.source} says {', '.join(truth)} — change the sentence or the "
                                "constant, never one of them alone")
    expected = probe_frequency(PROBE_WEEKDAYS)
    for name in scheduled:
        text = files[name]
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
