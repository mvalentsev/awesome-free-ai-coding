"""Page catalogs distinguish a spending wallet from independently free offers."""
import json
import re
from datetime import date, datetime, timezone, timedelta

import httpx
import pytest
import respx

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, probe_entry


def catalog_data():
    return {
        "source": "https://vendor.example/pricing", "unit": "Credits",
        "period": "day", "example_budget": "us",
        "read": {"table_heading": "Model hours", "models_question": "Which models?",
                 "budgets_question": "How do credits work?",
                 "limited_question": "What is limited mode?",
                 "limited_prefix": "limited mode includes", "limited_suffix": ", with"},
        "budgets": [{"id": "us", "amount": 100, "countries": ["US"]},
                    {"id": "other", "amount": 25, "scope": "else"},
                    {"id": "vpn", "amount": 20, "scope": "vpn"}],
        "conditions": {"plan": {"kind": "paid", "quote": "Gamma needs a paid plan."}},
        "models": [
            {"name": "Alpha", "model": {"family": "alpha"}, "hours": "unlimited",
             "limited": True, "first_free": {"on": "2026-09-01",
                                              "source": "https://vendor.example/launch"}},
            {"name": "Beta", "model": {"family": "beta"}, "hours": 10, "limited": True},
            {"name": "Gamma", "model": {"family": "gamma"}, "condition": "plan"},
        ],
    }


def entry(data=None):
    return Entry.model_validate({
        "id": "vendor", "name": "Vendor", "url": "https://vendor.example",
        "category": "agent-cli", "free_part": "models", "offering": "Ad-funded agent",
        "first_seen": "2026-09-01", "last_verified": "2026-10-05",
        "probe": {"type": "page-keywords", "endpoint": "https://vendor.example/pricing",
                  "keywords": ["Credits every day for free"]},
        "page_catalog": data or catalog_data(),
    })


def session_catalog_data():
    data = catalog_data()
    data["limited_allowance"] = "6 one-hour sessions per day"
    data["models"][1]["first_free"] = {"on": "2026-09-01", "source": data["source"]}
    return data


def test_uniform_session_allowance_is_a_free_lane_beside_the_spending_wallet():
    data = session_catalog_data()
    data["models"][1]["listed"] = True
    e = entry(data)
    assert [m.family for m in e.models] == ["beta"]
    assert [n.family for n in e.newcomers] == ["alpha"]
    assert entry().models == []
    assert not e.page_catalog.independently_free(e.page_catalog.models[2])


@pytest.mark.parametrize("surface", ["site", "readme", "provider", "index", "model"])
def test_shared_session_allowance_stays_in_limits_instead_of_model_labels(tmp_path, surface):
    from pathlib import Path
    from freetier_radar.models import save_registry
    from freetier_radar.render import (build_index, build_model_page, build_provider_page,
                                     render_readme, render_site)
    data = session_catalog_data()
    for model in data["models"][:2]:
        model["listed"] = True
    e = entry(data)
    today = date(2026, 10, 6)
    allowance = data["limited_allowance"]
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [e])
    if surface == "site":
        text = render_site(reg, Path("templates"), tmp_path / "index.html", today=today)
        model_text = re.search(r'<td class="models"[^>]*>(.*?)</td>', text, re.S).group(1)
    elif surface == "readme":
        text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=today)
        model_text = next(line for line in text.splitlines() if line.startswith('- **[Vendor]'))
    elif surface == "provider":
        text = build_provider_page(e, [], today, registry=[e], pages={"alpha", "beta"})
        model_text = text.split("## Free models\n", 1)[1].split("## Limits,", 1)[0]
    elif surface == "index":
        row = build_index([e], today)["entries"][0]
        text = row["limits"]
        model_text = json.dumps(row["access_labels"]["models"])
    else:
        text = build_model_page("beta", [e], [], today, pages={"alpha", "beta"})
        model_text = text.split('<details markdown="block">', 1)[0]
    assert allowance not in model_text
    assert "beta" in model_text
    assert text.count(allowance) == (0 if surface == "readme" else 1)


