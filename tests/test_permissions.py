import unittest

from opencode_harness.config import PermissionConfig
from opencode_harness.permissions import ApprovalRequest, check_shell_permission, classify_shell_command, request_approval


class PermissionTests(unittest.TestCase):
    def test_allows_read_only_command(self) -> None:
        decision = check_shell_permission("git status --short", PermissionConfig())
        self.assertTrue(decision.allowed)


    def test_allows_python_unittest_command(self) -> None:
        decision = check_shell_permission("python -m unittest discover -s tests", PermissionConfig())
        self.assertTrue(decision.allowed)

    def test_classifies_git_show_as_read_only(self) -> None:
        classification = classify_shell_command("git show --stat")

        self.assertEqual(classification.category, "read_only")
        self.assertEqual(classification.tokens[:2], ("git", "show"))

    def test_blocks_network_like_command(self) -> None:
        decision = check_shell_permission("pip install pytest", PermissionConfig(allow_network=False))
        self.assertFalse(decision.allowed)
        self.assertIn("network", decision.reason)

    def test_blocks_compound_command_even_if_first_part_is_read_only(self) -> None:
        decision = check_shell_permission("git status --short && rm -rf .", PermissionConfig())

        self.assertFalse(decision.allowed)
        self.assertIn("compound", decision.reason)

    def test_blocks_shell_redirection(self) -> None:
        decision = check_shell_permission("echo hello > note.txt", PermissionConfig())

        self.assertFalse(decision.allowed)
        self.assertIn("redirection", decision.reason)

    def test_blocks_write_like_command(self) -> None:
        decision = check_shell_permission("git reset --hard", PermissionConfig())

        self.assertFalse(decision.allowed)
        self.assertIn("write-like", decision.reason)

    def test_network_command_still_requires_allowlist_when_network_is_enabled(self) -> None:
        decision = check_shell_permission("curl https://example.com", PermissionConfig(allow_network=True))

        self.assertFalse(decision.allowed)
        self.assertIn("network", classify_shell_command("curl https://example.com").category)

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
