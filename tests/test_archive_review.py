from datetime import date, timedelta
from pathlib import Path
import json
import subprocess

import httpx
import pytest
import respx
import yaml

from freetier_radar.archive_review import (ARCHIVE_RECHECK_DAYS, collect, due_entries, markdown)
from freetier_radar.models import ArchiveReview, Entry
from freetier_radar.review import Bundle

TODAY = date(2026, 10, 27)


def archived(**changes):
    row = dict(id='vendor', name='Vendor', category='api-free-tier',
               url='https://vendor.example', source_urls=['https://vendor.example/pricing'],
               offering='A past free offer', first_seen='2026-07-19', last_verified='2026-07-19',
               delisted={'on': '2026-09-01', 'reason': 'the previous allowance ended'},
               probe={'type': 'page-keywords', 'endpoint': 'https://vendor.example/pricing',
                      'keywords': ['one million free tokens']})
    row.update(changes)
    return Entry.model_validate(row)


@pytest.mark.parametrize('age,due', [(None, True), (0, False), (6, False), (7, True), (8, True)])
def test_manual_review_date_controls_the_archive_deadline(age, due):
    review = ArchiveReview(checked_on=TODAY-timedelta(days=age), sources=['https://vendor.example/current']) if age is not None else None
    entry = archived(archive_review=review)
    assert bool(due_entries([entry], {}, TODAY)) is due
    assert due_entries([entry], {}, TODAY, all_archived=True) == [entry]
    assert ARCHIVE_RECHECK_DAYS == 7


@pytest.mark.parametrize('kind', ['live', 'future-retirement', 'duplicate', 'blocked', 'blocked-subdomain'])
def test_ineligible_sources_are_excluded_before_any_http(kind):
    entry = archived()
    blocked = {}
    if kind == 'live':
        entry = entry.model_copy(update={'delisted': None, 'last_verified': TODAY})
    elif kind == 'future-retirement':
        entry = entry.model_copy(update={'delisted': None, 'retired_on': TODAY+timedelta(days=1), 'last_verified': TODAY})
    elif kind == 'duplicate':
        entry = entry.model_copy(update={'duplicate_of': 'original'})
    elif kind == 'blocked':
        blocked = {'vendor.example': 'rejected for cause'}
    else:
        entry = entry.model_copy(update={'url': 'https://api.vendor.example'})
        blocked = {'vendor.example': 'rejected for cause'}
    assert due_entries([entry], blocked, TODAY, all_archived=True) == []


def test_vendor_retirement_is_reviewed_even_without_a_manual_delisting():
    entry = archived(delisted=None, retired_on=TODAY)
    assert due_entries([entry], {}, TODAY) == [entry]


@pytest.mark.parametrize('changes', [dict(delisted=None),
    dict(delisted=None,retired_on=TODAY+timedelta(days=1)),
    dict(archive_review={'checked_on':date(2026,8,31),'sources':['https://vendor.example/current']})])
def test_manual_review_stamp_requires_an_already_archived_row(changes):
    with pytest.raises(ValueError,match='archived by that review date'):
        archived(**{'archive_review':{'checked_on':TODAY,'sources':['https://vendor.example/current']},**changes})


@respx.mock
async def test_review_reads_current_conditions_beyond_the_last_offer_sources(tmp_path):
    entry = archived(archive_review={'checked_on':TODAY-timedelta(days=7),
                                    'sources':['https://vendor.example/current']})
    respx.get(entry.probe.endpoint).respond(200,text='An old page')
    current = respx.get('https://vendor.example/current').respond(200,text='A new separate free mode')
    async with httpx.AsyncClient() as client:
        report = await collect([entry],{},TODAY,Bundle(tmp_path/'evidence',Path.cwd()),client=client)
    assert current.call_count == 1
    assert 'https://vendor.example/current' in report['rows'][0]['sources']
    assert entry.archive_review.checked_on == TODAY-timedelta(days=7)


@pytest.mark.parametrize('sources', [[], ['http://vendor.example'], ['https://user:secret@vendor.example']])
def test_review_needs_credential_free_primary_sources(sources):
    with pytest.raises(ValueError):
        archived(archive_review={'checked_on':TODAY,'sources':sources})


@respx.mock
async def test_current_free_offer_is_fetched_but_never_restores_or_earns_a_date(tmp_path):
    entry = archived()
    before = entry.model_dump_json()
    route = respx.get(entry.probe.endpoint).respond(200, text='one million free tokens every month')
    async with httpx.AsyncClient() as client:
        report = await collect([entry], {}, TODAY, Bundle(tmp_path/'evidence', Path.cwd()), client=client)
    assert route.call_count == 1
    assert report['rows'][0]['historical_probe_findings'] == []
    assert report['rows'][0]['needs_manual_review']
    assert report['sources'][0]['readable']
    assert 'one million free tokens' in (tmp_path/'evidence'/report['sources'][0]['file']).read_text()
    assert entry.model_dump_json() == before
    assert report['rows'][0]['reviewed_on'] is None
    assert 'manual review required' in markdown(report)


@respx.mock
async def test_compressed_source_is_decoded_once_and_retained(tmp_path):
    import gzip
    entry = archived()
    body = b'one million free tokens every month'
    respx.get(entry.probe.endpoint).respond(200, content=gzip.compress(body),
        headers={'Content-Type':'text/html; charset=utf-8','Content-Encoding':'gzip'})
    async with httpx.AsyncClient() as client:
        report = await collect([entry], {}, TODAY, Bundle(tmp_path/'evidence',Path.cwd()),client=client)
    source = report['sources'][0]
    assert source['readable'], source
    assert report['rows'][0]['historical_probe_findings'] == []
    assert (tmp_path/'evidence'/source['file']).read_bytes() == body