def test_a_model_specific_session_condition_keeps_its_access_label():
    from freetier_radar.render import build_index
    data = session_catalog_data()
    quote = "Beta is free in the US, one session a day for every account."
    data["conditions"]["us-session"] = {"kind": "free-session", "quote": quote}
    data["models"][1].update(hours=None, limited=False, condition="us-session", listed=True)
    row = build_index([entry(data)], date(2026, 10, 6))["entries"][0]
    assert row["access_labels"]["models"]["beta"] == quote


def test_older_session_catalog_remains_readable_but_current_missing_dates_are_flagged(tmp_path):
    from freetier_radar.models import load_registry, save_registry
    from freetier_radar.validate import check
    import yaml
    data = catalog_data()
    data["limited_allowance"] = "6 one-hour sessions per day"
    e = entry(data)
    assert e.models == []
    save_registry(tmp_path / "registry.yaml", [e])
    for name, content in [('blocklist', []), ('dismissed', {'dismissed': []}),
                          ('watchlist', {'watched': []}), ('sources', {'read': []})]:
        (tmp_path / (name + '.yaml')).write_text(yaml.safe_dump(content))
    assert load_registry(tmp_path / "registry.yaml")[0].models == []
    assert any("first_free evidence" in p and "Beta" in p for p in check(tmp_path, date(2026, 10, 6)))


def page(*, amount=100, hours=10, names=("Alpha", "Beta", "Gamma"), rows=None,
         limited="Alpha and Beta", sessions=6, condition="Gamma needs a paid plan."):
    faq = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "Which models?", "acceptedAnswer": {
            "text": "\n".join(f"- {name}: description." for name in names)}},
        {"@type": "Question", "name": "How do credits work?", "acceptedAnswer": {
            "text": f"- US: {amount} Credits a day\n- Everywhere else: 25\n- Any VPN or proxy: 20"}},
        {"@type": "Question", "name": "What is limited mode?", "acceptedAnswer": {
            "text": f"Session-based limited mode includes {limited}, with {sessions} one-hour sessions per day."}},
    ]}
    table = rows if rows is not None else f"<li>Unlimited hrs Alpha</li><li>{hours} hrs Beta</li>"
    return (f'<script type="application/ld+json">{json.dumps(faq)}</script>'
            f"<h2>Model hours</h2><p>{amount} Credits every day for free.</p><ul>{table}</ul>"
            f"<p>{condition}</p><h2>Other features</h2>")


@respx.mock
async def test_markdown_faq_checks_budgets_without_inventing_model_hour_prices(tmp_path):
    from freetier_radar.render import build_index
    from freetier_radar.models import load_registry,save_registry
    data=session_catalog_data()
    data['read'].update(format='markdown',table_heading=None)
    data['reviewed_on']=date.today().isoformat()
    data['conditions']['wallet']={'kind':'wallet','quote':'Credits buy one-hour model sessions.'}
    for model in data['models'][:2]:model.update(hours=None,condition='wallet',listed=True)
    body='''# Vendor
Credits every day for free.
## FAQ
### Which models?
- Alpha: Balanced.
- Beta: Reasoning.
- Gamma: Paid.
### How do credits work?
Credits buy one-hour model sessions.
- US: 100 Credits a day
- Everywhere else: 25
- Any VPN or proxy: 20
### What is limited mode?
Session-based limited mode includes Alpha and Beta, with 6 one-hour sessions per day.
Gamma needs a paid plan.
'''
    respx.get(data['source']).respond(200,text=body)
    async with httpx.AsyncClient() as client:
        good=await probe_entry(client,entry(data),attempts=1,backoff=0)
        respx.get(data['source']).respond(200,text=body.replace('US: 100','US: 150'))
        bad=await probe_entry(client,entry(data),attempts=1,backoff=0)
        respx.get(data['source']).respond(200,text=body)
        expired=await probe_entry(client,entry(data),attempts=1,backoff=0,today=date.today()+timedelta(days=7))
    assert good.status is ProbeStatus.PASS
    assert bad.status is ProbeStatus.STALE_IDS and 'budget US' in bad.detail
    assert expired.status is ProbeStatus.STALE_IDS and 'fresh dated review' in expired.detail
    row=build_index([entry(data)],date.today())['entries'][0]
    assert [m['family'] for m in row['models']]==['alpha','beta']
    assert 'hour prices are not published' in row['limits']
    assert 'Credits buy' not in json.dumps(row['access_labels']['models'])
    assert row['limits'].count('6 one-hour sessions per day')==1
    save_registry(tmp_path/'registry.yaml',[entry(data)])
    assert load_registry(tmp_path/'registry.yaml')[0].page_catalog.read.table_heading is None


