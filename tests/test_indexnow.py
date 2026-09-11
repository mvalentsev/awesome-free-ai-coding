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
    index = build_index([make(id="x"), make(id="y", probe_failures=3)], TODAY)
    urls = site_urls(index)
    assert urls[0] == PAGES_URL + "/"
    for path in ("providers/", "providers/x/", "providers/y/", "feed.xml", "llms.txt", "browse.html"):
        assert f"{PAGES_URL}/{path}" in urls, path
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
