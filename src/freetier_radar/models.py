from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel


class Category(str, Enum):
    AGENT_CLI = "agent-cli"
    API_FREE_TIER = "api-free-tier"
    TRIAL = "trial"
    AGGREGATOR = "aggregator"


class Tier(str, Enum):
    FRONTIER = "frontier"
    STRONG = "strong"


class ProbeType(str, Enum):
    API_MODELS = "api-models"
    PAGE_KEYWORDS = "page-keywords"


class ModelFamily(BaseModel):
    family: str
    tier: Tier = Tier.STRONG
    released: str = ""
    superseded_by: str | None = None


class Probe(BaseModel):
    type: ProbeType
    endpoint: str
    keywords: list[str] = []
    free_marker: str = ""


class Entry(BaseModel):
    id: str
    name: str
    category: Category
    url: str
    source_urls: list[str] = []
    card_required: bool = False
    offering: str
    limits: str = ""
    models: list[ModelFamily] = []
    probe: Probe
    first_seen: date
    last_verified: date
    probe_failures: int = 0
    provisional: bool = False


def load_registry(path: Path) -> list[Entry]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [Entry.model_validate(e) for e in data["entries"]]


def save_registry(path: Path, entries: list[Entry]) -> None:
    payload = {"entries": [e.model_dump(mode="json", exclude_none=True) for e in entries]}
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