@respx.mock
async def test_catalog_condition_is_checked_only_on_its_own_source():
    data=catalog_data();data['conditions']['plan']['source']='https://vendor.example/eligibility'
    respx.get(data['source']).respond(200,text=page())
    respx.get('https://vendor.example/eligibility').respond(200,text='Gamma is paid at token prices.')
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,entry(data),attempts=1,backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'conditions.plan' in result.detail


@respx.mock
async def test_unpublished_regional_amount_and_quoted_limited_budgets(tmp_path):
    from freetier_radar.models import load_registry, save_registry
    from freetier_radar.render import build_index
    data = session_catalog_data()
    data['read'].update(format='markdown', table_heading=None)
    data['reviewed_on'] = date.today().isoformat()
    data['budgets'] = [
        {'id': 'full', 'amount': None, 'countries': ['US', 'CA'], 'quote': 'Full access covers US and CA.'},
        {'id': 'else', 'amount': 25, 'scope': 'else', 'quote': 'free limited allowance is 25 Credits a day'},
        {'id': 'vpn', 'amount': 20, 'scope': 'vpn', 'quote': '20 on a VPN or proxy'},
    ]
    data['example_budget'] = 'full'
    data['conditions']['wallet'] = {'kind': 'wallet', 'quote': 'Credits buy one-hour model sessions.'}
    for model in data['models'][:2]:
        model.update(hours=None, condition='wallet', listed=True)
    body = '''# Vendor
Credits every day for free.
### Which models?
- Alpha: Balanced.
- Beta: Reasoning.
- Gamma: Paid.
### How do credits work?
Full access covers US and CA. Your settings show your own daily allowance.
Credits buy one-hour model sessions.
### What is limited mode?
The free limited allowance is 25 Credits a day, or 20 on a VPN or proxy.
Session-based limited mode includes Alpha and Beta, with 6 one-hour sessions per day.
Gamma needs a paid plan.
'''
    respx.get(data['source']).respond(200, text=body)
    async with httpx.AsyncClient() as client:
        good = await probe_entry(client, entry(data), attempts=1, backoff=0)
        respx.get(data['source']).respond(200, text=body.replace('25 Credits', '35 Credits'))
        bad = await probe_entry(client, entry(data), attempts=1, backoff=0)
    assert good.status is ProbeStatus.PASS
    assert bad.status is ProbeStatus.STALE_IDS and 'budgets[1].quote' in bad.detail
    published = build_index([entry(data)], date.today())['entries'][0]
    assert published['page_catalog']['budgets'][0]['amount'] is None
    limits = published['limits']
    assert 'amount not published (Credits per day)' in limits
    assert '25 Credits per day' in limits and '20 Credits per day' in limits
    assert '100 Credits per day' not in limits and '0 Credits per day' not in limits.replace('20 Credits', '')
    save_registry(tmp_path / 'registry.yaml', [entry(data)])
    assert load_registry(tmp_path / 'registry.yaml')[0].page_catalog.budgets[0].amount is None
    with pytest.raises(ValueError, match='amount must match'):
        wrong = dict(data, budgets=[dict(b) for b in data['budgets']])
        wrong['budgets'][1]['amount'] = 35
        entry(wrong)


@pytest.mark.parametrize("changed", [{"amount": 150}, {"hours": 20}])
@respx.mock
async def test_changed_budget_and_hours_are_review_findings(changed):
    respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(200, text=page(**changed)))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "page_catalog" in result.detail


