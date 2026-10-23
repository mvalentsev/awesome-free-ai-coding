"""Short gateway IDs must keep distinct model identities and access conditions."""
from datetime import date, datetime, timezone

import httpx
import pytest
import respx

from freetier_radar.models import Entry, expire_entries, family_access
from freetier_radar.prober import ProbeStatus, probe_entry


SOURCE='https://vendor.example/identity'
TARGET='https://maker.example/models/science-397b'
BASE={'id':'vendor','name':'Vendor','category':'aggregator','url':'https://vendor.example',
      'offering':'Free chat models','free_part':'models','first_seen':'2026-09-01',
      'last_verified':'2026-10-23','models':[{'family':'science-397b'}],
      'probe':{'type':'api-models','endpoint':'https://vendor.example/models',
               'require_zero_price':True}}


def entry(family='science-397b', *, client=False):
    lane={'model_ids':['science-free'],
          'model_bindings':{'science-free':{'family':family,'source':SOURCE,
                                          'quote':'The science-free route','target':TARGET}},
          'model_access':{'science-free':{'source':SOURCE,'until':'2026-10-31T23:59:00+03:00'}}}
    return Entry.model_validate({**BASE,'models':[{'family':family}],
                                 'client_lane' if client else 'api':lane if client else
                                 {'base_url':'https://vendor.example/v1',**lane}})


@pytest.mark.parametrize('family',['science-397b','science-preview-35b'])
@pytest.mark.parametrize('change',['none','target','quote','unreadable'])
@respx.mock
async def test_short_id_identity_is_checked_at_its_own_http_source(family, change):
    e=entry(family)
    respx.get(e.probe.endpoint).respond(200,json={'data':[
        {'id':'science-free','pricing':{'prompt':'0','completion':'0'}}]})
    body='<p>The science-free route</p><a href="'+TARGET+'">Model card</a>'
    if change=='target':body=body.replace('science-397b','different-model')
    if change=='quote':body=body.replace('science-free','other-free')
    respx.get(SOURCE).respond(503 if change=='unreadable' else 200,text=body)
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,e,attempts=1,backoff=0)
    assert result.status is (ProbeStatus.PASS if change=='none' else ProbeStatus.STALE_IDS)
    if change!='none':assert 'model binding' in result.detail


@pytest.mark.parametrize('model',[
    {'id':'science-free','pricing':{'prompt':'1','completion':'1'}},
    {'id':'science-free','pricing':{'prompt':'0','completion':'0'},'available':False},
    {'id':'another-free','pricing':{'prompt':'0','completion':'0'}},
])
@respx.mock
async def test_a_binding_never_restores_a_priced_withdrawn_or_missing_id(model):
    e=entry();respx.get(e.probe.endpoint).respond(200,json={'data':[model]})
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,e,attempts=1,backoff=0)
    assert result.status is ProbeStatus.FAIL


@pytest.mark.parametrize('client',[False,True])
def test_bound_id_keeps_its_deadline_model_page_and_expiry(client):
    from freetier_radar.render import build_model_page
    from freetier_radar.bars import waiting
    e=entry(client=client);today=date(2026,10,23)
    assert family_access(e,'science-397b').until.isoformat()=='2026-10-31T23:59:00+03:00'
    page=build_model_page('science-397b',[e],[],today)
    assert '2026-10-31' in page
    if not client:assert '`science-free`' in page
    assert waiting([e],{},today)==[]
    ended=expire_entries([e],datetime(2026,11,1,tzinfo=timezone.utc))[0]
    assert not ended.models
    lane=ended.client_lane if client else ended.api
    assert lane.model_ids==[] and 'science-free' in lane.ignored_ids
    assert lane.model_bindings['science-free'].family=='science-397b'


def test_same_short_id_does_not_merge_two_gateways_variants():
    from freetier_radar.models import entry_id_family
    stable=entry();preview=entry('science-preview-35b')
    assert entry_id_family(stable,'science-free')=='science-397b'
    assert entry_id_family(preview,'science-free')=='science-preview-35b'
    assert entry_id_family(preview,'science-free',['science-397b']) is None


@pytest.mark.parametrize('change',[
    {'source':'http://127.0.0.1/private'}, {'target':'javascript:alert(1)'},
    {'family':'../escape'}, {'quote':''}, {'quote':'   '}, {'quote':' x '}, {'quote':'...'},
    {'quote':'Science … model'}, {'read':'catalog'},
])
def test_binding_fields_reject_unsafe_or_uncheckable_identity(change):
    from pydantic import ValidationError
    from freetier_radar.models import ModelBinding
    with pytest.raises(ValidationError):
        ModelBinding.model_validate({'family':'science-397b','source':SOURCE,
                                     'quote':'The science-free route','target':TARGET,**change})


def test_binding_sources_and_quotes_are_enrolled_for_recheck():
    from freetier_radar.quotes import row_quotes,row_urls,row_quote_source
    e=entry();field='api.model_bindings.science-free.quote'
    assert SOURCE in row_urls(e)
    assert (field,'The science-free route') in row_quotes(e)
    assert row_quote_source(e,field)==SOURCE


def test_a_binding_for_an_unknown_id_is_refused():
    from pydantic import ValidationError
    raw=entry().model_dump(mode='json',exclude_none=True)
    raw['api']['model_bindings']['typo-free']=raw['api']['model_bindings'].pop('science-free')
    with pytest.raises(ValidationError,match='model_bindings'):
        Entry.model_validate(raw)


@pytest.mark.parametrize('change',['none','identity','other-row','duplicate'])
@respx.mock
async def test_catalog_binding_checks_only_the_exact_ids_identity(change):
    raw=entry().model_dump(mode='json',exclude_none=True)
    raw['api']['model_bindings']['science-free']={
        'family':'science-397b','read':'catalog','source':BASE['probe']['endpoint'],
        'quote':'Science stable 397B'}
    e=Entry.model_validate(raw)
    model={'id':'science-free','pricing':{'prompt':'0','completion':'0'},'description':'Science stable 397B'}
    items=[model]
    if change in ('identity','other-row'):model['description']='Science Preview 35B'
    if change=='other-row':
        e.api.ignored_ids.append('other-free')
        items.append({**model,'id':'other-free','description':'Science stable 397B'})
    if change=='duplicate':items.append(dict(model))
    respx.get(e.probe.endpoint).respond(200,json={'data':items})
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,e,attempts=1,backoff=0)
    assert result.status is (ProbeStatus.PASS if change=='none' else ProbeStatus.STALE_IDS)
    if change!='none':assert 'model binding' in result.detail
