from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .tools_types import ToolResult


McpHandler = Callable[[dict[str, object]], ToolResult]


@dataclass(frozen=True)
class ExternalToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    server: str | None = None


def external_tool_from_config(data: dict[str, Any]) -> ExternalToolSpec:
    name = str(data["name"])
    description = str(data.get("description", f"External MCP tool {name}."))
    input_schema = data.get("input_schema") or {"type": "object", "properties": {}}
    if not isinstance(input_schema, dict):
        raise ValueError(f"input_schema for MCP tool {name} must be an object")
    server = data.get("server")
    return ExternalToolSpec(
        name=name,
        description=description,
        input_schema=input_schema,
        server=str(server) if server is not None else None,
    )