@respx.mock
async def test_unchanged_catalog_is_checked_without_authentication_or_extra_requests():
    route = respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(200, text=page()))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is ProbeStatus.PASS
    assert route.call_count == 1
    assert "authorization" not in route.calls[0].request.headers


@pytest.mark.parametrize("old_copy", ["", "<p>Earlier allowance: 6 one-hour sessions per day.</p>"])
@respx.mock
async def test_limited_allowance_changes_are_checked_in_the_configured_faq(old_copy):
    respx.get("https://vendor.example/pricing").respond(200, text=page(sessions=1) + old_copy)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(session_catalog_data()), attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "limited_allowance" in result.detail


def test_page_promotion_deadlines_reach_the_bar_report():
    from freetier_radar.bars import waiting, report
    data = catalog_data(); data["models"][0]["first_free"]["on"] = "2026-10-05"
    data["model_access"] = {"Alpha": {"source": data["source"], "until": "2026-11-01T00:00:00Z"}}
    e = entry(data)
    today = date(2026, 10, 6)
    due = waiting([e], {}, today)[0]
    assert due.until == datetime(2026, 11, 1, tzinfo=timezone.utc)
    assert due.due_on == date(2026, 10, 5)
    assert "free until 2026-11-01T00:00:00+00:00" in report([e], {}, today)
    assert waiting([e], {}, date(2026, 11, 1)) == []


def test_shared_limits_do_not_leak_markdown_links_into_html(tmp_path):
    from pathlib import Path
    from freetier_radar.models import save_registry
    from freetier_radar.render import render_site
    data = catalog_data()
    data["model_access"] = {"Alpha": {"source": "https://vendor.example/terms", "until": "2026-11-01T00:00:00Z"}}
    e = entry(data)
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [e])
    html = render_site(reg, Path("templates"), tmp_path / "index.html", today=date(2026, 10, 6))
    limits = re.search(r'<td class="limits"[^>]*>(.*?)</td>', html, re.S).group(1)
    assert not re.search(r'\[[^\]]+\]\(https?://', limits)
    assert data["source"] in limits and "https://vendor.example/terms" in limits


@pytest.mark.parametrize("body, finding", [
    (page(names=("Alpha", "Beta", "Gamma", "Delta")), "model picker added: delta"),
    (page(names=("Alpha", "Gamma")), "model picker missing: beta"),
    (page(rows="<li>Unlimited hrs Alpha</li><li>10 hrs Beta</li><li>3 hrs Delta</li>"), "hours table models added: delta"),
    (page(rows="<li>10 hrs Beta</li>"), "hours table models missing: alpha"),
    (page(rows="<li>2 hrs Alpha</li><li>10 hrs Beta</li>"), "hours alpha: 2 (recorded unlimited)"),
    (page(limited="Alpha"), "limited-access models missing: beta"),
    (page(limited="Alpha and Beta and Gamma"), "limited-access models added: gamma"),
    (page(condition="Gamma now uses ordinary credits."), "conditions.plan.quote no longer evidenced"),
    (page().replace("Model hours", "Other hours"), "hours table unreadable"),
    (page().replace('application/ld+json', 'application/json'), "budgets unreadable"),
    (page().replace("100 Credits a day", "100 Coins a day"), "budgets unreadable"),
])
@respx.mock
async def test_changed_access_and_unreadable_contracts_are_visible(body, finding):
    respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(200, text=body))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert finding in result.detail


@respx.mock
async def test_old_prices_in_framework_state_do_not_mask_the_current_table():
    body = page(hours=20) + '<script>const retired = "10 hrs Beta";</script>'
    respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(200, text=body))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert "hours beta: 20 (recorded 10)" in result.detail


@respx.mock
async def test_a_retired_condition_in_framework_state_cannot_mask_changed_access():
    body = page(condition='Gamma costs credits now.') + '<script>const old = "Gamma needs a paid plan.";</script>'
    respx.get('https://vendor.example/pricing').respond(200, text=body)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert 'conditions.plan.quote no longer evidenced' in result.detail


