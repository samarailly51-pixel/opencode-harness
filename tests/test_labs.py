from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from opencode_harness.config import AgentConfig, HarnessConfig, ModelConfig, PermissionConfig
from opencode_harness.eval import load_eval_suite
from opencode_harness.labs import run_provider_comparison


class LabTests(unittest.TestCase):
    def test_deepseek_v4_suite_is_valid_utf8_json(self) -> None:
        name, cases = load_eval_suite(Path("model-labs/deepseek/deepseek-v4-suite.json"))

        self.assertEqual(name, "deepseek v4 coding-agent smoke")
        self.assertIn("中文总结", cases[-1].task)
        self.assertEqual(cases[-1].expect_contains, "模型")

    def test_deepseek_long_context_suite_is_valid(self) -> None:
        name, cases = load_eval_suite(Path("model-labs/deepseek/deepseek-v4-long-context-suite.json"))

        self.assertEqual(name, "deepseek v4 long-context suite")
        self.assertEqual(len(cases), 4)
        self.assertIn("LONG_CONTEXT_SUMMARY", cases[0].expect_contains or "")
        self.assertIn("LONG_CONTEXT_ZH", cases[-1].task)
        self.assertEqual(cases[-1].expect_contains, "LONG_CONTEXT_ZH")

    def test_deepseek_long_context_prompt_manifest_matches_suite(self) -> None:
        _, cases = load_eval_suite(Path("model-labs/deepseek/deepseek-v4-long-context-suite.json"))
        case_ids = {case.id for case in cases}
        prompts = json.loads(Path("model-labs/deepseek/prompts/long-context.json").read_text(encoding="utf-8"))

        linked_cases = {prompt["suite_case"] for prompt in prompts["prompts"]}

        self.assertEqual(linked_cases, case_ids)

    def test_deepseek_repair_suite_uses_workspace_templates_and_verify_commands(self) -> None:
        name, cases = load_eval_suite(Path("model-labs/deepseek/deepseek-v4-repair-suite.json"))

        self.assertEqual(name, "deepseek v4 coding-agent repair suite")
        self.assertEqual({case.id for case in cases}, {"repair-calculator", "repair-text-utils"})
        self.assertTrue(all(case.workspace_template for case in cases))
        self.assertTrue(all(case.verify_command == "python -m unittest discover -s tests -t ." for case in cases))
        self.assertEqual(cases[0].expect_contains, "REPAIR_CALCULATOR_PASS")

    def test_deepseek_coding_prompt_manifest_links_repair_cases(self) -> None:
        _, cases = load_eval_suite(Path("model-labs/deepseek/deepseek-v4-repair-suite.json"))
        case_ids = {case.id for case in cases}
        prompts = json.loads(Path("model-labs/deepseek/prompts/coding.json").read_text(encoding="utf-8"))
        linked_cases = {
            prompt["suite_case"]
            for prompt in prompts["prompts"]
            if "suite_case" in prompt
        }

        self.assertTrue(case_ids.issubset(linked_cases))

    def test_qwen_coding_suite_is_valid_utf8_json(self) -> None:
        name, cases = load_eval_suite(Path("model-labs/qwen/qwen-coding-agent-suite.json"))

        self.assertEqual(name, "qwen coding-agent suite")
        self.assertEqual(len(cases), 4)
        self.assertEqual(cases[0].expect_contains, "QWEN_TOOL_STABILITY")
        self.assertIn("中文总结", cases[-1].task)
        self.assertEqual(cases[-1].expect_contains, "QWEN_ZH_SUMMARY")

    def test_qwen_prompt_manifest_matches_suite(self) -> None:
        _, cases = load_eval_suite(Path("model-labs/qwen/qwen-coding-agent-suite.json"))
        case_ids = {case.id for case in cases}
        prompts = json.loads(Path("model-labs/qwen/prompts/coding.json").read_text(encoding="utf-8"))

        linked_cases = {prompt["suite_case"] for prompt in prompts["prompts"]}

        self.assertEqual(linked_cases, case_ids)

    def test_qwen_lab_is_listed_in_readme(self) -> None:
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("model-labs/qwen/README.md", readme)

    def test_run_provider_comparison_writes_comparison_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "repo").mkdir()
            suite = root / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "name": "lab smoke",
                        "cases": [
                            {
                                "id": "inspect",
                                "task": "inspect this repo",
                                "workspace": "repo",
                                "expect_contains": "Mock run completed",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            config = HarnessConfig(
                model=ModelConfig(provider="mock"),
                agent=AgentConfig(max_steps=2, context_chars=1000),
                permissions=PermissionConfig(),
            )
            comparison = root / "reports" / "provider-comparison.md"

            with patch.dict("os.environ", {}, clear=True):
                result = run_provider_comparison(
                    suite,
                    ["mock", "deepseek"],
                    config,
                    root / "eval-runs",
                    comparison,
                )

            self.assertTrue(comparison.exists())
            self.assertTrue(comparison.with_suffix(".json").exists())
            self.assertEqual(len(result.reports), 1)
            self.assertEqual(result.skipped[0].preset, "deepseek")
            markdown = comparison.read_text(encoding="utf-8")
            self.assertIn("lab smoke", markdown)
            self.assertIn("Skipped Providers", markdown)
            manifest = json.loads(comparison.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["skipped"][0]["reason"], "missing DEEPSEEK_API_KEY")
