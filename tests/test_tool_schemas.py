import unittest

from opencode_harness.mcp import ExternalToolSpec
from opencode_harness.tool_schemas import anthropic_tool_schemas, openai_tool_schemas


class ToolSchemaTests(unittest.TestCase):
    def test_openai_tool_schemas_include_core_tools(self) -> None:
        schemas = openai_tool_schemas()
        names = [schema["function"]["name"] for schema in schemas]

        self.assertIn("read_file", names)
        self.assertIn("apply_patch", names)
        self.assertIn("finish", names)
        self.assertTrue(all(schema["type"] == "function" for schema in schemas))

    def test_openai_tool_schemas_include_external_tools(self) -> None:
        schemas = openai_tool_schemas(
            [
                ExternalToolSpec(
                    name="mcp_lookup",
                    description="Lookup from an MCP server.",
                    input_schema={"type": "object", "properties": {"q": {"type": "string"}}},
                )
            ]
        )
        names = [schema["function"]["name"] for schema in schemas]

        self.assertIn("mcp_lookup", names)

    def test_anthropic_tool_schemas_include_core_tools(self) -> None:
        schemas = anthropic_tool_schemas()
        names = [schema["name"] for schema in schemas]

        self.assertIn("read_file", names)
        self.assertIn("apply_patch", names)
        self.assertIn("finish", names)
        self.assertTrue(all("input_schema" in schema for schema in schemas))

    def test_anthropic_tool_schemas_include_external_tools(self) -> None:
        schemas = anthropic_tool_schemas(
            [
                ExternalToolSpec(
                    name="mcp_lookup",
                    description="Lookup from an MCP server.",
                    input_schema={"type": "object", "properties": {"q": {"type": "string"}}},
                )
            ]
        )
        names = [schema["name"] for schema in schemas]

        self.assertIn("mcp_lookup", names)
