"""IndexNow: after a run publishes, tell the search engines which URLs changed.

Bing, Yandex, Naver, Seznam and Yep share one submission protocol, and Bing's
index is what DuckDuckGo and the search inside ChatGPT read — the second-largest
referrer this site has. Without a ping they recrawl on their own schedule,
which for a site this size is weeks; with one, the pages that changed on
Monday are read on Monday. The key proves the site is ours: a file named
after it at the site root, whose whole content is the key. It is not a
secret — anyone can read it, and all it lets anyone do is ask an engine to
crawl our own pages.
"""
import argparse
import json
import sys
from pathlib import Path

import httpx

from .render import PAGES_URL, PROVIDERS_DIR

ENDPOINT = "https://api.indexnow.org/indexnow"
HOST = "mvalentsev.github.io"
INDEXNOW_KEY = "eb68c254f1e03877b906ccc800002691"
KEY_FILE = f"{INDEXNOW_KEY}.txt"
TIMEOUT = 30.0


def site_urls(index: dict) -> list[str]:
    """Every page a search engine should re-read after a run: the README, the
    provider index, one page per row (archived rows included — a page that now
    says "archived" is exactly the change worth reading), the feed and the
    text and table views."""
    urls = [f"{PAGES_URL}/", f"{PAGES_URL}/{PROVIDERS_DIR}/"]
    urls += [e["page"] for e in index.get("entries", [])]
    urls += [f"{PAGES_URL}/feed.xml", f"{PAGES_URL}/llms.txt", f"{PAGES_URL}/browse.html"]
    return list(dict.fromkeys(urls))


def submit(urls: list[str], post=httpx.post) -> int:
    """One POST for the whole list; returns the HTTP status. 200 and 202 both
    mean accepted — the protocol answers before it crawls."""
    response = post(ENDPOINT, json={
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{PAGES_URL}/{KEY_FILE}",
        "urlList": list(urls),
    }, timeout=TIMEOUT)
    return response.status_code


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=Path("index.json"))
    args = parser.parse_args()
    index = json.loads(args.index.read_text(encoding="utf-8"))
    urls = site_urls(index)
    status = submit(urls)
    print(f"indexnow: submitted {len(urls)} urls, HTTP {status}")
    sys.exit(0 if status in (200, 202) else 1)
