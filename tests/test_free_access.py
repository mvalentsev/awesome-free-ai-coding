from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from freetier_radar.models import Entry, load_registry, save_registry
from freetier_radar.render import (
    build_context, build_index, build_litellm_config, build_models_index,
    build_opencode_config, build_provider_page, build_site_context,
)
from pathlib import Path

DAY = date(2026, 10, 1)
PAID = {"initial_payment_usd": 5, "until": "2026-10-06T23:59:00+03:00",
        "source": "https://vendor.example/promo"}


def entry(**changes):
    data = {"id": "gateway", "name": "Gateway", "url": "https://vendor.example",
            "category": "aggregator", "offering": "A free model gateway",
            "free_part": "models", "models": [{"family": "steady"}, {"family": "preview"}],
            "api": {"base_url": "https://vendor.example/v1", "model_ids": ["steady", "preview"],
                    "model_access": {"preview": PAID}},
            "probe": {"type": "api-models", "endpoint": "https://vendor.example/v1/models",
                      "require_zero_price": True},
            "first_seen": DAY, "last_verified": DAY, **changes}
    return Entry.model_validate(data)


def test_payment_and_deadline_survive_the_registry_and_reach_consumers(tmp_path):
    """Dropping access metadata would silently advertise paid-unlock access as unfunded."""
    path = tmp_path / "registry.yaml"
    save_registry(path, [entry()])
    row = load_registry(path)[0]
    data = build_index([row], DAY)
    assert data["entries"][0]["api"].get("model_access") == {"preview": PAID}
    for text in (build_provider_page(row, [], DAY), build_models_index([row], DAY)):
        assert "$5" in text and "2026-10-06" in text
    models = build_opencode_config([row], DAY)["provider"]["gateway"]["models"]
    assert "$5" in models["preview"]["name"] and "2026-10-06" in models["preview"]["name"]
    assert "$5" not in models["steady"]["name"]


@pytest.mark.parametrize("access", [
    {**PAID, "initial_payment_usd": 0},
    {**PAID, "initial_payment_usd": -1},
    {**PAID, "until": "2026-10-06T23:59:00"},
    {**PAID, "source": "http://vendor.example/promo"},
])
def test_invalid_access_conditions_cannot_be_published(access):
    with pytest.raises(ValidationError):
        entry(api={"base_url": "https://vendor.example/v1", "model_ids": ["steady", "preview"],
                   "model_access": {"preview": access}})


def test_upfront_payment_rows_follow_unfunded_rows_at_equal_rank():
    rows = [entry(id="a-paid", name="A Paid", access={"initial_payment_usd": 1,
                   "source": "https://vendor.example/pricing"}, api={"model_ids": ["steady"]}),
            entry(id="z-free", name="Z Free")]
    ctx = build_context(rows, DAY)
    assert [r["name"] for section in ctx["sections"] for r in section["rows"]] == ["Z Free", "A Paid"]


def test_paid_unlock_does_not_enter_an_automatic_free_fallback_pool():
    row = entry(models=[{"family": "steady", "tier": "strong", "aa_model": "steady"},
                        {"family": "preview", "tier": "strong", "aa_model": "preview"}])
    deployments = build_litellm_config([row], DAY)["model_list"]
    assert any(d["model_name"] == "gateway/preview" for d in deployments)
    pool = [d["litellm_params"]["model"] for d in deployments if d["model_name"] == "free/strong"]
    assert pool == ["openai/steady"]


def test_real_render_expires_at_the_vendor_instant_and_preserves_evidence(tmp_path):
    """A timed promotion must disappear from every generated callable surface, not just its label."""
    from freetier_radar.render import render_repository

    path = tmp_path / "registry.yaml"
    save_registry(path, [entry()])
    before = datetime(2026, 10, 6, 20, 58, 59, tzinfo=timezone.utc)
    render_repository(path, Path("templates"), tmp_path, today=before.date(), now=before)
    assert "preview" in build_opencode_config(load_registry(path), before.date())["provider"]["gateway"]["models"]
    after = datetime(2026, 10, 6, 20, 59, 0, tzinfo=timezone.utc)
    render_repository(path, Path("templates"), tmp_path, today=after.date(), now=after)
    row = load_registry(path)[0]
    assert row.api.model_ids == ["steady"]
    assert [m.family for m in row.models] == ["steady"]
    assert "preview" in row.api.ignored_ids
    assert row.api.model_access["preview"].until.isoformat() == "2026-10-06T23:59:00+03:00"
    assert "gateway/preview" not in (tmp_path / "configs/litellm.yaml").read_text()
    assert "preview" not in build_opencode_config([row], after.date())["provider"]["gateway"]["models"]
    assert '"event":"models"' in (tmp_path / "history.jsonl").read_text().replace(" ", "")


