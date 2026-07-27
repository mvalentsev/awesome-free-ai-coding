from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, model_validator

# Words every vendor keeps on the page long after the offer is gone. A probe
# built out of these alone verifies that the page loads, nothing more.
GENERIC_KEYWORDS = frozenset({
    "free", "free tier", "free plan", "free trial", "free credits", "credits",
    "api", "pricing", "price", "limits", "rate limits", "no credit card",
    "no credit card required", "sign up", "get started",
})

# How a vendor words a withdrawal. Missing keywords catch an offer that quietly
# vanished from the page; these catch the opposite case — the page still lists
# the free tier and announces, a paragraph below, that it is over. Every phrase
# names the free offer itself, so a page retiring some unrelated product does
# not fail a live entry.
DEAD_MARKERS = (
    "no longer free",
    "no longer available for free",
    "free tier has ended",
    "free trial has ended",
    "free plan has ended",
    "free access has ended",
    "free api service has ended",
    "free tier has been discontinued",
    "free plan has been discontinued",
    "free tier is being discontinued",
    "discontinuing the free",
    "discontinued the free",
    "sunsetting the free",
    "we are retiring the free",
    "end of the free tier",
)


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
    dead_markers: list[str] = []  # entry-specific withdrawal wording, on top of DEAD_MARKERS

    @model_validator(mode="after")
    def _keywords_must_anchor(self) -> Probe:
        """A page-keywords probe needs at least one keyword that dies with the
        offer — the free model's id, its quota figure, or the price row. Generic
        words alone keep passing for months after a free tier is withdrawn."""
        if self.type is ProbeType.PAGE_KEYWORDS:
            if not any(k.strip().lower() not in GENERIC_KEYWORDS for k in self.keywords):
                raise ValueError(
                    f"probe {self.endpoint}: keywords {self.keywords} are all generic — "
                    "anchor on a free model id, a quota figure or a price row"
                )
        return self


class ApiInfo(BaseModel):
    """Connection details a developer pastes into an agent/SDK config."""
    base_url: str | None = None
    key_url: str | None = None
    auth: str = "api-key"  # "api-key" | "none"
    openai_compatible: bool = True
    model_ids: list[str] = []  # exact callable ids for generated configs
    note: str = ""


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
    api: ApiInfo | None = None
    probe: Probe
    first_seen: date
    last_verified: date
    retired_on: date | None = None  # vendor-announced shutdown; archives the row on that day
    probe_failures: int = 0
    provisional: bool = False
    rank: int = 100  # sort key within a category: lower renders higher


def load_registry(path: Path) -> list[Entry]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [Entry.model_validate(e) for e in data["entries"]]


def save_registry(path: Path, entries: list[Entry]) -> None:
    payload = {"entries": [e.model_dump(mode="json", exclude_none=True) for e in entries]}
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
