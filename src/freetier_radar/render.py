from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .models import Category, Entry, load_registry

ARCHIVE_AFTER_DAYS = 60

CATEGORY_TITLES: dict[Category, str] = {
    Category.AGENT_CLI: "🤖 Coding agents & CLIs",
    Category.API_FREE_TIER: "🔌 LLM APIs with free tier",
    Category.TRIAL: "🎁 Trials (no card when possible)",
    Category.AGGREGATOR: "🧭 Aggregators (one key, many providers)",
}


def is_archived(entry: Entry, today: date) -> bool:
    if entry.probe_failures >= 3:
        return True
    if (today - entry.last_verified).days > ARCHIVE_AFTER_DAYS:
        return True
    if entry.models and all(m.superseded_by for m in entry.models):
        return True
    return False


def _row(e: Entry) -> dict[str, str]:
    fams = [m.family for m in e.models if m.superseded_by is None]
    return {
        "name": e.name,
        "url": e.url,
        "offering": e.offering,
        "limits": e.limits or "—",
        "card": "💳 Yes" if e.card_required else "✅ No",
        "verified": e.last_verified.isoformat(),
        "models": ", ".join(fams) if fams else "—",
    }


def build_context(entries: list[Entry], today: date) -> dict:
    active = [e for e in entries if not is_archived(e, today)]
    archived = [e for e in entries if is_archived(e, today)]
    sections = [
        {"title": title,
         "rows": [_row(e) for e in sorted((e for e in active if e.category is cat),
                                          key=lambda e: (e.rank, e.name.lower()))]}
        for cat, title in CATEGORY_TITLES.items()
    ]
    return {"date": today.isoformat(), "sections": sections,
            "archived": [_row(e) for e in archived], "active_count": len(active)}


def render_readme(registry_path: Path, template_dir: Path, out_path: Path, today: date | None = None) -> str:
    today = today or date.today()
    env = Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    text = env.get_template("README.md.j2").render(**build_context(load_registry(registry_path), today))
    out_path.write_text(text, encoding="utf-8")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--templates", type=Path, default=Path("templates"))
    parser.add_argument("--out", type=Path, default=Path("README.md"))
    args = parser.parse_args()
    render_readme(args.registry, args.templates, args.out)
    print(f"rendered {args.out}")
