"""IndexNow: after a run publishes, tell Bing, Yandex and the engines that
share their index which URLs changed, instead of waiting to be crawled."""
import re
from datetime import timedelta
from pathlib import Path

import pytest

from freetier_radar.indexnow import ENDPOINT, INDEXNOW_KEY, KEY_FILE, site_urls, submit
from freetier_radar.render import PAGES_URL, build_index
from test_render import TODAY, make

ROOT = Path(__file__).resolve().parent.parent


def test_bot_publication_explicitly_requests_a_pages_build_at_the_http_boundary():
    import respx
    from freetier_radar.indexnow import request_pages_build
    with respx.mock() as routes:
        build = routes.post('https://api.github.com/repos/mvalentsev/awesome-free-ai-coding/pages/builds').respond(201, json={'status': 'queued'})
        request_pages_build('test-token')
    assert build.call_count == 1
    assert build.calls[0].request.headers['Authorization'] == 'Bearer test-token'


def test_a_later_noop_repairs_failed_publication_but_keeps_a_current_build(monkeypatch):
    from freetier_radar import indexnow
    requested = []
    monkeypatch.setattr(indexnow, 'request_pages_build', lambda: requested.append(True))
    for status, commit, needs_request in [('built', 'current', False), ('queued', 'current', False),
                                          ('building', 'current', False), ('errored', 'current', True),
                                          ('built', 'old', True)]:
        monkeypatch.setattr(indexnow, 'latest_pages_build', lambda: (status, commit))
        assert indexnow.ensure_pages_build('current') is needs_request
    assert len(requested) == 2


def test_the_key_is_published_at_the_site_root_under_its_own_name():
    assert re.fullmatch(r"[a-f0-9]{32}", INDEXNOW_KEY)
    assert KEY_FILE == f"{INDEXNOW_KEY}.txt"
    assert (ROOT / KEY_FILE).read_text(encoding="utf-8").strip() == INDEXNOW_KEY


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


def test_the_key_location_and_payload_host_follow_the_public_site(monkeypatch):
    from freetier_radar import indexnow

    site = 'https://published.example/catalog'
    monkeypatch.setattr(indexnow, 'PAGES_URL', site)

    def post(url, json, timeout):
        assert json['host'] == 'published.example'
        assert json['keyLocation'] == f'{site}/{KEY_FILE}'
        return type('Response', (), {'status_code': 202})()

    assert submit([site + '/'], post=post) == 202


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


@pytest.mark.parametrize('published', ['built', 'errored', 'timeout'])
def test_the_indexnow_command_only_submits_after_the_exact_pages_build(monkeypatch, tmp_path, published):
    import json
    import sys
    from freetier_radar import indexnow

    index = tmp_path / 'index.json'
    index.write_text(json.dumps(build_index([make(id='x')], TODAY)))
    monkeypatch.setattr(sys, 'argv', ['freetier-indexnow', '--index', str(index),
                                     '--after-pages-build', 'exact-head'])
    waits = []
    submitted = []
    monkeypatch.setattr(indexnow, 'wait_for_pages', lambda sha: waits.append(sha) or published)
    monkeypatch.setattr(indexnow, 'submit', lambda urls: submitted.extend(urls) or 202)
    with pytest.raises(SystemExit) as result:
        indexnow.main()

    assert waits == ['exact-head']
    assert result.value.code == (0 if published == 'built' else 1)
    assert bool(submitted) == (published == 'built')


def test_only_the_pages_whose_data_changed_are_submitted():
    """Only the urls whose data changed are submitted, as the protocol asks:
    unchanged pages sent again and again spend the site's crawl for nothing. What changed is read off index.json, the site's data, before and
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
    is sent."""
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


