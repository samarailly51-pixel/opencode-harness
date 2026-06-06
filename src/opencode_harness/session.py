from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import json

from .messages import Message


@dataclass
class TodoItem:
    title: str
    status: str = "pending"


@dataclass
class SessionState:
    task: str = ""
    steps: int = 0
    status: str = "running"
    messages: list[Message] = field(default_factory=list)
    todos: list[TodoItem] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "SessionState":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            task=data.get("task", ""),
            steps=int(data.get("steps", 0)),
            status=data.get("status", "running"),
            messages=[
                Message(role=item["role"], content=item["content"])
                for item in data.get("messages", [])
            ],
            todos=[
                TodoItem(title=item["title"], status=item.get("status", "pending"))
                for item in data.get("todos", [])
            ],
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")

    def todo_summary(self) -> str:
        if not self.todos:
            return "(no todos)"
        return "\n".join(f"- [{item.status}] {item.title}" for item in self.todos)
