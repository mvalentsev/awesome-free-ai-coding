"""A free-table check must notice arrivals and ended waiting offers over HTTP."""
import httpx
import pytest

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, for_a_human, probe_entry
from datetime import date, timedelta


def table_entry(kind, *, newcomers=()):
    binding = ({'model_prices': {'headers': ['Model', 'Input', 'Output'],
                               'name_column': 'Model', 'price_columns': ['Input', 'Output']}}
               if kind == 'prices' else
               {'model_plan': {'headers': ['Model', 'Free', 'Pro'],
                               'name_column': 'Model', 'plan_column': 'Free', 'included_value': 'Yes'}})
    return Entry.model_validate({
        'id': 'vendor', 'name': 'Vendor', 'url': 'https://vendor.example',
        'source_urls': ['https://vendor.example/models'], 'category': 'agent-cli',
        'offering': 'A recurring free coding-model tier', 'free_part': 'models',
        'models': [{'family': 'alpha-1'}],
        'newcomers': [{'family': family, 'on': '2026-10-25',
                       'source': 'https://vendor.example/models'} for family in newcomers],
        'probe': {'type': 'page-keywords', 'endpoint': 'https://vendor.example/models',
                  'keywords': ['alpha-1'], **binding},
        'first_seen': '2026-07-19', 'last_verified': '2026-10-26'})


def html(kind, *, beta=True):
    headers = ['Model', 'Input', 'Output'] if kind == 'prices' else ['Model', 'Free', 'Pro']
    free = ['Free', 'Free'] if kind == 'prices' else ['Yes', 'Yes']
    paid = ['$1', 'Free'] if kind == 'prices' else ['No', 'Yes']
    rows = [('Alpha 1', free), ('Beta 2', free if beta else paid), ('Paid 3', paid)]
    return '<p>alpha-1</p><table><tr>' + ''.join('<th>'+h+'</th>' for h in headers) + '</tr>' + ''.join(
        '<tr>'+''.join('<td>'+v+'</td>' for v in [name, *values])+'</tr>' for name, values in rows) + '</table>'


@pytest.mark.parametrize('kind', ['prices', 'plan'])
async def test_unrecorded_free_table_arrival_is_a_human_finding_not_a_silent_pass(kind):
    entry = table_entry(kind)
    calls = []
    def respond(request):
        calls.append(str(request.url))
        return httpx.Response(200, text=html(kind))
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await probe_entry(client, entry, attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'Beta 2' in result.detail and 'Paid 3' not in result.detail
    assert for_a_human(result.detail) == result.detail
    assert calls == [entry.probe.endpoint]


@pytest.mark.parametrize('kind', ['prices', 'plan'])
async def test_waiting_model_losing_free_access_is_detected_before_its_promotion_date(kind):
    entry = table_entry(kind, newcomers=['beta-2'])
    async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, text=html(kind, beta=False)))) as client:
        result = await probe_entry(client, entry, attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'beta-2' in result.detail and 'newcomer' in result.detail
    assert for_a_human(result.detail) == result.detail


@pytest.mark.parametrize('kind', ['prices', 'plan'])
async def test_known_waiting_offer_does_not_promote_or_flag_paid_only_choices(kind):
    entry = table_entry(kind, newcomers=['beta-2'])
    before = entry.model_dump_json()
    async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, text=html(kind)))) as client:
        result = await probe_entry(client, entry, attempts=1, backoff=0)
    assert result.status is ProbeStatus.PASS
    assert entry.model_dump_json() == before


@pytest.mark.parametrize('kind', ['prices', 'plan'])
async def test_exact_vendor_label_tracks_waiting_access_without_guessing_model_identity(kind):
    value = table_entry(kind, newcomers=['beta-2-chat']).model_dump()
    value['newcomers'][0]['table_name'] = 'Beta 2'
    entry = Entry.model_validate(value)
    async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, text=html(kind)))) as client:
        result = await probe_entry(client, entry, attempts=1, backoff=0)
    assert result.status is ProbeStatus.PASS
    assert [m.family for m in entry.models] == ['alpha-1']


def excluded_entry(kind, *, age=0):
    value = table_entry(kind).model_dump()
    value['probe']['model_exclusions'] = [{'name': 'Beta 2',
        'source': 'https://vendor.example/decision-model',
        'quote': 'This decision model does not generate text or code.',
        'reviewed_on': date.today() - timedelta(days=age)}]
    return Entry.model_validate(value)


@pytest.mark.parametrize('age,status', [(-1,ProbeStatus.STALE_IDS),(6,ProbeStatus.PASS),(7,ProbeStatus.STALE_IDS)])
async def test_a_sourced_exclusion_cannot_silently_outlive_its_manual_review(age, status):
    entry = excluded_entry('prices', age=age)
    def respond(request):
        return httpx.Response(200, text=html('prices') if str(request.url)==entry.probe.endpoint else
                              'This decision model does not generate text or code.')
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await probe_entry(client, entry, attempts=1, backoff=0)
    assert result.status is status
    if age in (-1,7):
        assert 'dated review' in result.detail
        assert for_a_human(result.detail) == result.detail


