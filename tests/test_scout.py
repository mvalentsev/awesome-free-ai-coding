from datetime import date

from freetier_radar.models import Entry
from freetier_radar.scout import (
    LLMClient, apply_new, apply_supersede, apply_updates, extract_yaml_block, run_scout,
)

TODAY = date(2026, 7, 19)

BASE = {
    "name": "X", "category": "api-free-tier", "url": "https://x.ai",
    "offering": "old offering", "limits": "old limits",
    "first_seen": date(2026, 1, 1), "last_verified": date(2026, 1, 1),
    "probe": {"type": "page-keywords", "endpoint": "https://x.ai", "keywords": ["free"]},
}


def make(**kw) -> Entry:
    d = {**BASE, "id": kw.pop("id", "x"), **kw}
    return Entry.model_validate(d)


class StubLLM:
    def __init__(self, replies: dict[str, str]):
        self.replies = replies

    def complete(self, prompt: str) -> str:
        for key, reply in self.replies.items():
            if key in prompt:
                return reply
        return "```yaml\n{}\n```"


def test_extract_yaml_block():
    assert extract_yaml_block("blah\n```yaml\na: 1\n```\nend") == "a: 1\n"
    assert extract_yaml_block("a: 1") == "a: 1"


def test_apply_updates_only_editable():
    entries = [make()]
    applied = apply_updates(entries, [{"id": "x", "limits": "new limits", "id_hack": "y", "name": "Hacked"}])
    assert applied == ["x"]
    assert entries[0].limits == "new limits"
    assert entries[0].name == "X"
    assert entries[0].id == "x"


def test_apply_new_skips_duplicates_and_invalid():
    entries = [make()]
    added = apply_new(entries, [
        {"id": "x", "name": "dup"},
        {"id": "new1", "name": "New", "category": "trial", "url": "https://n.ai",
         "offering": "trial", "probe": {"type": "page-keywords", "endpoint": "https://n.ai", "keywords": ["free"]}},
        {"id": "broken"},
    ], TODAY)
    assert added == ["new1"]
    assert len(entries) == 2
    new = entries[1]
    assert new.provisional is True and new.first_seen == TODAY and new.last_verified == TODAY


def test_apply_supersede():
    entries = [make(models=[{"family": "old"}, {"family": "cur"}])]
    done = apply_supersede(entries, [{"family": "old", "superseded_by": "cur"}, {"family": "nope", "superseded_by": "cur"}])
    assert done == ["old"]
    assert entries[0].models[0].superseded_by == "cur"
    assert entries[0].models[1].superseded_by is None


def test_run_scout_orchestration():
    llm = StubLLM({
        "FIX-FAILED": "```yaml\nupdates:\n  - id: x\n    limits: fixed\n```",
        "DISCOVER-NEW": "```yaml\nnew_entries: []\n```",
        "MODEL-GENERATIONS": "```yaml\nsupersede:\n  - family: old\n    superseded_by: cur\n```",
    })
    entries = [make(models=[{"family": "old"}])]
    result = run_scout(llm, entries, [{"id": "x", "detail": "boom"}], lambda urls: {u: "page text" for u in urls}, TODAY)
    assert result["updates"] == ["x"]
    assert result["supersede"] == ["old"]
    assert entries[0].limits == "fixed"
    assert entries[0].models[0].superseded_by == "cur"
