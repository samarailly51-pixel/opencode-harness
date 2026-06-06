from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
from typing import Any


class TraceWriter:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event_type: str, data: dict[str, Any]) -> None:
        event = {
            "time": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "data": _json_safe(data),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def update_latest(self) -> None:
        latest = self.path.parent / "latest.jsonl"
        if self.path.resolve() != latest.resolve():
            shutil.copyfile(self.path, latest)


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value