@respx.mock
async def test_an_unavailable_page_is_not_a_model_removal():
    respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(503))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE


def test_catalog_is_the_only_saved_model_record_and_tiers_survive_the_workflow(tmp_path):
    from freetier_radar.models import Tier, load_registry, save_registry
    data = catalog_data()
    data["models"][0]["listed"] = True
    e = entry(data)
    assert [m.family for m in e.models] == ["alpha"]
    assert not e.newcomers
    assert e.models[0] is e.page_catalog.models[0].model
    e.models[0].tier = Tier.STRONG
    e.models[0].aa_model = "alpha"
    path = tmp_path / "registry.yaml"
    save_registry(path, [e])
    import yaml
    raw = yaml.safe_load(path.read_text())["entries"][0]
    assert "models" not in raw and "newcomers" not in raw
    assert raw["page_catalog"]["models"][0]["model"]["tier"] == "strong"
    restored = load_registry(path)[0]
    assert restored.models == e.models


def test_only_independently_free_offers_start_a_family_bar():
    from freetier_radar.bars import waiting
    e = entry()
    assert e.models == []
    assert [(n.family, n.on) for n in e.newcomers] == [("alpha", date(2026, 9, 1))]
    pending = waiting([e], {}, date(2026, 10, 6))
    assert [(m.model_id, m.due_on) for m in pending] == [("alpha", date(2026, 9, 15))]
    assert {m.model.family for m in e.page_catalog.models} == {"alpha", "beta", "gamma"}


@pytest.mark.parametrize("alter", [
    lambda d: d["models"][1].update(listed=True),
    lambda d: d["models"][2].update(listed=True),
    lambda d: d["models"][1].update(first_free={"on": "2026-09-01", "source": "https://vendor.example/launch"}),
    lambda d: d["models"][0].pop("first_free"),
    lambda d: d["models"][0].update(hours=True),
    lambda d: d["models"][0].update(condition="plan"),
    lambda d: d["budgets"][0].update(countries=["XX"]),
    lambda d: d["budgets"][0].update(amount=True),
    lambda d: d["budgets"].append({"id": "duplicate", "amount": 30, "countries": ["US"]}),
    lambda d: d.update(example_budget="missing"),
    lambda d: d["models"][0].update(condition="undefined", hours=None),
    lambda d: d["conditions"].update(unused={"kind": "paid", "quote": "Some new restriction"}),
    lambda d: d.update(source="https://unprobed.example/catalog"),
])
def test_invalid_or_contradictory_catalog_records_are_rejected(alter):
    from pydantic import ValidationError
    data = catalog_data()
    alter(data)
    with pytest.raises(ValidationError):
        entry(data)


def test_unchecked_wallet_tiers_are_refused_without_making_old_snapshots_unreadable(tmp_path):
    from freetier_radar.models import Tier, load_registry, save_registry
    from freetier_radar.validate import check
    import yaml
    data = catalog_data(); data['models'][1]['model']['tier'] = 'strong'
    e = entry(data)
    save_registry(tmp_path / 'registry.yaml', [e])
    for name, content in [('blocklist', []), ('dismissed', {'dismissed': []}),
                          ('watchlist', {'watched': []}), ('sources', {'read': []})]:
        (tmp_path / (name + '.yaml')).write_text(yaml.safe_dump(content))
    assert load_registry(tmp_path / 'registry.yaml')[0].page_catalog.models[1].model.tier is Tier.STRONG
    finding = 'registry: vendor page_catalog has an unchecked tier on Beta'
    assert finding in check(tmp_path, date(2026, 10, 6))
    e.page_catalog.models[1].model.tier = None
    save_registry(tmp_path / 'registry.yaml', [e])
    assert finding not in check(tmp_path, date(2026, 10, 6))


