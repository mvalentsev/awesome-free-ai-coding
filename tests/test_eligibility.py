"""Current free-plan eligibility cannot be inferred from a model's existence."""
import httpx
import pytest
import respx
import json
import yaml

from freetier_radar.prober import ProbeStatus, probe_entry
from test_page_catalog import entry, page, session_catalog_data


@respx.mock
async def test_matching_promotion_copy_without_scoped_eligibility_is_not_verified():
    data = session_catalog_data()
    quote = "Beta is free in the US, one session a day for every account."
    source = "https://vendor.example/promotion"
    data["conditions"]["session"] = {"kind": "free-session", "quote": quote, "source": source}
    data["models"][1].update(hours=None, limited=False, condition="session", listed=True)
    e = entry(data)
    respx.get(data["source"]).respond(200, text=page(rows="<li>Unlimited hrs Alpha</li>", limited="Alpha"))
    respx.get(source).respond(200, text=quote)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, e, attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS
    assert "eligibility" in result.detail


@respx.mock
async def test_an_offer_sentence_keeps_its_scope_across_inline_links_and_typography():
    from freetier_radar.models import Entry
    row = Entry.model_validate({
        "id": "vendor", "name": "Vendor", "url": "https://vendor.example",
        "category": "trial", "free_part": "sum", "offering": "No-card trial",
        "first_seen": "2026-09-01", "last_verified": "2026-10-05",
        "probe": {"type": "page-keywords", "endpoint": "https://vendor.example/plans",
                  "keywords": ["The vendor's trial includes $5 of usage."]}})
    respx.get(row.probe.endpoint).respond(200, text="<p>The vendor’s <a href='/trial'>trial</a> includes $5 of usage.</p>")
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, row, attempts=1, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_source_review_rejects_priced_models_beside_matching_quotes(tmp_path, monkeypatch):
    from freetier_radar import review
    from freetier_radar.models import Entry
    row = Entry.model_validate({
        "id": "vendor", "name": "Vendor", "url": "https://vendor.example",
        "category": "api-free-tier", "free_part": "models", "offering": "Free models",
        "limits": "“Free models are available to all.”", "source_urls": ["https://vendor.example/faq"],
        "first_seen": "2026-09-01", "last_verified": "2026-10-05",
        "models": [{"family": "alpha"}],
        "api": {"base_url": "https://api.vendor.example/v1", "model_ids": ["alpha"]},
        "probe": {"type": "api-models", "endpoint": "https://api.vendor.example/v1/models",
                  "require_zero_price": True}})
    bundle = review.Bundle(tmp_path / "evidence", tmp_path)
    bundle.save("scope", {"base": "b" * 40, "sha": "a" * 40, "rows": ["vendor"], "paths": []})
    monkeypatch.setattr(review, "blob", lambda *args: yaml.safe_dump({"entries": [row.model_dump(mode="json")]}).encode())
    respx.get(row.probe.endpoint).respond(200, json={"data": [{"id": "alpha", "pricing": {"prompt": "1", "completion": "1"}}]})
    respx.get(row.source_urls[0]).respond(200, text="Free models are available to all.")
    result = await review.sources(bundle, [])
    assert all(q["found"] for q in result["quotes"])
    assert not result["passed"]
    assert not result["model_checks"][0]["passed"]


@pytest.mark.parametrize("value,expected", [("Free", ProbeStatus.PASS),
                                           ("Paid plan", ProbeStatus.STALE_MODELS)])
@respx.mock
async def test_eligibility_checks_the_free_cell_beside_the_same_paid_model(value, expected):
    data = session_catalog_data()
    quote = "Beta is free in the US, one session a day for every account."
    source = "https://vendor.example/plans"
    data["conditions"]["session"] = {"kind": "free-session", "quote": quote, "source": source,
        "eligibility": {"plan": "Free", "value": "Free", "table": {
            "headers": ["Model", "Free", "Starter"], "column": "Free", "rows": ["Beta"]}}}
    data["models"][1].update(hours=None, limited=False, condition="session", listed=True)
    respx.get(data["source"]).respond(200, text=page(rows="<li>Unlimited hrs Alpha</li>", limited="Alpha"))
    data["conditions"]["session"]["eligibility"]["plan_price"] = {
        "headers": ["Model", "Free", "Starter"], "column": "Free", "rows": ["Monthly price"]}
    respx.get(source).respond(200, text=quote + f'''<table>
        <tr><th>Model</th><th>Free</th><th>Starter</th></tr>
        <tr><td>Monthly price</td><td>$0</td><td>$8</td></tr>
        <tr><td>Beta</td><td>{value}</td><td>1 hr</td></tr></table>''')
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(data), attempts=1, backoff=0)
    assert result.status is expected


@respx.mock
async def test_a_free_model_cell_does_not_make_a_recurring_paid_plan_free():
    data = session_catalog_data()
    quote = "Beta gets one free session daily."
    source = "https://vendor.example/plans"
    data["conditions"]["session"] = {"kind": "free-session", "quote": quote, "source": source,
        "eligibility": {"plan": "Free", "value": "Free", "table": {
            "headers": ["Model", "Free"], "column": "Free", "rows": ["Beta"]}}}
    data["models"][1].update(hours=None, limited=False, condition="session", listed=True)
    data["conditions"]["session"]["eligibility"]["plan_price"] = {
        "headers": ["Model", "Free"], "column": "Free", "rows": ["Monthly price"]}
    respx.get(data["source"]).respond(200, text=page(rows="<li>Unlimited hrs Alpha</li>", limited="Alpha"))
    respx.get(source).respond(200, text=quote + '''<table>
        <tr><th>Model</th><th>Free</th></tr>
        <tr><td>Monthly price</td><td>$8</td></tr>
        <tr><td>Beta</td><td>Free</td></tr></table>''')
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(data), attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS


@pytest.mark.parametrize("markup", ["", "<tr><td>Beta</td><td>Free</td></tr>" * 2])
@respx.mock
async def test_missing_or_duplicate_free_cells_do_not_verify(markup):
    data = session_catalog_data()
    quote = "Beta gets one free session daily."
    source = "https://vendor.example/plans"
    data["conditions"]["session"] = {"kind": "free-session", "quote": quote, "source": source,
        "eligibility": {"plan": "Free", "value": "Free", "table": {
            "headers": ["Model", "Free"], "column": "Free", "rows": ["Beta"]}}}
    data["models"][1].update(hours=None, limited=False, condition="session", listed=True)
    data["conditions"]["session"]["eligibility"]["plan_price"] = {
        "headers": ["Model", "Free"], "column": "Free", "rows": ["Monthly price"]}
    respx.get(data["source"]).respond(200, text=page(rows="<li>Unlimited hrs Alpha</li>", limited="Alpha"))
    respx.get(source).respond(200, text=quote + '<table><tr><th>Model</th><th>Free</th></tr><tr><td>Monthly price</td><td>$0</td></tr>' + markup + '</table>')
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(data), attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS
