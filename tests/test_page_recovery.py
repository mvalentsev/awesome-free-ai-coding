"""Public-page walls are transport failures; a recovered page still needs proof."""
from types import SimpleNamespace

import httpx
import pytest
import respx

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, probe_entry
from freetier_radar.page_reader import _addresses as REAL_ADDRESSES

URL = 'https://vendor.example/pricing'
HTML = '<html><body>Prototype and test with our free API; no credit card</body></html>'

def entry():
    return Entry.model_validate({'id':'vendor', 'name':'Vendor', 'category':'api-free-tier',
        'url':'https://vendor.example', 'offering':'Public free tier',
        'first_seen':'2026-01-01','last_verified':'2026-01-01',
        'probe':{'type':'page-keywords','endpoint':URL,'keywords':['Prototype and test with our free API','no credit card']}})

@respx.mock
async def test_blocked_page_recovered_at_http_boundary(monkeypatch):
    import curl_cffi
    calls=[]
    def read(url, **kwargs):
        calls.append((url,kwargs))
        return SimpleNamespace(status_code=200,content=HTML.encode(),url=url,
                               headers={'content-type':'text/html'})
    monkeypatch.setattr(curl_cffi,'get',read)
    direct=respx.get(URL).respond(403,text='<html>Checking your browser</html>',
                                headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        verdict=await probe_entry(client,entry(),backoff=0)
    assert verdict.status is ProbeStatus.PASS
    assert direct.call_count==1 and len(calls)==1

@respx.mock
async def test_successful_transport_cannot_restore_ended_offer(monkeypatch):
    import curl_cffi
    monkeypatch.setattr(curl_cffi,'get',lambda url,**kwargs:SimpleNamespace(
        status_code=200,content=b'<html>Paid plans only</html>',url=url,
        headers={'content-type':'text/html'}))
    respx.get(URL).respond(403,text='<html>Checking your browser</html>',
                           headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        verdict=await probe_entry(client,entry(),backoff=0)
    assert verdict.status is ProbeStatus.FAIL
    assert 'missing keywords' in verdict.detail

@pytest.mark.parametrize('status,body,headers',[
    (200,HTML,{'content-type':'text/html'}),
    (200,'Paid plans only',{'content-type':'text/html'}),
    (401,'Checking your browser',{'content-type':'text/html'}),
    (404,'Checking your browser',{'content-type':'text/html'}),
    (410,'Checking your browser',{'content-type':'text/html'}),
    (429,'Checking your browser',{'content-type':'text/html','Retry-After':'120'}),
    (403,'Checking your browser',{'content-type':'text/html','Retry-After':'120'}),
    (403,'{"error":"Checking your browser"}',{'content-type':'application/json'}),
    (500,'Checking your browser',{'content-type':'text/html'}),
])
@respx.mock
async def test_recovery_only_when_anonymous_page_is_blocked(monkeypatch,status,body,headers):
    import curl_cffi
    calls=[]
    monkeypatch.setattr(curl_cffi,'get',lambda *a,**k:calls.append(a))
    direct=respx.get(URL).respond(status,text=body,headers=headers)
    async with httpx.AsyncClient() as client:
        await probe_entry(client,entry(),backoff=0)
    assert calls==[]
    assert direct.call_count == (3 if status==500 else 1)

@pytest.mark.parametrize('credentials',[
    {'headers':{'Authorization':'Bearer private'}},
    {'headers':{'X-API-Key':'private'}},
    {'cookies':{'session':'private'}},
    {'auth':('private','secret')},
])
@respx.mock
async def test_client_credentials_never_enter_alternate_transport(monkeypatch,credentials):
    import curl_cffi
    calls=[]
    monkeypatch.setattr(curl_cffi,'get',lambda *a,**k:calls.append(a))
    respx.get(URL).respond(403,text='<html>Checking your browser</html>',headers={'content-type':'text/html'})
    async with httpx.AsyncClient(**credentials) as client:
        result=await probe_entry(client,entry(),backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE and calls==[]

@respx.mock
async def test_api_catalog_never_uses_page_recovery(monkeypatch):
    import curl_cffi
    from freetier_radar.prober import _fetch_catalog
    calls=[]
    monkeypatch.setattr(curl_cffi,'get',lambda *a,**k:calls.append(a))
    respx.get(URL).respond(403,text='<html>Checking your browser</html>',headers={'content-type':'text/html'})
    api=entry();from freetier_radar.models import ProbeType
    api.probe.type=ProbeType.API_MODELS
    async with httpx.AsyncClient() as client:
        result=await probe_entry(client,api,backoff=0)
        catalog,why=await _fetch_catalog(client,URL,1,0)
    assert result.status is ProbeStatus.INCONCLUSIVE and catalog is None and calls==[]

@pytest.mark.parametrize('url',[
    'http://vendor.example/pricing','https://127.0.0.1/pricing',
    'https://[::1]/pricing','https://private.local/pricing','https://localhost/pricing',
    'https://user:secret@vendor.example/pricing','https://vendor.example/pricing?token=secret',
    'https://api.vendor.example/models','https://vendor.example/v1/models',
])
def test_private_or_nonpage_targets_cannot_start_recovery(url):
    from freetier_radar.page_reader import public_page_url
    assert not public_page_url(url)

@pytest.mark.parametrize('status,body,headers',[
    (403,'Checking your browser',{'content-type':'text/html'}),
    (404,HTML,{'content-type':'text/html'}),
    (429,HTML,{'content-type':'text/html','Retry-After':'60'}),
    (200,'<title>Checking your browser</title>',{'content-type':'text/html'}),
    (200,'{"free":true}',{'content-type':'application/json'}),
])
@respx.mock
async def test_unreadable_alternate_answer_preserves_unavailable_verdict(monkeypatch,status,body,headers):
    import curl_cffi
    monkeypatch.setattr(curl_cffi,'get',lambda url,**kw:SimpleNamespace(
        status_code=status,content=body.encode(),headers=headers,url=url))
    respx.get(URL).respond(403,text='<html>Checking your browser</html>',headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        verdict=await probe_entry(client,entry(),backoff=0)
    assert verdict.status is ProbeStatus.INCONCLUSIVE

@respx.mock
async def test_redirect_to_private_destination_does_not_get_fetched(monkeypatch):
    import curl_cffi
    calls=[]
    def alternate(url,**kwargs):
        calls.append(url)
        return SimpleNamespace(status_code=302,content=b'',url=url,
            headers={'location':'https://127.0.0.1/secrets'})
    monkeypatch.setattr(curl_cffi,'get',alternate)
    respx.get(URL).respond(403,text='<html>Checking your browser</html>',headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        verdict=await probe_entry(client,entry(),backoff=0)
    assert verdict.status is ProbeStatus.INCONCLUSIVE and calls==[URL]

@respx.mock
async def test_audit_keeps_original_wall_and_recovered_bytes(monkeypatch,tmp_path):
    import curl_cffi,json,hashlib
    from freetier_radar.page_reader import page_evidence
    monkeypatch.setattr(curl_cffi,'get',lambda url,**kwargs:SimpleNamespace(
        status_code=200,content=HTML.encode(),url=url,headers={'content-type':'text/html'}))
    respx.get(URL).respond(403,text='<html>Checking your browser</html>',headers={'content-type':'text/html'})
    with page_evidence(tmp_path):
        async with httpx.AsyncClient() as client:
            assert (await probe_entry(client,entry(),backoff=0)).status is ProbeStatus.PASS
    receipt=json.loads(next(tmp_path.glob('*.json')).read_text())
    assert [a['status'] for a in receipt['attempts']]==[403,200]
    for a in receipt['attempts']:
        assert hashlib.sha256((tmp_path/a['file']).read_bytes()).hexdigest()==a['sha256']
    assert (tmp_path/receipt['attempts'][1]['file']).read_bytes()==HTML.encode()

@respx.mock
async def test_publication_byte_check_uses_original_http_only(monkeypatch,tmp_path):
    import curl_cffi
    from freetier_radar.review import Bundle,fetch
    calls=[]
    monkeypatch.setattr(curl_cffi,'get',lambda *a,**k:calls.append(a))
    respx.get(URL).respond(403,text='<html>Checking your browser</html>',headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        receipt=await fetch(client,URL,Bundle(tmp_path,tmp_path),expected=HTML.encode(),page=True)
    assert not receipt['passed'] and calls==[]


def test_sync_recovery_respects_remaining_deadline(monkeypatch):
    import curl_cffi
    from freetier_radar.page_reader import recover_page_sync
    calls=[]
    def alternate(url,**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(status_code=200,content=HTML.encode(),url=url,headers={'content-type':'text/html'})
    monkeypatch.setattr(curl_cffi,'get',alternate)
    wall=httpx.Response(403,text='Checking your browser',headers={'content-type':'text/html'},request=httpx.Request('GET',URL))
    with httpx.Client() as client:
        assert recover_page_sync(client,wall,time_left=0) is wall
        recovered=recover_page_sync(client,wall,time_left=2)
    assert recovered.status_code==200 and len(calls)==1 and 0<calls[0]['timeout']<=2
    assert calls[0]['allow_redirects'] is False
    assert calls[0]['headers']=={'Cache-Control':'no-cache'}

@respx.mock
async def test_http_200_challenge_recovered_but_noscript_notice_is_not(monkeypatch):
    import curl_cffi
    calls=[]
    def alternate(url,**kw):
        calls.append(url)
        return SimpleNamespace(status_code=200,content=HTML.encode(),url=url,headers={'content-type':'text/html'})
    monkeypatch.setattr(curl_cffi,'get',alternate)
    route=respx.get(URL).respond(200,text='<title>Checking your browser</title>',headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        assert (await probe_entry(client,entry(),backoff=0)).status is ProbeStatus.PASS
        route.respond(200,text=HTML+'<noscript>Please enable JavaScript to view</noscript>',headers={'content-type':'text/html'})
        assert (await probe_entry(client,entry(),backoff=0)).status is ProbeStatus.PASS
    assert calls==[URL]

@respx.mock
async def test_recovery_cannot_substitute_another_source(monkeypatch):
    import curl_cffi
    monkeypatch.setattr(curl_cffi,'get',lambda *a,**k:SimpleNamespace(status_code=200,
        content=HTML.encode(),url='https://other.example/pricing',headers={'content-type':'text/html'}))
    respx.get(URL).respond(403,text='Checking your browser',headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        assert (await probe_entry(client,entry(),backoff=0)).status is ProbeStatus.INCONCLUSIVE

@respx.mock
async def test_quotes_scout_and_review_share_original_html(monkeypatch,tmp_path):
    import curl_cffi
    from freetier_radar.quotes import fetch_pages
    from freetier_radar.scout import probe_check_sync
    from freetier_radar.review import Bundle,fetch
    monkeypatch.setattr(curl_cffi,'get',lambda url,**k:SimpleNamespace(status_code=200,
        content=HTML.encode(),url=url,headers={'content-type':'text/html'}))
    respx.get(URL).respond(403,text='Checking your browser',headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        texts,failed=await fetch_pages(client,[URL])
        assert not failed and any('free api' in t.lower() for t in texts)
        receipt=await fetch(client,URL,Bundle(tmp_path,tmp_path),page=True)
        assert receipt['passed'] and [a['status'] for a in receipt['attempts']]==[403,200]
        assert (tmp_path/receipt['file']).read_bytes()==HTML.encode()
        texts,failed=await fetch_pages(client,[URL],catalogs={URL})
        assert not texts and failed
    with httpx.Client() as client:
        assert probe_check_sync(entry(),client) is None

@respx.mock
async def test_oversized_decoded_body_aborts_recovery(monkeypatch):
    import curl_cffi
    from freetier_radar import page_reader
    from curl_cffi.requests.exceptions import RequestException
    from curl_cffi.curl import CURL_WRITEFUNC_ERROR
    monkeypatch.setattr(page_reader,'RECOVERY_BYTES',16)
    def alternate(url,**kw):
        assert kw['content_callback'](b'x'*17)==CURL_WRITEFUNC_ERROR
        raise RequestException('write callback stopped oversized body')
    monkeypatch.setattr(curl_cffi,'get',alternate)
    respx.get(URL).respond(403,text='Checking your browser',headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        assert (await probe_entry(client,entry(),backoff=0)).status is ProbeStatus.INCONCLUSIVE


def test_resolver_rejects_mixed_public_private_addresses(monkeypatch):
    import socket
    monkeypatch.setattr(socket,'getaddrinfo',lambda *a,**k:[
        (socket.AF_INET,socket.SOCK_STREAM,6,'',('1.1.1.1',443)),
        (socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',443))])
    with pytest.raises(ValueError,match='public addresses'):
        REAL_ADDRESSES('vendor.example')


@respx.mock
async def test_already_decoded_profile_html_is_not_decompressed_twice(monkeypatch):
    import curl_cffi
    monkeypatch.setattr(curl_cffi,'get',lambda url,**kw:SimpleNamespace(status_code=200,
        content=HTML.encode(),url=url,headers={'content-type':'text/html','content-encoding':'gzip','content-length':'10'}))
    respx.get(URL).respond(403,text='Checking your browser',headers={'content-type':'text/html'})
    async with httpx.AsyncClient() as client:
        assert (await probe_entry(client,entry(),backoff=0)).status is ProbeStatus.PASS

@pytest.mark.parametrize('first_url,first_headers',[
    (URL+'?token=private',{}),
    (URL,{'Authorization':'Bearer private'}),
    ('https://127.0.0.1/private',{}),
])
def test_original_redirect_chain_cannot_hide_sensitive_request(monkeypatch,first_url,first_headers):
    import curl_cffi
    from freetier_radar.page_reader import recover_page_sync
    calls=[]
    def alternate(url,**kw):
        calls.append(url)
        return SimpleNamespace(status_code=200,content=HTML.encode(),url=url,headers={'content-type':'text/html'})
    monkeypatch.setattr(curl_cffi,'get',alternate)
    first=httpx.Response(302,headers={'location':URL},request=httpx.Request('GET',first_url,headers=first_headers))
    final=httpx.Response(403,text='Checking your browser',headers={'content-type':'text/html'},
        request=httpx.Request('GET',URL),history=[first])
    with httpx.Client() as client:
        assert recover_page_sync(client,final) is final
    assert calls==[]
