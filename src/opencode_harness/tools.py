from __future__ import annotations

from pathlib import Path
import re
import subprocess

from .config import PermissionConfig
from .mcp import ExternalToolSpec, McpHandler
from .permissions import check_shell_permission
from .repo_map import build_repo_map, pack_context
from .session import SessionState, TodoItem
from .tools_types import ToolResult


class ToolRegistry:
    def __init__(
        self,
        workspace: Path,
        permissions: PermissionConfig,
        session: SessionState | None = None,
        external_tools: list[ExternalToolSpec] | None = None,
        external_handlers: dict[str, McpHandler] | None = None,
    ) -> None:
        self.workspace = workspace.resolve()
        self.permissions = permissions
        self.session = session
        self.external_tools = {tool.name: tool for tool in external_tools or []}
        self.external_handlers = external_handlers or {}

    def run(self, name: str, args: dict[str, object]) -> ToolResult:
        if name in self.external_tools:
            return self.run_external(name, args)
        if name == "list_files":
            return self.list_files(str(args.get("path", ".")))
        if name == "read_file":
            return self.read_file(str(args["path"]))
        if name == "search_text":
            return self.search_text(str(args["pattern"]), str(args.get("path", ".")))
        if name == "write_file":
            return self.write_file(str(args["path"]), str(args.get("content", "")))
        if name == "replace_text":
            return self.replace_text(str(args["path"]), str(args["old"]), str(args["new"]))
        if name == "apply_patch":
            return self.apply_patch(str(args["patch"]))
        if name == "todo_set":
            return self.todo_set(args.get("items", []))
        if name == "todo_list":
            return self.todo_list()
        if name == "repo_map":
            return self.repo_map()
        if name == "context_pack":
            return self.context_pack(str(args.get("query", "")))
        if name == "shell":
            return self.shell(str(args["command"]))
        if name == "git_diff":
            return self.shell("git diff -- .")
        if name == "finish":
            return ToolResult(True, str(args.get("summary", "done")))
        return ToolResult(False, f"Unknown tool: {name}")

    def tool_specs(self) -> list[ExternalToolSpec]:
        return list(self.external_tools.values())

    def run_external(self, name: str, args: dict[str, object]) -> ToolResult:
        handler = self.external_handlers.get(name)
        if handler is None:
            spec = self.external_tools[name]
            server_hint = f" from server {spec.server}" if spec.server else ""
            return ToolResult(False, f"External MCP tool {name}{server_hint} is declared but no client is attached")
        return handler(args)

    def list_files(self, path: str) -> ToolResult:
        root = self._resolve(path)
        if not root.exists():
            return ToolResult(False, f"Path does not exist: {path}")
        files = []
        for item in sorted(root.iterdir(), key=lambda entry: entry.name.lower()):
            suffix = "/" if item.is_dir() else ""
            files.append(f"{item.name}{suffix}")
        return ToolResult(True, "\n".join(files) or "(empty)")

    def read_file(self, path: str) -> ToolResult:
        file_path = self._resolve(path)
        if not file_path.is_file():
            return ToolResult(False, f"Not a file: {path}")
        return ToolResult(True, file_path.read_text(encoding="utf-8", errors="replace"))

    def search_text(self, pattern: str, path: str) -> ToolResult:
        root = self._resolve(path)
        matches: list[str] = []
        for file_path in root.rglob("*"):
            if not file_path.is_file() or ".git" in file_path.parts:
                continue
            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                if pattern in line:
                    relative = file_path.relative_to(self.workspace)
                    matches.append(f"{relative}:{line_no}: {line}")
                    if len(matches) >= 100:
                        return ToolResult(True, "\n".join(matches))
        return ToolResult(True, "\n".join(matches) or "(no matches)")

    def write_file(self, path: str, content: str) -> ToolResult:
        if not self.permissions.allow_write:
            return ToolResult(False, "Blocked: file writes are disabled by policy")
        file_path = self._resolve(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return ToolResult(True, f"Wrote {path} ({len(content)} bytes)")

    def replace_text(self, path: str, old: str, new: str) -> ToolResult:
        if not self.permissions.allow_write:
            return ToolResult(False, "Blocked: file writes are disabled by policy")
        file_path = self._resolve(path)
        if not file_path.is_file():
            return ToolResult(False, f"Not a file: {path}")
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if old not in text:
            return ToolResult(False, f"Text not found in {path}")
        updated = text.replace(old, new, 1)
        file_path.write_text(updated, encoding="utf-8")
        return ToolResult(True, f"Replaced text in {path}")

    def apply_patch(self, patch: str) -> ToolResult:
        if not self.permissions.allow_write:
            return ToolResult(False, "Blocked: file writes are disabled by policy")
        try:
            changed = _apply_unified_diff(self.workspace, patch)
        except ValueError as error:
            return ToolResult(False, str(error))
        return ToolResult(True, "Patched files:\n" + "\n".join(changed))

    def todo_set(self, items: object) -> ToolResult:
        if self.session is None:
            return ToolResult(False, "No session is attached")
        if not isinstance(items, list):
            return ToolResult(False, "items must be a list")
        todos: list[TodoItem] = []
        for item in items:
            if isinstance(item, str):
                todos.append(TodoItem(title=item))
            elif isinstance(item, dict):
                title = str(item.get("title", "")).strip()
                status = str(item.get("status", "pending")).strip()
                if title:
                    todos.append(TodoItem(title=title, status=status))
        self.session.todos = todos
        return ToolResult(True, self.session.todo_summary())

    def todo_list(self) -> ToolResult:
        if self.session is None:
            return ToolResult(False, "No session is attached")
        return ToolResult(True, self.session.todo_summary())

    def repo_map(self) -> ToolResult:
        return ToolResult(True, build_repo_map(self.workspace).render())

    def context_pack(self, query: str) -> ToolResult:
        repo_map = build_repo_map(self.workspace)
        return ToolResult(True, pack_context(repo_map, query))

    def shell(self, command: str) -> ToolResult:
        decision = check_shell_permission(command, self.permissions)
        if not decision.allowed:
            return ToolResult(False, f"Blocked: {decision.reason}")
        completed = subprocess.run(
            command,
            cwd=self.workspace,
            shell=True,
            text=True,
            capture_output=True,
            timeout=120,
        )
        output = completed.stdout
        if completed.stderr:
            output += "\n[stderr]\n" + completed.stderr
        return ToolResult(completed.returncode == 0, output.strip())

    def _resolve(self, path: str) -> Path:
        candidate = (self.workspace / path).resolve()
        if candidate != self.workspace and self.workspace not in candidate.parents:
            raise ValueError(f"Path escapes workspace: {path}")
        return candidate


def _apply_unified_diff(workspace: Path, patch: str) -> list[str]:
    lines = patch.splitlines()
    index = 0
    changed: list[str] = []
    while index < len(lines):
        line = lines[index]
        if not line.startswith("--- "):
            index += 1
            continue
        old_path = _clean_diff_path(line[4:].strip())
        index += 1
        if index >= len(lines) or not lines[index].startswith("+++ "):
            raise ValueError("Invalid patch: expected +++ line")
        new_path = _clean_diff_path(lines[index][4:].strip())
        target_path = new_path if new_path != "/dev/null" else old_path
        if target_path == "/dev/null":
            raise ValueError("Deleting files is not supported by apply_patch")
        file_path = (workspace / target_path).resolve()
        if file_path != workspace and workspace not in file_path.parents:
            raise ValueError(f"Path escapes workspace: {target_path}")
        original = file_path.read_text(encoding="utf-8", errors="replace").splitlines() if file_path.exists() else []
        updated = original[:]
        index += 1
        while index < len(lines) and lines[index].startswith("@@"):
            header = lines[index]
            old_start = _parse_hunk_old_start(header)
            hunk_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].startswith("@@") and not lines[index].startswith("--- "):
                hunk_lines.append(lines[index])
                index += 1
            old_block = [item[1:] for item in hunk_lines if item.startswith((" ", "-"))]
            new_block = [item[1:] for item in hunk_lines if item.startswith((" ", "+"))]
            position = _find_hunk_position(updated, old_block, old_start)
            if position is None:
                raise ValueError(f"Patch context not found in {target_path}")
            updated = updated[:position] + new_block + updated[position + len(old_block):]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("\n".join(updated) + ("\n" if updated else ""), encoding="utf-8")
        changed.append(target_path)
    if not changed:
        raise ValueError("No file patches found")
    return changed


