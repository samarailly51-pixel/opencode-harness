from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Callable

from .config import HarnessConfig
from .mcp import ExternalToolSpec, McpHandler
from .mcp_client import McpServerSpec, StdioMcpClient
from .tools_types import ToolResult


CORE_TOOL_NAMES = {
    "list_files",
    "read_file",
    "search_text",
    "write_file",
    "replace_text",
    "apply_patch",
    "todo_set",
    "todo_list",
    "repo_map",
    "context_pack",
    "shell",
    "git_diff",
    "finish",
}


@dataclass(frozen=True)
class McpServerDiagnostic:
    name: str
    status: str
    tool_count: int = 0
    capabilities: dict[str, object] | None = None
    server_info: dict[str, object] | None = None
    error: str | None = None


@dataclass(frozen=True)
class McpRuntime:
    tools: list[ExternalToolSpec]
    handlers: dict[str, McpHandler]
    clients: list[StdioMcpClient]
    approval_modes: dict[str, str]
    diagnostics: list[McpServerDiagnostic]

    def close(self) -> None:
        for client in self.clients:
            client.close()


def build_mcp_runtime(config: HarnessConfig) -> McpRuntime:
    tools: list[ExternalToolSpec] = []
    handlers: dict[str, McpHandler] = {}
    approval_modes: dict[str, str] = {}
    diagnostics: list[McpServerDiagnostic] = []
    clients: dict[str, StdioMcpClient] = {}
    used_names = set(CORE_TOOL_NAMES)
    configured_tool_originals: dict[str, str] = {}

    for tool in config.mcp_tools:
        tool_name = _unique_tool_name(tool.name, tool.server or "config", used_names)
        spec = ExternalToolSpec(
            name=tool_name,
            description=_description_with_alias(
                ExternalToolSpec(
                    name=tool.name,
                    description=tool.description or f"External MCP tool {tool.name}.",
                    input_schema=tool.input_schema or {"type": "object", "properties": {}},
                    server=tool.server,
                ),
                tool_name,
            ),
            input_schema=tool.input_schema or {"type": "object", "properties": {}},
            server=tool.server,
        )
        tools.append(spec)
        used_names.add(tool_name)
        configured_tool_originals[tool_name] = tool.name

    server_approval_modes = {
        server.name: server.approval_mode or "inherit"
        for server in config.mcp_servers
    }

    for server in config.mcp_servers:
        client = StdioMcpClient(
            McpServerSpec(name=server.name, command=server.command, args=server.args)
        )
        clients[server.name] = client
        try:
            discovered = client.list_tools()
            for discovered_tool in discovered:
                tool_name = _unique_tool_name(discovered_tool.name, server.name, used_names)
                spec = ExternalToolSpec(
                    name=tool_name,
                    description=_description_with_alias(discovered_tool, tool_name),
                    input_schema=discovered_tool.input_schema,
                    server=server.name,
                )
                tools.append(spec)
                handlers[tool_name] = _tool_handler(client, discovered_tool.name)
                approval_modes[tool_name] = server.approval_mode or "inherit"
                used_names.add(tool_name)

            _add_server_utility_tools(
                server.name,
                client,
                tools,
                handlers,
                approval_modes,
                used_names,
                server.approval_mode or "inherit",
            )
            diagnostics.append(
                McpServerDiagnostic(
                    name=server.name,
                    status="running",
                    tool_count=len(discovered),
                    capabilities=client.capabilities,
                    server_info=client.server_info,
                )
            )
        except Exception as error:
            diagnostics.append(
                McpServerDiagnostic(
                    name=server.name,
                    status="error",
                    error=str(error),
                )
            )

    for tool in tools:
        if tool.server and tool.server in clients and tool.name not in handlers:
            original_name = configured_tool_originals.get(tool.name, tool.name)
            handlers[tool.name] = _tool_handler(clients[tool.server], original_name)
            approval_modes[tool.name] = server_approval_modes.get(tool.server, "inherit")

    return McpRuntime(
        tools=tools,
        handlers=handlers,
        clients=list(clients.values()),
        approval_modes=approval_modes,
        diagnostics=diagnostics,
    )