def test_expiry_keeps_a_family_with_another_live_id_and_ignores_broader_names():
    from freetier_radar.models import expire_entries, family_access
    row = entry(models=[{"family": "glm-5.3"}, {"family": "glm-5.3-flash"}], api={
        "base_url": "https://vendor.example/v1",
        "model_ids": ["glm-5.3", "glm-5.3-flash-free", "glm-5.3-flash-promo"],
        "model_access": {"glm-5.3-flash-promo": PAID}})
    assert family_access(row, "glm-5.3-flash") is None
    current = expire_entries([row], datetime(2026, 10, 7, tzinfo=timezone.utc))[0]
    assert [m.family for m in current.models] == ["glm-5.3", "glm-5.3-flash"]
    assert current.api.model_ids == ["glm-5.3", "glm-5.3-flash-free"]


def test_expired_only_lane_cannot_emit_empty_client_defaults(tmp_path):
    from freetier_radar.models import expire_entries
    from freetier_radar.render import build_claude_code_sh, codex_ready
    row = entry(models=[{"family": "preview"}], api={
        "base_url": "https://vendor.example/v1", "model_ids": ["preview"],
        "model_access": {"preview": PAID}, "anthropic_base_url": "https://vendor.example",
        "codex": {"base_url": "https://vendor.example/v1", "source": "https://vendor.example/codex",
                  "quote": "Configure Codex for this gateway"}})
    current = expire_entries([row], datetime(2026, 10, 7, tzinfo=timezone.utc))[0]
    assert "gateway" not in build_opencode_config([current], date(2026, 10, 7))["provider"]
    assert not codex_ready(current)
    assert 'claude-gateway()' not in build_claude_code_sh([current], date(2026, 10, 7))


def test_short_promotion_gets_a_discoverable_model_page_immediately():
    from freetier_radar.render import model_pages
    assert "preview" in model_pages([entry()], [], DAY)


def test_model_conditions_appear_once_next_to_the_callable_id():
    from freetier_radar.render import build_model_page
    row = entry(limits="Steady has a daily allowance shared with other free models. "
                      "Preview is available only after an initial payment, until the published deadline. "
                      "Paid usage draws from a prepaid balance. Requests above the free allowance "
                      "require paid fallback to be enabled; creating extra keys does not increase the allowance.")
    page = build_model_page("preview", [row], [], DAY)
    body = page.split("{% raw %}", 1)[1]
    assert body.count("$5") == 1
    assert body.count("2026-10-06 23:59+03:00") == 1
    assert "`preview`: requires $5" in body
    assert "<summary>Provider-wide limits</summary>" in body
    assert row.limits in body


def test_compact_list_labels_keep_payment_and_fee_with_full_details_on_the_page():
    from freetier_radar.models import access_words
    row = entry(api={"base_url": "https://vendor.example/v1", "model_ids": ["steady", "preview"],
                     "model_access": {"preview": {**PAID, "topup_fee_percent": 8}}})
    rendered = next(r for s in build_site_context([row], DAY)["sections"] for r in s["rows"])
    label = rendered["models"][1]["access"]
    assert label == "requires $5 top-up + 8% fee; until 2026-10-06"
    assert build_index([row], DAY)["entries"][0]["access_labels"]["models"]["preview"] == label
    assert access_words(row.api.model_access["preview"]) == (
        "requires $5 one-time top-up + 8% fee; free until 2026-10-06 23:59+03:00")


