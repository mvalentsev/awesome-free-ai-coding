"""Read current and historical data with the same safe YAML parser."""
from typing import Any

import yaml


_SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def load_yaml(text: str | bytes) -> Any:
    return yaml.load(text, Loader=_SAFE_LOADER)
