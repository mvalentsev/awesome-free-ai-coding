import httpx
import respx

from freetier_radar.discovery import (
    Evidence, Hit, domain_of, format_evidence, gather_evidence,
    github_search, hn_search, tavily_search,
)


def test_domain_of():
    assert domain_of("https://www.x.ai/pricing?a=1") == "x.ai"
    assert domain_of("https://sub.x.ai/") == "sub.x.ai"


@respx.mock
def test_tavily_search():
    respx.post("https://api.tavily.com/search").mock(return_value=httpx.Response(
        200, json={"results": [{"url": "https://a.dev", "title": "A", "content": "free tier"},
                               {"title": "no url, skipped"}]}
    ))
    with httpx.Client() as c:
        hits = tavily_search(c, "key", "free llm api")
    assert hits == [Hit("https://a.dev", "A", "free tier", "tavily")]


@respx.mock
def test_hn_search_falls_back_to_item_link():
    respx.get("https://hn.algolia.com/api/v1/search").mock(return_value=httpx.Response(
        200, json={"hits": [{"url": "https://c.dev", "title": "C"},
                            {"url": None, "title": "Ask HN", "objectID": "42"}]}
    ))
    with httpx.Client() as c:
        hits = hn_search(c, "free llm api")
    assert hits[0].url == "https://c.dev"
    assert hits[1].url == "https://news.ycombinator.com/item?id=42"


@respx.mock
def test_github_search_filters_low_stars():
    respx.get("https://api.github.com/search/repositories").mock(return_value=httpx.Response(
        200, json={"items": [
            {"html_url": "https://github.com/a/big", "full_name": "a/big",
             "description": "free llm", "stargazers_count": 500},
            {"html_url": "https://github.com/a/tiny", "full_name": "a/tiny",
             "description": "", "stargazers_count": 3},
        ]}
    ))
    with httpx.Client() as c:
        hits = github_search(c, "free llm api")
    assert [h.url for h in hits] == ["https://github.com/a/big"]


@respx.mock
def test_gather_evidence_keyless_dedup_and_filters(monkeypatch):
    import freetier_radar.discovery as disc
    monkeypatch.setattr(disc, "CURATED_FEEDS", ["https://raw.example.com/list.md"])
    respx.get("https://hn.algolia.com/api/v1/search").mock(return_value=httpx.Response(
        200, json={"hits": [{"url": "https://newtool.dev/pricing", "title": "New tool"},
                            {"url": "https://newtool.dev/pricing", "title": "dup"},
                            {"url": "https://reddit.com/r/thread", "title": "noise"},
                            {"url": "https://x.ai/known", "title": "already covered"}]}
    ))
    respx.get("https://api.github.com/search/repositories").mock(return_value=httpx.Response(
        200, json={"items": []}
    ))
    respx.get("https://raw.example.com/list.md").mock(return_value=httpx.Response(200, text="- curated"))
    respx.get("https://newtool.dev/pricing").mock(return_value=httpx.Response(
        200, text="<html><body>Generous free tier</body></html>"
    ))
    with httpx.Client() as c:
        ev = gather_evidence(["q1"], {"x.ai"}, env={}, http=c)
    assert [h.url for h in ev.hits] == ["https://newtool.dev/pricing"]
    assert ev.pages["https://newtool.dev/pricing"].strip() == "Generous free tier"
    assert ev.feeds == {"https://raw.example.com/list.md": "- curated"}
    assert ev.providers == ["hn", "curated-feeds"]


def test_format_evidence_and_is_empty():
    assert Evidence().is_empty()
    ev = Evidence(hits=[Hit("https://a.dev", "A", "snippet", "hn")],
                  pages={"https://a.dev": "text", "https://empty.dev": ""},
                  feeds={"https://feed.md": "- item"})
    text = format_evidence(ev)
    assert "- [hn] A — https://a.dev :: snippet" in text
    assert "PAGE https://a.dev:\ntext" in text
    assert "https://empty.dev" not in text
    assert "CURATED FEED https://feed.md" in text
