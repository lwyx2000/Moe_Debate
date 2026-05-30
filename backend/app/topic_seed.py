from __future__ import annotations

import json
from pathlib import Path

from .models import DebateTopic, TopicCollection

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_seed_topics() -> list[DebateTopic]:
    data = json.loads((DATA_DIR / "topics.json").read_text(encoding="utf-8"))
    return [DebateTopic(**item) for item in data]


def load_seed_collections() -> list[TopicCollection]:
    data = json.loads((DATA_DIR / "topic_collections.json").read_text(encoding="utf-8"))
    return [TopicCollection(**item) for item in data]
