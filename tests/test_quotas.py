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


def test_a_hidden_allowance_does_not_invent_a_renewal_period():
    from freetier_radar.quotas import UsageQuota,quota_words
    q=UsageQuota.model_validate({**QUOTA,'amount':None,'unit':'usage','period':None,
        'scope':'account','quote':'Limited Agent requests','reviewed_on':'2026-10-06'})
    text=quota_words(q)
    assert 'amount not published' in text and 'day' not in text and 'month' not in text
    assert 'period not published' in text


def test_concurrent_work_is_not_a_recurring_request_budget():
    from freetier_radar.quotas import UsageQuota,quota_words
    q=UsageQuota.model_validate({**QUOTA,'amount':3,'unit':'tasks','period':'concurrent',
        'scope':'account','quote':'3 concurrent tasks'})
    assert quota_words(q)=='3 tasks at once per account'


def test_explicit_unmetered_usage_stays_distinct_from_an_unpublished_amount():
    from freetier_radar.quotas import UsageQuota,quota_words
    q=UsageQuota.model_validate({**QUOTA,'amount':None,'unit':'completions','period':None,
        'scope':'account','state':'unmetered','quote':'Unlimited Tab completions',
        'reviewed_on':'2026-10-06'})
    assert 'Unmetered completions' in quota_words(q) and 'not published' not in quota_words(q)


@respx.mock
@pytest.mark.parametrize('changed', ['cell', 'column', 'plan'])
async def test_free_table_limits_bind_the_plan_model_and_column_at_http_boundary(changed):
    q={**QUOTA,'amount':30,'period':'minute','read':'table','quote':'Free Plan Limits',
       'table':{'headers':['MODEL ID','RPM','RPD'],'column':'RPM','rows':['coding-model'],
                'active_tab':'Free Plan Limits','active_class':'selected'}}
    e=Entry.model_validate({**BASE,'quotas':[q]})
    headers=['MODEL ID','RPM','RPD'] if changed!='column' else ['MODEL ID','RPD','RPM']
    active='Free Plan Limits' if changed!='plan' else 'Paid Plan Limits'
    cells=['coding-model','30','100'] if changed!='cell' else ['coding-model','10','100']
    body='<table><thead><tr><th><button class="selected">'+active+'</button><button>Free Plan Limits</button></th></tr><tr>'
    body+=''.join('<th>'+h+'</th>' for h in headers)+'</tr></thead></table><table><tbody><tr>'
    body+=''.join('<td>'+v+'</td>' for v in cells)+'</tr><tr><td>other-model</td><td>30</td><td>100</td></tr></tbody></table>'
    respx.get(e.probe.endpoint).respond(200,text=BASE['probe']['keywords'][0])
    respx.get(q['source']).respond(200,text=body)
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,e,attempts=1,backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'table' in result.detail


@respx.mock
async def test_a_current_document_release_overrides_a_still_readable_old_allowance():
    from freetier_radar.quotes import check_entries
    q={**QUOTA,'source':'https://vendor.example/index',
       'follow':{'field':'Data.TargetPrefix','suffix':'/limits.md'}}
    e=Entry.model_validate({**BASE,'quotas':[q]})
    respx.get(e.probe.endpoint).respond(200,text=BASE['probe']['keywords'][0])
    respx.get(q['source']).respond(200,json={'Data':{'TargetPrefix':'https://vendor.example/new'}})
    respx.get('https://vendor.example/old/limits.md').respond(200,text=q['quote'])
    respx.get('https://vendor.example/new/limits.md').respond(200,text='100 requests per hour per IP')
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,e,attempts=1,backoff=0)
        missing,_=await check_entries([e],client)
    assert result.status is ProbeStatus.STALE_IDS
    assert any(m.field=='quotas[0].quote' for m in missing)


