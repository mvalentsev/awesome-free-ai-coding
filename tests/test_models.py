from datetime import date, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

import yaml

from freetier_radar.models import (SOURCE_RECHECK_DAYS, WATCH_RECHECK_DAYS, Entry, Watched,
                                    is_anchor, is_covered, is_source_current, known_domains,
                                    load_registry, load_sources, load_watchlist, save_registry,
                                    watch_match)


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
            {"family": "deepseek", "tier": "frontier", "released": "2025-12"},
            {"family": "qwen3-coder", "tier": "strong", "released": "2025-07"},
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
    """Generic words alone outlive the offer — mimo-code kept passing on a
    README that still advertised a channel the client had already cut off."""
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
    """Every one of these was live in the registry, on a page that would keep
    serving them for months after the free tier was withdrawn — `hobby` and
    `free quota` outlive any offer, and the first version of the rule only
    caught the handful of phrases listed verbatim in GENERIC_KEYWORDS."""
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
    """A row taken off the list stays in the registry as the record of what the
    list once published, and on its first day the list published probes
    anchored on the bare word "free". No probe reads a delisted row, so the
    anchor rule — a rule about what may keep a live row live — has nothing
    left to protect there; rewriting the old keywords would falsify the record."""
    seed = {**sample_entry(), "probe": {"type": "page-keywords", "endpoint": "https://x.ai",
                                        "keywords": ["free"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(seed)
    delisted = {**seed, "delisted": {"on": date(2026, 7, 19), "reason": "nothing behind the claim"}}
    assert Entry.model_validate(delisted).probe.keywords == ["free"]


def test_a_delisting_says_why():
    """The reason is what the Archive shows beside the row. A delisting without
    one is a row that vanished with extra steps."""
    with pytest.raises(ValidationError):
        Entry.model_validate({**sample_entry(), "delisted": {"on": date(2026, 7, 19), "reason": "  "}})


def test_zero_price_flag_belongs_to_a_models_api():
    """A pricing page publishes no machine-readable prices, so the flag would sit
    there doing nothing — silent for a check whose job is to catch a price."""
    misplaced = {**sample_entry(), "probe": {"type": "page-keywords",
                                             "endpoint": "https://x.ai/pricing",
                                             "keywords": ["solar-mini", "free"],
                                             "require_zero_price": True}}
    with pytest.raises(ValidationError):
        Entry.model_validate(misplaced)

    on_the_api = {**sample_entry(), "probe": {**sample_entry()["probe"], "require_zero_price": True}}
    assert Entry.model_validate(on_the_api).probe.require_zero_price


def test_ignored_ids_belong_beside_a_price_list():
    """Same reasoning as require_zero_price: the list is read where the probe
    compares a catalog's zero-priced rows with api.model_ids and nowhere else.
    On a page probe, or on a catalog whose prices are not read, it would sit in
    the registry recording a decision nothing ever acts on."""
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


def test_ignored_ids_are_written_only_where_set(tmp_path: Path):
    """Every api block in the registry already carries model_ids and note, empty
    or not. A list that means something on eight rows should not add a blank
    line to the other twenty-six."""
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
    """A lane is the key of a JSON document whose array is read as the catalog. A
    page-keywords probe reads the response as text, so there the field would sit
    in the registry doing nothing — the silence the other probe validators
    refuse."""
    on_a_page = {**sample_entry(), "probe": {"type": "page-keywords",
                                             "endpoint": "https://x.ai/pricing",
                                             "keywords": ["solar-mini", "free"],
                                             "lane": "free"}}
    with pytest.raises(ValidationError):
        Entry.model_validate(on_a_page)

    on_the_api = {**sample_entry(), "probe": {**sample_entry()["probe"], "lane": "free"}}
    assert Entry.model_validate(on_the_api).probe.lane == "free"


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
    """The whole difference between this file and blocklist.yaml. A verdict that
    kept suppressing forever would be a blocklist entry with softer wording."""
    path = tmp_path / "watchlist.yaml"
    save_yaml(path, {"watched": [watched(checked_on="2026-05-01")]})
    wl = load_watchlist(path)
    last_day = date(2026, 5, 1) + timedelta(days=WATCH_RECHECK_DAYS)
    assert watch_match("example.ai", wl, last_day) is not None
    assert watch_match("example.ai", wl, last_day + timedelta(days=1)) is None


def test_a_missing_watchlist_is_an_empty_one(tmp_path: Path):
    assert load_watchlist(tmp_path / "nope.yaml") == []


def test_a_watch_entry_needs_a_domain():
    with pytest.raises(ValidationError):
        Watched.model_validate(watched(domains=[]))


def read_source(**kw) -> dict:
    return {"url": "https://github.com/someone/a-list", "name": "someone/a-list",
            "checked_on": "2026-08-01", "reason": "carries no provider-level data",
            "reopen_if": "it starts publishing endpoints", **kw}


def test_a_source_verdict_expires_so_a_list_gets_re_read(tmp_path: Path):
    """watchlist.yaml's clock, one level up. A list that carried nothing in
    August can be carrying a provider by February, and nobody re-opens a file
    of verdicts on their own."""
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
    """NVIDIA is the case that made this a function. The registry reaches it at
    build.nvidia.com while models.dev lists integrate.api.nvidia.com, and a
    known-domain set built from the url alone reported our own entry as a new
    lead. An entry is known at every host it publishes."""
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
    """Copilot's row lives at github.com/features/copilot, so github.com was a
    known domain — and every hit the scout's GitHub search returns is a
    repository on github.com. Measured 2026-09-14: five repository hits for the
    five discovery queries, none of them kept. On a host that serves anyone's
    repository, what the registry knows is the owner, and a raw file is the
    same owner's."""
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
    # A vendor proposed back at another of its own hosts: nvidia-nim-free and
    # zai-free reached a live probe on 2026-09-14 that way.
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
    for each conversation — opencode Zen's x-opencode-session, without which
    its free ids have answered 400 MissingSessionID since 2026-09-07. It is
    read as a header name wherever the list tells a reader how to connect, so
    it has to be one, and it says how to call a base URL, so the row needs one."""
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
    it to /v1/messages/v1/messages, and a trailing slash would double the one
    in between."""
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
    does not work as published right now while it waits for the vendor to say
    why — opencode Zen started refusing every client but OpenCode on 2026-09-17
    with no word from OpenCode. It is dated, because a note like this must be
    able to go stale; it links where the problem is followed, and a link a reader
    clicks from the README has to be https; and it speaks about a base URL, so
    the row needs one."""
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
    """LLM Tech's quickstart prints "a shared free trial key" for anyone to call
    its lane with, so a reader needs no account — only the key the vendor hands
    everyone. It is sent as a bearer token, so the lane is a keyed one (a lane
    with auth none has no key to publish); it needs key_url, the vendor's page
    that prints it, because that page is what makes it the vendor's key and not
    a shared one; and the run calls the lane with it on the first of model_ids,
    so there has to be one."""
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
    """Two rows named one project for two months: MiMoCode, a placeholder from
    the list's first day at a domain that has never resolved, and MiMo Code,
    Xiaomi's agent, whose own README prints the name as one word. A row is
    never deleted, so the second one keeps its id — the id is its page's URL —
    and `duplicate_of` names the row that holds the service. Folding is a
    reviewer's decision, so the row carries the delisting that says why, and no
    row is folded into itself."""
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
