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
    elif method == "resources/list":
        response["result"] = {
            "resources": [
                {
                    "uri": "docs://guide",
                    "name": "Guide",
                    "description": "Test guide.",
                    "mimeType": "text/plain",
                }
            ]
        }
    elif method == "resources/read":
        response["result"] = {
            "contents": [
                {
                    "uri": message["params"]["uri"],
                    "mimeType": "text/plain",
                    "text": "resource text",
                }
            ]
        }
    elif method == "prompts/list":
        response["result"] = {
            "prompts": [
                {
                    "name": "review",
                    "description": "Review prompt.",
                    "arguments": [{"name": "topic", "required": True}],
                }
            ]
        }
    elif method == "prompts/get":
        args = message["params"].get("arguments", {})
        response["result"] = {
            "messages": [
                {
                    "role": "user",
                    "content": {"type": "text", "text": "review " + args.get("topic", "")},
                }
            ]
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
                resources = client.list_resources()
                resource = client.read_resource("docs://guide")
                prompts = client.list_prompts()
                prompt = client.get_prompt("review", {"topic": "agent"})
            finally:
                client.close()

            self.assertEqual(tools[0].name, "lookup")
            self.assertEqual(tools[0].server, "fake")
            self.assertTrue(result.ok)
            self.assertEqual(result.content, "found agent")
            self.assertEqual(resources[0].uri, "docs://guide")
            self.assertIn("resource text", resource.content)
            self.assertEqual(prompts[0].name, "review")
            self.assertIn("review agent", prompt.content)