def test_payment_is_disclosed_even_when_the_family_has_no_callable_id():
    from freetier_radar.render import build_model_page
    row = entry(access={"initial_payment_usd": 5, "source": PAID["source"]},
                api={"base_url": "https://vendor.example/v1", "model_ids": ["steady"]})
    page = build_model_page("preview", [row], [], DAY)
    assert "requires $5 one-time top-up" in page
    assert "Callable ids: the row lists none for this model" in page


def test_bars_reports_an_unlisted_dated_promotion_without_waiting_two_weeks():
    from freetier_radar.bars import waiting
    row = entry(models=[{"family": "steady"}])
    pending = waiting([row], {}, DAY)
    assert len(pending) == 1 and pending[0].model_id == "preview"
    assert pending[0].due_on == DAY


def test_bars_never_promotes_an_expired_id_before_the_publication_writer_runs():
    from freetier_radar.bars import waiting
    row = entry(models=[{"family": "steady"}])
    assert waiting([row], {}, date(2026, 10, 7)) == []


def test_access_sources_are_reread_and_deduplicated():
    from freetier_radar.quotes import row_urls
    row = entry(source_urls=[PAID["source"]], access={"initial_payment_usd": 1,
                "source": "https://vendor.example/pricing"}, api={"model_ids": ["preview"],
                "model_access": {"preview": {"source": PAID["source"], "until": PAID["until"]}}})
    urls = row_urls(row)
    assert urls.count(PAID["source"]) == 1
    assert "https://vendor.example/pricing" in urls