@pytest.mark.parametrize('source_status,body', [(200,'Now a coding model.'),(404,'gone')])
async def test_changed_or_unavailable_exclusion_reason_is_a_live_http_finding(source_status, body):
    entry = excluded_entry('prices')
    def respond(request):
        return httpx.Response(200,text=html('prices')) if str(request.url)==entry.probe.endpoint else httpx.Response(source_status,text=body)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await probe_entry(client, entry, attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'exclusion' in result.detail and for_a_human(result.detail) == result.detail


def test_exclusion_cannot_cover_a_current_family_or_waiting_offer():
    value = excluded_entry('prices').model_dump()
    value['probe']['model_exclusions'][0]['name'] = 'Alpha 1'
    with pytest.raises(ValueError, match='cannot hide'):
        Entry.model_validate(value)
    value['probe']['model_exclusions'][0]['name'] = 'Beta 2'
    value['newcomers'] = [{'family':'beta-2','on':'2026-10-25','source':'https://vendor.example/models'}]
    with pytest.raises(ValueError, match='cannot hide'):
        Entry.model_validate(value)


def test_a_label_is_not_a_sourced_exclusion_reason():
    value = excluded_entry('prices').model_dump()
    value['probe']['model_exclusions'][0]['quote'] = 'Free'
    with pytest.raises(ValueError,match='complete eligibility statement'):
        Entry.model_validate(value)


def test_scout_does_not_accept_a_proposal_which_hides_a_new_free_row():
    from freetier_radar.scout import probe_check_sync
    entry = table_entry('plan')
    with httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,text=html('plan')))) as client:
        finding = probe_check_sync(entry,client)
    assert 'Beta 2' in finding and for_a_human(finding) == finding


async def test_new_version_is_not_hidden_under_an_existing_broader_family():
    entry = table_entry('prices', newcomers=['beta-2'])
    body = html('prices').replace('</table>', '<tr><td>Alpha 1.1</td><td>Free</td><td>Free</td></tr></table>')
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:httpx.Response(200,text=body))) as client:
        result = await probe_entry(client,entry,attempts=1,backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'Alpha 1.1' in result.detail


def test_current_waiting_choices_remain_visible_without_entering_the_qualified_family_list():
    from freetier_radar.render import build_provider_page, build_model_page
    value = table_entry('prices',newcomers=['beta-2']).model_dump()
    value['newcomers'][0]['table_name'] = 'Beta 2 Free'
    entry = Entry.model_validate(value)
    body = build_provider_page(entry,[],date.today(),registry=[entry])
    assert 'Beta 2 Free' in body.split('## Connect',1)[1].split('\n## ',1)[0]
    assert 'Beta 2 Free' not in body.split('## Free models',1)[1].split('\n## ',1)[0]
    assert [m.family for m in entry.models] == ['alpha-1']
    model_page = build_model_page('alpha-1',[entry],[],date.today())
    assert 'Beta 2 Free' not in model_page


@pytest.mark.parametrize('extra_variant', [False,True])
async def test_qualified_family_binds_one_exact_decorated_table_row(extra_variant):
    value=table_entry('prices',newcomers=['beta-2']).model_dump()
    value['models'][0]['table_name']='Alpha 1 (thinking)*'
    entry=Entry.model_validate(value)
    body=html('prices').replace('<td>Alpha 1</td>','<td>Alpha 1 (thinking)*</td>')
    if extra_variant:body=body.replace('</table>','<tr><td>Alpha 1</td><td>Free</td><td>Free</td></tr></table>')
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:httpx.Response(200,text=body))) as client:
        result=await probe_entry(client,entry,attempts=1,backoff=0)
    assert result.status is (ProbeStatus.STALE_IDS if extra_variant else ProbeStatus.PASS)


async def test_catalog_arrival_does_not_hide_an_explicit_free_offer_with_another_id_suffix():
    value=table_entry('prices').model_dump()
    value['category']='api-free-tier';value['probe']={'type':'api-models','endpoint':'https://vendor.example/models','free_marker':':free','require_zero_price':True}
    value['api']={'base_url':'https://vendor.example/v1','auth':'api-key','openai_compatible':True,'model_ids':['alpha-1:free']}
    entry=Entry.model_validate(value)
    data={'data':[{'id':'alpha-1:free','isFree':True,'pricing':{'prompt':'0','completion':'0'}},
                  {'id':'beta-2-free','isFree':True,'pricing':{'prompt':'0','completion':'0'}},
                  {'id':'paid-3','isFree':False,'pricing':{'prompt':'0','completion':'0'}}]}
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=data))) as client:
        result=await probe_entry(client,entry,attempts=1,backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'beta-2-free' in result.detail and 'paid-3' not in result.detail
    assert for_a_human(result.detail)==result.detail
    assert entry.api.model_ids==['alpha-1:free']


@pytest.mark.parametrize('present',[False,True])
async def test_plain_page_waiting_choices_stay_visible_and_missing_names_request_review(present):
    from freetier_radar.render import build_provider_page
    value=table_entry('prices',newcomers=['beta-2']).model_dump();value['probe'].pop('model_prices')
    entry=Entry.model_validate(value);body='alpha-1 free tier'+(' and beta-2' if present else '')
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:httpx.Response(200,text=body))) as client:
        result=await probe_entry(client,entry,attempts=1,backoff=0)
    assert result.status is (ProbeStatus.PASS if present else ProbeStatus.STALE_IDS)
    if present:
        rendered=build_provider_page(entry,[],date.today(),registry=[entry])
        assert 'beta-2' in rendered.split('## Connect',1)[1].split('\n## ',1)[0]
    else:assert for_a_human(result.detail)==result.detail and 'beta-2' in result.detail