def _add_server_utility_tools(
    server_name: str,
    client: StdioMcpClient,
    tools: list[ExternalToolSpec],
    handlers: dict[str, McpHandler],
    approval_modes: dict[str, str],
    used_names: set[str],
    approval_mode: str,
) -> None:
    prefix = f"mcp_{_tool_slug(server_name)}"
    utility_specs: list[tuple[str, str, dict[str, object], Callable[[dict[str, object]], ToolResult]]] = [
        (
            f"{prefix}_list_resources",
            f"List MCP resources exposed by server {server_name}.",
            {"type": "object", "properties": {}, "additionalProperties": False},
            lambda args: _safe_tool_call(lambda: _list_resources(client)),
        ),
        (
            f"{prefix}_read_resource",
            f"Read an MCP resource from server {server_name}.",
            {
                "type": "object",
                "properties": {"uri": {"type": "string", "description": "Resource URI."}},
                "required": ["uri"],
                "additionalProperties": False,
            },
            lambda args: _safe_tool_call(lambda: client.read_resource(str(args["uri"]))),
        ),
        (
            f"{prefix}_list_prompts",
            f"List MCP prompts exposed by server {server_name}.",
            {"type": "object", "properties": {}, "additionalProperties": False},
            lambda args: _safe_tool_call(lambda: _list_prompts(client)),
        ),
        (
            f"{prefix}_get_prompt",
            f"Get an MCP prompt from server {server_name}.",
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Prompt name."},
                    "arguments": {"type": "object", "description": "Prompt arguments."},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
            lambda args: _safe_tool_call(
                lambda: client.get_prompt(
                    str(args["name"]),
                    args.get("arguments", {}) if isinstance(args.get("arguments", {}), dict) else {},
                )
            ),
        ),
        (
            f"{prefix}_status",
            f"Return lifecycle diagnostics for MCP server {server_name}.",
            {"type": "object", "properties": {}, "additionalProperties": False},
            lambda args: ToolResult(
                True,
                json.dumps(
                    {
                        "server": server_name,
                        "status": "running",
                        "capabilities": client.capabilities,
                        "server_info": client.server_info,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
            ),
        ),
    ]
    for name, description, schema, handler in utility_specs:
        tool_name = _unique_tool_name(name, server_name, used_names)
        tools.append(
            ExternalToolSpec(
                name=tool_name,
                description=description,
                input_schema=schema,
                server=server_name,
            )
        )
        handlers[tool_name] = handler
        approval_modes[tool_name] = approval_mode
        used_names.add(tool_name)


def _tool_handler(client: StdioMcpClient, original_name: str) -> McpHandler:
    return lambda args: _safe_tool_call(lambda: client.call_tool(original_name, args))


def _safe_tool_call(callback: Callable[[], ToolResult]) -> ToolResult:
    try:
        return callback()
    except Exception as error:
        return ToolResult(False, str(error))


def _list_resources(client: StdioMcpClient) -> ToolResult:
    resources = client.list_resources()
    lines = [
        f"{item.uri}\t{item.name}\t{item.mime_type or ''}\t{item.description}".rstrip()
        for item in resources
    ]
    return ToolResult(True, "\n".join(lines) or "(no resources)")


def _list_prompts(client: StdioMcpClient) -> ToolResult:
    prompts = client.list_prompts()
    lines = [f"{item.name}\t{item.description}".rstrip() for item in prompts]
    return ToolResult(True, "\n".join(lines) or "(no prompts)")


def _unique_tool_name(name: str, server_name: str, used_names: set[str]) -> str:
    candidate = _tool_slug(name)
    if candidate not in used_names:
        return candidate
    prefix = f"mcp_{_tool_slug(server_name)}"
    candidate = f"{prefix}_{candidate}"
    index = 2
    while candidate in used_names:
        candidate = f"{prefix}_{_tool_slug(name)}_{index}"
        index += 1
    return candidate


def _tool_slug(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")
    if not slug:
        slug = "tool"
    if slug[0].isdigit():
        slug = f"mcp_{slug}"
    return slug


def _description_with_alias(tool: ExternalToolSpec, alias: str) -> str:
    if alias == tool.name:
        return tool.description
    return f"{tool.description} Original MCP tool name: {tool.name}."
