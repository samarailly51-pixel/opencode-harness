from __future__ import annotations

from dataclasses import dataclass
import json
import subprocess
import threading
from typing import Any

from . import __version__
from .mcp import ExternalToolSpec
from .tools_types import ToolResult


@dataclass(frozen=True)
class McpServerSpec:
    name: str
    command: str
    args: tuple[str, ...] = ()


@dataclass(frozen=True)
class McpResource:
    uri: str
    name: str
    description: str = ""
    mime_type: str | None = None


@dataclass(frozen=True)
class McpPrompt:
    name: str
    description: str = ""
    arguments: list[dict[str, Any]] | None = None


class StdioMcpClient:
    def __init__(self, spec: McpServerSpec, timeout: float = 30.0) -> None:
        self.spec = spec
        self.timeout = timeout
        self._next_id = 1
        self._lock = threading.Lock()
        self._process: subprocess.Popen[str] | None = None
        self.capabilities: dict[str, Any] = {}
        self.server_info: dict[str, Any] = {}

    def start(self) -> None:
        if self._process is not None:
            return
        self._process = subprocess.Popen(
            [self.spec.command, *self.spec.args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        result = self.request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "opencode-harness", "version": __version__},
            },
        )
        self.capabilities = result.get("capabilities", {}) if isinstance(result.get("capabilities"), dict) else {}
        self.server_info = result.get("serverInfo", {}) if isinstance(result.get("serverInfo"), dict) else {}
        self.notify("notifications/initialized", {})

    def close(self) -> None:
        if self._process is None:
            return
        process = self._process
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                stream.close()
        self._process = None

    def list_tools(self) -> list[ExternalToolSpec]:
        self.start()
        result = self.request("tools/list", {})
        tools = []
        for item in result.get("tools", []):
            name = str(item["name"])
            tools.append(
                ExternalToolSpec(
                    name=name,
                    description=str(item.get("description", f"MCP tool {name}.")),
                    input_schema=item.get("inputSchema") or {"type": "object", "properties": {}},
                    server=self.spec.name,
                )
            )
        return tools

    def call_tool(self, name: str, args: dict[str, object]) -> ToolResult:
        self.start()
        result = self.request("tools/call", {"name": name, "arguments": args})
        if result.get("isError"):
            return ToolResult(False, _mcp_content_to_text(result.get("content", [])))
        return ToolResult(True, _mcp_content_to_text(result.get("content", [])))

    def list_resources(self) -> list[McpResource]:
        self.start()
        result = self.request("resources/list", {})
        resources = []
        for item in result.get("resources", []):
            uri = str(item["uri"])
            resources.append(
                McpResource(
                    uri=uri,
                    name=str(item.get("name", uri)),
                    description=str(item.get("description", "")),
                    mime_type=(
                        str(item["mimeType"])
                        if item.get("mimeType") is not None
                        else None
                    ),
                )
            )
        return resources

    def read_resource(self, uri: str) -> ToolResult:
        self.start()
        result = self.request("resources/read", {"uri": uri})
        return ToolResult(True, _mcp_resource_contents_to_text(result.get("contents", [])))

    def list_prompts(self) -> list[McpPrompt]:
        self.start()
        result = self.request("prompts/list", {})
        prompts = []
        for item in result.get("prompts", []):
            prompts.append(
                McpPrompt(
                    name=str(item["name"]),
                    description=str(item.get("description", "")),
                    arguments=item.get("arguments") if isinstance(item.get("arguments"), list) else None,
                )
            )
        return prompts

    def get_prompt(self, name: str, args: dict[str, object]) -> ToolResult:
        self.start()
        result = self.request("prompts/get", {"name": name, "arguments": args})
        return ToolResult(True, _mcp_prompt_messages_to_text(result.get("messages", [])))

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            process = self._require_process()
            request_id = self._next_id
            self._next_id += 1
            payload = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params,
            }
            assert process.stdin is not None
            process.stdin.write(json.dumps(payload) + "\n")
            process.stdin.flush()
            response = self._read_response(request_id)
            if "error" in response:
                raise RuntimeError(str(response["error"]))
            result = response.get("result", {})
            return result if isinstance(result, dict) else {}

    def notify(self, method: str, params: dict[str, Any]) -> None:
        process = self._require_process()
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        assert process.stdin is not None
        process.stdin.write(json.dumps(payload) + "\n")
        process.stdin.flush()

    def _read_response(self, request_id: int) -> dict[str, Any]:
        process = self._require_process()
        assert process.stdout is not None
        while True:
            line = process.stdout.readline()
            if line == "":
                raise RuntimeError("MCP server closed stdout")
            data = json.loads(line)
            if data.get("id") == request_id:
                return data

    def _require_process(self) -> subprocess.Popen[str]:
        if self._process is None:
            self._process = subprocess.Popen(
                [self.spec.command, *self.spec.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )
        return self._process


def _mcp_content_to_text(content: object) -> str:
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "text":
            parts.append(str(item.get("text", "")))
        else:
            parts.append(json.dumps(item, ensure_ascii=False))
    return "\n".join(part for part in parts if part)


def _mcp_resource_contents_to_text(contents: object) -> str:
    if not isinstance(contents, list):
        return ""
    parts: list[str] = []
    for item in contents:
        if not isinstance(item, dict):
            continue
        uri = str(item.get("uri", ""))
        mime_type = str(item.get("mimeType", ""))
        prefix = " ".join(part for part in [uri, mime_type] if part)
        text = item.get("text")
        if text is not None:
            parts.append((prefix + "\n" if prefix else "") + str(text))
        elif item.get("blob") is not None:
            parts.append((prefix + "\n" if prefix else "") + str(item.get("blob")))
    return "\n\n".join(part for part in parts if part)


def _mcp_prompt_messages_to_text(messages: object) -> str:
    if not isinstance(messages, list):
        return ""
    parts: list[str] = []
    for item in messages:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "message"))
        content = _mcp_content_to_text([item.get("content", {})])
        parts.append(f"{role}: {content}" if content else role)
    return "\n".join(parts)
