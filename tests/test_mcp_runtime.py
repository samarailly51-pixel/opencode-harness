from pathlib import Path
import sys
import tempfile
import textwrap
import unittest

from opencode_harness.config import HarnessConfig, McpServerConfig, PermissionConfig
from opencode_harness.mcp_runtime import build_mcp_runtime
from opencode_harness.tools import ToolRegistry


FAKE_SERVER = r'''
import json
import sys

TOOL_NAME = sys.argv[1]

for line in sys.stdin:
    message = json.loads(line)
    method = message.get("method")
    if "id" not in message:
        continue
    response = {"jsonrpc": "2.0", "id": message["id"]}
    if method == "initialize":
        response["result"] = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
            "serverInfo": {"name": TOOL_NAME, "version": "0.1.0"},
        }
    elif method == "tools/list":
        response["result"] = {
            "tools": [
                {
                    "name": TOOL_NAME,
                    "description": "Test tool.",
                    "inputSchema": {"type": "object", "properties": {}},
                }
            ]
        }
    elif method == "tools/call":
        response["result"] = {
            "content": [{"type": "text", "text": "called " + message["params"]["name"]}],
            "isError": False,
        }
    elif method == "resources/list":
        response["result"] = {
            "resources": [{"uri": "docs://" + TOOL_NAME, "name": TOOL_NAME + " docs"}]
        }
    elif method == "resources/read":
        response["result"] = {
            "contents": [{"uri": message["params"]["uri"], "text": "resource " + TOOL_NAME}]
        }
    elif method == "prompts/list":
        response["result"] = {"prompts": [{"name": "review", "description": "Review."}]}
    elif method == "prompts/get":
        response["result"] = {
            "messages": [
                {"role": "user", "content": {"type": "text", "text": "prompt " + TOOL_NAME}}
            ]
        }
    else:
        response["error"] = {"code": -32601, "message": "not found"}
    print(json.dumps(response), flush=True)
'''


class McpRuntimeTests(unittest.TestCase):
    def test_runtime_adds_resources_prompts_status_and_namespaces_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            server = root / "fake_mcp_server.py"
            server.write_text(textwrap.dedent(FAKE_SERVER), encoding="utf-8")
            config = HarnessConfig(
                mcp_servers=(
                    McpServerConfig("one", sys.executable, (str(server), "lookup")),
                    McpServerConfig("two", sys.executable, (str(server), "lookup")),
                )
            )

            runtime = build_mcp_runtime(config)
            try:
                names = {tool.name for tool in runtime.tools}
                tools = ToolRegistry(
                    root,
                    PermissionConfig(),
                    external_tools=runtime.tools,
                    external_handlers=runtime.handlers,
                    external_approval_modes=runtime.approval_modes,
                )
                resource_list = tools.run("mcp_one_list_resources", {})
                resource = tools.run("mcp_one_read_resource", {"uri": "docs://lookup"})
                prompts = tools.run("mcp_one_list_prompts", {})
                prompt = tools.run("mcp_one_get_prompt", {"name": "review"})
                status = tools.run("mcp_one_status", {})
            finally:
                runtime.close()

            self.assertIn("lookup", names)
            self.assertIn("mcp_two_lookup", names)
            self.assertIn("mcp_one_list_resources", names)
            self.assertTrue(resource_list.ok)
            self.assertIn("docs://lookup", resource_list.content)
            self.assertIn("resource lookup", resource.content)
            self.assertIn("review", prompts.content)
            self.assertIn("prompt lookup", prompt.content)
            self.assertIn('"status": "running"', status.content)
            self.assertEqual(runtime.diagnostics[0].status, "running")

    def test_server_approval_mode_overrides_global_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            server = root / "fake_mcp_server.py"
            server.write_text(textwrap.dedent(FAKE_SERVER), encoding="utf-8")
            config = HarnessConfig(
                permissions=PermissionConfig(approval_mode="never"),
                mcp_servers=(
                    McpServerConfig(
                        "one",
                        sys.executable,
                        (str(server), "lookup"),
                        approval_mode="ask",
                    ),
                ),
            )

            runtime = build_mcp_runtime(config)
            try:
                tools = ToolRegistry(
                    root,
                    PermissionConfig(approval_mode="never"),
                    external_tools=runtime.tools,
                    external_handlers=runtime.handlers,
                    external_approval_modes=runtime.approval_modes,
                    approval_callback=lambda request: False,
                )
                result = tools.run("lookup", {})
            finally:
                runtime.close()

            self.assertFalse(result.ok)
            self.assertIn("Blocked", result.content)

    def test_discovered_core_tool_name_is_namespaced(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            server = root / "fake_mcp_server.py"
            server.write_text(textwrap.dedent(FAKE_SERVER), encoding="utf-8")
            config = HarnessConfig(
                mcp_servers=(
                    McpServerConfig("core", sys.executable, (str(server), "read_file")),
                )
            )

            runtime = build_mcp_runtime(config)
            try:
                names = {tool.name for tool in runtime.tools}
                tools = ToolRegistry(
                    root,
                    PermissionConfig(),
                    external_tools=runtime.tools,
                    external_handlers=runtime.handlers,
                    external_approval_modes=runtime.approval_modes,
                )
                result = tools.run("mcp_core_read_file", {})
            finally:
                runtime.close()

            self.assertIn("mcp_core_read_file", names)
            self.assertTrue(result.ok)
            self.assertEqual(result.content, "called read_file")