def test_declared_deadline_expires_the_free_family_but_preserves_the_wallet():
    from freetier_radar.models import FreePart, expire_entries
    data = catalog_data()
    data["models"][0]["listed"] = True
    data["model_access"] = {"Alpha": {"source": data["source"], "until": "2026-10-06T00:00:00Z"}}
    e = entry(data)
    before = expire_entries([e], datetime(2026, 10, 5, 23, 59, tzinfo=timezone.utc))[0]
    assert before.models[0].family == "alpha"
    after = expire_entries([e], datetime(2026, 10, 6, tzinfo=timezone.utc))[0]
    assert after.models == [] and after.newcomers == []
    assert after.free_part is FreePart.SUM
    assert after.page_catalog.models[0].expired
    assert after.page_catalog.model_access["Alpha"].until is not None
    assert after.retired_on is None
    assert e.models[0].family == "alpha" and not e.page_catalog.models[0].expired


def test_payment_and_deadline_are_disclosed_and_ended_offers_lose_their_hours():
    from freetier_radar.models import expire_entries
    from freetier_radar.page_catalog import catalog_words
    from freetier_radar.render import build_provider_page
    data = catalog_data()
    data['model_access'] = {'Alpha': {'source': data['source'], 'until': '2026-10-06T00:00:00Z',
                                    'initial_payment_usd': 1}}
    e = entry(data)
    for text in (catalog_words(e.page_catalog), build_provider_page(e, [], date(2026, 10, 5))):
        assert 'requires $1 one-time top-up' in text
        assert 'free until 2026-10-06 00:00+00:00' in text
        assert f"terms: {data['source']}" in text
    after = expire_entries([e], datetime(2026, 10, 6, tzinfo=timezone.utc))[0]
    text = build_provider_page(after, [], date(2026, 10, 6))
    alpha = text.split('Alpha: ', 1)[1].split('; Beta:', 1)[0]
    assert alpha.startswith('offer ended') and 'unlimited hours' not in alpha
    assert 'available in limited mode' not in alpha
    assert 'offer ended 2026-10-06 00:00+00:00' in alpha


def test_weekly_budget_keeps_its_period_in_all_presentations():
    from freetier_radar.page_catalog import catalog_words, check_page_catalog
    from freetier_radar.render import build_provider_page
    data = catalog_data(); data['period'] = 'week'
    e = entry(data)
    body = page().replace('a day', 'a week').replace('every day', 'every week')
    assert check_page_catalog(body, e.page_catalog) == []
    for text in (catalog_words(e.page_catalog), build_provider_page(e, [], date(2026, 10, 6))):
        assert 'Weekly allowance' in text and 'Shared weekly credits'.lower() in text.lower()
        assert 'daily' not in text.lower()


@pytest.mark.parametrize('body,finding', [(page(amount=150),'budget US: 150'), (None,'source unreadable')])
@respx.mock
async def test_review_receipts_cannot_pass_a_changed_or_unreadable_catalog(tmp_path, monkeypatch, body, finding):
    from freetier_radar import review
    from freetier_radar.models import _row_payload
    import yaml
    e = entry()
    monkeypatch.setattr(review, 'blob', lambda *args: yaml.safe_dump({'entries': [_row_payload(e)]}).encode())
    respx.get(e.probe.endpoint).respond(200 if body else 503, text=body or '')
    respx.get(e.page_catalog.models[0].first_free.source).respond(200, text='Dated launch evidence')
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    bundle.save('scope', {'base': 'a'*40, 'sha': 'b'*40, 'rows': [e.id], 'paths': []})
    result = await review.sources(bundle, [])
    assert not result['passed']
    assert any(finding in note for note in result['page_catalogs'][0]['notes'])
    assert not result['page_catalogs'][0]['passed']
    if body:
        assert all(q['found'] for q in result['quotes'])


@respx.mock
async def test_a_catalog_condition_cannot_be_confirmed_by_an_unrelated_old_source():
    from freetier_radar.quotes import check_entries
    e = entry()
    e.source_urls = ["https://vendor.example/old-blog"]
    respx.get(e.probe.endpoint).mock(return_value=httpx.Response(200, text=page(condition="Gamma costs credits.")))
    respx.get(e.source_urls[0]).mock(return_value=httpx.Response(200, text="Gamma needs a paid plan."))
    respx.get(e.page_catalog.models[0].first_free.source).respond(200, text='Dated launch evidence')
    async with httpx.AsyncClient() as client:
        missing, unread = await check_entries([e], client)
    assert unread == {}
    assert [(m.field, m.unverified) for m in missing] == [("page_catalog.conditions.plan.quote", False)]


