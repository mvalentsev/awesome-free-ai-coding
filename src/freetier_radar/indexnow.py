"""IndexNow: after a run publishes, tell the search engines which URLs changed.

Bing, Yandex, Naver, Seznam and Yep share one submission protocol, and Bing's
index is what DuckDuckGo and the search inside ChatGPT read. Without a ping
they can take days to weeks to notice a change. The key proves the site is
ours: a file named after it at the site root, whose whole content is the key.
The protocol would keep it private; here it is public, and all it lets anyone
do is ask an engine to crawl our own pages. Entry point: `freetier-indexnow` (`main`).
"""
import argparse
import json
import os
import re
import sys
import time
from functools import cache
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

import httpx

from . import git
from .discovery import github_headers
from .layout import node_for
from .page_dates import content_hash, page_parts
from .render import PAGES_URL, REPO_URL, checked_page_url, models_index_url, providers_index_url

ENDPOINT = "https://api.indexnow.org/indexnow"
INDEXNOW_KEY = "eb68c254f1e03877b906ccc800002691"
KEY_FILE = f"{INDEXNOW_KEY}.txt"
DELIVERY_REF = "refs/heads/indexnow-delivered"
TIMEOUT = 30.0
# How long a ping waits for Pages to build its commit: fifteen minutes.
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
    text = git.show(repo, rev, path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def changed_since(before: str, now: dict, repo: Path = Path("."),
                  path: str = "index.json", *, after: str = "HEAD") -> list[str]:
    """Compare with the caller's baseline, including changes visible only on pages."""
    old_index = index_at(before, path, repo)
    urls = changed_urls(old_index, now)
    if old_index is None:
        return urls
    for changed in git.changed_paths(repo, before, after):
        node = node_for(changed)
        if not (node and node.published and node.kept and changed.endswith(".md")):
            continue
        old, new = (git.show(repo, ref, changed) for ref in (before, after))
        if new is None or (old is not None and content_hash(old) == content_hash(new)):
            continue
        # The writer's permalink is the served address, including index pages.
        fields, _ = page_parts(new)
        permalink = fields.get("permalink")
        if not isinstance(permalink, str) or not permalink.startswith("/") or permalink.startswith("//"):
            raise ValueError(f"{changed} has an invalid Pages permalink")
        urls.append(f"{PAGES_URL}{permalink}")
    return list(dict.fromkeys(urls))


def submit(urls: list[str], post=httpx.post) -> int:
    """One POST for the whole list; returns the HTTP status. 200 and 202 both
    mean accepted — the protocol answers before it crawls."""
    response = post(ENDPOINT, json={
        "host": urlsplit(PAGES_URL).hostname,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{PAGES_URL}/{KEY_FILE}",
        "urlList": list(urls),
    }, timeout=TIMEOUT)
    return response.status_code


def request_pages_build(token: str | None = None) -> None:
    """Explicitly publish a bot push with a Pages-write installation token."""
    token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    repo = REPO_URL.removeprefix("https://github.com/")
    response = httpx.post(f"https://api.github.com/repos/{repo}/pages/builds",
                          headers=github_headers(token), timeout=TIMEOUT)
    response.raise_for_status()


def ensure_pages_build(sha: str, force: bool = False, *,
                       superseded: Callable[[str], bool] | None = None) -> bool:
    """Repair a missing/failed build, without rebuilding an already served commit."""
    try:
        status, commit = latest_pages_build()
    except (OSError, httpx.HTTPError, ValueError):
        status, commit = "", ""
    if not force and status in ("built", "building", "queued") and (
        commit == sha or (superseded is not None and superseded(commit))
    ):
        return False
    request_pages_build()
    return True


def latest_pages_build(token: str | None = None) -> tuple[str, str]:
    """The status and commit of the repository's newest Pages build, read with
    the workflow's token (GH_TOKEN or GITHUB_TOKEN)."""
    token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    repo = REPO_URL.removeprefix("https://github.com/")
    response = httpx.get(f"https://api.github.com/repos/{repo}/pages/builds/latest",
                         headers=github_headers(token), timeout=TIMEOUT)
    response.raise_for_status()
    build = response.json()
    return build.get("status", ""), build.get("commit", "")


def wait_for_pages(sha: str, fetch: Callable[[], tuple[str, str]] = latest_pages_build,
                   sleep: Callable[[float], None] = time.sleep,
                   attempts: int = PAGES_ATTEMPTS, every: float = PAGES_EVERY, *,
                   superseded: Callable[[str], bool] | None = None) -> str:
    """Wait until Pages has built commit `sha`: "built", "errored" — the build
    of that commit failed — or "timeout". A newer build can supersede a queued
    delivery. A build that cannot be read is waited out."""
    for attempt in range(attempts):
        try:
            status, commit = fetch()
        except (OSError, httpx.HTTPError, ValueError):
            status, commit = "", ""
        if commit == sha and status in ("built", "errored"):
            return status
        if superseded is not None and superseded(commit):
            return "superseded"
        if attempt < attempts - 1:
            sleep(every)
    return "timeout"


def send_changes(before: str | None, index: dict, path: Path, sha: str,
                 repo: Path = Path(".")) -> int:
    urls = (changed_since(before, index, repo=repo, path=path.as_posix(), after=sha)
            if before else site_urls(index))
    if not urls:
        print(f"indexnow: no page's data changed since {before[:7] if before else sha[:7]}, nothing submitted")
        return 0
    status = submit(urls)
    print(f"indexnow: submitted {len(urls)} urls, HTTP {status}")
    return 0 if status in (200, 202) else 1


def deliver(path: Path, *, repair: bool, rebuild: bool, repo: Path = Path(".")) -> int:
    """Reconcile the checked-out main commit in the serialized sender."""
    head = git.run(repo, "rev-parse", "HEAD")
    head.check_returncode()
    sha = head.stdout.strip()
    receipt = git.run(repo, "ls-remote", "--exit-code", "origin", DELIVERY_REF)
    if receipt.returncode == 2:  # Git found the remote, but the ref is absent.
        before = None
    else:
        receipt.check_returncode()
        before, _, ref = receipt.stdout.strip().partition("\t")
        if ref != DELIVERY_REF or not re.fullmatch(r"[0-9a-f]{40}", before):
            raise ValueError("invalid IndexNow delivery ref")
        ancestor = git.run(repo, "merge-base", "--is-ancestor", before, sha)
        if ancestor.returncode:
            raise ValueError(f"IndexNow delivery ref {before} must be an ancestor of {sha}")

    if before == sha and not rebuild:
        print(f"indexnow: {sha} already reconciled")
        return 0

    @cache
    def superseded(candidate: str) -> bool:
        if (not isinstance(candidate, str) or candidate == sha
                or not re.fullmatch(r"[0-9a-f]{40}", candidate)):
            return False
        if git.run(repo, "cat-file", "-e", f"{candidate}^{{commit}}").returncode:
            git.run(repo, "fetch", "--no-tags", "origin", "main").check_returncode()
        return git.run(repo, "merge-base", "--is-ancestor", sha, candidate).returncode == 0

    if repair or rebuild:
        ensure_pages_build(sha, force=rebuild, superseded=superseded)
    waited = wait_for_pages(sha, superseded=superseded)
    print(f"indexnow: Pages build of {sha}: {waited}")
    if waited == "superseded":
        return 0  # A queued push or hourly reconciliation reads current main.
    if waited != "built":
        return 1

    index = index_at(sha, path.as_posix(), repo=repo)
    if index is None:
        raise ValueError(f"cannot read {path} from the published commit {sha}")
    result = send_changes(before, index, path, sha, repo=repo)
    if result:
        return result
    if before == sha:
        print(f"indexnow: {sha} already reconciled")
    else:
        # A normal branch update is fast-forward only. A failed push leaves the
        # previous receipt intact so an unrecorded submission can be retried.
        update = git.run(repo, "push", "origin", f"{sha}:{DELIVERY_REF}")
        if update.returncode:
            print(update.stderr, end="", file=sys.stderr)
            return 1
        print(f"indexnow: recorded delivery at {sha}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=Path("index.json"))
    parser.add_argument("--after-pages-build", metavar="SHA",
                        help="wait until GitHub Pages has built this commit before pinging")
    builds = parser.add_mutually_exclusive_group()
    builds.add_argument("--request-pages-build", action="store_true",
                        help="explicitly request a Pages branch build (needs Pages write)")
    builds.add_argument("--ensure-pages-build", action="store_true",
                        help="repair a missing or failed Pages branch build")
    parser.add_argument("--before", metavar="SHA",
                        help="submit only the pages that changed since this commit")
    parser.add_argument("--deliver", action="store_true",
                        help="reconcile main and persist the delivery ref from the serialized workflow")
    args = parser.parse_args()
    if args.deliver:
        if args.before or args.after_pages_build:
            parser.error("--deliver determines its own baseline and publication")
        sys.exit(deliver(args.index, repair=args.ensure_pages_build, rebuild=args.request_pages_build))
    if args.request_pages_build or args.ensure_pages_build:
        if not args.after_pages_build:
            parser.error("requesting a Pages build needs --after-pages-build SHA")
        requested = ensure_pages_build(args.after_pages_build, force=args.request_pages_build)
        # A no-op expiry may be repairing an earlier failed publication. Tell
        # engines about all pages then, rather than comparing HEAD with itself.
        if requested and args.before == args.after_pages_build:
            args.before = None
    if args.after_pages_build:
        waited = wait_for_pages(args.after_pages_build)
        print(f"indexnow: Pages build of {args.after_pages_build[:7]}: {waited}")
        if waited != "built":
            sys.exit(1)
    index = json.loads(args.index.read_text(encoding="utf-8"))
    sys.exit(send_changes(args.before, index, args.index, args.after_pages_build or "HEAD"))