@respx.mock
async def test_catalog_rates_cannot_borrow_a_paid_tier_or_another_models_cap():
    q={**QUOTA,'amount':5,'period':'minute','read':'catalog-field','model_ids':['coding-model'],
       'quote':'"L0"','catalog_field':{'collection':'tiers','where':{'tier_id':'L0'},'field':'rpm'}}
    e=Entry.model_validate({**BASE,'quotas':[q]})
    respx.get(e.probe.endpoint).respond(200,text=BASE['probe']['keywords'][0])
    respx.get(q['source']).respond(200,json={'data':[
        {'id':'coding-model','tiers':[{'tier_id':'L0','rpm':0},{'tier_id':'L1','rpm':5}]},
        {'id':'other-model','tiers':[{'tier_id':'L0','rpm':5}]}]})
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,e,attempts=1,backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'coding-model' in result.detail and 'rpm' in result.detail


def test_ended_model_quota_retains_evidence_without_advertising_current_allowance():
    from freetier_radar.quotas import structured_quotas
    e=Entry.model_validate({**BASE,'api':{'base_url':'https://api.vendor.example/v1',
        'model_ids':['continuing-model'],'ignored_ids':['ended-model'],
        'model_access':{'ended-model':{'source':QUOTA['source'],'until':'2026-10-01T23:59:00Z'}}},
        'probe':{'type':'api-models','endpoint':QUOTA['source'],'require_zero_price':True},
        'quotas':[{**QUOTA,'read':'catalog','model_ids':['ended-model']}]})
    assert e.quotas[0].model_ids==['ended-model']
    assert structured_quotas(e)==[]


def test_multiple_source_bindings_for_the_same_labeled_allowance_print_it_once():
    from freetier_radar.quotas import quota_summary
    e=Entry.model_validate({**BASE,'quotas':[
        {**QUOTA,'label':'Published model caps','scope':'account-model','model_ids':['one']},
        {**QUOTA,'label':'Published model caps','scope':'account-model','model_ids':['two']} ]})
    text=quota_summary(e)
    assert text.count('200 requests/hour')==1
    assert '`one`' in text and '`two`' in text


def test_same_label_cannot_share_different_caps_between_models():
    from freetier_radar.quotas import quota_summary
    e=Entry.model_validate({**BASE,'quotas':[
        {**QUOTA,'label':'Free models','scope':'account-model','model_ids':['one']},
        {**QUOTA,'amount':100,'quote':'100 requests per hour per account per model',
         'label':'Free models','scope':'account-model','model_ids':['two']}]})
    paragraphs=quota_summary(e).split('\n\n')
    assert len(paragraphs)==2
    assert '200 requests/hour' in paragraphs[0] and '`one`' in paragraphs[0] and '`two`' not in paragraphs[0]
    assert '100 requests/hour' in paragraphs[1] and '`two`' in paragraphs[1] and '`one`' not in paragraphs[1]


def test_one_time_grant_cannot_look_like_a_recurring_allowance():
    from freetier_radar.quotas import UsageQuota, quota_words
    quota=UsageQuota.model_validate({**QUOTA,'amount':10,'unit':'USD',
        'period':'one-time','scope':'account','quote':'$10 signup credit'})
    assert '$10 once per account' == quota_words(quota)


@respx.mock
async def test_expired_catalog_quota_is_not_reported_as_a_current_missing_claim():
    from freetier_radar.quotes import check_entries
    e=Entry.model_validate({**BASE,'api':{'base_url':'https://api.vendor.example/v1',
        'model_ids':['continuing-model'],'ignored_ids':['ended-model'],
        'model_access':{'ended-model':{'source':QUOTA['source'],'until':'2026-10-01T23:59:00Z'}}},
        'probe':{'type':'api-models','endpoint':QUOTA['source'],'require_zero_price':True},
        'quotas':[{**QUOTA,'read':'catalog','model_ids':['ended-model']}]})
    respx.get(QUOTA['source']).respond(200,json={'data':[{'id':'continuing-model'}]})
    async with httpx.AsyncClient() as client:
        missing,_=await check_entries([e],client)
    assert missing==[]
    assert e.quotas[0].model_ids==['ended-model']
