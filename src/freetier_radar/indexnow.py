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
from functools import cache, partial
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

import httpx

from . import git
from .discovery import github_headers
from .layout import ATOM_FEED, BROWSE_PAGE, INDEXNOW_KEY, INDEXNOW_KEY_FILE as KEY_FILE
from .layout import SITE_PAGE, TEXT_LIST, node_for
from .page_dates import content_hash, page_parts
from .render import (BROWSE_URL, FEED_URL, PAGES_URL, REPO_URL, checked_page_url,
                     models_index_url, providers_index_url)

ENDPOINT = "https://api.indexnow.org/indexnow"
DELIVERY_REF = "refs/heads/indexnow-delivered"
MAIN_REF = "refs/heads/main"
PAGES_ENVIRONMENT = "github-pages"
TIMEOUT = 30.0
# How long a ping waits for Pages to build its commit: fifteen minutes.
PAGES_ATTEMPTS = 60
PAGES_EVERY = 15.0
# Grace period for the automatic Pages build on a push.
PAGES_REPAIR_GRACE = 60.0
STANDALONE_PAGES = {SITE_PAGE: f"{PAGES_URL}/", ATOM_FEED: FEED_URL,
                    TEXT_LIST: f"{PAGES_URL}/{TEXT_LIST}", BROWSE_PAGE: BROWSE_URL}
# The text list's build stamp changes even when its offer text is identical.
TEXT_LIST_BUILD_DATE = re.compile(r"(?m)^(> [^\n]*? Generated )\d{4}-\d{2}-\d{2}( from the registry;)")


def _detail_urls(index: dict) -> list[str]:
    return [providers_index_url(), checked_page_url(),
            *(e["page"] for e in index.get("entries", [])), models_index_url(),
            *(m["page"] for m in index.get("models", []) if m.get("page"))]


def site_urls(index: dict) -> list[str]:
    """Every page a search engine should re-read after a run: the home page, the
    provider index, the page of services checked and not listed, one page per
    row (archived rows too: a page that now says "archived" is a change worth
    reading), the index of every model and a page per model that has one, the
    feed and the text and table views."""
    urls = [STANDALONE_PAGES[SITE_PAGE], *_detail_urls(index),
            *(STANDALONE_PAGES[path] for path in (ATOM_FEED, TEXT_LIST, BROWSE_PAGE))]
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
        wanted.add(STANDALONE_PAGES[SITE_PAGE])
    if rows_moved:
        wanted.update((*STANDALONE_PAGES.values(), providers_index_url()))
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
    shared_pages_changed = False
    for changed in git.changed_paths(repo, before, after):
        node = node_for(changed)
        if node is None:
            continue
        if node.pages_input:
            shared_pages_changed = True
            continue
        static_url = STANDALONE_PAGES.get(changed)
        if not node.published or not (static_url or node.kept):
            continue
        if static_url in urls:
            continue
        new = git.show(repo, after, changed)
        if new is None:
            continue
        if static_url and changed != TEXT_LIST:
            urls.append(static_url)
            continue
        old = git.show(repo, before, changed)
        if url := _changed_page_url(changed, old, new):
            urls.append(url)
    if shared_pages_changed:
        urls.extend(_detail_urls(now))
    return list(dict.fromkeys(urls))


def _changed_page_url(path: str, old: str | None, new: str) -> str | None:
    if path == TEXT_LIST:
        if old is not None:
            strip_date = partial(TEXT_LIST_BUILD_DATE.sub, r"\1\2", count=1)
            if strip_date(old) == strip_date(new):
                return None
        return STANDALONE_PAGES[TEXT_LIST]
    if old is not None and content_hash(old) == content_hash(new):
        return None
    # The writer's permalink is the served address, including index pages.
    fields, _ = page_parts(new)
    permalink = fields.get("permalink")
    if not isinstance(permalink, str) or not permalink.startswith("/") or permalink.startswith("//"):
        raise ValueError(f"{path} has an invalid Pages permalink")
    return f"{PAGES_URL}{permalink}"


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
    if not force:
        status, commit = _pages_state(latest_pages_deployment)
        if status in ("built", "building", "queued") and (
            commit == sha or (superseded is not None and superseded(commit))
        ):
            return False
        # A branch build can be queued before Pages creates its deployment.
        status, commit = _pages_state(latest_pages_build)
        if status in ("building", "queued") and commit == sha:
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


