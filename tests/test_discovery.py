import httpx
import respx

from freetier_radar.discovery import (
    Evidence, Hit, _feed_excerpt, domain_of, fetch_page_texts, format_evidence,
    gather_evidence, github_search, hn_search, models_dev_digest, tavily_search,
)

MODELS_DEV = "https://models.dev/api.json"


def provider(pid, api, *costs, doc=None, name=None):
    """One models.dev provider: a cost pair per model, in that catalog's shape."""
    return {
        "id": pid, "name": name or pid.title(), "api": api, "doc": doc,
        "models": {f"m{i}": {"id": f"{pid}/m{i}", "cost": {"input": c[0], "output": c[1]}}
                   for i, c in enumerate(costs)},
    }


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
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(200, json={}))
    with httpx.Client() as c:
        ev = gather_evidence(["q1"], {"x.ai"}, env={}, http=c)
    assert [h.url for h in ev.hits] == ["https://newtool.dev/pricing"]
    assert ev.pages["https://newtool.dev/pricing"].strip() == "Generous free tier"
    assert ev.feeds == {"https://raw.example.com/list.md": "- curated"}
    assert ev.providers == ["hn", "curated-feeds"]


def test_a_feed_that_fits_the_limit_is_read_whole():
    assert _feed_excerpt("- one lead", limit=100) == "- one lead"


def test_an_oversized_feed_is_read_from_both_ends():
    """Measured 2026-08-14 against the feeds actually configured: read head-first
    only, free-coding-models' sources.js gave up 9 of its 20 providers and none
    of their endpoints, because the object mapping provider to URL is the last
    5005 characters of the file. Both ends, same 20000-char budget: 20 of 20 with
    endpoints, and the only other oversized feed lost no row it had before. What
    the elision drops is the middle — model rows for providers both ends already
    name."""
    text = "HEAD" + "x" * 200 + "TAIL"
    excerpt = _feed_excerpt(text, limit=100)
    assert excerpt.startswith("HEAD") and excerpt.endswith("TAIL")
    assert "108 characters elided" in excerpt


@respx.mock
def test_gather_evidence_stores_the_excerpt_not_the_whole_feed(monkeypatch):
    import freetier_radar.discovery as disc
    monkeypatch.setattr(disc, "CURATED_FEEDS", ["https://raw.example.com/list.md"])
    monkeypatch.setattr(disc, "FEED_TEXT_LIMIT", 80)
    respx.get("https://hn.algolia.com/api/v1/search").mock(
        return_value=httpx.Response(200, json={"hits": []}))
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"items": []}))
    respx.get("https://raw.example.com/list.md").mock(
        return_value=httpx.Response(200, text="first provider" + "." * 100 + "last provider"))
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(200, json={}))
    with httpx.Client() as c:
        ev = gather_evidence(["q1"], set(), env={}, http=c)
    feed = ev.feeds["https://raw.example.com/list.md"]
    assert feed.startswith("first provider") and feed.endswith("last provider")


@respx.mock
def test_gather_evidence_collects_the_models_dev_digest(monkeypatch):
    import freetier_radar.discovery as disc
    monkeypatch.setattr(disc, "CURATED_FEEDS", [])
    respx.get("https://hn.algolia.com/api/v1/search").mock(
        return_value=httpx.Response(200, json={"hits": []}))
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"items": []}))
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(200, json={
        "newgw": provider("newgw", "https://api.newgw.com/v1", (0, 0)),
        "known": provider("known", "https://api.known.ai/v1", (0, 0)),
    }))
    with httpx.Client() as c:
        ev = gather_evidence(["q1"], {"known.ai"}, env={}, http=c)
    assert "newgw" in ev.digests[MODELS_DEV] and "known" not in ev.digests[MODELS_DEV]
    assert "models.dev" in ev.providers


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


@respx.mock
def test_page_text_is_the_page_and_not_its_machinery():
    """Measured 2026-09-02 across the 45 live rows' first source urls: script
    blocks were a median 30% of the raw HTML and 98% of the worst page, and the
    5000-character cap was being spent on them and on the site's menus — the
    only retirement signal in the whole sweep was the word "Deprecations" in
    ai.google.dev's sidebar, while three body-text mentions sat past the cap
    unseen. Structured data stays: Freebuff publishes its FAQ as JSON-LD and
    nowhere else."""
    respx.get("https://p.dev").mock(return_value=httpx.Response(200, text=(
        '<html><head><style>.nav{color:red}</style>'
        '<script>window.__d={"retired":true}</script>'
        '<script type="application/ld+json">{"@type":"Question","name":"Is it free?"}</script>'
        '</head><body><nav>Release notes Deprecations Libraries</nav>'
        '<noscript>Please enable JavaScript</noscript>'
        '<p>Free tier: 1,000 requests a day</p>'
        '<footer>Product shut down notices</footer></body></html>')))
    with httpx.Client() as c:
        text = fetch_page_texts(["https://p.dev"], c)["https://p.dev"]
    assert "Free tier: 1,000 requests a day" in text
    assert "Is it free?" in text
    for noise in ("Deprecations", "retired", "shut down", "enable JavaScript", "color:red"):
        assert noise not in text