def test_expire_only_command_is_a_noop_before_any_deadline(tmp_path):
    import subprocess
    import sys
    path = tmp_path / "registry.yaml"
    future = {**PAID, "until": "2099-10-06T23:59:00+03:00"}
    save_registry(path, [entry(api={"base_url": "https://vendor.example/v1",
                                  "model_ids": ["steady", "preview"], "model_access": {"preview": future}})])
    before = path.read_bytes()
    result = subprocess.run([sys.executable, "-m", "freetier_radar.render", "--registry", str(path),
                             "--out", str(tmp_path / "README.md"), "--expire-only"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert path.read_bytes() == before
    assert not (tmp_path / "README.md").exists()


def test_client_defaults_choose_an_unfunded_id_even_if_the_paid_id_is_first():
    from freetier_radar.render import build_codex_profile, build_claude_code_sh
    row = entry(api={"base_url": "https://vendor.example/v1", "model_ids": ["preview", "steady"],
                     "model_access": {"preview": PAID}, "anthropic_base_url": "https://vendor.example",
                     "codex": {"base_url": "https://vendor.example/v1", "source": "https://vendor.example/codex",
                               "quote": "Configure Codex for this gateway"}})
    assert 'model = "steady"' in build_codex_profile(row)
    assert 'ANTHROPIC_MODEL="steady"' in build_claude_code_sh([row], DAY)


@pytest.mark.parametrize("client_only", [False, True])
def test_expired_last_id_can_be_saved_and_loaded_without_losing_conditions(tmp_path, client_only):
    from freetier_radar.models import expire_entries
    lane = {"model_ids": ["preview"], "model_access": {"preview": PAID}}
    changes = {"models": [{"family": "preview"}]}
    if client_only:
        changes.update(api=None, client_lane=lane)
    else:
        lane.update(base_url="https://vendor.example/v1", codex={
            "base_url": "https://vendor.example/v1", "source": "https://vendor.example/codex",
            "quote": "Configure Codex for this gateway"})
        changes["api"] = lane
    current = expire_entries([entry(**changes)], datetime(2026, 10, 7, tzinfo=timezone.utc))
    path = tmp_path / "registry.yaml"
    save_registry(path, current)
    row = load_registry(path)[0]
    block = row.api or row.client_lane
    assert block.model_ids == [] and "preview" in block.ignored_ids
    assert block.model_access["preview"].initial_payment_usd == 5
    assert build_index([row], date(2026, 10, 7))["entries"][0]["archived"]
    assert row.first_seen == DAY and row.last_verified == DAY


async def test_expired_codex_lane_still_checks_the_catalog_without_calling_an_empty_model():
    import httpx
    import respx
    from freetier_radar.models import expire_entries
    from freetier_radar.prober import probe_entry, ProbeStatus
    row = entry(models=[{"family": "preview"}], api={
        "base_url": "https://vendor.example/v1", "model_ids": ["preview"],
        "model_access": {"preview": PAID}, "codex": {
            "base_url": "https://vendor.example/v1", "source": "https://vendor.example/codex",
            "quote": "Configure Codex for this gateway"}})
    current = expire_entries([row], datetime(2026, 10, 7, tzinfo=timezone.utc))[0]
    with respx.mock(assert_all_called=True) as routes:
        routes.get(current.probe.endpoint).respond(200, json={"data": [
            {"id": "preview", "pricing": {"prompt": "0.1", "completion": "0.2"}}]})
        async with httpx.AsyncClient() as client:
            result = await probe_entry(client, current, backoff=0)
    assert result.status is ProbeStatus.PASS


def test_model_deadline_does_not_erase_a_provider_payment_requirement():
    from freetier_radar.models import id_access, family_access, requires_payment
    row = entry(access={"initial_payment_usd": 1, "payment_kind": "card verification",
                        "source": "https://vendor.example/pricing"}, api={
        "base_url": "https://vendor.example/v1", "model_ids": ["preview"],
        "model_access": {"preview": {"until": PAID["until"], "source": PAID["source"]}}})
    assert requires_payment(row) and requires_payment(row, "preview")
    assert id_access(row, "preview").payment_kind == "card verification"
    assert family_access(row, "preview").initial_payment_usd == 1


def test_delayed_expiry_records_the_vendor_deadline_day_instead_of_the_run_day():
    from freetier_radar.models import expire_entries
    row = entry(models=[{"family": "preview"}], api={
        "model_ids": ["preview"], "model_access": {"preview": PAID}})
    current = expire_entries([row], datetime(2026, 10, 8, tzinfo=timezone.utc))[0]
    assert current.retired_on == date(2026, 10, 6)


def test_scoped_payment_cannot_replace_or_hide_a_whole_offer_payment():
    with pytest.raises(ValidationError, match="whole-offer payment"):
        entry(access={"initial_payment_usd": 10, "source": "https://vendor.example/pricing"})


def test_model_name_list_and_monthly_digest_disclose_the_same_conditions():
    from freetier_radar.render import build_llms_txt
    from freetier_radar.announce import build_digest
    row = entry()
    llms = build_llms_txt([row], DAY)
    provider_line = next(x for x in llms.splitlines() if x.startswith('- [Gateway]'))
    model_line = next(x for x in llms.splitlines() if x.startswith('- [preview]'))
    _, digest = build_digest([row], [], DAY)
    for text in (provider_line, model_line, digest):
        assert '$5' in text and '2026-10-06 23:59+03:00' in text


def test_real_expiry_command_archives_an_ended_offer_and_keeps_its_page(tmp_path):
    import subprocess
    import sys
    from datetime import timedelta
    from freetier_radar.render import render_repository
    from freetier_radar.history import archive_reason
    ended = datetime.now(timezone.utc) - timedelta(seconds=5)
    access = {**PAID, "until": ended.isoformat()}
    row = entry(models=[{"family": "preview"}], first_seen=ended.date(), last_verified=ended.date(),
                api={"base_url": "https://vendor.example/v1", "model_ids": ["preview"],
                     "model_access": {"preview": access}})
    path = tmp_path / "registry.yaml"
    save_registry(path, [row])
    before = ended - timedelta(seconds=1)
    render_repository(path, Path("templates"), tmp_path, today=before.date(), now=before)
    result = subprocess.run([sys.executable, '-m', 'freetier_radar.render', '--registry', str(path),
                             '--out', str(tmp_path / 'README.md'), '--expire-only'],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    current = load_registry(path)[0]
    assert current.retired_on == ended.date()
    assert archive_reason(current, ended.date()).startswith('documented free promotions ended')
    assert 'no longer free' in (tmp_path / 'models/preview.md').read_text()
    assert '"archived"' in (tmp_path / 'history.jsonl').read_text()
    assert 'gateway' not in build_opencode_config([current], ended.date())['provider']
