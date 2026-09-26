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
import os
import sys
import time
from pathlib import Path
from typing import Callable

import httpx

from .render import PAGES_URL, REPO_URL, checked_page_url, models_index_url, providers_index_url

ENDPOINT = "https://api.indexnow.org/indexnow"
HOST = "mvalentsev.github.io"
INDEXNOW_KEY = "eb68c254f1e03877b906ccc800002691"
KEY_FILE = f"{INDEXNOW_KEY}.txt"
TIMEOUT = 30.0
# How long a ping waits for Pages to build its commit: fifteen minutes, where a
# build takes one or two.
PAGES_ATTEMPTS = 60
PAGES_EVERY = 15.0


def site_urls(index: dict) -> list[str]:
    """Every page a search engine should re-read after a run: the README, the
    provider index, the page of services checked and not listed, one page per row (archived rows included — a page that now
    says "archived" is exactly the change worth reading), the index of every
    model and a page per model that has one, the feed and the text and table
    views."""
    urls = [f"{PAGES_URL}/", providers_index_url(), checked_page_url()]
    urls += [e["page"] for e in index.get("entries", [])]
    urls += [models_index_url()]
    urls += [m["page"] for m in index.get("models", []) if m.get("page")]
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


def latest_pages_build(token: str | None = None) -> tuple[str, str]:
    """The status and commit of the repository's newest Pages build, read with
    the workflow's token (GH_TOKEN or GITHUB_TOKEN)."""
    token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    repo = REPO_URL.removeprefix("https://github.com/")
    response = httpx.get(f"https://api.github.com/repos/{repo}/pages/builds/latest",
                         headers={"Accept": "application/vnd.github+json",
                                  **({"Authorization": f"Bearer {token}"} if token else {})},
                         timeout=TIMEOUT)
    response.raise_for_status()
    build = response.json()
    return build.get("status", ""), build.get("commit", "")


def wait_for_pages(sha: str, fetch: Callable[[], tuple[str, str]] = latest_pages_build,
                   sleep: Callable[[float], None] = time.sleep,
                   attempts: int = PAGES_ATTEMPTS, every: float = PAGES_EVERY) -> str:
    """Wait until Pages has built commit `sha`: "built", "errored" — the build
    of that commit failed — or "timeout". An engine that fetched on the ping
    would otherwise read the pages Pages had not rebuilt yet; the scheduled run
    and a hand push both wait here. A build that cannot be read is waited out,
    never fatal: the ping is best effort."""
    for attempt in range(attempts):
        try:
            status, commit = fetch()
        except (OSError, httpx.HTTPError, ValueError):
            status, commit = "", ""
        if commit == sha and status in ("built", "errored"):
            return status
        if attempt < attempts - 1:
            sleep(every)
    return "timeout"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=Path("index.json"))
    parser.add_argument("--after-pages-build", metavar="SHA",
                        help="wait until GitHub Pages has built this commit before pinging")
    args = parser.parse_args()
    if args.after_pages_build:
        waited = wait_for_pages(args.after_pages_build)
        print(f"indexnow: Pages build of {args.after_pages_build[:7]}: {waited}")
        if waited == "errored":
            sys.exit(1)
    index = json.loads(args.index.read_text(encoding="utf-8"))
    urls = site_urls(index)
    status = submit(urls)
    print(f"indexnow: submitted {len(urls)} urls, HTTP {status}")
    sys.exit(0 if status in (200, 202) else 1)
