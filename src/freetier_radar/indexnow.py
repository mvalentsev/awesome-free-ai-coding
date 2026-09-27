"""IndexNow: after a run publishes, tell the search engines which URLs changed.

Bing, Yandex, Naver, Seznam and Yep share one submission protocol, and Bing's
index is what DuckDuckGo and the search inside ChatGPT read. Without a ping
they recrawl on their own schedule, which for a site this size is weeks. The
key proves the site is ours: a file named after it at the site root, whose
whole content is the key. It is not a secret — all it lets anyone do is ask an
engine to crawl our own pages. Entry point: `freetier-indexnow` (`main`).
"""
import argparse
import json
import os
import subprocess
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
    """Every page a search engine should re-read after a run: the home page, the
    provider index, the page of services checked and not listed, one page per
    row (archived rows too: a page that now says "archived" is a change worth
    reading), the index of every model and a page per model that has one, the
    feed and the text and table views."""
    urls = [f"{PAGES_URL}/", providers_index_url(), checked_page_url()]
    urls += [e["page"] for e in index.get("entries", [])]
    urls += [models_index_url()]
    urls += [m["page"] for m in index.get("models", []) if m.get("page")]
    urls += [f"{PAGES_URL}/feed.xml", f"{PAGES_URL}/llms.txt", f"{PAGES_URL}/browse.html"]
    return list(dict.fromkeys(urls))



def changed_urls(before: dict | None, after: dict) -> list[str]:
    """The pages whose data changed between two readings of index.json — the
    index as the push found it and as it left it — in site_urls' order.

    A row whose record moved sends its own page and the pages of the models it
    lists, which print it; a model whose record moved sends its page and the
    models index; the pages that list every row — the providers index, the
    feed, llms.txt and browse.html — go whenever a row did, the checked page
    when the watchlist did, and the home page on any of the three. The index's
    `generated` day is no change, nor is the render date in every page's
    footer. With no earlier index to read, every page is new to the engine."""
    if before is None:
        return site_urls(after)
    old_rows = {e["id"]: e for e in before.get("entries", [])}
    old_models = {m["family"]: m for m in before.get("models", [])}
    new_models = {m["family"]: m for m in after.get("models", [])}
    model_pages = {f: m["page"] for f, m in {**old_models, **new_models}.items() if m.get("page")}
    wanted: set[str] = set()
    rows_moved = False
    for e in after.get("entries", []):
        old = old_rows.get(e["id"])
        if old == e:
            continue
        rows_moved = True
        wanted.add(e["page"])
        families = {m["family"] for m in e.get("models", [])}
        families |= {m["family"] for m in (old or {}).get("models", [])}
        wanted |= {model_pages[f] for f in families if f in model_pages}
    models_moved = [f for f in set(old_models) | set(new_models)
                    if old_models.get(f) != new_models.get(f)]
    wanted |= {model_pages[f] for f in models_moved if f in model_pages}
    watch_moved = before.get("watchlist") != after.get("watchlist")
    if rows_moved or models_moved or watch_moved:
        wanted.add(f"{PAGES_URL}/")
    if rows_moved:
        wanted |= {providers_index_url(), f"{PAGES_URL}/feed.xml", f"{PAGES_URL}/llms.txt",
                   f"{PAGES_URL}/browse.html"}
    if models_moved:
        wanted.add(models_index_url())
    if watch_moved:
        wanted.add(checked_page_url())
    ordered = [u for u in site_urls(after) if u in wanted]
    return ordered + sorted(wanted - set(ordered))


def index_at(rev: str, path: str = "index.json", repo: Path = Path(".")) -> dict | None:
    """index.json as commit `rev` holds it, or None where git has no such commit
    or file there — a new branch's all-zero `before`, a clone too shallow to
    reach it."""
    run = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=repo, capture_output=True, text=True)
    if run.returncode != 0:
        return None
    try:
        return json.loads(run.stdout)
    except json.JSONDecodeError:
        return None


# The subject the scheduled run gives its verification commit. Its push pings
# the pages that commit changed (update.yml) and starts no workflow.
VERIFICATION_SUBJECT = "chore: verification"


def changed_since(before: str, now: dict, repo: Path = Path("."),
                  path: str = "index.json") -> list[str]:
    """changed_urls from commit `before` to `now`, leaving out what each of the
    run's verification commits in between changed: the run pinged those pages
    itself when it pushed, and because its push starts no workflow the next
    hand push counts from an older ping. The commit being pinged is never left
    out, so the run's own ping, from HEAD^, sends its verification commit
    whole; and a `before` git cannot read sends every page, as changed_urls
    does."""
    log = subprocess.run(["git", "log", "--reverse", "--first-parent", "--format=%H %s",
                          f"{before}..HEAD"], cwd=repo, capture_output=True, text=True)
    commits = [line.partition(" ") for line in log.stdout.splitlines()] if log.returncode == 0 else []
    head = commits[-1][0] if commits else None
    cuts = [sha for sha, _, subject in commits
            if subject.startswith(VERIFICATION_SUBJECT) and sha != head]
    wanted: list[str] = []
    start = before
    for cut in cuts:
        segment = index_at(f"{cut}^", path, repo)
        if segment is not None:
            wanted += changed_urls(index_at(start, path, repo), segment)
        start = cut
    wanted += changed_urls(index_at(start, path, repo), now)
    order = site_urls(now)
    return [u for u in order if u in set(wanted)] + [u for u in dict.fromkeys(wanted) if u not in order]

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
    parser.add_argument("--before", metavar="SHA",
                        help="submit only the pages whose data changed since this commit's index.json")
    args = parser.parse_args()
    if args.after_pages_build:
        waited = wait_for_pages(args.after_pages_build)
        print(f"indexnow: Pages build of {args.after_pages_build[:7]}: {waited}")
        if waited == "errored":
            sys.exit(1)
    index = json.loads(args.index.read_text(encoding="utf-8"))
    urls = changed_since(args.before, index, path=args.index.as_posix()) if args.before else site_urls(index)
    if not urls:
        print(f"indexnow: no page's data changed since {args.before[:7]}, nothing submitted")
        sys.exit(0)
    status = submit(urls)
    print(f"indexnow: submitted {len(urls)} urls, HTTP {status}")
    sys.exit(0 if status in (200, 202) else 1)
