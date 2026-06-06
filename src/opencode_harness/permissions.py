from __future__ import annotations

from dataclasses import dataclass

from .config import PermissionConfig


READ_ONLY_COMMANDS = (
    "dir",
    "git diff",
    "git status",
    "ls",
    "pytest",
    "python -m pytest",
    "rg",
    "type",
)

NETWORK_MARKERS = (
    "curl ",
    "Invoke-WebRequest",
    "npm install",
    "pip install",
    "pnpm install",
    "yarn add",
)


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str


def check_shell_permission(command: str, config: PermissionConfig) -> PermissionDecision:
    if not config.allow_shell:
        return PermissionDecision(False, "shell commands are disabled")
    if not config.allow_network and any(marker.lower() in command.lower() for marker in NETWORK_MARKERS):
        return PermissionDecision(False, "network-like command blocked by policy")
    normalized = command.strip().lower()
    if any(normalized.startswith(prefix) for prefix in READ_ONLY_COMMANDS):
        return PermissionDecision(True, "read-only command allowed")
    return PermissionDecision(False, "command is not in the default allowlist")