@pytest.mark.parametrize('status,body', [(404, 'gone'), (403, 'blocked'),
    (429, 'wait'), (200, '<title>Just a moment...</title><script>window._cf_chl_opt={}</script>')])
@respx.mock
async def test_unavailable_sources_remain_visible_without_an_eligibility_verdict(tmp_path, status, body):
    entry = archived()
    headers = {'Content-Type': 'text/html'}
    if status == 429:
        headers['Retry-After'] = '60'
    route = respx.get(entry.probe.endpoint).respond(status, text=body, headers=headers)
    async with httpx.AsyncClient() as client:
        report = await collect([entry], {}, TODAY, Bundle(tmp_path/'evidence', Path.cwd()), client=client)
    assert route.call_count == 1
    assert not report['sources'][0]['readable']
    assert report['rows'][0]['historical_probe_findings'] == ['last-offer probe source is unavailable']
    assert '1/1 sources unavailable' in markdown(report)


async def test_blocklisted_links_and_redirects_are_never_fetched(tmp_path):
    entry = archived(source_urls=['https://hostile.example/page'])
    requests = []
    def respond(request):
        requests.append(str(request.url))
        assert request.url.host == 'vendor.example'
        return httpx.Response(302, headers={'Location': 'https://hostile.example/redirect'})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        report = await collect([entry], {'hostile.example': 'rejected for cause'}, TODAY,
                               Bundle(tmp_path/'evidence', Path.cwd()), client=client)
    assert requests == [entry.probe.endpoint]
    assert len(report['sources']) == 2
    assert all(not source['readable'] for source in report['sources'])
    assert all('excluded' in source['error'] for source in report['sources'])


@respx.mock
async def test_dynamic_probe_index_uses_its_current_target(tmp_path):
    entry = archived(probe={'type':'page-keywords','endpoint':'https://vendor.example/index.json',
                           'keywords':['one million free tokens'],
                           'follow':{'field':'release','suffix':'/offer'}})
    respx.get(entry.probe.endpoint).respond(200,json={'release':'https://vendor.example/current'})
    target=respx.get('https://vendor.example/current/offer').respond(200,text='one million free tokens')
    respx.get('https://vendor.example/pricing').respond(200,text='pricing')
    async with httpx.AsyncClient() as client:
        report=await collect([entry],{},TODAY,Bundle(tmp_path/'evidence',Path.cwd()),client=client)
    assert target.call_count == 1
    assert report['rows'][0]['historical_probe_findings'] == []
    assert 'https://vendor.example/current/offer' in report['rows'][0]['sources']


@respx.mock
async def test_body_and_overall_time_limits_preserve_incomplete_reads(tmp_path, monkeypatch):
    import freetier_radar.archive_review as module
    entry=archived()
    monkeypatch.setattr(module,'RECOVERY_BYTES',4)
    respx.get(entry.probe.endpoint).respond(200,text='too large')
    async with httpx.AsyncClient() as client:
        report=await collect([entry],{},TODAY,Bundle(tmp_path/'size',Path.cwd()),client=client)
    assert 'body limit' in report['sources'][0]['error']
    monkeypatch.setattr(module,'ARCHIVE_REVIEW_SECONDS',0)
    async with httpx.AsyncClient() as client:
        report=await collect([entry],{},TODAY,Bundle(tmp_path/'time',Path.cwd()),client=client)
    assert 'budget exhausted' in report['sources'][0]['error']


def test_scheduled_collection_runs_before_any_writer_or_backend_and_preserves_evidence(tmp_path):
    workflow=yaml.safe_load(Path('.github/workflows/update.yml').read_text())
    steps=workflow['jobs']['update']['steps']
    position=next(i for i,s in enumerate(steps) if s.get('name')=='Collect archived offers due for manual review')
    step=steps[position]
    assert '!inputs.provider_ids' in step['if']
    assert position < next(i for i,s in enumerate(steps) if s.get('name')=='Commit verification results to main')
    assert position < next(i for i,s in enumerate(steps) if s.get('name','').startswith('Scout ('))
    upload=next(s for s in steps if s.get('name')=='Preserve archived-offer review evidence')
    assert 'always()' in upload['if'] and '!inputs.provider_ids' in upload['if']
    assert upload['with']['path']=='failures/archive-review/'
    stub=tmp_path/'uv';receipt=tmp_path/'args.json'
    stub.write_text('#!/usr/bin/env python3\nimport sys,json\nfrom pathlib import Path\n'
                    'Path("args.json").write_text(json.dumps(sys.argv[1:]))\nprint("archive evidence")\n')
    stub.chmod(0o755)
    import os
    result=subprocess.run(['bash','-e','-c',step['run']],cwd=tmp_path,capture_output=True,text=True,
                          env={**os.environ,'PATH':str(tmp_path)+os.pathsep+os.environ['PATH'],
                               'GITHUB_STEP_SUMMARY':str(tmp_path/'summary')})
    assert result.returncode==0,result.stderr
    assert json.loads(receipt.read_text())==['run','freetier-archive-review','--out','failures/archive-review']
    assert 'archive evidence' in (tmp_path/'summary').read_text()
