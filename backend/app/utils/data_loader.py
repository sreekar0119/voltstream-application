from __future__ import annotations
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "mock_data"


def read_json(filename: str) -> list[dict[str, Any]]:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing mock dataset: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(filename: str, payload: list[dict[str, Any]]) -> None:
    path = DATA_DIR / filename
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
