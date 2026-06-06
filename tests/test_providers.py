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

    def test_unknown_preset_has_choices(self) -> None:
        with self.assertRaisesRegex(ValueError, "Choices"):
            apply_preset("missing", ModelConfig())
