import unittest

from opencode_harness.messages import Message
from opencode_harness.models import MockModel, _parse_anthropic_tool_calls, _parse_openai_tool_calls


class ModelTests(unittest.TestCase):
    def test_mock_model_returns_provider_transcript(self) -> None:
        response = MockModel().complete([Message("user", "inspect this repo")], tools=True)

        self.assertIsNotNone(response.transcript)
        self.assertEqual(response.transcript.provider, "mock")
        self.assertEqual(response.transcript.request["messages"][0]["role"], "user")
        self.assertEqual(response.transcript.response["content"], response.content)

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
