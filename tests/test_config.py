from pathlib import Path
import tempfile
import unittest

from opencode_harness.config import load_config


class ConfigTests(unittest.TestCase):
    def test_load_mcp_tool_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "och.config.toml"
            path.write_text(
                """
[[mcp_tools]]
name = "mcp_lookup"
description = "Lookup from an MCP server."
server = "docs"

[mcp_tools.input_schema]
type = "object"

[[mcp_servers]]
name = "docs"
command = "python"
args = ["server.py"]
""".strip(),
                encoding="utf-8",
            )

            config = load_config(path)

            self.assertEqual(config.mcp_tools[0].name, "mcp_lookup")
            self.assertEqual(config.mcp_tools[0].server, "docs")
            self.assertEqual(config.mcp_tools[0].input_schema, {"type": "object"})
            self.assertEqual(config.mcp_servers[0].name, "docs")
            self.assertEqual(config.mcp_servers[0].args, ("server.py",))
