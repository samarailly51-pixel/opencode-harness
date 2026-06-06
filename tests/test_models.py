import unittest

from opencode_harness.models import _parse_anthropic_tool_calls, _parse_openai_tool_calls


class ModelTests(unittest.TestCase):
    def test_parse_openai_tool_calls(self) -> None:
        calls = _parse_openai_tool_calls(
            {
                "content": None,
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "read_file",
                            "arguments": "{\"path\":\"README.md\"}",
                        },
                    }
                ],
            }
        )

        self.assertIsNotNone(calls)
        self.assertEqual(calls[0].name, "read_file")
        self.assertEqual(calls[0].args, {"path": "README.md"})

    def test_parse_openai_tool_calls_handles_bad_json(self) -> None:
        calls = _parse_openai_tool_calls(
            {
                "tool_calls": [
                    {
                        "function": {
                            "name": "repo_map",
                            "arguments": "{bad",
                        },
                    }
                ],
            }
        )

        self.assertIsNotNone(calls)
        self.assertEqual(calls[0].args, {})

    def test_parse_anthropic_tool_calls(self) -> None:
        calls = _parse_anthropic_tool_calls(
            {
                "content": [
                    {"type": "text", "text": "I will inspect."},
                    {
                        "type": "tool_use",
                        "id": "toolu_1",
                        "name": "read_file",
                        "input": {"path": "README.md"},
                    },
                ]
            }
        )

        self.assertIsNotNone(calls)
        self.assertEqual(calls[0].name, "read_file")
        self.assertEqual(calls[0].args, {"path": "README.md"})

    def test_parse_anthropic_tool_calls_handles_bad_input(self) -> None:
        calls = _parse_anthropic_tool_calls(
            {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "repo_map",
                        "input": "bad",
                    }
                ]
            }
        )

        self.assertIsNotNone(calls)
        self.assertEqual(calls[0].args, {})
