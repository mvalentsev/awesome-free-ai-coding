"""IndexNow: after a run publishes, tell Bing, Yandex and the engines that
share their index which URLs changed, instead of waiting to be crawled."""
import re
from pathlib import Path

from freetier_radar.indexnow import ENDPOINT, INDEXNOW_KEY, KEY_FILE, site_urls, submit
from freetier_radar.render import PAGES_URL, build_index
from test_render import TODAY, make

ROOT = Path(__file__).resolve().parent.parent


def test_the_key_is_published_at_the_site_root_under_its_own_name():
    assert re.fullmatch(r"[a-f0-9]{32}", INDEXNOW_KEY)
    assert KEY_FILE == f"{INDEXNOW_KEY}.txt"
    assert (ROOT / KEY_FILE).read_text(encoding="utf-8").strip() == INDEXNOW_KEY


def test_site_urls_cover_what_a_search_engine_should_recrawl():
    index = build_index([make(id="x", models=[{"family": "kimi-k3"}, {"family": "solo"}]),
                         make(id="w", models=[{"family": "kimi-k3"}]),
                         make(id="y", probe_failures=3)], TODAY)
    urls = site_urls(index)
    assert urls[0] == PAGES_URL + "/"
    for path in ("providers/", "providers/checked/", "providers/x/", "providers/y/", "feed.xml", "llms.txt",
                 "browse.html", "models/", "models/kimi-k3/"):
        assert f"{PAGES_URL}/{path}" in urls, path
    assert f"{PAGES_URL}/models/solo/" not in urls, "one row and no tier: no page"
    assert len(urls) == len(set(urls))


def test_submit_posts_the_indexnow_payload_and_returns_the_status():
    calls = []

    class Response:
        status_code = 202
        text = ""

    def post(url, json=None, timeout=None):
        calls.append((url, json))
        return Response()

    urls = [PAGES_URL + "/", PAGES_URL + "/providers/x/"]
    assert submit(urls, post=post) == 202
    assert calls == [(ENDPOINT, {
        "host": "mvalentsev.github.io",
        "key": INDEXNOW_KEY,
        "keyLocation": f"{PAGES_URL}/{KEY_FILE}",
        "urlList": urls,
    })]


def test_the_ping_waits_for_pages_to_publish_the_commit():
    """An engine that fetched on the ping would read the page before Pages built
    it, so both the scheduled run and a hand push wait for the build of their
    own commit — one wait, here, for both."""
    from freetier_radar.indexnow import wait_for_pages
    builds = iter([("building", "new"), ("built", "old"), ("built", "new")])
    slept = []
    assert wait_for_pages("new", fetch=lambda: next(builds), sleep=slept.append) == "built"
    assert len(slept) == 2
    assert wait_for_pages("new", fetch=lambda: ("errored", "new"), sleep=slept.append) == "errored"
    assert wait_for_pages("new", fetch=lambda: ("built", "old"), sleep=lambda s: None,
                          attempts=3) == "timeout"


def test_a_build_that_cannot_be_read_is_waited_out_not_fatal():
    from freetier_radar.indexnow import wait_for_pages

    def unreachable():
        raise OSError("no network")
    assert wait_for_pages("sha", fetch=unreachable, sleep=lambda s: None, attempts=2) == "timeout"


def test_only_the_pages_whose_data_changed_are_submitted():
    """The ping submitted every url of the site on every push that published a
    file — 186 of them four times on 2026-09-27, for commits that each touched a
    handful of rows — where the protocol asks for the urls that changed, and an
    engine sent the same unchanged pages again and again has reason to discount
    the pings. What changed is read off index.json, the site's data, before and
    after the push; the footer's render date moves every page every day and is
    no change to a reader."""
    from freetier_radar.indexnow import changed_urls

    def rows(limits="50 requests a day"):
        return [make(id="x", models=[{"family": "kimi-k3"}], limits=limits),
                make(id="w", models=[{"family": "kimi-k3"}]), make(id="y")]
    before = build_index(rows(), TODAY)
    assert changed_urls(before, build_index(rows(), TODAY)) == []
    after = build_index(rows("40 requests a day"), TODAY)
    urls = changed_urls(before, after)
    assert f"{PAGES_URL}/providers/x/" in urls
    assert f"{PAGES_URL}/providers/w/" not in urls and f"{PAGES_URL}/providers/y/" not in urls
    # the model pages that list the row, and the pages that list every row
    assert f"{PAGES_URL}/models/kimi-k3/" in urls
    for path in ("", "providers/", "feed.xml", "llms.txt", "browse.html"):
        assert f"{PAGES_URL}/{path}" in urls, path
    assert f"{PAGES_URL}/providers/checked/" not in urls
    # with no earlier index to read, every page is new to the engine
    assert changed_urls(None, after) == site_urls(after)


def test_the_ping_reads_the_index_as_the_push_found_it(tmp_path):
    """The index before the push is the one at the commit the push started from:
    `git show <before>:index.json`. A commit that is not there — a new branch's
    all-zero `before`, a shallow clone — gives no earlier index, and every page
    is sent, as before."""
    import json
    import subprocess
    from freetier_radar.indexnow import index_at
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "index.json").write_text(json.dumps({"entries": [], "models": []}), encoding="utf-8")
    subprocess.run(["git", "add", "index.json"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"],
                   cwd=tmp_path, check=True)
    assert index_at("HEAD", "index.json", repo=tmp_path) == {"entries": [], "models": []}
    assert index_at("0" * 40, "index.json", repo=tmp_path) is None


def test_both_pings_send_only_what_their_push_changed():
    """The scheduled run pings after its own verification commit, from the
    commit it started on. indexnow.yml pings after any other push, and a push
    that lands while it waits for Pages cancels it, so it sends what changed
    since the last ping that went out — the head of its last successful run —
    and only where that cannot be read since the commit its own push started
    from; its checkout reaches back far enough to read either."""
    import yaml
    run = yaml.safe_load((ROOT / ".github/workflows/update.yml").read_text(encoding="utf-8"))
    step = next(s for s in run["jobs"]["update"]["steps"] if "freetier-indexnow" in s.get("run", ""))
    assert '--before "$(git rev-parse HEAD^)"' in step["run"]
    ping = yaml.safe_load((ROOT / ".github/workflows/indexnow.yml").read_text(encoding="utf-8"))
    steps = ping["jobs"]["ping"]["steps"]
    call = next(s for s in steps if "freetier-indexnow" in s.get("run", ""))
    assert "actions/workflows/indexnow.yml/runs?status=success" in call["run"]
    assert '--before "${since:-${{ github.event.before }}}"' in call["run"]
    checkout = next(s for s in steps if s.get("uses", "").startswith("actions/checkout"))
    assert checkout.get("with", {}).get("fetch-depth") == 0
