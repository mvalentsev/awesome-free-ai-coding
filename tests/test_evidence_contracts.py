"""Independent regressions for source scope and published eligibility."""
import json
import re
import subprocess
from pathlib import Path

import httpx
import pytest
import respx
from pydantic import ValidationError

from freetier_radar.models import FreeSince, Notice, PageCatalog
from freetier_radar.prober import probe_entry
from freetier_radar.render import build_index, needs_no_account
from freetier_radar.source_urls import valid_source_url
from test_page_catalog import catalog_data, entry, page
from test_render import TODAY, make


def quoted_catalog():
    data = catalog_data()
    data['budgets'][0].update(countries=['US', 'KR'], quote='US, KR: 100 Credits a day')
    data['budgets'][1]['quote'] = 'Everywhere else: 25'
    data['budgets'][2]['quote'] = 'Any VPN or proxy: 20'
    return data


def test_complete_quoted_country_scope_is_required_before_rendering():
    data = quoted_catalog()
    data['budgets'][0]['countries'].remove('KR')
    with pytest.raises(ValidationError, match='countries'):
        PageCatalog.model_validate(data)


@respx.mock
async def test_http_page_probe_reports_incomplete_quoted_country_scope():
    e = entry(quoted_catalog())
    e.page_catalog.budgets[0].countries.remove('KR')
    respx.get(e.probe.endpoint).respond(200, text=page().replace('US:', 'US, KR:'))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, e, attempts=1, backoff=0)
    assert 'KR' in result.detail, result.detail


@pytest.mark.parametrize('api,expected', [
    ({'auth':'none'}, False),
    ({'auth':'none','base_url':'https://vendor.example/v1'}, True),
    ({'auth':'api-key','base_url':'https://vendor.example/v1'}, False),
    ({'auth':'api-key','base_url':'https://vendor.example/v1',
      'public_key':'public-trial','key_url':'https://vendor.example/try','model_ids':['trial']}, True),
])
def test_actual_browser_filter_agrees_with_generated_eligibility(api, expected):
    e = make(api=api)
    published = build_index([e], TODAY)['entries'][0]
    source = Path('browse.html').read_text()
    functions = '\n'.join(re.search(r'  function '+name+r'\(e\) \{[^\n]+\}', source).group(0)
                          for name in ('keyless','publicKey','noAccount'))
    js = functions+'\nprocess.stdout.write(JSON.stringify(noAccount(JSON.parse(process.argv[1]))));'
    result = subprocess.run(['node','-e',js,json.dumps(published)], capture_output=True,text=True,check=True)
    assert json.loads(result.stdout) is expected
    assert needs_no_account(e) is expected


@pytest.mark.parametrize('model,data', [
    (Notice, {'since':'2026-10-10','text':'A dated notice','url':'https://'}),
    (FreeSince, {'id':'model','on':'2026-10-10','source':'https://'}),
])
def test_source_url_requires_a_hostname(model, data):
    with pytest.raises(ValidationError):
        model.model_validate(data)


@pytest.mark.parametrize('url', ['https://', 'https:///page', 'https://@host/page',
                                'https://user:secret@host/page', 'https://bad host/page',
                                'https://host:bad/page', 'https://[invalid/page'])
def test_source_links_reject_malformed_hosts_and_credentials(url):
    assert not valid_source_url(url)


def test_source_schemes_remain_explicit_and_valid_links_are_preserved():
    assert valid_source_url('https://vendor.example:443/page?q=a#part')
    assert not valid_source_url('http://vendor.example/page')
    assert valid_source_url('http://vendor.example/page', schemes=('http','https'))
