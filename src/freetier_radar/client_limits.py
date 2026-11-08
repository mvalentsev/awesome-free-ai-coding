"""Read token limits from an official, structured client configuration example.

OpenCode v2.2.5's provider/models/limit shape was measured on 2026-11-04.
Each provider's own source remains explicit and is rechecked independently.
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Entry


class _CodeBlocks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.parts: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"pre", "code"}:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in {"pre", "code"} and self.depth:
            self.depth -= 1
            if not self.depth:
                self.blocks.append("".join(self.parts))
                self.parts = []

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _config_examples(body: str) -> list[tuple[str, object]]:
    parser = _CodeBlocks()
    parser.feed(body)
    blocks = parser.blocks + re.findall(r"```(?:jsonc?)?\s*\n(.*?)```", body, re.S)
    # A source may be the configuration file itself, rather than an HTML page.
    if body.lstrip().startswith("{"):
        blocks.append(body)
    examples = []
    for block in blocks:
        try:
            config = json.loads(block, object_pairs_hook=_unique_object)
        except (ValueError, RecursionError):
            config = None
        examples.append((block, config))
    return examples


def _example_limits(examples: list[tuple[str, object]], provider: str,
                    model: str) -> tuple[dict | None, str]:
    found = set()
    for block, config in examples:
        if config is None:
            if all(json.dumps(key) in block for key in ("provider", "models", provider, model)):
                return None, "documented limits invalid"
            continue
        if not isinstance(config, dict):
            continue
        providers = config.get("provider")
        source = providers.get(provider) if isinstance(providers, dict) else None
        models = source.get("models") if isinstance(source, dict) else None
        row = models.get(model) if isinstance(models, dict) else None
        if not isinstance(row, dict) or "limit" not in row:
            continue
        limits = row["limit"]
        if not isinstance(limits, dict):
            return None, "documented limits invalid"
        context, output = limits.get("context"), limits.get("output")
        if (type(context) is not int or type(output) is not int
                or not 0 < output <= context):
            return None, "documented limits invalid"
        found.add((context, output))
    if len(found) != 1:
        return None, "documented limits ambiguous" if found else "documented limits unavailable"
    context, output = found.pop()
    return {"context_tokens": context, "output_tokens": output}, ""


def opencode_limits(body: str, provider: str, model: str) -> tuple[dict | None, str]:
    """Require one unambiguous provider/model limit in JSON code examples."""
    return _example_limits(_config_examples(body), provider, model)


def limit_sources(entry: Entry) -> list[str]:
    if not entry.api:
        return []
    sources = [l.source for mid, l in entry.api.model_limits.items()
               if mid in entry.api.model_ids and l.read == "opencode-config"]
    sources.extend(s.source for mid, s in entry.api.opencode_output_sources.items()
                   if mid in entry.api.model_ids)
    return list(dict.fromkeys(sources))


def model_limit_changes(entry: Entry, bodies: dict[str, str]) -> list[str]:
    if not entry.api:
        return []
    findings = []
    from .quotes import flatten, page_texts
    for mid, source in entry.api.opencode_output_sources.items():
        if mid not in entry.api.model_ids:
            continue
        body = bodies.get(source.source)
        if body is None or not any(flatten(source.quote) in text for text in page_texts(body)):
            findings.append(f"api.opencode_output_tokens {mid}: documented output parameter changed or unavailable")
    examples = {}
    for mid, limits in entry.api.model_limits.items():
        if mid not in entry.api.model_ids or limits.read != "opencode-config":
            continue
        body = bodies.get(limits.source)
        if body is None:
            detail = "source could not be checked"
        else:
            if limits.source not in examples:
                examples[limits.source] = _config_examples(body)
            actual, detail = _example_limits(examples[limits.source], limits.source_provider, mid)
            if actual is not None:
                detail = ", ".join(f"{key}={value} (recorded {getattr(limits, key)})"
                                   for key, value in actual.items()
                                   if value != getattr(limits, key))
        if detail:
            findings.append(f"api.model_limits {mid}: {detail}")
    return findings