def latest_pages_deployment(token: str | None = None) -> tuple[str, str]:
    """Read the production Pages deployment and its latest status."""
    # The branch build can name the previous SHA after a newer Pages deployment
    # already succeeded. Deployment and status REST endpoints (GitHub Docs)
    # matched the live Pages bytes on 2026-11-22.
    token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    repo = REPO_URL.removeprefix("https://github.com/")
    endpoint = f"https://api.github.com/repos/{repo}/deployments"
    headers = github_headers(token)
    response = httpx.get(endpoint, params={"environment": PAGES_ENVIRONMENT, "per_page": 1},
                         headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    deployments = response.json()
    if not deployments:
        return "", ""
    deployment = deployments[0]
    if deployment.get("environment") != PAGES_ENVIRONMENT:
        return "", ""
    sha, deployment_id = deployment.get("sha"), deployment.get("id")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha) or type(deployment_id) is not int:
        raise ValueError("invalid Pages deployment")
    response = httpx.get(f"{endpoint}/{deployment_id}/statuses", params={"per_page": 1},
                         headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    statuses = response.json()
    if not statuses:
        return "", ""
    latest = statuses[0]
    state = latest.get("state")
    if state == "success":
        url = latest.get("environment_url")
        return ("built", sha) if isinstance(url, str) and url.rstrip("/") == PAGES_URL else ("", "")
    if state in ("failure", "error"):
        return "errored", sha
    if state == "in_progress":
        return "building", sha
    if state in ("pending", "queued"):
        return "queued", sha
    return "", ""


def _pages_state(fetch: Callable[[], tuple[str, str]]) -> tuple[str, str]:
    try:
        return fetch()
    except (OSError, httpx.HTTPError, ValueError):
        return "", ""


def wait_for_pages(sha: str, fetch: Callable[[], tuple[str, str]] = latest_pages_deployment,
                   sleep: Callable[[float], None] = time.sleep,
                   attempts: int = PAGES_ATTEMPTS, every: float = PAGES_EVERY, *,
                   superseded: Callable[[str], bool] | None = None,
                   repair: Callable[[], bool] | None = None) -> str:
    """Wait until Pages has built commit `sha`: "built", "errored" — the build
    of that commit failed — or "timeout". A newer build can supersede a queued
    delivery. With a repair callback, give the automatic build a grace period
    before checking once whether a request is needed."""
    for attempt in range(attempts):
        status, commit = _pages_state(fetch)
        if commit == sha and status in ("built", "errored"):
            return status
        if superseded is not None and superseded(commit):
            return "superseded"
        if (repair is not None and attempt * every >= PAGES_REPAIR_GRACE and commit != sha
                and attempt < attempts - 1):
            if repair():
                print(f"indexnow: requested Pages repair for {sha}")
            repair = None
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


def _remote_revisions(repo: Path, *refs: str) -> dict[str, str]:
    listed = git.run(repo, "ls-remote", "--refs", "origin", *refs)
    listed.check_returncode()
    revisions = {}
    for line in listed.stdout.splitlines():
        sha, _, ref = line.partition("\t")
        if ref not in refs or ref in revisions or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("invalid IndexNow remote ref listing")
        revisions[ref] = sha
    return revisions


def delivery_current(repo: Path = Path(".")) -> bool:
    """Compare both remote refs in one observation, even from a stale checkout."""
    revisions = _remote_revisions(repo, MAIN_REF, DELIVERY_REF)
    main = revisions.get(MAIN_REF)
    if main is None or main != revisions.get(DELIVERY_REF):
        return False
    print(f"indexnow: {main} already reconciled")
    return True


def deliver(path: Path, *, repair: bool, rebuild: bool, repo: Path = Path(".")) -> int:
    """Reconcile the checked-out main commit in the serialized sender."""
    head = git.run(repo, "rev-parse", "HEAD")
    head.check_returncode()
    sha = head.stdout.strip()
    before = _remote_revisions(repo, DELIVERY_REF).get(DELIVERY_REF)
    if before:
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

    # A push build can check out main yet deploy under the previous SHA
    # (GitHub Pages run 45869650818, checked 2026-11-26).
    request_repair = partial(ensure_pages_build, sha, superseded=superseded)
    requested = (repair or rebuild) and request_repair(force=rebuild)
    waited = wait_for_pages(sha, superseded=superseded,
                            repair=None if requested else request_repair)
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
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--deliver", action="store_true",
                        help="reconcile main and persist the delivery ref from the serialized workflow")
    modes.add_argument("--check-delivery", action="store_true",
                       help="exit successfully only if the remote main revision is already reconciled")
    args = parser.parse_args()
    if args.check_delivery:
        if args.before or args.after_pages_build or args.request_pages_build or args.ensure_pages_build:
            parser.error("--check-delivery only checks the remote delivery ref")
        sys.exit(0 if delivery_current() else 1)
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