def test_the_hourly_expiry_recovers_a_failed_notification_without_another_push(tmp_path):
    """Execute the actual publisher steps with a real Git remote and stubbed HTTP."""
    import json
    import os
    import subprocess
    import sys

    import yaml

    def run(*args, **kwargs):
        return subprocess.run(args, cwd=tmp_path, text=True, capture_output=True, **kwargs)

    def git(*args, repo=tmp_path):
        return run('git', '-C', str(repo), *args, check=True).stdout.strip()

    def commit(rows, *, repo=tmp_path):
        (repo / 'index.json').write_text(json.dumps(build_index(rows, TODAY)))
        git('add', 'index.json', repo=repo)
        git('-c', 'user.name=Test', '-c', 'user.email=test@example.org', 'commit',
            '--allow-empty', '-qm', 'publish', repo=repo)
        git('push', 'origin', 'HEAD:main', repo=repo)
        return git('rev-parse', 'HEAD', repo=repo)

    git('init', '-q', '-b', 'main')
    git('init', '-q', '--bare', str(tmp_path / 'remote.git'))
    git('remote', 'add', 'origin', str(tmp_path / 'remote.git'))
    start = commit([make(id='old')])
    cursor = 'refs/heads/indexnow-delivered'
    git('push', 'origin', f'{start}:{cursor}')
    current = commit([make(id='old'), make(id='new')])

    workflows = {name: yaml.safe_load((ROOT / '.github/workflows' / f'{name}.yml').read_text())
                 for name in ('indexnow', 'update', 'expire')}
    worker = workflows['indexnow']
    triggers = worker.get('on', worker.get(True))
    assert set(triggers) == {'push', 'workflow_dispatch'}
    assert triggers['push']['branches'] == ['main']
    assert worker['jobs']['ping']['if'] == "github.ref == 'refs/heads/main'"
    assert worker['concurrency']['cancel-in-progress'] is False
    steps = worker['jobs']['ping']['steps']
    checkout = next(s for s in steps if s.get('uses', '').startswith('actions/checkout'))
    assert checkout['with'] == {'ref': 'main', 'fetch-depth': 0}

    def step(workflow, job):
        return next(s for s in workflows[workflow]['jobs'][job]['steps']
                    if 'freetier-indexnow' in s.get('run', '') or
                    'workflow run indexnow.yml' in s.get('run', ''))

    assert "steps.publish.outcome == 'success'" in step('expire', 'expire')['if']
    assert '!inputs.dry_run' in step('update', 'update')['if']
    (tmp_path / 'worker.sh').write_text(step('indexnow', 'ping')['run'])
    (tmp_path / 'network.py').write_text("""
import json
import os
import signal
from pathlib import Path

import respx

from freetier_radar.indexnow import ENDPOINT, main

with respx.mock() as routes:
    pages = 'https://api.github.com/repos/mvalentsev/awesome-free-ai-coding/pages/builds'
    routes.get(pages + '/latest').respond(200, json={
        'status': 'built', 'commit': os.environ['SERVED_SHA'],
    })
    def submit(request):
        with Path('requests.jsonl').open('a') as log:
            log.write(json.dumps(json.loads(request.content)['urlList']) + '\\n')
        if os.environ['INDEXNOW_STATUS'] == 'cancelled':
            os.kill(os.getpid(), signal.SIGTERM)
        return respx.MockResponse(int(os.environ['INDEXNOW_STATUS']))
    routes.post(ENDPOINT).mock(side_effect=submit)
    main()
""")
    (tmp_path / 'publisher.sh').write_text("""
uv() {
    [[ "$1 $2" == 'run freetier-indexnow' ]] || return 22
    shift 2
    "$TEST_PYTHON" network.py "$@"
}
export -f uv
gh() {
    if [[ "$1 $2 $3" == 'workflow run indexnow.yml' ]]; then
        [[ "$4 $5 $6 $7" == "--repo $GITHUB_REPOSITORY --ref main" ]] || return 24
        EVENT=workflow_dispatch bash -eo pipefail worker.sh
    else
        return 23
    fi
}
export -f gh
""")

    def invoke(workflow, job, status, *, served=current):
        return run('bash', '-eo', 'pipefail', '-c', 'source publisher.sh\n' + step(workflow, job)['run'],
                   env={**os.environ, 'TEST_PYTHON': sys.executable, 'REBUILD_PAGES': 'false',
                        'EVENT': 'push', 'SERVED_SHA': served, 'INDEXNOW_STATUS': str(status),
                        'GITHUB_REPOSITORY': 'mvalentsev/awesome-free-ai-coding'})

    def accepted():
        return git('ls-remote', 'origin', cursor).split()[0]

    first = invoke('update', 'update', 503)
    assert first.returncode == 1, first.stderr
    assert accepted() == start
    retry = invoke('expire', 'expire', 202)
    assert retry.returncode == 0, retry.stderr
    assert accepted() == current, retry.stdout
    duplicate = invoke('expire', 'expire', 200)
    assert duplicate.returncode == 0, duplicate.stderr
    def recorded_posts():
        return [json.loads(line) for line in (tmp_path / 'requests.jsonl').read_text().splitlines()]

    posts = recorded_posts()
    assert len(posts) == 2 and posts[0] == posts[1]
    assert f'{PAGES_URL}/providers/new/' in posts[1]
    assert f'{PAGES_URL}/providers/old/' not in posts[1]

    rows = [make(id='old'), make(id='new'), make(id='during-cancel')]
    interrupted = commit(rows)
    cancelled = invoke('update', 'update', 'cancelled', served=interrupted)
    assert cancelled.returncode == 143, cancelled.stderr
    assert accepted() == current

    other_checkout = tmp_path / 'other'
    git('clone', '-q', '-b', 'main', str(tmp_path / 'remote.git'), str(other_checkout))
    newest_rows = [*rows, make(id='after-cancel')]
    latest = commit(newest_rows, repo=other_checkout)
    assert run('git', 'cat-file', '-e', latest).returncode != 0
    stale = invoke('indexnow', 'ping', 200, served=latest)
    assert stale.returncode == 0 and 'superseded' in stale.stdout, stale.stderr
    assert accepted() == current
    assert len(recorded_posts()) == 3

    git('merge', '--ff-only', 'FETCH_HEAD')
    recovered = invoke('indexnow', 'ping', 200, served=latest)
    assert recovered.returncode == 0, recovered.stderr
    assert accepted() == latest
    posts = recorded_posts()
    assert len(posts) == 4
    assert {url for url in posts[-1] if '/providers/' in url and url != PAGES_URL + '/providers/'} == {
        f'{PAGES_URL}/providers/during-cancel/', f'{PAGES_URL}/providers/after-cancel/',
    }

    unchanged = commit(newest_rows)
    empty = invoke('expire', 'expire', 200, served=unchanged)
    assert empty.returncode == 0 and 'nothing submitted' in empty.stdout, empty.stderr
    assert accepted() == unchanged
    assert len(recorded_posts()) == 4


