from __future__ import annotations

from dataclasses import replace

from .config import ModelConfig


PRESETS: dict[str, ModelConfig] = {
    "mock": ModelConfig(provider="mock", model="mock-coder"),
    "deepseek": ModelConfig(
        provider="openai-compatible",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        api_key_env="DEEPSEEK_API_KEY",
    ),
    "qwen": ModelConfig(
        provider="openai-compatible",
        base_url="https://dashscope.aliyuncs.com/compatible-mode",
        model="qwen-plus",
        api_key_env="DASHSCOPE_API_KEY",
    ),
    "openai": ModelConfig(
        provider="openai-compatible",
        base_url="https://api.openai.com",
        model="gpt-4.1",
        api_key_env="OPENAI_API_KEY",
    ),
    "claude": ModelConfig(
        provider="anthropic",
        base_url="https://api.anthropic.com",
        model="claude-sonnet-4-5",
        api_key_env="ANTHROPIC_API_KEY",
    ),
}


def apply_preset(name: str, current: ModelConfig) -> ModelConfig:
    try:
        preset = PRESETS[name]
    except KeyError as error:
        choices = ", ".join(sorted(PRESETS))
        raise ValueError(f"Unknown preset: {name}. Choices: {choices}") from error
    return replace(
        preset,
        temperature=current.temperature,
        max_tokens=current.max_tokens,
    )
