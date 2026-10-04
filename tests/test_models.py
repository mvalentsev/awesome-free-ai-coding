from datetime import date, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

import yaml

from freetier_radar.models import (SOURCE_RECHECK_DAYS, WATCH_RECHECK_DAYS, Entry, Watched,
                                    id_family, is_anchor, is_covered, is_source_current,
                                    known_domains, load_registry, load_sources, load_watchlist,
                                    prose_names, save_registry, watch_match)


def save_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def sample_entry() -> dict:
    return {
        "id": "openrouter-free",
        "name": "OpenRouter (free models)",
        "category": "api-free-tier",
        "url": "https://openrouter.ai",
        "source_urls": ["https://openrouter.ai/docs"],
        "card_required": False,
        "offering": "Free variants of frontier models via one API",
        "limits": "50 req/day free",
        "models": [
            {"family": "deepseek", "tier": "frontier"},
            {"family": "qwen3-coder", "tier": "strong"},
        ],
        "probe": {
            "type": "api-models",
            "endpoint": "https://openrouter.ai/api/v1/models",
            "free_marker": ":free",
        },
        "first_seen": date(2026, 7, 19),
        "last_verified": date(2026, 7, 19),
    }


def test_entry_validates():
    e = Entry.model_validate(sample_entry())
    assert e.id == "openrouter-free"
    assert e.probe_failures == 0
    assert e.provisional is False
    assert e.models[0].superseded_by is None


