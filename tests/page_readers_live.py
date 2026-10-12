"""Bounded real public-page comparison; never earns registry verification."""
import argparse
import importlib.metadata
import json
import pathlib
import shutil
import time
from datetime import datetime, timezone

import httpx
from freetier_radar.models import load_registry
from freetier_radar.prober import UA, check_content

parser = argparse.ArgumentParser()
parser.add_argument('--out', required=True)
parser.add_argument('--backends', nargs='+', default=['httpx', 'jina', 'curl', 'chromium', 'scrapling', 'firecrawl'])
args = parser.parse_args()
out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)
entries = {e.id: e for e in load_registry(pathlib.Path('registry.yaml')) if e.id in {'sea-lion', 'qodo'}}
records = []

def record(backend, ident, start, status=None, content=b'', final_url=None, metadata=None, error=None):
    entry = entries[ident]; content = content.encode() if isinstance(content, str) else content
    stem = backend+'-'+ident
    (out/(stem+'.raw')).write_bytes(content)
    verdict = check_content(httpx.Response(status or 599, content=content,
        headers={'content-type': 'text/html'}, request=httpx.Request('GET', final_url or entry.probe.endpoint)), entry) if content else 'no body'
    item = {'backend':backend,'id':ident,'checked_at':datetime.now(timezone.utc).isoformat(),
        'elapsed_s':round(time.monotonic()-start,2),'target_http':status,'final_url':final_url,
        'bytes':len(content),'content_verdict':verdict,'passed':status is not None and 200<=status<300 and verdict is None,
        'metadata':metadata or {},'error':error,'raw':stem+'.raw'}
    records.append(item); (out/(stem+'.json')).write_text(json.dumps(item,indent=2)+'\n')
    print(json.dumps({k:item[k] for k in ['backend','id','target_http','elapsed_s','bytes','content_verdict','passed','error']}),flush=True)

for backend in args.backends:
    for ident, entry in entries.items():
        url=entry.probe.endpoint;start=time.monotonic()
        try:
            if backend=='httpx':
                with httpx.Client(headers=UA,timeout=20,follow_redirects=True) as client:r=client.get(url)
                record(backend,ident,start,r.status_code,r.content,str(r.url),{'headers':dict(r.headers)})
            elif backend=='jina':
                headers={'X-No-Cache':'true','X-Respond-With':'html','X-Timeout':'20','Accept':'application/json'}
                with httpx.Client(timeout=30,follow_redirects=True) as client:r=client.get('https://r.jina.ai/'+url,headers=headers)
                (out/(backend+'-'+ident+'-service.raw')).write_bytes(r.content)
                try:data=r.json()
                except ValueError:data={}
                page=data.get('data',{}) if isinstance(data,dict) else {};body=page.get('html','')
                status=page.get('httpStatus');source=page.get('url')
                record(backend,ident,start,status,body,source,{'service_http':r.status_code,'headers':dict(r.headers),'data_fields':list(page),'fresh_requested':True})
            elif backend=='firecrawl':
                body={'url':url,'formats':['rawHtml'],'onlyMainContent':False,'maxAge':0,'timeout':20000}
                with httpx.Client(timeout=30) as client:r=client.post('https://api.firecrawl.dev/v2/scrape',json=body)
                (out/(backend+'-'+ident+'-service.raw')).write_bytes(r.content)
                data=r.json();meta=data.get('data',{}).get('metadata',{})
                record(backend,ident,start,meta.get('statusCode'),data.get('data',{}).get('rawHtml',''),meta.get('url'),
                    {'service_http':r.status_code,'sourceURL':meta.get('sourceURL'),'proxyUsed':meta.get('proxyUsed'),
                     'success':data.get('success'),'fresh_requested':True})
            elif backend=='curl':
                import curl_cffi
                r=curl_cffi.get(url,impersonate='chrome',timeout=20,allow_redirects=True)
                record(backend,ident,start,r.status_code,r.content,r.url,{'version':importlib.metadata.version('curl_cffi'),'headers':dict(r.headers)})
            elif backend=='chromium':
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser=p.chromium.launch(executable_path=shutil.which('google-chrome'),headless=True)
                    context=browser.new_context();page=context.new_page();responses=[]
                    page.on('response',lambda response:responses.append({'status':response.status,'url':response.url}) if response.request.resource_type=='document' and response.frame==page.main_frame else None)
                    response=page.goto(url,wait_until='domcontentloaded',timeout=20000)
                    try:page.wait_for_function("words=>words.every(w=>document.body.innerText.toLowerCase().includes(w.toLowerCase()))",arg=entry.probe.keywords,timeout=15000)
                    except Exception:pass
                    record(backend,ident,start,responses[-1]['status'] if responses else response.status,page.content(),page.url,{'version':importlib.metadata.version('playwright'),'documents':responses,'title':page.title()})
                    context.close();browser.close()
            elif backend=='scrapling':
                from scrapling.fetchers import StealthyFetcher
                r=StealthyFetcher.fetch(url,headless=True,executable_path=shutil.which('google-chrome'),
                    google_search=False,solve_cloudflare=False,timeout=20000,retries=1,wait=1000)
                record(backend,ident,start,r.status,r.body,r.url,{'version':importlib.metadata.version('scrapling')})
        except Exception as error:
            record(backend,ident,start,error=type(error).__name__+': '+str(error))
(out/'result.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'records':records,
    'meaning':'Real anonymous public-page retrieval and deterministic content checks; no earned fields changed.'},indent=2)+'\n')
