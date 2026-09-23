"""Hand-written files state figures the code applies — how long a verdict
lasts, how often the run probes, how a row leaves. The pages print them from
the constants; these files cannot, so each such sentence is held to its
constant and the day the two part is a failed check."""
from pathlib import Path

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


def test_the_committed_files_state_what_the_code_applies():
    assert check_claims(ROOT) == []
