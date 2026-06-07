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
    "local-openai": ModelConfig(
        provider="openai-compatible",
        base_url="http://localhost:8000",
        model="local-coder",
        api_key_env="LOCAL_MODEL_API_KEY",
    ),
    "vllm": ModelConfig(
        provider="openai-compatible",
        base_url="http://localhost:8000",
        model="local-coder",
        api_key_env="VLLM_API_KEY",
    ),
    "sglang": ModelConfig(
        provider="openai-compatible",
        base_url="http://localhost:30000",
        model="local-coder",
        api_key_env="SGLANG_API_KEY",
    ),
    "ollama": ModelConfig(
        provider="openai-compatible",
        base_url="http://localhost:11434",
        model="qwen2.5-coder:7b",
        api_key_env="OLLAMA_API_KEY",
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
