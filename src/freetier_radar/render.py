from __future__ import annotations

import argparse
import json
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
        "verified": e.last_verified.isoformat() + (" 🧪" if e.provisional else ""),
        "models": ", ".join(fams) if fams else "—",
    }


def env_var(entry_id: str) -> str:
    return entry_id.removesuffix("-free").replace("-", "_").replace(".", "_").upper() + "_API_KEY"


def _connectable(entries: list[Entry], today: date) -> list[Entry]:
    return sorted(
        (e for e in entries
         if not is_archived(e, today) and e.api and e.api.base_url and e.api.openai_compatible),
        key=lambda e: (e.rank, e.name.lower()),
    )


def build_context(entries: list[Entry], today: date) -> dict:
    active = [e for e in entries if not is_archived(e, today)]
    archived = [e for e in entries if is_archived(e, today)]
    sections = [
        {"title": title,
         "rows": [_row(e) for e in sorted((e for e in active if e.category is cat),
                                          key=lambda e: (e.rank, e.name.lower()))]}
        for cat, title in CATEGORY_TITLES.items()
    ]
    connections = [
        {"name": e.name, "base_url": e.api.base_url,
         "auth": "—" if e.api.auth == "none" else f"`{env_var(e.id)}`",
         "key_url": e.api.key_url or "", "note": e.api.note}
        for e in _connectable(entries, today)
    ]
    return {"date": today.isoformat(), "sections": sections,
            "archived": [_row(e) for e in archived], "active_count": len(active),
            "has_provisional": any(e.provisional for e in active),
            "connections": connections}


def build_index(entries: list[Entry], today: date) -> dict:
    return {
        "generated": today.isoformat(),
        "source": "https://github.com/mvalentsev/awesome-free-ai-coding",
        "entries": [
            {**e.model_dump(mode="json", exclude_none=True), "archived": is_archived(e, today)}
            for e in entries
        ],
    }


def build_opencode_config(entries: list[Entry], today: date) -> dict:
    providers = {}
    for e in _connectable(entries, today):
        options: dict = {"baseURL": e.api.base_url}
        if e.api.auth != "none":
            options["apiKey"] = "{env:" + env_var(e.id) + "}"
        ids = e.api.model_ids or [m.family for m in e.models if m.superseded_by is None]
        models = {mid: {"name": mid} for mid in ids}
        providers[e.id] = {
            "npm": "@ai-sdk/openai-compatible",
            "name": e.name,
            "options": options,
            "models": models,
        }
    return {"$schema": "https://opencode.ai/config.json", "provider": providers}


def build_env_example(entries: list[Entry], today: date) -> str:
    lines = [
        "# Free LLM providers — generated from registry.yaml, do not edit by hand.",
        "# Fill the keys you use, then `source` this file. Every endpoint is",
        "# OpenAI-compatible: point any SDK/agent at the base URL next to the key.",
        "",
    ]
    for e in _connectable(entries, today):
        if e.api.auth == "none":
            lines.append(f"# ── {e.name} — no key needed · base: {e.api.base_url}")
        else:
            key_hint = f" · get a key: {e.api.key_url}" if e.api.key_url else ""
            lines.append(f"# ── {e.name} — base: {e.api.base_url}{key_hint}")
            lines.append(f'export {env_var(e.id)}=""')
        if e.api.note:
            lines.append(f"#    note: {e.api.note}")
        lines.append("")
    return "\n".join(lines)


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


def render_artifacts(registry_path: Path, root: Path, today: date | None = None) -> None:
    """index.json + configs/ — the machine-usable outputs, regenerated with the README."""
    today = today or date.today()
    entries = load_registry(registry_path)
    (root / "index.json").write_text(
        json.dumps(build_index(entries, today), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    configs = root / "configs"
    configs.mkdir(parents=True, exist_ok=True)
    (configs / "opencode.json").write_text(
        json.dumps(build_opencode_config(entries, today), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    (configs / "free-llm.env.example").write_text(
        build_env_example(entries, today) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--templates", type=Path, default=Path("templates"))
    parser.add_argument("--out", type=Path, default=Path("README.md"))
    args = parser.parse_args()
    render_readme(args.registry, args.templates, args.out)
    render_artifacts(args.registry, args.out.parent if args.out.parent != Path("") else Path("."))
    print(f"rendered {args.out}, index.json, configs/")