@respx.mock
def test_a_json_page_is_kept_as_it_is():
    """Pollinations' first source url is its model catalog, JSON with a "<" in
    one description: the tag stripper ate everything from there to the next
    ">" and the scout was handed 286 characters of a 20-kilobyte page."""
    respx.get("https://c.dev/models").mock(return_value=httpx.Response(
        200, json=[{"name": "fast", "description": "for prompts < 4k tokens"},
                   {"name": "big", "description": "everything > that"}],
    ))
    with httpx.Client() as c:
        text = fetch_page_texts(["https://c.dev/models"], c)["https://c.dev/models"]
    assert '"big"' in text and "everything > that" in text


@respx.mock
def test_the_digest_names_a_provider_with_a_zero_cost_row():
    """The point of the source: 185 providers carrying a machine-readable price
    per model, which is a lead stream no prose feed can match."""
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(200, json={
        "newgw": provider("newgw", "https://api.newgw.com/v1", (0, 0), (1.5, 3.0),
                          doc="https://newgw.com/docs", name="NewGW"),
        "paidgw": provider("paidgw", "https://api.paidgw.com/v1", (1.0, 2.0)),
    }))
    with httpx.Client() as c:
        digest = models_dev_digest(c, known_domains=set())
    assert "newgw (NewGW)" in digest and "https://api.newgw.com/v1" in digest
    assert "1/2 rows at cost 0" in digest and "newgw/m0" in digest
    assert "paidgw" not in digest


@respx.mock
def test_the_digest_leaves_out_what_the_curated_files_already_answer():
    """A digest that re-proposes the registry is noise the scout pays for twice."""
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(200, json={
        "known": provider("known", "https://api.known.ai/v1", (0, 0)),
        "sub": provider("sub", "https://api.sub.known.ai/v1", (0, 0)),
    }))
    with httpx.Client() as c:
        digest = models_dev_digest(c, known_domains={"known.ai"})
    assert digest == ""


@respx.mock
def test_the_digest_leaves_out_a_local_runtime():
    """LMStudio and its kin publish a loopback address and a catalog of models
    priced 0 — free because you are the one hosting them, which is not an offer
    anyone can be pointed at."""
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(200, json={
        "lmstudio": provider("lmstudio", "http://127.0.0.1:1234/v1", (0, 0)),
        "local": provider("local", "http://localhost:8080/v1", (0, 0)),
    }))
    with httpx.Client() as c:
        assert models_dev_digest(c, known_domains=set()) == ""


@respx.mock
def test_the_digest_says_what_a_zero_in_this_catalog_does_not_mean():
    """Verified 2026-08-14: kenari reads 38/38 at zero because it quotes IDR in a
    unit models.dev could not parse, and every *-coding-plan provider reads zero
    because the usage is inside a paid subscription. A lead stream that does not
    carry its own caveat is a proposal generator."""
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(200, json={
        "newgw": provider("newgw", "https://api.newgw.com/v1", (0, 0)),
    }))
    with httpx.Client() as c:
        digest = models_dev_digest(c, known_domains=set())
    assert "subscription" in digest and "currency" in digest


@respx.mock
def test_the_digest_is_empty_rather_than_raising_when_the_catalog_is_down():
    """An optional source must never sink the phase that carries the others."""
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(503))
    with httpx.Client() as c:
        assert models_dev_digest(c, known_domains=set()) == ""


def test_format_evidence_renders_a_digest_under_its_own_heading():
    ev = Evidence(digests={MODELS_DEV: "- newgw (NewGW) ..."})
    text = format_evidence(ev)
    assert "DERIVED FROM" in text and MODELS_DEV in text and "- newgw (NewGW) ..." in text


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


@respx.mock
def test_the_digest_leaves_out_a_provider_whose_only_url_is_a_code_host():
    """qvac's one URL is an npm package that spawns a local `qvac serve`, and
    models.dev's vercel entry points at a GitHub repo — a package page or a
    repository names a client, not a vendor, so nothing on it can be matched to
    the registry or probed as an offer. Measured 2026-09-05: the two were the
    only providers on such hosts, and one of them is a listed row the digest
    kept proposing back."""
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(200, json={
        "pkg": provider("pkg", None, (0, 0), doc="https://www.npmjs.com/package/@pkg/provider"),
        "repo": provider("repo", None, (0, 0), doc="https://github.com/org/repo"),
    }))
    with httpx.Client() as c:
        assert models_dev_digest(c, known_domains=set()) == ""


@respx.mock
def test_gather_evidence_keeps_an_answered_domain_out_of_the_digest_but_in_the_hits(monkeypatch):
    """A watchlist verdict is a zero somebody already followed, so its digest
    line is prompt spent twice; a search hit about the same vendor is the fresh
    evidence a reopen_if is waiting for, so it stays."""
    import freetier_radar.discovery as disc
    monkeypatch.setattr(disc, "CURATED_FEEDS", [])
    respx.get("https://hn.algolia.com/api/v1/search").mock(
        return_value=httpx.Response(200, json={"hits": [
            {"url": "https://watched.ai/blog/free-lane", "title": "Watched opens a free lane"}]}))
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"items": []}))
    respx.get(MODELS_DEV).mock(return_value=httpx.Response(200, json={
        "newgw": provider("newgw", "https://api.newgw.com/v1", (0, 0)),
        "watched": provider("watched", "https://api.watched.ai/v1", (0, 0)),
    }))
    with httpx.Client() as c:
        ev = gather_evidence(["q1"], set(), env={}, http=c, max_pages=0,
                             answered_domains={"watched.ai"})
    assert "newgw" in ev.digests[MODELS_DEV] and "watched" not in ev.digests[MODELS_DEV]
    assert [h.url for h in ev.hits] == ["https://watched.ai/blog/free-lane"]
