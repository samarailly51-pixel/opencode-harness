from pathlib import Path
import sys
import tempfile
import textwrap
import unittest

from opencode_harness.mcp_client import McpServerSpec, StdioMcpClient


FAKE_SERVER = r'''
import json
import sys

for line in sys.stdin:
    message = json.loads(line)
    method = message.get("method")
    if "id" not in message:
        continue
    response = {"jsonrpc": "2.0", "id": message["id"]}
    if method == "initialize":
        response["result"] = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "fake", "version": "0.1.0"},
        }
    elif method == "tools/list":
        response["result"] = {
            "tools": [
                {
                    "name": "lookup",
                    "description": "Lookup test data.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                }
            ]
        }
    elif method == "tools/call":
        args = message["params"]["arguments"]
        response["result"] = {
            "content": [{"type": "text", "text": "found " + args["query"]}],
            "isError": False,
        }
    else:
        response["error"] = {"code": -32601, "message": "not found"}
    print(json.dumps(response), flush=True)
'''


class McpClientTests(unittest.TestCase):
    def test_stdio_mcp_client_lists_and_calls_tools(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            server = Path(temp_dir) / "fake_mcp_server.py"
            server.write_text(textwrap.dedent(FAKE_SERVER), encoding="utf-8")
            client = StdioMcpClient(
                McpServerSpec(name="fake", command=sys.executable, args=(str(server),))
            )
            try:
                tools = client.list_tools()
                result = client.call_tool("lookup", {"query": "agent"})
            finally:
                client.close()

            self.assertEqual(tools[0].name, "lookup")
            self.assertEqual(tools[0].server, "fake")
            self.assertTrue(result.ok)
            self.assertEqual(result.content, "found agent")
