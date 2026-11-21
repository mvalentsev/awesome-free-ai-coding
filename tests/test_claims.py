"""Registered assertions follow their shared rules. Numerical values can be
generated; missing or rewritten sentences and values that drift still fail
validation."""
from datetime import time
from pathlib import Path

import pytest
import yaml

from freetier_radar.claims import CLAIMS, Claim, check_claims

ROOT = Path(__file__).resolve().parent.parent


def _root(tmp_path: Path, text: str, cron: str = "23 5 * * 1,4", **files: str) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "CONTRIBUTING.md").write_text(text, encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "update.yml").write_text(
        yaml.safe_dump({"on": {"schedule": [{"cron": cron}]}, "jobs": {}}), encoding="utf-8")
    for name, body in files.items():
        (tmp_path / name).write_text(body, encoding="utf-8")
    return tmp_path


RECHECK = Claim("CONTRIBUTING.md", r"expires after (\d+) days", lambda root: ("90",),
                "models.WATCH_RECHECK_DAYS")


def test_a_sentence_that_states_a_constant_is_held_to_it(tmp_path):
    root = _root(tmp_path, "Intro.\nA verdict expires after 60 days.\n")
    assert check_claims(root, (RECHECK,), scheduled=()) == [
        "CONTRIBUTING.md:2 says `expires after 60 days` and models.WATCH_RECHECK_DAYS says 90 "
        "— change the sentence or the constant, never one of them alone"]
    assert check_claims(_root(tmp_path / "ok", "A verdict expires after 90 days.\n"),
                        (RECHECK,), scheduled=()) == []


def test_contributing_writer_generates_rule_values_from_the_registered_truth(tmp_path, monkeypatch):
    from freetier_radar import claims
    from freetier_radar.render import MAP_BEGIN, MAP_END, render_contributing

    sentence = "A verdict is retained and it expires after {} days, at which point the scout\n"
    root = _root(tmp_path, sentence.format(90) + sentence.format(30) +
                          "The vendor's historical offer lasted 30 days.\n" +
                          f"{MAP_BEGIN}\nold map\n{MAP_END}\n")
    claim = next(c for c in CLAIMS if c.source == "models.WATCH_RECHECK_DAYS")
    monkeypatch.setattr(claims, "WATCH_RECHECK_DAYS", 90)
    assert check_claims(root, (claim,), scheduled=())
    text = render_contributing(root / "CONTRIBUTING.md", root / "CONTRIBUTING.md")
    assert text.count("expires after 90 days") == 2
    assert "The vendor's historical offer lasted 30 days." in text
    assert check_claims(root, (claim,), scheduled=()) == []


def test_contributing_writer_generates_the_evidence_age_and_its_unit(tmp_path, monkeypatch):
    from freetier_radar import claims
    from freetier_radar.render import MAP_BEGIN, MAP_END, render_contributing

    root = _root(tmp_path, 'records older than one day cannot authorize a new push.\n'
                          f'{MAP_BEGIN}\nold map\n{MAP_END}\n')
    claim = next(c for c in CLAIMS if c.source.startswith('quality.fresh_eligibility;'))
    for days, words in [(2, 'two days'), (1, 'one day')]:
        monkeypatch.setattr(claims, 'ELIGIBILITY_MAX_AGE_DAYS', days)
        text = render_contributing(root / 'CONTRIBUTING.md', root / 'CONTRIBUTING.md')
        assert f'records older than {words} cannot authorize' in text
        assert check_claims(root, (claim,), scheduled=()) == []


def test_dated_promotion_and_rotating_wait_copy_share_the_bar_constant(tmp_path, monkeypatch):
    from freetier_radar import claims
    from freetier_radar.render import MAP_BEGIN, MAP_END, render_contributing

    root = _root(tmp_path, 'An undated model on a rotating lane waits two weeks.\n'
                          'A dated promotion qualifies even if it ends within two weeks.\n'
                          f'{MAP_BEGIN}\nold map\n{MAP_END}\n')
    rules = tuple(c for c in CLAIMS if c.source == 'bars.BAR_DAYS'
                  and ('rotating lane waits' in c.pattern or 'ends within' in c.pattern))
    for days, words in [(21, 'three weeks'), (1, '1 day'), (10, '10 days')]:
        monkeypatch.setattr(claims, 'BAR_DAYS', days)
        assert check_claims(root, rules, scheduled=())
        text = render_contributing(root / 'CONTRIBUTING.md', root / 'CONTRIBUTING.md')
        assert f'waits {words}' in text
        assert f'ends within {words}' in text
        assert check_claims(root, rules, scheduled=()) == []