def test_a_push_submits_pages_with_new_related_links_but_not_date_churn(tmp_path):
    import json
    from freetier_radar import git
    from freetier_radar.indexnow import changed_since
    from freetier_radar.render import build_model_page, model_page_url

    def commit(message):
        git.run(tmp_path, "add", ".").check_returncode()
        result = git.run(tmp_path, "-c", "user.name=Test", "-c", "user.email=t@t",
                         "commit", "-qm", message)
        result.check_returncode()
        return git.run(tmp_path, "rev-parse", "HEAD").stdout.strip()

    git.run(tmp_path, "init", "-q").check_returncode()
    (tmp_path / "models").mkdir()
    primary, related, peer = "glm-5.3", "glm-5.2", "kimi-k3"
    rows = [make(id="alpha", models=[{"family": primary}]),
            make(id="beta", models=[{"family": primary}, {"family": related}]),
            make(id="peer", models=[{"family": peer}]),
            make(id="second-peer", models=[{"family": peer}])]
    index_path = tmp_path / "index.json"
    first = build_index(rows, TODAY)
    index_path.write_text(json.dumps(first))
    for family in (primary, peer):
        page = build_model_page(family, rows, [], TODAY)
        (tmp_path / "models" / f"{family}.md").write_text(page)
    before = commit("initial pages")

    rows.append(make(id="gamma", models=[{"family": related}]))
    after = build_index(rows, TODAY)
    index_path.write_text(json.dumps(after))
    for family in (primary, related):
        page = build_model_page(family, rows, [], TODAY)
        (tmp_path / "models" / f"{family}.md").write_text(page)
    peer_path = tmp_path / "models" / f"{peer}.md"
    peer_text = peer_path.read_text()
    rerendered = re.sub(r"last_modified_at: [^\n]+", f"last_modified_at: {TODAY + timedelta(days=1)}",
                        peer_text)
    assert rerendered != peer_text
    peer_path.write_text(rerendered)
    published = commit("publish related page")

    primary_record = lambda index: next(m for m in index["models"] if m["family"] == primary)
    assert primary_record(first) == primary_record(after)
    page = (tmp_path / "models" / f"{primary}.md").read_text()
    assert model_page_url(related) in page.split("## Related models")[1]
    assert model_page_url(peer) in site_urls(after)
    urls = changed_since(before, after, repo=tmp_path, after=published)
    assert model_page_url(related) in urls
    assert model_page_url(primary) in urls
    assert model_page_url(peer) not in urls
