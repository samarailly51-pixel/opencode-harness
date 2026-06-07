from __future__ import annotations

from dataclasses import dataclass
import re
import shlex
from typing import Callable

from .config import PermissionConfig


READ_ONLY_EXECUTABLES = {
    "dir",
    "get-childitem",
    "get-content",
    "ls",
    "pytest",
    "rg",
    "type",
}

READ_ONLY_GIT_SUBCOMMANDS = {
    "cat-file",
    "diff",
    "log",
    "ls-files",
    "ls-tree",
    "rev-parse",
    "show",
    "status",
}

READ_ONLY_PYTHON_MODULES = {
    "pytest",
    "unittest",
}

NETWORK_EXECUTABLES = {
    "curl",
    "iwr",
    "invoke-restmethod",
    "invoke-webrequest",
    "wget",
}

NETWORK_COMMANDS = (
    ("npm", "install"),
    ("pip", "install"),
    ("pnpm", "add"),
    ("pnpm", "install"),
    ("python", "-m", "pip", "install"),
    ("python3", "-m", "pip", "install"),
    ("yarn", "add"),
    ("yarn", "install"),
)

WRITE_EXECUTABLES = {
    "copy",
    "cp",
    "del",
    "erase",
    "mkdir",
    "move",
    "mv",
    "new-item",
    "ni",
    "rm",
    "rmdir",
    "remove-item",
    "ren",
    "rename-item",
    "set-content",
    "tee",
}

WRITE_COMMANDS = (
    ("git", "add"),
    ("git", "checkout"),
    ("git", "clean"),
    ("git", "commit"),
    ("git", "merge"),
    ("git", "mv"),
    ("git", "pull"),
    ("git", "push"),
    ("git", "rebase"),
    ("git", "reset"),
    ("git", "restore"),
    ("git", "rm"),
    ("git", "switch"),
)

SHELL_CONTROL_PATTERN = re.compile(r"(&&|\|\||;|\||`|\$\(|\n|\r)")
REDIRECTION_PATTERN = re.compile(r"(^|\s)(>>?|<)(\s|$)")


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str


@dataclass(frozen=True)
class ApprovalRequest:
    kind: str
    action: str
    reason: str


@dataclass(frozen=True)
class ShellCommandClassification:
    category: str
    reason: str
    tokens: tuple[str, ...]


ApprovalCallback = Callable[[ApprovalRequest], bool]


def check_shell_permission(command: str, config: PermissionConfig) -> PermissionDecision:
    if not config.allow_shell:
        return PermissionDecision(False, "shell commands are disabled")
    classification = classify_shell_command(command)
    if classification.category == "empty":
        return PermissionDecision(False, classification.reason)
    if classification.category == "network":
        if not config.allow_network:
            return PermissionDecision(False, classification.reason)
        return PermissionDecision(False, "network command is not in the default allowlist")
    if classification.category == "read_only":
        return PermissionDecision(True, classification.reason)
    return PermissionDecision(False, classification.reason)


def classify_shell_command(command: str) -> ShellCommandClassification:
    stripped = command.strip()
    if not stripped:
        return ShellCommandClassification("empty", "empty shell command", ())
    if SHELL_CONTROL_PATTERN.search(stripped):
        return ShellCommandClassification("compound", "compound shell commands require approval", ())
    if REDIRECTION_PATTERN.search(stripped):
        return ShellCommandClassification("write", "shell redirection can write files", ())
    tokens = _split_command(stripped)
    if not tokens:
        return ShellCommandClassification("unknown", "command could not be parsed", ())
    normalized = tuple(_normalize_token(token) for token in tokens)
    executable = _base_executable(normalized[0])
    command_tokens = (executable, *normalized[1:])
    if _starts_with_any(command_tokens, NETWORK_COMMANDS) or executable in NETWORK_EXECUTABLES:
        return ShellCommandClassification("network", "network-like command blocked by policy", command_tokens)
    if _starts_with_any(command_tokens, WRITE_COMMANDS) or executable in WRITE_EXECUTABLES:
        return ShellCommandClassification("write", "write-like shell command requires approval", command_tokens)
    if _is_read_only_command(command_tokens):
        return ShellCommandClassification("read_only", "read-only command allowed", command_tokens)
    return ShellCommandClassification("unknown", "command is not in the default allowlist", command_tokens)


def request_approval(
    request: ApprovalRequest,
    config: PermissionConfig,
    callback: ApprovalCallback | None = None,
) -> PermissionDecision:
    if config.approval_mode != "ask":
        return PermissionDecision(False, "approval mode is not interactive")
    approved = callback(request) if callback is not None else prompt_for_approval(request)
    if approved:
        return PermissionDecision(True, "approved by user")
    return PermissionDecision(False, "not approved by user")


def prompt_for_approval(request: ApprovalRequest) -> bool:
    print()
    print(f"Approval required for {request.kind}: {request.action}")
    print(f"Reason: {request.reason}")
    answer = input("Allow? [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def _split_command(command: str) -> tuple[str, ...]:
    try:
        return tuple(shlex.split(command, posix=False))
    except ValueError:
        return ()


def _normalize_token(token: str) -> str:
    return token.strip().strip('"').strip("'").lower()


def _base_executable(token: str) -> str:
    normalized = token.replace("\\", "/")
    name = normalized.rsplit("/", 1)[-1]
    if name.endswith(".exe") or name.endswith(".cmd") or name.endswith(".bat") or name.endswith(".ps1"):
        name = name.rsplit(".", 1)[0]
    return name


def _starts_with_any(tokens: tuple[str, ...], prefixes: tuple[tuple[str, ...], ...]) -> bool:
    return any(tokens[:len(prefix)] == prefix for prefix in prefixes)


def _is_read_only_command(tokens: tuple[str, ...]) -> bool:
    executable = tokens[0]
    if executable in READ_ONLY_EXECUTABLES:
        return True
    if executable == "git" and len(tokens) > 1:
        return tokens[1] in READ_ONLY_GIT_SUBCOMMANDS
    if executable in {"python", "python3", "py"} and len(tokens) > 2 and tokens[1] == "-m":
        return tokens[2] in READ_ONLY_PYTHON_MODULES
    return False
