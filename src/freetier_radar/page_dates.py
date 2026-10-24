"""Stable content modification dates for generated Markdown pages.

Verification remains the probe's provenance. Existing generated pages and Git
record substantive changes, including corrections that produce no history event.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path

import yaml

from . import git

MODIFIED = "last_modified_at"


def _parts(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    fields, separator, body = text[4:].partition("\n---\n")
    return (yaml.safe_load(fields) or {}, body) if separator else ({}, text)


def content_hash(text: str) -> str:
    fields, body = _parts(text)
    fields.pop(MODIFIED, None)
    # Only the writer's daily stamp is incidental. Verification dates, changes
    # to wording around it, titles, source URLs and limits remain substantive.
    body = re.sub(r"(Generated from `registry\.yaml` on )\d{4}-\d{2}-\d{2}", r"\1", body)
    content = json.dumps(fields, default=str, sort_keys=True, ensure_ascii=False) + "\n" + body
    return hashlib.sha256(content.encode()).hexdigest()


@lru_cache(maxsize=2048)
def _committed_date(repo: Path, head: str, rel: str, fingerprint: str) -> date | None:
    """Recover the latest substantive change, ignoring daily generation stamps."""
    changed = None
    for sha, stamp in git.commits(repo, "--first-parent", head, "--", rel, field="%ct"):
        previous = git.show(repo, sha, rel)
        if previous is None or content_hash(previous) != fingerprint:
            break
        changed = datetime.fromtimestamp(int(stamp), timezone.utc).date()
    return changed


class PageDates:
    def __init__(self, source: Path, today: date):
        self.source = source.resolve()
        self.today = today
        result = git.run(self.source, "rev-parse", "--show-toplevel")
        self.repo = Path(result.stdout.strip()) if result.returncode == 0 else None
        if self.repo and git.run(self.repo, "rev-parse", "--is-shallow-repository").stdout.strip() == "true":
            self.repo = None
        self.head = (git.run(self.repo, "rev-parse", "HEAD").stdout.strip()
                     if self.repo is not None else "")

    def stamp(self, rel: str, text: str) -> str:
        fields, body = _parts(text)
        fingerprint = content_hash(text)
        path = self.source / rel
        previous = path.read_text(encoding="utf-8") if path.is_file() else ""
        old, _ = _parts(previous)
        same = bool(previous) and content_hash(previous) == fingerprint
        if same:
            # Full Git provenance repairs stale legacy dates. A source archive
            # or shallow clone retains the recorded date; later full history
            # can still reconcile it without a migration flag or extra ledger.
            inherited = old.get(MODIFIED, fields.get(MODIFIED, self.today))
            historical = (_committed_date(self.repo, self.head,
                          path.relative_to(self.repo).as_posix(), fingerprint)
                          if self.repo is not None and self.head else None)
            modified = min(historical, self.today) if historical else date.fromisoformat(str(inherited))
        else:
            modified = self.today
        fields[MODIFIED] = modified
        return "---\n" + yaml.safe_dump(fields, allow_unicode=True, sort_keys=False,
                                        width=10000).rstrip() + "\n---\n" + body