def _clean_diff_path(path: str) -> str:
    if path == "/dev/null":
        return path
    path = path.split("\t", 1)[0]
    if path.startswith("a/") or path.startswith("b/"):
        path = path[2:]
    return path


def _find_block(lines: list[str], block: list[str]) -> int | None:
    if not block:
        return len(lines)
    max_start = len(lines) - len(block)
    for start in range(max_start + 1):
        if lines[start:start + len(block)] == block:
            return start
    return None


def _parse_hunk_old_start(header: str) -> int | None:
    match = re.match(r"@@\s+-(\d+)(?:,\d+)?\s+\+\d+(?:,\d+)?\s+@@", header)
    if not match:
        return None
    return int(match.group(1))


def _find_hunk_position(lines: list[str], old_block: list[str], old_start: int | None) -> int | None:
    if old_start is not None:
        expected = max(old_start - 1, 0)
        if lines[expected:expected + len(old_block)] == old_block:
            return expected
        nearby = _find_nearby_block(lines, old_block, expected)
        if nearby is not None:
            return nearby
    return _find_block(lines, old_block)


def _find_nearby_block(lines: list[str], block: list[str], expected: int, radius: int = 4) -> int | None:
    if not block:
        return expected
    start = max(expected - radius, 0)
    stop = min(expected + radius, len(lines) - len(block))
    for position in range(start, stop + 1):
        if lines[position:position + len(block)] == block:
            return position
    return None
