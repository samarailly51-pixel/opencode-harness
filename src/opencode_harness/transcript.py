from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .mcp import ExternalToolSpec
from .messages import Message


@dataclass(frozen=True)
class ProviderTranscript:
    provider: str
    request_format: str
    response_format: str
    request: dict[str, Any]
    response: dict[str, Any]
    metadata: dict[str, Any] | None = None


def mock_transcript(
    messages: list[Message],
    tools: bool,
    extra_tools: list[ExternalToolSpec] | None,
    response: dict[str, Any],
) -> ProviderTranscript:
    return ProviderTranscript(
        provider="mock",
        request_format="opencode-harness.mock.v1",
        response_format="opencode-harness.mock.v1",
        request={
            "messages": [_message_data(message) for message in messages],
            "tools_enabled": tools,
            "extra_tools": [_tool_name(tool) for tool in extra_tools or []],
        },
        response=response,
    )


def openai_chat_transcript(
    payload: dict[str, Any],
    response: dict[str, Any],
    endpoint: str,
) -> ProviderTranscript:
    return ProviderTranscript(
        provider="openai-compatible",
        request_format="openai.chat_completions.v1",
        response_format="openai.chat_completions.v1",
        request=payload,
        response=response,
        metadata={"endpoint": endpoint},
    )


def anthropic_messages_transcript(
    payload: dict[str, Any],
    response: dict[str, Any],
    endpoint: str,
) -> ProviderTranscript:
    return ProviderTranscript(
        provider="anthropic",
        request_format="anthropic.messages.v1",
        response_format="anthropic.messages.v1",
        request=payload,
        response=response,
        metadata={"endpoint": endpoint},
    )


def _message_data(message: Message) -> dict[str, str]:
    return {"role": message.role, "content": message.content}


def _tool_name(tool: ExternalToolSpec) -> str:
    return tool.name
