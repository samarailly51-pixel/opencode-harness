import unittest

from opencode_harness.config import PermissionConfig
from opencode_harness.permissions import ApprovalRequest, check_shell_permission, request_approval


class PermissionTests(unittest.TestCase):
    def test_allows_read_only_command(self) -> None:
        decision = check_shell_permission("git status --short", PermissionConfig())
        self.assertTrue(decision.allowed)


    def test_blocks_network_like_command(self) -> None:
        decision = check_shell_permission("pip install pytest", PermissionConfig(allow_network=False))
        self.assertFalse(decision.allowed)
        self.assertIn("network", decision.reason)

    def test_non_interactive_approval_mode_denies(self) -> None:
        decision = request_approval(
            ApprovalRequest(kind="write", action="note.txt", reason="file writes are disabled"),
            PermissionConfig(approval_mode="never"),
            lambda request: True,
        )

        self.assertFalse(decision.allowed)
        self.assertIn("not interactive", decision.reason)

    def test_ask_approval_mode_uses_callback(self) -> None:
        requests: list[ApprovalRequest] = []

        decision = request_approval(
            ApprovalRequest(kind="shell", action="echo hello", reason="not allowlisted"),
            PermissionConfig(approval_mode="ask"),
            lambda request: requests.append(request) is None or True,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(requests[0].kind, "shell")

    def test_ask_approval_mode_can_deny(self) -> None:
        decision = request_approval(
            ApprovalRequest(kind="mcp", action="lookup", reason="external tool call"),
            PermissionConfig(approval_mode="ask"),
            lambda request: False,
        )

        self.assertFalse(decision.allowed)
        self.assertIn("not approved", decision.reason)