def test_blind_page_probe_is_rejected():
    """Generic words alone outlive the offer: a page that still advertises a
    channel the vendor has cut off goes on matching them."""
    blind = {**sample_entry(), "probe": {"type": "page-keywords",
                                         "endpoint": "https://x.ai/pricing",
                                         "keywords": ["free", "no credit card required"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(blind)

    anchored = {**blind, "probe": {**blind["probe"], "keywords": ["solar-mini", "free"]}}
    assert Entry.model_validate(anchored).probe.keywords[0] == "solar-mini"


@pytest.mark.parametrize("keyword", [
    "mistral-medium",                                   # a model id
    '"name":"free"',                                    # a JSON field of the vendor's own API
    "advanced_model_request_limit",
    '"name":"hobby","price":"0"',                       # the free plan's own price row
    "$0.10, subject to change",                         # the size of the free grant
    "anonymous users get one request every 15 seconds",  # the anonymous quota, in words
    "valid for 90 days after you activate",
    "light quota to code with agents",                  # the plan described in the vendor's words
    "codex are included in your chatgpt free",
])
def test_an_anchor_dies_with_the_offer(keyword):
    assert is_anchor(keyword)


@pytest.mark.parametrize("keyword", [
    "free", "hobby", "no signup", "free quota", "monthly credits",
    "no credit card required",
    "Free-Tier",                       # dressing a generic word up does not anchor it
    '"free"',
    "sign up for free and get started",  # long, and still says nothing
    "get started for free today",
])
def test_page_furniture_is_not_an_anchor(keyword):
    """What a page keeps serving for months after its free tier is withdrawn —
    `hobby`, `free quota` — is furniture, whether or not GENERIC_KEYWORDS
    lists it."""
    assert not is_anchor(keyword)


def test_a_weak_anchor_is_rejected_even_when_it_is_not_a_listed_generic():
    weak = {**sample_entry(), "probe": {"type": "page-keywords",
                                        "endpoint": "https://cursor.com/pricing",
                                        "keywords": ["hobby", "no credit card required"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(weak)

    anchored = {**weak, "probe": {**weak["probe"],
                                  "keywords": ['"name":"hobby","price":"0"', "limited agent requests"]}}
    assert Entry.model_validate(anchored).probe.keywords[1] == "limited agent requests"


def test_a_delisted_row_keeps_the_probe_it_was_published_with():
    """A delisted row is the record of what the list once published, probe
    included, and no probe reads it, so the anchor rule does not hold there:
    rewriting its old keywords would falsify the record."""
    seed = {**sample_entry(), "probe": {"type": "page-keywords", "endpoint": "https://x.ai",
                                        "keywords": ["free"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(seed)
    delisted = {**seed, "delisted": {"on": date(2026, 7, 19), "reason": "nothing behind the claim"}}
    assert Entry.model_validate(delisted).probe.keywords == ["free"]


def test_a_delisting_says_why():
    """The reason is what the Archive shows beside the row, so a blank one is
    refused."""
    with pytest.raises(ValidationError):
        Entry.model_validate({**sample_entry(), "delisted": {"on": date(2026, 7, 19), "reason": "  "}})


def test_zero_price_flag_belongs_to_a_models_api():
    """A pricing page publishes no machine-readable prices, so the flag there
    would check nothing."""
    misplaced = {**sample_entry(), "probe": {"type": "page-keywords",
                                             "endpoint": "https://x.ai/pricing",
                                             "keywords": ["solar-mini", "free"],
                                             "require_zero_price": True}}
    with pytest.raises(ValidationError):
        Entry.model_validate(misplaced)

    on_the_api = {**sample_entry(), "probe": {**sample_entry()["probe"], "require_zero_price": True}}
    assert Entry.model_validate(on_the_api).probe.require_zero_price


def test_ignored_ids_belong_beside_a_price_list():
    """`api.ignored_ids` is read only where the probe compares a catalog's
    zero-priced rows with api.model_ids; on a page probe, or on a catalog whose
    prices are not read, nothing would act on it."""
    on_a_page = {**sample_entry(),
                 "probe": {"type": "page-keywords", "endpoint": "https://x.ai/pricing",
                           "keywords": ["solar-mini", "free"]},
                 "api": {"base_url": "https://api.x.ai/v1", "ignored_ids": ["vendor/router"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(on_a_page)

    prices_unread = {**sample_entry(),
                     "api": {"base_url": "https://api.x.ai/v1", "ignored_ids": ["vendor/router"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(prices_unread)

    prices_read = {**prices_unread,
                   "probe": {**sample_entry()["probe"], "require_zero_price": True}}
    assert Entry.model_validate(prices_read).api.ignored_ids == ["vendor/router"]


def test_an_id_is_listed_or_ignored_never_both():
    both = {**sample_entry(),
            "probe": {**sample_entry()["probe"], "require_zero_price": True},
            "api": {"base_url": "https://api.x.ai/v1", "model_ids": ["vendor/a:free"],
                    "ignored_ids": ["vendor/a:free"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(both)


def test_a_page_probe_cannot_hide_an_undated_id_beside_expired_evidence():
    data = {**sample_entry(),
            "probe": {"type": "page-keywords", "endpoint": "https://x.ai/pricing",
                      "keywords": ["one million free tokens"]},
            "api": {"base_url": "https://api.x.ai/v1", "model_ids": ["steady"],
                    "ignored_ids": ["ended", "undated"],
                    "model_access": {"ended": {"source": "https://x.ai/promo",
                                               "until": "2026-10-01T00:00:00Z"}}}}
    with pytest.raises(ValidationError, match="ignored_ids needs an api-models"):
        Entry.model_validate(data)
    data["api"]["model_access"]["undated"] = {"source": "https://x.ai/pricing", "initial_payment_usd": 5}
    with pytest.raises(ValidationError, match="ignored_ids needs an api-models"):
        Entry.model_validate(data)


def test_ignored_ids_are_written_only_where_set(tmp_path: Path):
    """A list that means something on a few rows adds no line to the others."""
    p = tmp_path / "registry.yaml"
    plain = Entry.model_validate({**sample_entry(), "api": {"base_url": "https://api.x.ai/v1"}})
    save_registry(p, [plain])
    assert "ignored_ids" not in p.read_text(encoding="utf-8")

    ignoring = Entry.model_validate({
        **sample_entry(),
        "probe": {**sample_entry()["probe"], "require_zero_price": True},
        "api": {"base_url": "https://api.x.ai/v1", "ignored_ids": ["vendor/router"]}})
    save_registry(p, [ignoring])
    assert load_registry(p)[0].api.ignored_ids == ["vendor/router"]


def test_a_catalog_url_belongs_to_a_page_probe_with_ids_to_check():
    """An api-models probe already reads its endpoint as the catalog, so a
    second one there would be two answers to one question; and a page probe
    with no api.model_ids has nothing for the catalog to check — either way
    the field would sit in the registry doing nothing."""
    on_the_api = {**sample_entry(),
                  "probe": {**sample_entry()["probe"], "catalog": "https://api.x.ai/v1/models"}}
    with pytest.raises(ValidationError):
        Entry.model_validate(on_the_api)

    page = {"type": "page-keywords", "endpoint": "https://x.ai/pricing",
            "keywords": ["solar-mini", "free"], "catalog": "https://api.x.ai/v1/models"}
    nothing_to_check = {**sample_entry(), "probe": page, "api": {"base_url": "https://api.x.ai/v1"}}
    with pytest.raises(ValidationError):
        Entry.model_validate(nothing_to_check)

    checked = {**sample_entry(), "probe": page,
               "api": {"base_url": "https://api.x.ai/v1", "model_ids": ["solar-mini"]}}
    assert Entry.model_validate(checked).probe.catalog == "https://api.x.ai/v1/models"


def test_a_lane_belongs_to_an_api_models_probe():
    """A lane is the key of a JSON document whose array is read as the catalog; a
    page-keywords probe reads the response as text, so there the field would do
    nothing."""
    on_a_page = {**sample_entry(), "probe": {"type": "page-keywords",
                                             "endpoint": "https://x.ai/pricing",
                                             "keywords": ["solar-mini", "free"],
                                             "lane": "free"}}
    with pytest.raises(ValidationError):
        Entry.model_validate(on_a_page)

    on_the_api = {**sample_entry(), "probe": {**sample_entry()["probe"], "lane": "free"}}
    assert Entry.model_validate(on_the_api).probe.lane == "free"


CLIENT_LANE_PROBE = {"type": "api-models", "endpoint": "https://api.x.ai/api/v1/ai/recommended-models",
                     "lane": "free"}


def test_a_lane_served_only_inside_the_vendor_s_client_records_its_ids_in_client_lane(
        tmp_path: Path):
    """A lane served only inside the vendor's client (Cline's free models) has no
    endpoint to paste and no `api` block, so `client_lane` records its ids, for
    the run to notice an arrival and freetier-bars to date it. A row with no
    such lane writes nothing."""
    p = tmp_path / "registry.yaml"
    row = Entry.model_validate({
        **sample_entry(), "category": "agent-cli", "probe": CLIENT_LANE_PROBE,
        "client_lane": {"model_ids": ["cline-free/a-1", "stealth/b"], "no_family_ids": ["stealth/b"],
                        "note": "stealth/b is a codename that names no model"}})
    plain = Entry.model_validate({**sample_entry(), "id": "plain"})
    save_registry(p, [row, plain])
    loaded = load_registry(p)
    assert loaded[0].client_lane.model_ids == ["cline-free/a-1", "stealth/b"]
    assert loaded[0].client_lane.no_family_ids == ["stealth/b"]
    assert loaded[1].client_lane is None
    assert p.read_text(encoding="utf-8").count("client_lane") == 1


def test_a_lane_is_recorded_in_one_place():
    """A lane an API serves keeps its ids in api.model_ids, which the configs are
    written from; client_lane is for a lane no API serves. Both on one row would
    be two lists of one lane, bound to drift apart."""
    both = {**sample_entry(), "probe": CLIENT_LANE_PROBE,
            "api": {"base_url": "https://api.x.ai/v1", "model_ids": ["cline-free/a-1"]},
            "client_lane": {"model_ids": ["cline-free/a-1"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(both)


def test_a_client_lane_is_held_to_a_lane_its_probe_can_read():
    """The ids are checked against what the probe reads, in both directions, so
    the probe has to be able to tell the free lane from the rest of what it
    reads: a lane key, or prices it reads at zero. On a page, or on a catalog
    it cannot read free off, the list would sit in the registry checked by
    nothing — and a lane with no ids records nothing."""
    ids = {"model_ids": ["cline-free/a-1"]}
    on_a_page = {**sample_entry(), "client_lane": ids,
                 "probe": {"type": "page-keywords", "endpoint": "https://x.ai/pricing",
                           "keywords": ["solar-mini", "free"]}}
    free_unread = {**sample_entry(), "client_lane": ids}
    no_ids = {**sample_entry(), "probe": CLIENT_LANE_PROBE, "client_lane": {"model_ids": []}}
    for row in (on_a_page, free_unread, no_ids):
        with pytest.raises(ValidationError):
            Entry.model_validate(row)
    priced = {**sample_entry(), "client_lane": ids,
              "probe": {**sample_entry()["probe"], "require_zero_price": True}}
    assert Entry.model_validate(priced).client_lane.model_ids == ["cline-free/a-1"]


NGC_SEARCH = "https://api.ngc.nvidia.com/v2/search/catalog/resources/ENDPOINT?q=free"


def test_a_free_list_marks_what_a_models_api_reads_as_free():
    """The list stands in for the prices a catalog does not publish, so it is
    read only where an api-models probe asks whether a row is free. Anywhere
    else it would sit in the registry changing nothing — on a page probe, or on
    a catalog probe that never asks the question."""
    on_a_page = {**sample_entry(), "probe": {"type": "page-keywords",
                                             "endpoint": "https://x.ai/pricing",
                                             "keywords": ["solar-mini", "free"],
                                             "free_list": NGC_SEARCH}}
    unasked = {**sample_entry(), "probe": {**sample_entry()["probe"], "free_list": NGC_SEARCH}}
    plain = {**sample_entry(), "probe": {**sample_entry()["probe"], "require_zero_price": True,
                                         "free_list": NGC_SEARCH.replace("https", "http")}}
    for misplaced in (on_a_page, unasked, plain):
        with pytest.raises(ValidationError):
            Entry.model_validate(misplaced)

    read = {**sample_entry(), "probe": {**sample_entry()["probe"], "require_zero_price": True,
                                        "free_list": NGC_SEARCH}}
    assert Entry.model_validate(read).probe.free_list == NGC_SEARCH


CREDIT_PAGE = {"type": "page-keywords", "endpoint": "https://x.ai/pricing",
               "keywords": ["$5 in free credits every month", "free"]}


def test_a_sum_to_spend_names_no_model():
    """A signup credit, a grant of tokens every model draws on, an allowance at
    each model's own price: no model is free by itself, so the column names
    none."""
    credit = {**sample_entry(), "probe": CREDIT_PAGE, "free_part": "sum"}
    with pytest.raises(ValidationError, match="sum to spend"):
        Entry.model_validate(credit)
    assert Entry.model_validate({**credit, "models": []}).free_part == "sum"


def test_a_free_part_the_vendor_names_no_model_for_names_none_here():
    """Copilot Free picks the model itself — "access to models is available
    through auto model selection only" — so a family would be a claim the
    vendor never makes."""
    auto = {**sample_entry(), "probe": CREDIT_PAGE, "free_part": "unnamed"}
    with pytest.raises(ValidationError, match="unnamed"):
        Entry.model_validate(auto)
    assert Entry.model_validate({**auto, "models": []}).free_part == "unnamed"


def test_a_lane_the_probe_reads_free_is_models_whatever_else_the_row_offers():
    """A probe that reads each model's own free mark — a zero price, a free
    marker, a lane key, a free list — is reading free models, so the row's free
    part cannot be a sum or unnamed: Vercel's $5 a month sits beside models it
    prices at zero, and those are the column."""
    marked = {**sample_entry(), "models": []}
    laned = {**sample_entry(), "models": [], "category": "agent-cli",
             "probe": CLIENT_LANE_PROBE, "client_lane": {"model_ids": ["cline-free/a-1"]}}
    for row in (marked, laned):
        for part in ("sum", "unnamed"):
            with pytest.raises(ValidationError, match="reads free models"):
                Entry.model_validate({**row, "free_part": part})
        assert Entry.model_validate({**row, "free_part": "models"}).free_part == "models"


def test_the_free_part_is_written_beside_the_offer_and_only_where_set(tmp_path: Path):
    p = tmp_path / "registry.yaml"
    credit = Entry.model_validate({**sample_entry(), "id": "credit", "probe": CREDIT_PAGE,
                                   "models": [], "free_part": "sum"})
    unset = Entry.model_validate({**sample_entry(), "id": "unset"})
    save_registry(p, [credit, unset])
    text = p.read_text(encoding="utf-8")
    assert text.count("free_part") == 1
    assert text.index("limits:") < text.index("free_part: sum") < text.index("models: []")
    assert load_registry(p)[0].free_part == "sum"


WAYBACK = ("https://web.archive.org/web/20260914103442/"
           "https://www.alibabacloud.com/help/en/model-studio/model-pricing")


def test_an_earlier_record_of_a_free_id_is_one_the_lane_lists(tmp_path: Path):
    """A Wayback snapshot of the vendor's free list, or the vendor's own snapshot
    of its lane, can show an id free before this registry first read it; the
    record names the id, the day and the source, and only for an id the lane
    lists — a date for an id nowhere else in the row dates nothing."""
    api = {"base_url": "https://api.x.ai/v1", "model_ids": ["m-1", "m-2"]}
    seen = {"id": "m-2", "on": "2026-09-14", "source": WAYBACK}
    row = Entry.model_validate({**sample_entry(), "api": {**api, "free_since": [seen]}})
    assert row.api.free_since[0].on == date(2026, 9, 14)
    for wrong in ({**seen, "id": "m-9"}, {**seen, "source": "web.archive.org/web/2026"}):
        with pytest.raises(ValidationError):
            Entry.model_validate({**sample_entry(), "api": {**api, "free_since": [wrong]}})
    lane = {"model_ids": ["cline-free/a-1"], "free_since": [{**seen, "id": "cline-free/a-1"}]}
    laned = Entry.model_validate({**sample_entry(), "category": "agent-cli",
                                  "probe": CLIENT_LANE_PROBE, "client_lane": lane})
    assert laned.client_lane.free_since[0].id == "cline-free/a-1"
    p = tmp_path / "registry.yaml"
    save_registry(p, [row, Entry.model_validate({**sample_entry(), "id": "plain", "api": api})])
    assert p.read_text(encoding="utf-8").count("free_since") == 1



def test_a_page_rows_newcomer_is_dated_by_a_record_where_no_lane_dates_it(tmp_path: Path):
    """A page row of free models has no ids for a lane to list (Freebuff's hour
    table, opencode's Zen page), so `newcomers` names the family a model will
    join as, the first day a record shows it free, and the record. A row with a
    lane dates its ids there, and a sum names no model at all."""
    page = {**sample_entry(), "free_part": "models",
            "probe": {"type": "page-keywords", "endpoint": "https://x.ai/pricing",
                      "keywords": ["one million free tokens"]}}
    seen = {"family": "solar-pro-4", "on": "2026-09-26", "source": WAYBACK}
    row = Entry.model_validate({**page, "newcomers": [seen]})
    assert (row.newcomers[0].family, row.newcomers[0].on) == ("solar-pro-4", date(2026, 9, 26))
    for wrong in ({**seen, "source": "web.archive.org/web/2026"}, {**seen, "family": "Solar Pro+4"}):
        with pytest.raises(ValidationError):
            Entry.model_validate({**page, "newcomers": [wrong]})
    laned = {**page, "api": {"base_url": "https://api.x.ai/v1", "model_ids": ["m-1"]}}
    with pytest.raises(ValidationError, match="newcomers"):
        Entry.model_validate({**laned, "newcomers": [seen]})
    with pytest.raises(ValidationError, match="newcomers"):
        Entry.model_validate({**page, "free_part": "sum", "models": [], "newcomers": [seen]})
    p = tmp_path / "registry.yaml"
    save_registry(p, [row, Entry.model_validate({**page, "id": "plain"})])
    assert p.read_text(encoding="utf-8").count("newcomers") == 1
    assert load_registry(p)[0].newcomers == row.newcomers

def test_registry_roundtrip(tmp_path: Path):
    p = tmp_path / "registry.yaml"
    save_registry(p, [Entry.model_validate(sample_entry())])
    loaded = load_registry(p)
    assert len(loaded) == 1
    assert loaded[0].last_verified == date(2026, 7, 19)
    assert loaded[0].category.value == "api-free-tier"
    assert loaded[0].probe.type.value == "api-models"


def watched(**kw) -> dict:
    return {"domains": ["example.ai"], "name": "Example",
            "checked_on": "2026-08-01", "reason": "no free tier today",
            "reopen_if": "they publish one", **kw}


def test_a_watch_verdict_covers_subdomains_and_every_spelling(tmp_path: Path):
    path = tmp_path / "watchlist.yaml"
    save_yaml(path, {"watched": [watched(domains=["modelscope.cn", "modelscope.ai"])]})
    wl = load_watchlist(path)
    today = date(2026, 8, 14)
    assert watch_match("api-inference.modelscope.cn", wl, today) is not None
    assert watch_match("modelscope.ai", wl, today) is not None
    assert watch_match("modelscope.com", wl, today) is None


def test_a_watch_verdict_expires_instead_of_burying_the_service(tmp_path: Path):
    """A watch verdict expires after WATCH_RECHECK_DAYS, which is what sets it
    apart from a blocklist entry."""
    path = tmp_path / "watchlist.yaml"
    save_yaml(path, {"watched": [watched(checked_on="2026-05-01")]})
    wl = load_watchlist(path)
    last_day = date(2026, 5, 1) + timedelta(days=WATCH_RECHECK_DAYS)
    assert watch_match("example.ai", wl, last_day) is not None
    assert watch_match("example.ai", wl, last_day + timedelta(days=1)) is None


def test_a_missing_watchlist_is_an_empty_one(tmp_path: Path):
    assert load_watchlist(tmp_path / "nope.yaml") == []


def test_a_hand_kept_list_is_its_key_or_a_bare_list_and_nothing_when_empty(tmp_path: Path):
    """The watchlist, sources and dismissals read the same way: the records under
    the file's key, or the file itself where it is a bare list, and none from an
    empty file or an empty key."""
    path = tmp_path / "watchlist.yaml"
    path.write_text(yaml.safe_dump([watched()]), encoding="utf-8")
    assert [w.name for w in load_watchlist(path)] == ["Example"]
    save_yaml(path, {"watched": None})
    assert load_watchlist(path) == []
    path.write_text("", encoding="utf-8")
    assert load_watchlist(path) == []


def test_a_watch_entry_needs_a_domain():
    with pytest.raises(ValidationError):
        Watched.model_validate(watched(domains=[]))


def read_source(**kw) -> dict:
    return {"url": "https://github.com/someone/a-list", "name": "someone/a-list",
            "checked_on": "2026-08-01", "reason": "carries no provider-level data",
            "reopen_if": "it starts publishing endpoints", **kw}


def test_a_source_verdict_expires_so_a_list_gets_re_read(tmp_path: Path):
    """A source verdict expires like a watch verdict: a list that carried nothing
    can start carrying a provider, and nobody reopens a file of verdicts
    unprompted."""
    path = tmp_path / "sources.yaml"
    save_yaml(path, {"read": [read_source(checked_on="2026-05-01")]})
    (source,) = load_sources(path)
    last_day = date(2026, 5, 1) + timedelta(days=SOURCE_RECHECK_DAYS)
    assert is_source_current(source, last_day)
    assert not is_source_current(source, last_day + timedelta(days=1))


def test_a_source_is_read_less_often_than_an_offer_is_rechecked():
    """Different subject, different clock: a vendor can open a free tier any
    week, but a directory rarely changes what kind of directory it is."""
    assert SOURCE_RECHECK_DAYS > WATCH_RECHECK_DAYS


def test_a_missing_sources_file_is_an_empty_one(tmp_path: Path):
    assert load_sources(tmp_path / "nope.yaml") == []


def test_known_domains_covers_where_an_entry_is_actually_reached():
    """An entry is known at every host it publishes — url, source urls and API
    base — since a catalog may list it at another one (NVIDIA's row is at
    build.nvidia.com, models.dev lists integrate.api.nvidia.com)."""
    e = Entry.model_validate({
        **sample_entry(),
        "url": "https://build.nvidia.com",
        "source_urls": ["https://docs.api.nvidia.com/nim/"],
        "api": {"base_url": "https://integrate.api.nvidia.com/v1", "auth": "api-key"},
    })
    assert known_domains([e]) == {
        "build.nvidia.com", "docs.api.nvidia.com", "integrate.api.nvidia.com",
    }


def test_known_domains_of_an_entry_without_an_api_block():
    e = Entry.model_validate(sample_entry())
    assert known_domains([e]) == {"openrouter.ai"}


def test_known_domains_names_the_owner_on_a_host_many_owners_share():
    """On a host that serves anyone's repository, what the registry knows is the
    owner, and a raw file is the same owner's: a row at github.com/features
    does not cover every repository the scout's GitHub search returns."""
    e = Entry.model_validate({
        **sample_entry(),
        "url": "https://github.com/features/copilot",
        "source_urls": ["https://raw.githubusercontent.com/XiaomiMiMo/MiMo-Code/main/README.md",
                        "https://huggingface.co/docs/inference-providers"],
    })
    assert known_domains([e]) == {
        "github.com/features", "github.com/xiaomimimo", "huggingface.co/docs",
    }


@pytest.mark.parametrize("url, known, covered", [
    # A vendor proposed back at another of its own hosts.
    ("https://api.z.ai/api/paas/v4", {"z.ai"}, True),
    ("https://nvidia.com/en-us/ai/", {"build.nvidia.com"}, True),
    ("https://www.x.ai/pricing", {"x.ai"}, True),
    # A sibling is another product, and a shared suffix is not a shared label.
    ("https://docs.api.nvidia.com/nim", {"integrate.api.nvidia.com"}, False),
    ("https://notz.ai", {"z.ai"}, False),
    # On a shared host only the owner counts, and the host is nobody's parent.
    ("https://github.com/openai/codex-universal", {"github.com/openai"}, True),
    ("https://raw.githubusercontent.com/OpenAI/codex/main/README.md", {"github.com/openai"}, True),
    ("https://github.com/HenriGrimm/Minnow", {"github.com/openai"}, False),
    ("https://github.com/someone/agent", {"docs.github.com"}, False),
    ("https://huggingface.co/spaces/someone/free-llm", {"router.huggingface.co"}, False),
    ("https://huggingface.co/spaces/someone/free-llm", {"huggingface.co/docs"}, False),
])
def test_a_url_is_covered_by_the_vendor_whose_host_or_repository_it_is(url, known, covered):
    assert is_covered(url, known) is covered


def test_a_session_header_is_a_header_name_on_a_row_with_an_endpoint():
    """`api.session_header` names the header in which a vendor wants a stable id
    for each conversation (opencode Zen's x-opencode-session). It is printed as
    a header name wherever the list tells a reader how to connect, so it has to
    be one, and it says how to call a base URL, so the row needs one."""
    d = sample_entry()
    d["api"] = {"base_url": "https://x.ai/v1", "session_header": "x-opencode-session"}
    assert Entry.model_validate(d).api.session_header == "x-opencode-session"
    d["api"] = {"base_url": "https://x.ai/v1", "session_header": "x opencode session"}
    with pytest.raises(ValidationError, match="header name"):
        Entry.model_validate(d)
    d["api"] = {"session_header": "x-opencode-session"}
    with pytest.raises(ValidationError, match="base_url"):
        Entry.model_validate(d)


def test_anthropic_base_url_is_the_base_claude_code_appends_to():
    """The field is what ANTHROPIC_BASE_URL takes, and Claude Code appends
    /v1/messages itself — so a value that already ends in the route would send
    it to /v1/messages/v1/messages; a trailing slash is dropped, so the base is
    written one way."""
    d = sample_entry()
    d["api"] = {"base_url": "https://x.ai/v1", "anthropic_base_url": "https://x.ai/"}
    assert Entry.model_validate(d).api.anthropic_base_url == "https://x.ai"
    d["api"] = {"base_url": "https://x.ai/v1", "anthropic_base_url": "https://x.ai/v1/messages"}
    with pytest.raises(ValidationError, match="appends /v1/messages"):
        Entry.model_validate(d)
    d["api"] = {"base_url": "https://x.ai/v1", "anthropic_base_url": "http://x.ai"}
    with pytest.raises(ValidationError, match="https"):
        Entry.model_validate(d)


def test_a_notice_is_a_dated_word_to_readers_about_a_lane():
    """`api.notice` is the list saying, in its own voice, that a lane it publishes
    does not work as published right now. It is dated, so it can go stale; its
    text is not blank; its link, clicked from the README, is https; and it
    speaks about a base URL, so the row needs one."""
    d = sample_entry()
    d["api"] = {"base_url": "https://x.ai/v1", "auth": "none", "notice": {
        "since": "2026-09-17", "text": "Every client but the vendor's own is refused.",
        "url": "https://github.com/x/x/issues/1"}}
    notice = Entry.model_validate(d).api.notice
    assert notice.since == date(2026, 9, 17)
    assert notice.url == "https://github.com/x/x/issues/1"
    d["api"]["notice"] = {"since": "2026-09-17", "text": "  "}
    with pytest.raises(ValidationError, match="text"):
        Entry.model_validate(d)
    d["api"]["notice"] = {"since": "2026-09-17", "text": "Refused.", "url": "http://x.ai/status"}
    with pytest.raises(ValidationError, match="https"):
        Entry.model_validate(d)
    d["api"] = {"notice": {"since": "2026-09-17", "text": "Refused."}}
    with pytest.raises(ValidationError, match="base_url"):
        Entry.model_validate(d)


def test_a_notice_holds_for_a_bounded_time_and_then_stops():
    """A notice that never expires is a dead lane kept on the page by a note
    nobody revisits. It holds for NOTICE_HOLD_DAYS from its date and not a day
    longer, and an absent notice holds nothing."""
    from freetier_radar.models import NOTICE_HOLD_DAYS, Notice, notice_holds
    notice = Notice(since=date(2026, 9, 17), text="Refused.")
    assert notice_holds(notice, date(2026, 9, 17))
    assert notice_holds(notice, date(2026, 9, 17) + timedelta(days=NOTICE_HOLD_DAYS))
    assert not notice_holds(notice, date(2026, 9, 17) + timedelta(days=NOTICE_HOLD_DAYS + 1))
    assert not notice_holds(None, date(2026, 9, 17))


def test_a_notice_survives_a_registry_round_trip_and_an_absent_one_writes_nothing(tmp_path: Path):
    d = sample_entry()
    d["api"] = {"base_url": "https://x.ai/v1", "auth": "none", "notice": {
        "since": "2026-09-17", "text": "Refused."}}
    plain = sample_entry()
    plain["id"], plain["url"] = "plain", "https://plain.ai"
    plain["api"] = {"base_url": "https://plain.ai/v1"}
    path = tmp_path / "registry.yaml"
    save_registry(path, [Entry.model_validate(d), Entry.model_validate(plain)])
    written = path.read_text(encoding="utf-8")
    assert written.count("notice:") == 1 and "url: null" not in written
    loaded = load_registry(path)
    assert loaded[0].api.notice.text == "Refused." and loaded[1].api.notice is None


def test_a_lane_that_wants_the_client_s_own_user_agent_says_so_on_a_row_with_an_endpoint():
    """OpenCode's client rules ask for two headers, not one: "Identify itself
    with its own user agent, such as my-coding-agent/1.0, rather than a generic
    SDK or HTTP-library name" beside the stable session id. The field says a lane
    asks for that, and it says how to call a base URL, so the row needs one."""
    d = sample_entry()
    d["api"] = {"base_url": "https://x.ai/v1", "client_user_agent": True}
    assert Entry.model_validate(d).api.client_user_agent is True
    d["api"] = {"client_user_agent": True}
    with pytest.raises(ValidationError, match="base_url"):
        Entry.model_validate(d)


def test_a_public_key_is_the_vendor_s_own_key_for_a_keyed_lane_on_a_page_that_prints_it():
    """`api.public_key` is the key a vendor prints for anyone to call its lane
    with (LLM Tech's "shared free trial key"). It is sent as a bearer token, so
    the lane is keyed; key_url is the vendor's page that prints it, which is
    what makes it the vendor's key; and the run calls the first of model_ids
    with it, so there has to be one."""
    d = sample_entry()
    api = {"base_url": "https://x.ai/v1", "key_url": "https://x.ai/docs",
           "model_ids": ["m-1"], "public_key": "lt-trial-123"}
    d["api"] = api
    assert Entry.model_validate(d).api.public_key == "lt-trial-123"
    for broken, match in (({"auth": "none"}, "auth"),
                          ({"key_url": None}, "key_url"),
                          ({"model_ids": []}, "model_ids"),
                          ({"base_url": None}, "base_url"),
                          ({"public_key": "lt trial 123"}, "whitespace"),
                          ({"public_key": ""}, "whitespace")):
        d["api"] = {**api, **broken}
        with pytest.raises(ValidationError, match=match):
            Entry.model_validate(d)


def test_client_limits_round_trip_and_require_the_rechecked_catalog(tmp_path: Path):
    row = sample_entry()
    limits = {"context_tokens": 32768, "output_tokens": 16384,
              "source": row["probe"]["endpoint"]}
    row["api"] = {"base_url": "https://openrouter.ai/api/v1", "model_ids": ["qwen3-coder:free"],
                  "model_limits": {"qwen3-coder:free": limits}}
    entry = Entry.model_validate(row)
    path = tmp_path / "registry.yaml"
    save_registry(path, [entry])
    assert load_registry(path)[0].api.model_limits == entry.api.model_limits
    for broken in ({"context_tokens": 0}, {"output_tokens": True},
                   {"output_tokens": 32769}, {"source": "http://openrouter.ai/api/v1/models"},
                   {"source": "https://openrouter.ai/unchecked"}):
        row["api"]["model_limits"] = {"qwen3-coder:free": {**limits, **broken}}
        with pytest.raises(ValidationError):
            Entry.model_validate(row)
    row["api"]["model_limits"] = {"unlisted": limits}
    with pytest.raises(ValidationError, match="unlisted IDs"):
        Entry.model_validate(row)


def test_refusing_a_bearer_token_is_said_of_a_keyless_lane_only():
    """A keyed lane is always called with a bearer token, so a lane that refuses
    one can only be keyless (OVHcloud's anonymous lane answers "Bearer none"
    with 403 and a bare call with 200). It is written only where set."""
    d = sample_entry()
    d["api"] = {"base_url": "https://x.ai/v1", "auth": "none", "refuses_bearer": True}
    entry = Entry.model_validate(d)
    assert entry.api.refuses_bearer
    assert "refuses_bearer" not in Entry.model_validate(
        {**d, "api": {"base_url": "https://x.ai/v1", "auth": "none"}}).api.model_dump()
    d["api"] = {"base_url": "https://x.ai/v1", "auth": "api-key", "refuses_bearer": True}
    with pytest.raises(ValidationError, match="refuses_bearer"):
        Entry.model_validate(d)


def test_data_use_is_the_vendor_s_word_on_training_with_the_page_it_is_on():
    """What a free offer does with what a reader sends is a claim like the rest:
    yes, opt-out or no, in the vendor's words, on a page anyone can open."""
    d = sample_entry()
    d["data_use"] = {"trains": "yes", "quote": "Content used to improve our products",
                     "url": "https://ai.google.dev/gemini-api/docs/pricing"}
    assert Entry.model_validate(d).data_use.trains == "yes"
    for broken, match in (({"trains": "sometimes"}, "trains"),
                          ({"quote": "  "}, "quote"),
                          ({"quote": 'says "no"'}, "quote"),
                          ({"url": "http://x.ai/privacy"}, "https")):
        d["data_use"] = {"trains": "no", "quote": "We never train on your prompts",
                         "url": "https://x.ai/privacy", **broken}
        with pytest.raises(ValidationError, match=match):
            Entry.model_validate(d)


def test_a_probe_that_follows_an_index_names_a_field_and_reads_a_page():
    """ModelScope serves its docs under a dated release path that the site
    replaces while old paths keep answering, and names the current one in a
    JSON index. `probe.follow` is how a page-keywords probe starts there: the
    endpoint is the index, `field` the dotted path to the value in it and
    `suffix` what goes after it. It is a page the probe reads for keywords, so
    an api-models probe has no use for it."""
    d = sample_entry()
    d["probe"] = {"type": "page-keywords", "endpoint": "https://x.ai/api/doc-index",
                  "keywords": ["200 credits a day"],
                  "follow": {"field": "Data.TargetPrefix", "suffix": "/dist/limits.md"}}
    follow = Entry.model_validate(d).probe.follow
    assert (follow.field, follow.suffix) == ("Data.TargetPrefix", "/dist/limits.md")
    for broken, match in (({"field": "Data..Prefix"}, "dotted path"),
                          ({"field": ""}, "dotted path"),
                          ({"suffix": "dist/limits.md"}, "starts with /")):
        d["probe"]["follow"] = {"field": "Data.TargetPrefix", "suffix": "/dist/limits.md", **broken}
        with pytest.raises(ValidationError, match=match):
            Entry.model_validate(d)
    d = sample_entry()
    d["probe"]["follow"] = {"field": "Data.TargetPrefix"}
    with pytest.raises(ValidationError, match="page-keywords"):
        Entry.model_validate(d)


def test_a_row_folded_into_another_keeps_its_id_and_names_the_row_that_holds_it():
    """A row is never deleted, so a row folded into another keeps its id — the id
    is its page's URL — and `duplicate_of` names the row that holds the service.
    Folding is a reviewer's decision, so the row carries the delisting that says
    why, and no row is folded into itself."""
    d = {**sample_entry(), "id": "mimocode", "duplicate_of": "mimo-code"}
    with pytest.raises(ValidationError, match="delisted"):
        Entry.model_validate(d)
    d["delisted"] = {"on": date(2026, 7, 19), "reason": "the same project as MiMo Code"}
    assert Entry.model_validate(d).duplicate_of == "mimo-code"
    with pytest.raises(ValidationError, match="itself"):
        Entry.model_validate({**d, "duplicate_of": "mimocode"})


def test_folded_into_is_the_row_the_registry_holds_the_service_under():
    from freetier_radar.models import folded_into
    holder = Entry.model_validate({**sample_entry(), "id": "mimo-code", "name": "MiMo Code"})
    folded = Entry.model_validate({
        **sample_entry(), "id": "mimocode", "name": "MiMoCode", "duplicate_of": "mimo-code",
        "delisted": {"on": date(2026, 7, 19), "reason": "the same project as MiMo Code"}})
    assert folded_into([holder, folded], folded) is holder
    assert folded_into([holder, folded], holder) is None
    assert folded_into([folded], folded) is None


def test_an_id_is_the_most_specific_family_that_names_it():
    """`family_names` reads a family as a substring of the squashed id, so
    `glm-5` names coding-glm-5.2-free and `glm-5.3` names zai-org/GLM-5.3-Flash;
    among a row's families, an id is the most specific one's (see `id_family`)."""
    families = ["glm-5", "glm-5.2", "glm-5.3", "glm-5.3-flash"]
    assert id_family(families, "coding-glm-5.2-free") == "glm-5.2"
    assert id_family(families, "zai-org/GLM-5.3-Flash") == "glm-5.3-flash"
    assert id_family(families, "z-ai/glm-5.3:free") == "glm-5.3"
    assert id_family(families, "coding-glm-5-free") == "glm-5"
    assert id_family(families, "moonshotai/kimi-k3") is None


def test_a_sentence_names_a_model_as_a_reader_writes_it():
    """Prose spells a model as its vendor does — "Nemotron 3 Ultra", "MiMo-V2.5",
    "GLM 5.3 Flash" — so case and separators go, but the name stays a whole
    word: "GLM-5.3" is not glm-5, whose version it goes on past, and
    "X Minimal" is no x-mini."""
    assert prose_names("Big Pickle, Nemotron 3 Ultra and MiMo-V2.5", "nemotron-3-ultra")
    assert prose_names("Big Pickle, Nemotron 3 Ultra and MiMo-V2.5", "mimo-v2.5")
    assert prose_names("GLM 5.3 Flash by default", "glm-5.3-flash")
    assert prose_names("GLM-5.3-Flash", "glm-5.3")
    assert not prose_names("GLM-5.3 and Kimi K3", "glm-5")
    assert not prose_names("X Minimal aside", "x-mini")
    assert not prose_names("Claude and open-weight models", "claude-sonnet-4.5")
    assert prose_names("on Qwen3.8 27B.", "qwen3.8-27b")



def test_an_id_that_drops_a_mixture_of_experts_active_parameters_is_the_familys():
    """Regolo's id for Qwen3.5-122B-A10B is qwen3.5-122b. The active-parameter
    count may be left off — never swapped for another."""
    from freetier_radar.models import family_names
    assert family_names("qwen3.5-122b-a10b", "qwen3.5-122b")
    assert family_names("gemma-4-26b-a4b", "google/gemma-4-26b-it")
    assert family_names("qwen3.5-122b-a10b", "Qwen/Qwen3.5-122B-A10B-FP8")
    assert not family_names("qwen3-30b-a3b", "qwen3-30b-a6b")
    assert not family_names("qwen3.5-122b-a10b", "qwen3.5-12b")


@pytest.mark.parametrize("taken", ["index", "checked"])
def test_a_row_id_is_never_the_name_of_a_provider_page_that_is_no_rows(taken):
    """A row's page is providers/<id>.md, beside the index of every provider and
    the page of services checked; a row by either name would overwrite one."""
    with pytest.raises(ValidationError, match="is not a row's page name"):
        Entry.model_validate({**sample_entry(), "id": taken})