def test_a_sentence_rewritten_past_its_claim_is_reported(tmp_path):
    """A claim that stops matching checks nothing, which is how a hand-written
    figure drifts: the sentence is reworded, the figure goes with it."""
    root = _root(tmp_path, "Verdicts are kept for a quarter.\n")
    assert check_claims(root, (RECHECK,), scheduled=()) == [
        "CONTRIBUTING.md no longer has the sentence stating models.WATCH_RECHECK_DAYS "
        "(claims.CLAIMS: `expires after (\\d+) days`) — point the claim at the sentence that "
        "states it now"]


def test_the_schedule_is_said_the_way_the_cron_keeps_it(tmp_path):
    root = _root(tmp_path, "The run probes every row twice a week.\n",
                 **{"_config.yml": 'description: "probe-verified three times a week"\n'})
    assert check_claims(root, (), scheduled=("CONTRIBUTING.md", "_config.yml")) == [
        "_config.yml:1 says `three times a week` and the scheduled run probes twice a week "
        "(models.PROBE_WEEKDAYS)"]


@pytest.mark.parametrize('schedules', [
    ['23 5 * * 1,3,5'],
    ['23 5,17 * * 1,4'],
    ['23 5 * 11 1,4'],
    ['23 5 * * 1,4', '23 17 * * 1,4'],
    ['23 5 * * 1-4'],
])
def test_verification_requires_one_complete_scheduled_rule(tmp_path, schedules):
    root = _root(tmp_path, '')
    workflow = root / '.github/workflows/update.yml'
    workflow.write_text(yaml.safe_dump({'on': {'schedule': [{'cron': cron} for cron in schedules]}}))
    assert check_claims(root, (), scheduled=())


def test_a_manual_only_update_workflow_breaks_the_scheduled_claim(tmp_path):
    root = _root(tmp_path, '')
    (root / '.github/workflows/update.yml').write_text('on:\n  workflow_dispatch:\n')
    assert check_claims(root, (), scheduled=()) == [
        '.github/workflows/update.yml has no scheduled verification'
    ]


def test_the_contribution_guide_generates_the_verification_frequency(tmp_path, monkeypatch):
    from freetier_radar import models
    from freetier_radar.render import MAP_BEGIN, MAP_END, render_contributing

    root = _root(tmp_path, 'The scheduled run does this twice a week.\n'
                          f'{MAP_BEGIN}\nold map\n{MAP_END}\n', cron='23 5 * * *')
    monkeypatch.setattr(models, 'PROBE_WEEKDAYS', frozenset(range(7)))
    guide = root / 'CONTRIBUTING.md'
    rendered = render_contributing(guide, guide)
    assert rendered.startswith('The scheduled run does this every day.\n')


def test_verification_schedule_generates_the_actual_workflow(tmp_path, monkeypatch):
    from freetier_radar import claims, models
    root = _root(tmp_path, '')
    (root / 'pyproject.toml').write_bytes((ROOT / 'pyproject.toml').read_bytes())
    workflow = root / '.github/workflows/update.yml'
    workflow.write_text((ROOT / '.github/workflows/update.yml').read_text())
    before = yaml.safe_load(workflow.read_text())
    trigger = 'on' if 'on' in before else True
    monkeypatch.setattr(models, 'PROBE_TIME_UTC', time(hour=7, minute=14))
    for days, expected in [({0, 2, 6}, '14 7 * * 0,2,6'), (set(range(7)), '14 7 * * *')]:
        monkeypatch.setattr(models, 'PROBE_WEEKDAYS', days)
        assert check_claims(root, (), scheduled=())
        rendered = claims.render_claims(workflow.read_text(), '.github/workflows/update.yml', root)
        workflow.write_text(rendered)
        after = yaml.safe_load(rendered)
        assert after[trigger]['schedule'] == [{'cron': expected}]
        before[trigger]['schedule'] = after[trigger]['schedule']
        assert after == before
        assert check_claims(root, (), scheduled=()) == []


