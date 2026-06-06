import unittest

from opencode_harness.config import PermissionConfig
from opencode_harness.permissions import check_shell_permission


class PermissionTests(unittest.TestCase):
    def test_allows_read_only_command(self) -> None:
        decision = check_shell_permission("git status --short", PermissionConfig())
        self.assertTrue(decision.allowed)


    def test_blocks_network_like_command(self) -> None:
        decision = check_shell_permission("pip install pytest", PermissionConfig(allow_network=False))
        self.assertFalse(decision.allowed)
        self.assertIn("network", decision.reason)
