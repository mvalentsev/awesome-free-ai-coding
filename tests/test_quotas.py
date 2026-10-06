import httpx
import pytest
import respx
from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, probe_entry

BASE = {'id':'vendor','name':'Vendor','url':'https://vendor.example','category':'api-free-tier',
        'offering':'A recurring free quota','first_seen':'2026-09-01','last_verified':'2026-10-05',
        'probe':{'type':'page-keywords','endpoint':'https://vendor.example/pricing',
                 'keywords':['Recurring free quota for chat']}}
QUOTA = {'amount':200,'unit':'requests','period':'hour','scope':'ip',
         'source':'https://vendor.example/limits','quote':'200 requests per hour per IP'}

@respx.mock
async def test_a_live_offer_does_not_hide_a_changed_numeric_quota():
    e=Entry.model_validate({**BASE,'quotas':[QUOTA]})
    respx.get(e.probe.endpoint).respond(200,text='Recurring free quota for chat')
    respx.get(QUOTA['source']).respond(200,text='100 requests per hour per IP')
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,e,attempts=1,backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'quota' in result.detail and 'no longer' in result.detail

@pytest.mark.parametrize('change', [
    {'amount':True}, {'amount':float('nan')}, {'amount':300}, {'unit':'tokens'},
    {'period':'month'}, {'window':7}, {'read':'constant','constant':'x;alert(1)'},
    {'amount':None}, {'source':'file:///tmp/limits'},
])
def test_unbound_or_invalid_numeric_claims_are_refused(change):
    from pydantic import ValidationError
    from freetier_radar.quotas import UsageQuota
    with pytest.raises(ValidationError):
        UsageQuota.model_validate({**QUOTA,**change})

@respx.mock
async def test_unreadable_quota_is_a_review_note_without_archiving_the_live_offer():
    e=Entry.model_validate({**BASE,'quotas':[QUOTA]})
    respx.get(e.probe.endpoint).respond(200,text='Recurring free quota for chat')
    respx.get(QUOTA['source']).respond(503)
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,e,attempts=1,backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'could not be checked' in result.detail and '503' in result.detail

@respx.mock
async def test_another_models_old_cap_cannot_confirm_the_affected_model():
    e=Entry.model_validate({**BASE,
       'models':[{'family':'qwen3-coder'},{'family':'phi-4'}],
       'api':{'base_url':'https://api.vendor.example/v1','model_ids':['qwen/qwen3-coder:free','microsoft/phi-4:free']},
       'probe':{'type':'api-models','endpoint':'https://api.vendor.example/v1/models','require_zero_price':True},
       'quotas':[{**QUOTA,'source':'https://api.vendor.example/v1/models','scope':'account-model',
                  'read':'catalog','model_ids':['qwen/qwen3-coder:free']}]})
    respx.get(e.probe.endpoint).respond(200,json={'data':[
        {'id':'qwen/qwen3-coder:free','pricing':{'prompt':'0','completion':'0'},'description':'100 requests per hour per IP'},
        {'id':'microsoft/phi-4:free','pricing':{'prompt':'0','completion':'0'},'description':QUOTA['quote']}]})
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,e,attempts=1,backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'qwen/qwen3-coder:free: quota quote no longer' in result.detail


def test_a_changed_constant_is_detected_even_beside_an_old_quote():
    from freetier_radar.quotas import UsageQuota,quota_changes
    q=UsageQuota.model_validate({**QUOTA,'amount':20,'period':'minute','read':'constant',
                                'constant':'FREE_MODEL_RATE_LIMIT_RPM',
                                'quote':'Free models allow 20 requests per minute.'})
    notes=quota_changes('<p>Free models allow 20 requests per minute.</p><script>const FREE_MODEL_RATE_LIMIT_RPM=10;</script>',q)
    assert len(notes)==1 and '=10 (recorded 20)' in notes[0]

@respx.mock
async def test_an_unpublished_amount_expires_for_review_without_becoming_zero():
    from datetime import date
    from freetier_radar.quotas import UNKNOWN_RECHECK_DAYS,quota_summary
    q={**QUOTA,'amount':None,'quote':'Daily allowance shown in your dashboard',
       'period':'day','reviewed_on':'2026-10-01'}
    e=Entry.model_validate({**BASE,'quotas':[q]})
    respx.get(e.probe.endpoint).respond(200,text='Recurring free quota for chat')
    respx.get(q['source']).respond(200,text=q['quote'])
    async with httpx.AsyncClient() as client:
        fresh=await probe_entry(client,e,attempts=1,backoff=0,today=date(2026,10,1))
        due=await probe_entry(client,e,attempts=1,backoff=0,today=date(2026,10,1+UNKNOWN_RECHECK_DAYS))
    assert fresh.status is ProbeStatus.PASS
    assert due.status is ProbeStatus.STALE_IDS and 'fresh dated review' in due.detail
    assert 'amount not published' in quota_summary(e) and '0 requests' not in quota_summary(e)


def test_shared_short_paragraph_is_shown_once_in_the_existing_fold():
    from freetier_radar.render import _site_fold
    lead='200 requests/hour per IP'
    rest='Only free routes are available anonymously. '*12
    folded=_site_fold(lead+'\n\n'+rest)
    assert folded['teaser']==lead+' …'
    assert folded['text']==rest and lead not in folded['text']


def test_a_multi_number_quote_cannot_assign_a_daily_cap_to_a_minute():
    from pydantic import ValidationError
    from freetier_radar.quotas import UsageQuota
    q={'amount':100,'unit':'requests','period':'minute','scope':'account',
       'source':'https://vendor.example/limits',
       'quote':'5 requests per minute, 100 requests per day, and 1 million tokens per day'}
    with pytest.raises(ValidationError):
        UsageQuota.model_validate(q)
    with pytest.raises(ValidationError):
        UsageQuota.model_validate({**q,'value_phrase':'100 requests per day'})
    assert UsageQuota.model_validate({**q,'period':'day','value_phrase':'100 requests per day'}).amount==100


def test_machine_json_keeps_an_unpublished_amount_explicitly_null():
    from datetime import date
    from freetier_radar.render import build_index
    e=Entry.model_validate({**BASE,'quotas':[{**QUOTA,'amount':None,
        'quote':'Daily allowance shown in your dashboard','period':'day','reviewed_on':'2026-10-01'}]})
    row=build_index([e],date(2026,10,6))['entries'][0]
    assert 'amount' in row['quotas'][0] and row['quotas'][0]['amount'] is None
