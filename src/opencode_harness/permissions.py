from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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


@dataclass(frozen=True)
class ApprovalRequest:
    kind: str
    action: str
    reason: str


ApprovalCallback = Callable[[ApprovalRequest], bool]


def check_shell_permission(command: str, config: PermissionConfig) -> PermissionDecision:
    if not config.allow_shell:
        return PermissionDecision(False, "shell commands are disabled")
    if not config.allow_network and any(marker.lower() in command.lower() for marker in NETWORK_MARKERS):
        return PermissionDecision(False, "network-like command blocked by policy")
    normalized = command.strip().lower()
    if any(normalized.startswith(prefix) for prefix in READ_ONLY_COMMANDS):
        return PermissionDecision(True, "read-only command allowed")
    return PermissionDecision(False, "command is not in the default allowlist")


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
