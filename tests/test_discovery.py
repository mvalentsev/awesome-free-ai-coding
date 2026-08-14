import httpx
import respx

from freetier_radar.discovery import (
    Evidence, Hit, domain_of, fetch_page_texts, format_evidence, gather_evidence,
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


@respx.mock
def test_gather_evidence_opens_no_connection_once_its_budget_is_gone():
    """Nothing is mocked here on purpose: respx raises on any request, so a phase
    that starts spending a budget it does not have fails loudly instead of
    quietly eating the LLM phases' share of the run."""
    with httpx.Client() as c:
        ev = gather_evidence(["q1"], set(), env={}, http=c, time_left=lambda: 0.0)
    assert ev.is_empty() and ev.providers == []


@respx.mock
def test_gather_evidence_keeps_what_it_paid_for_when_the_budget_runs_out(monkeypatch):
    """Partial evidence is still evidence. The phase stops buying more; it does
    not throw away the hits it already has. Neither the page nor the feed is
    mocked — fetching either one after the budget is gone is the failure."""
    import freetier_radar.discovery as disc
    monkeypatch.setattr(disc, "CURATED_FEEDS", ["https://raw.example.com/list.md"])
    budget = {"left": 30.0}

    def spend_it_all(request):
        budget["left"] = 0.0
        return httpx.Response(200, json={"hits": [{"url": "https://newtool.dev/pricing",
                                                   "title": "New tool"}]})

    respx.get("https://hn.algolia.com/api/v1/search").mock(side_effect=spend_it_all)
    with httpx.Client() as c:
        ev = gather_evidence(["q1"], set(), env={}, http=c, time_left=lambda: budget["left"])
    assert [h.url for h in ev.hits] == ["https://newtool.dev/pricing"]
    assert ev.pages == {} and ev.feeds == {}
    assert ev.providers == ["hn"]


@respx.mock
def test_fetch_page_texts_stops_at_the_deadline():
    """Ten arbitrary hosts, 30 seconds of read timeout each: the loop is where an
    unbounded evidence phase actually runs out of run."""
    budget = {"left": 30.0}

    def spend_it_all(request):
        budget["left"] = 0.0
        return httpx.Response(200, text="<p>first</p>")

    respx.get("https://a.dev").mock(side_effect=spend_it_all)
    with httpx.Client() as c:
        pages = fetch_page_texts(["https://a.dev", "https://b.dev"], c,
                                 time_left=lambda: budget["left"])
    assert list(pages) == ["https://a.dev"]


@respx.mock
def test_a_page_fetch_never_outlives_the_budget_it_is_spending():
    """Checking the clock between requests bounds how many are made; capping the
    request itself is what stops one hung host from spending what is left."""
    route = respx.get("https://slow.dev").mock(return_value=httpx.Response(200, text="ok"))
    with httpx.Client() as c:
        fetch_page_texts(["https://slow.dev"], c, time_left=lambda: 4.0)
    timeout = route.calls.last.request.extensions["timeout"]
    assert timeout == {"connect": 4.0, "read": 4.0, "write": 4.0, "pool": 4.0}


@respx.mock
def test_a_page_fetch_keeps_its_own_timeout_when_the_budget_is_wide():
    """The cap only ever shrinks: with the run's budget intact the fetch keeps
    the timeouts the module set for it."""
    route = respx.get("https://ok.dev").mock(return_value=httpx.Response(200, text="ok"))
    with httpx.Client() as c:
        fetch_page_texts(["https://ok.dev"], c, time_left=lambda: 900.0)
    timeout = route.calls.last.request.extensions["timeout"]
    assert timeout == {"connect": 10.0, "read": 30.0, "write": 30.0, "pool": 30.0}


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
