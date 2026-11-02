"""A Framer shell is unreadable; only the same rendered page can prove an offer."""
import json
from types import SimpleNamespace

import httpx
import pytest
import respx

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, probe_entry

URL = "https://vendor.example/cli"
INDEX = "https://framerusercontent.com/sites/exampleSite/searchIndex-example.json"
SHELL = ('<html><head><title>Vendor</title>'
         f'<meta name="framer-search-index" content="{INDEX}"></head>'
         '<body><script>render()</script><div id="main"></div></body></html>')
HTML = '<html><body>One Command, Full PR Review; Start Free Trial; NO CC REQUIRED</body></html>'


def entry():
    return Entry.model_validate({"id": "vendor", "name": "Vendor", "category": "trial",
        "url": URL, "offering": "CLI trial", "first_seen": "2026-01-01",
        "last_verified": "2026-01-01", "probe": {"type": "page-keywords",
        "endpoint": URL, "keywords": ["One Command, Full PR Review", "Start Free Trial", "NO CC REQUIRED"]}})


@respx.mock
async def test_empty_framer_page_recovers_at_http_boundary(monkeypatch):
    import curl_cffi
    calls = []
    def read(url, **kw):
        calls.append(url)
        return SimpleNamespace(status_code=200, url=url, content=HTML.encode(),
                               headers={"content-type": "text/html"})
    monkeypatch.setattr(curl_cffi, "get", read)
    respx.get(URL).respond(200, text=SHELL, headers={"content-type": "text/html"})
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert calls == [URL]  # No cross-page search index is fetched.


@pytest.mark.parametrize("status,body,content_type,expected", [
    (200, SHELL, "text/html", ProbeStatus.INCONCLUSIVE),
    (404, HTML, "text/html", ProbeStatus.INCONCLUSIVE),
    (429, HTML, "text/html", ProbeStatus.INCONCLUSIVE),
    (200, '{"claim":"Start Free Trial"}', "application/json", ProbeStatus.INCONCLUSIVE),
    (200, '<html><body>Paid plans only</body></html>', "text/html", ProbeStatus.FAIL),
])
@respx.mock
async def test_shell_failure_is_not_withdrawal_but_readable_paid_page_is(monkeypatch, status, body, content_type, expected):
    import curl_cffi
    monkeypatch.setattr(curl_cffi, "get", lambda url, **kw: SimpleNamespace(
        status_code=status, url=url, content=body.encode(), headers={"content-type": content_type}))
    respx.get(URL).respond(200, text=SHELL, headers={"content-type": "text/html"})
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), backoff=0)
    assert result.status is expected


@respx.mock
async def test_other_route_cannot_restore_the_cli_offer(monkeypatch):
    import curl_cffi
    calls = []
    def read(url, **kw):
        calls.append(url)
        if url == URL:
            return SimpleNamespace(status_code=302, url=url, content=b"",
                headers={"location": "/pricing"})
        return SimpleNamespace(status_code=200, url=url, content=HTML.encode(),
                               headers={"content-type": "text/html"})
    monkeypatch.setattr(curl_cffi, "get", read)
    respx.get(URL).respond(200, text=SHELL, headers={"content-type": "text/html"})
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE
    assert calls == [URL, "https://vendor.example/pricing"]


@pytest.mark.parametrize("credentials", [
    {"headers": {"Authorization": "Bearer private"}}, {"cookies": {"session": "private"}},
    {"headers": {"X-API-Key": "private"}}, {"auth": ("user", "password")},
])
@respx.mock
async def test_authenticated_shell_never_uses_alternate_transport(monkeypatch, credentials):
    import curl_cffi
    calls = []
    monkeypatch.setattr(curl_cffi, "get", lambda *args, **kw: calls.append(args))
    respx.get(URL).respond(200, text=SHELL, headers={"content-type": "text/html"})
    async with httpx.AsyncClient(**credentials) as client:
        result = await probe_entry(client, entry(), backoff=0)
    assert calls == [] and result.status is ProbeStatus.INCONCLUSIVE


@pytest.mark.parametrize("status,headers,body", [
    (200, {"content-type": "text/html"}, SHELL.replace('<div id="main"></div>', '<p>Paid plans only</p>')),
    (200, {"content-type": "text/html", "Retry-After": "120"}, SHELL),
    (401, {"content-type": "text/html"}, SHELL),
    (404, {"content-type": "text/html"}, SHELL),
    (429, {"content-type": "text/html"}, SHELL),
    (200, {"content-type": "text/html"}, SHELL.replace("framer-search-index", "unrelated-index")),
])
@respx.mock
async def test_missing_claim_or_retry_header_is_not_reason_for_retry(monkeypatch, status, headers, body):
    import curl_cffi
    calls = []
    monkeypatch.setattr(curl_cffi, "get", lambda *args, **kw: calls.append(args))
    respx.get(URL).respond(status, text=body, headers=headers)
    async with httpx.AsyncClient() as client:
        await probe_entry(client, entry(), backoff=0)
    assert calls == []


@respx.mock
async def test_quote_reader_preserves_both_actual_http_responses(monkeypatch, tmp_path):
    import curl_cffi
    from freetier_radar.page_reader import page_evidence
    from freetier_radar.quotes import fetch_pages
    monkeypatch.setattr(curl_cffi, "get", lambda url, **kw: SimpleNamespace(
        status_code=200, url=url, content=HTML.encode(), headers={"content-type": "text/html"}))
    respx.get(URL).respond(200, text=SHELL, headers={"content-type": "text/html"})
    with page_evidence(tmp_path):
        async with httpx.AsyncClient() as client:
            pages, unread = await fetch_pages(client, [URL])
    assert not unread and any("no cc required" in p for p in pages)
    receipt = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert [a["backend"] for a in receipt["attempts"]] == ["httpx", "curl_cffi"]
    assert (tmp_path / receipt["attempts"][0]["file"]).read_text() == SHELL
    assert (tmp_path / receipt["attempts"][1]["file"]).read_text() == HTML


@respx.mock
async def test_sync_path_and_bounded_failure_are_unreadable(monkeypatch):
    import curl_cffi
    from freetier_radar.page_reader import recover_page_sync
    from freetier_radar.prober import page_response_ok
    calls = []
    def read(url, **kw):
        calls.append(url)
        raise OSError("unavailable")
    monkeypatch.setattr(curl_cffi, "get", read)
    respx.get(URL).respond(200, text=SHELL, headers={"content-type": "text/html"})
    with httpx.Client() as client:
        shell = client.get(URL)
        assert recover_page_sync(client, shell, time_left=0) is shell
        assert calls == [] and not page_response_ok(shell)
        assert recover_page_sync(client, shell) is shell
    assert calls == [URL] and not page_response_ok(shell)
