from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any
from urllib import request

from .config import ModelConfig
from .mcp import ExternalToolSpec
from .messages import Message
from .tool_schemas import anthropic_tool_schemas, openai_tool_schemas


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, object]


@dataclass(frozen=True)
class ModelResponse:
    content: str
    tool_calls: list[ToolCall] | None = None


class ChatModel:
    def complete(
        self,
        messages: list[Message],
        tools: bool = False,
        extra_tools: list[ExternalToolSpec] | None = None,
    ) -> ModelResponse:
        raise NotImplementedError


class MockModel(ChatModel):
    def complete(
        self,
        messages: list[Message],
        tools: bool = False,
        extra_tools: list[ExternalToolSpec] | None = None,
    ) -> ModelResponse:
        if any(message.content.startswith("Observation from") for message in messages):
            return ModelResponse('{"tool":"finish","args":{"summary":"Mock run completed. Configure a real provider for coding work."}}')
        user_text = "\n".join(message.content for message in messages if message.role == "user")
        if "inspect" in user_text.lower() or "repo" in user_text.lower():
            return ModelResponse('{"tool":"list_files","args":{"path":"."}}')
        return ModelResponse('{"tool":"finish","args":{"summary":"Mock run completed. Configure a real provider for coding work."}}')


class OpenAICompatibleModel(ChatModel):
    def __init__(self, config: ModelConfig) -> None:
        if not config.base_url:
            raise ValueError("base_url is required for openai-compatible provider")
        self.config = config

    def complete(
        self,
        messages: list[Message],
        tools: bool = False,
        extra_tools: list[ExternalToolSpec] | None = None,
    ) -> ModelResponse:
        api_key = os.environ.get(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key environment variable: {self.config.api_key_env}")

        url = self.config.base_url.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if tools:
            payload["tools"] = openai_tool_schemas(extra_tools)
            payload["tool_choice"] = "auto"
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(http_request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        message = data["choices"][0]["message"]
        content = message.get("content") or ""
        tool_calls = _parse_openai_tool_calls(message)
        return ModelResponse(content=content, tool_calls=tool_calls)


class AnthropicModel(ChatModel):
    def __init__(self, config: ModelConfig) -> None:
        if not config.base_url:
            raise ValueError("base_url is required for anthropic provider")
        self.config = config

    def complete(
        self,
        messages: list[Message],
        tools: bool = False,
        extra_tools: list[ExternalToolSpec] | None = None,
    ) -> ModelResponse:
        api_key = os.environ.get(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key environment variable: {self.config.api_key_env}")

        system = "\n".join(message.content for message in messages if message.role == "system")
        chat_messages = [
            {"role": message.role, "content": message.content}
            for message in messages
            if message.role in {"user", "assistant"}
        ]
        payload = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": system,
            "messages": chat_messages,
        }
        if tools:
            payload["tools"] = anthropic_tool_schemas(extra_tools)
        url = self.config.base_url.rstrip("/") + "/v1/messages"
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url,
            data=body,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(http_request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        text_parts = [
            part.get("text", "")
            for part in data.get("content", [])
            if part.get("type") == "text"
        ]
        return ModelResponse(
            content="\n".join(text_parts),
            tool_calls=_parse_anthropic_tool_calls(data),
        )


def build_model(config: ModelConfig) -> ChatModel:
    if config.provider == "mock":
        return MockModel()
    if config.provider == "openai-compatible":
        return OpenAICompatibleModel(config)
    if config.provider == "anthropic":
        return AnthropicModel(config)
    raise ValueError(f"Unsupported provider: {config.provider}")


def _parse_openai_tool_calls(message: dict[str, Any]) -> list[ToolCall] | None:
    raw_calls = message.get("tool_calls") or []
    calls: list[ToolCall] = []
    for raw_call in raw_calls:
        function = raw_call.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments") or "{}"
        if not name:
            continue
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError:
            args = {}
        if not isinstance(args, dict):
            args = {}
        calls.append(ToolCall(name=str(name), args=args))
    return calls or None


def _parse_anthropic_tool_calls(data: dict[str, Any]) -> list[ToolCall] | None:
    calls: list[ToolCall] = []
    for part in data.get("content", []):
        if part.get("type") != "tool_use":
            continue
        name = part.get("name")
        tool_input = part.get("input") or {}
        if not name:
            continue
        if not isinstance(tool_input, dict):
            tool_input = {}
        calls.append(ToolCall(name=str(name), args=tool_input))
    return calls or None