def test_render_projects_the_python_floor_to_every_workflow_and_keeps_the_indexnow_filter(render_source):
    import shutil

    from freetier_radar.render import render_all
    from test_render import TODAY

    root = render_source
    (root / 'pyproject.toml').write_text('[project]\nrequires-python = ">=3.13"\n')
    shutil.copytree(ROOT / '.github', root / '.github')
    shutil.copyfile(ROOT / 'CONTRIBUTING.md', root / 'CONTRIBUTING.md')
    indexnow = root / '.github/workflows/indexnow.yml'
    indexnow.write_text(indexnow.read_text().replace('      - "index.json"', '      - "stray.json"'))
    render_all(root / 'registry.yaml', ROOT / 'templates', root, today=TODAY)

    for name in ('ci', 'conformance', 'expire', 'indexnow', 'read-page', 'update'):
        workflow = yaml.safe_load((root / f'.github/workflows/{name}.yml').read_text())
        jobs = workflow['jobs']
        concrete = [step['with']['python-version']
                    for job in jobs.values() for step in job['steps']
                    if step.get('with', {}).get('python-version', '').startswith('3.')]
        assert concrete == ['3.13'], name
        if name == 'ci':
            assert jobs['test']['strategy']['matrix']['python'] == ['3.13', '3.14', '3.15']
    assert 'Python 3.13 to 3.15' in (root / 'CONTRIBUTING.md').read_text()
    assert '      - "index.json"' in indexnow.read_text()
    assert '      - "stray.json"' not in indexnow.read_text()


def test_shared_frequency_generates_static_text_without_rewriting_its_format(tmp_path, monkeypatch):
    from freetier_radar import claims, models

    monkeypatch.setattr(models, 'PROBE_WEEKDAYS', frozenset(range(7)))
    for filename, text in [
        ('_config.yml', 'description: "probe-verified twice a week"\n'),
        ('browse.html', '<p>Probe-verified twice a week; every offer has its own page.</p>'),
        ('assets/social-preview.svg', '<svg><text>Live probes twice a week</text></svg>'),
    ]:
        assert claims.render_claims(text, filename, tmp_path) == text.replace('twice a week', 'every day')


def test_browse_and_pages_settings_follow_their_shared_rules(tmp_path, monkeypatch):
    from freetier_radar import claims

    monkeypatch.setattr(claims, 'PROVISIONAL_PROMOTE_DAYS', 21)
    monkeypatch.setattr(claims, 'PAGES_URL', 'https://new.example/new-path')
    monkeypatch.setattr(claims, 'BROWSE_COMPARE_LIMIT', 2)
    browse = (ROOT / 'browse.html').read_text()
    config = (ROOT / '_config.yml').read_text()

    actual = claims.render_claims(browse, 'browse.html', tmp_path)
    assert 'href="https://new.example/new-path/browse.html"' in actual
    assert 'listed for less than three weeks' in actual
    assert 'Select up to <span id="comparison-limit">2</span> offers' in actual
    actual = claims.render_claims(config, '_config.yml', tmp_path)
    assert 'url: https://new.example\nbaseurl: /new-path\n' in actual


def test_every_claim_names_where_its_truth_lives():
    for claim in CLAIMS:
        assert claim.source and claim.file, claim.pattern


def test_documented_aa_hold_rejects_an_automatic_writer_that_ignores_it(tmp_path, monkeypatch):
    from freetier_radar import tiers
    root = _root(tmp_path, (ROOT / 'CONTRIBUTING.md').read_text())
    claim = next(c for c in CLAIMS if 'aa_auto' in c.pattern)
    assert check_claims(root, (claim,), scheduled=()) == []
    original = tiers.unmeasured
    def ignore_holds(entries, board):
        rows = [e.model_copy(update={'models': [m.model_copy(update={'aa_auto': True})
                                               for m in e.models]}) for e in entries]
        return original(rows, board)
    monkeypatch.setattr(tiers, 'unmeasured', ignore_holds)
    assert check_claims(root, (claim,), scheduled=())


@pytest.mark.parametrize('values', ['"agent-cli": 1, "api-free-tier": 0, "trial": 2, "aggregator": 3',
                                   '"agent-cli": 0, "api-free-tier": 1, "trial": 9, "aggregator": 3',
                                   '"agent-cli": 0, "api-free-tier": 1e9, "trial": 2, "aggregator": 3'])
def test_browse_category_order_cannot_diverge_while_retaining_the_same_keys(tmp_path, values):
    root = _root(tmp_path, '', **{'browse.html': 'var ORDER = {' + values + '};'})
    claim = next(c for c in CLAIMS if c.file == 'browse.html' and 'var ORDER' in c.pattern)
    assert check_claims(root, (claim,), scheduled=())


def test_browse_category_order_accepts_the_established_order(tmp_path):
    root = _root(tmp_path, '', **{'browse.html':
        'var ORDER = {"agent-cli": 0, "api-free-tier": 1, "trial": 2, "aggregator": 3};'})
    claim = next(c for c in CLAIMS if c.file == 'browse.html' and 'var ORDER' in c.pattern)
    assert check_claims(root, (claim,), scheduled=()) == []
