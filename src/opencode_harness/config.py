from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import tomllib


@dataclass(frozen=True)
class ModelConfig:
    provider: str = "mock"
    model: str = "mock-coder"
    base_url: str | None = None
    api_key_env: str = "OCH_API_KEY"
    temperature: float = 0.2
    max_tokens: int = 2048


@dataclass(frozen=True)
class AgentConfig:
    max_steps: int = 8
    context_chars: int = 6000


@dataclass(frozen=True)
class PermissionConfig:
    allow_write: bool = False
    allow_shell: bool = True
    allow_network: bool = False
    approval_mode: str = "never"


@dataclass(frozen=True)
class McpToolConfig:
    name: str
    description: str = ""
    input_schema: dict[str, Any] | None = None
    server: str | None = None


@dataclass(frozen=True)
class McpServerConfig:
    name: str
    command: str
    args: tuple[str, ...] = ()


@dataclass(frozen=True)
class HarnessConfig:
    model: ModelConfig = ModelConfig()
    agent: AgentConfig = AgentConfig()
    permissions: PermissionConfig = PermissionConfig()
    mcp_tools: tuple[McpToolConfig, ...] = ()
    mcp_servers: tuple[McpServerConfig, ...] = ()


def load_config(path: Path | None) -> HarnessConfig:
    if path is None:
        default_path = Path("och.config.toml")
        path = default_path if default_path.exists() else None

    if path is None:
        return HarnessConfig()

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    model_data = data.get("model", {})
    agent_data = data.get("agent", {})
    permission_data = data.get("permissions", {})
    mcp_tool_data = data.get("mcp_tools", [])
    mcp_server_data = data.get("mcp_servers", [])

    return HarnessConfig(
        model=ModelConfig(**model_data),
        agent=AgentConfig(**agent_data),
        permissions=PermissionConfig(**permission_data),
        mcp_tools=tuple(McpToolConfig(**item) for item in mcp_tool_data),
        mcp_servers=tuple(
            McpServerConfig(
                name=str(item["name"]),
                command=str(item["command"]),
                args=tuple(str(arg) for arg in item.get("args", ())),
            )
            for item in mcp_server_data
        ),
    )
