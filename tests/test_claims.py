"""Hand-written files state figures the code applies — how long a verdict
lasts, how often the run probes, how a row leaves. The pages print them from
the constants; these files cannot, so each such sentence is held to its
constant and the day the two part is a failed check."""
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
    monkeypatch.setattr(claims, 'BAR_DAYS', 21)
    assert check_claims(root, rules, scheduled=())
    text = render_contributing(root / 'CONTRIBUTING.md', root / 'CONTRIBUTING.md')
    assert 'waits three weeks' in text
    assert 'ends within three weeks' in text
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


def test_the_cron_and_the_schedule_the_pages_state_are_one(tmp_path):
    root = _root(tmp_path, "Nothing about it.\n", cron="23 5 * * 1,3,5")
    assert check_claims(root, (), scheduled=()) == [
        ".github/workflows/update.yml runs on weekdays 1,3,5 and models.PROBE_WEEKDAYS says "
        "1,4 — the pages would say twice a week"]


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
