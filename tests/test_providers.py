import unittest

from opencode_harness.config import ModelConfig
from opencode_harness.providers import apply_preset


class ProviderPresetTests(unittest.TestCase):
    def test_deepseek_preset(self) -> None:
        config = apply_preset("deepseek", ModelConfig(temperature=0.7, max_tokens=99))

        self.assertEqual(config.provider, "openai-compatible")
        self.assertEqual(config.base_url, "https://api.deepseek.com")
        self.assertEqual(config.api_key_env, "DEEPSEEK_API_KEY")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 99)

    def test_local_presets_are_openai_compatible(self) -> None:
        local = apply_preset("local-openai", ModelConfig())
        vllm = apply_preset("vllm", ModelConfig())
        sglang = apply_preset("sglang", ModelConfig())
        ollama = apply_preset("ollama", ModelConfig())

        self.assertEqual(local.provider, "openai-compatible")
        self.assertEqual(local.base_url, "http://localhost:8000")
        self.assertEqual(local.api_key_env, "LOCAL_MODEL_API_KEY")
        self.assertEqual(vllm.api_key_env, "VLLM_API_KEY")
        self.assertEqual(sglang.base_url, "http://localhost:30000")
        self.assertEqual(ollama.base_url, "http://localhost:11434")

    def test_unknown_preset_has_choices(self) -> None:
        with self.assertRaisesRegex(ValueError, "Choices"):
            apply_preset("missing", ModelConfig())