def test_all_published_views_contain_the_wallet_picker_without_calling_paid_models_free():
    from freetier_radar.render import build_index, build_llms_txt, build_provider_page, build_site_context, build_context
    e = entry()
    today = date(2026, 10, 6)
    index = build_index([e], today)
    assert index["models"] == []
    assert index["entries"][0]["models"] == []
    assert "Beta: shared daily credits" in index["entries"][0]["limits"]
    provider = build_provider_page(e, [], today, registry=[e], pages=set())
    assert "Alpha: unmetered offer; unlimited hours; available in limited mode" in provider
    assert "Beta: shared daily credits; 10 hours with the whole 100-Credits allowance; available in limited mode" in provider
    assert "Gamma: paid plan" in provider
    assert "Gamma needs a paid plan." in provider
    text = build_llms_txt([e], today, pages=set())
    assert "Beta: shared daily credits" in text and "Gamma: paid plan" in text
    assert "free models: `beta`" not in text and "free models: `gamma`" not in text
    context = build_site_context([e], today, pages=set())
    row = next(r for s in context["sections"] for r in s["rows"])
    assert row["models"] == []
    assert next(r for s in build_context([e], today)["sections"] for r in s["rows"])["models"] == ""


@pytest.mark.parametrize("listed", [False, True])
def test_catalog_uses_the_existing_provider_sections(listed):
    from freetier_radar.render import build_provider_page
    data = catalog_data(); data["models"][0]["listed"] = listed
    e = entry(data)
    ordinary = Entry.model_validate(e.model_dump(exclude={"page_catalog"}))
    today = date(2026, 10, 6)
    headings = lambda row: re.findall(r"^## (.+)$", build_provider_page(row, [], today), re.M)
    assert headings(e) == headings(ordinary) == [
        "What you get", "Free models", "Limits, in the vendor's words", "Connect", "Evidence", "History",
    ]


@pytest.mark.parametrize("listed", [False, True])
def test_catalog_keeps_model_navigation_in_the_existing_family_slots(tmp_path, listed):
    from pathlib import Path
    from freetier_radar.models import save_registry
    from freetier_radar.render import render_readme, render_site, build_providers_index
    data = catalog_data(); data["models"][0]["listed"] = listed
    e = entry(data)
    today = date(2026, 10, 6)
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [e])
    site = render_site(reg, Path("templates"), tmp_path / "index.html", today=today)
    cell = re.search(r'<td class="models"[^>]*>(.*?)</td>', site, re.S).group(1)
    if listed:
        # Every navigation item in this column is an eligible family chip.
        chips = re.findall(r'<(?:a|span) class="chip[^"]*"[^>]*>(.*?)</(?:a|span)>', cell, re.S)
        assert chips == ["alpha"]
        assert len(re.findall(r'<a\b', cell)) == len(re.findall(r'<a class="chip', cell))
        assert re.sub(r'<[^>]+>', '', cell).strip() == "alpha"
    else:
        assert cell.strip() == '<span class="empty">—</span>'
    readme = render_readme(reg, Path("templates"), tmp_path / "README.md", today=today)
    listing = next(line for line in readme.split("## 📋 The list", 1)[1].splitlines()
                   if line.startswith('- **[Vendor]'))
    small = re.search(r'<sub>(.*?)</sub>', listing).group(1)
    assert re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', small) == (
        "verified 2026-10-05" + ("\u00a0· `alpha`" if listed else ""))
    index = build_providers_index([e], today)
    row = next(line for line in index.splitlines() if line.startswith('- [Vendor]'))
    assert re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', row) == (
        "- Vendor — verified 2026-10-05" + ("\u00a0· `alpha`" if listed else ""))
