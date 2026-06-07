from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import os

from .config import HarnessConfig
from .eval import EvalReport, compare_eval_reports, run_eval_suite
from .providers import PRESETS, apply_preset


@dataclass(frozen=True)
class SkippedProvider:
    preset: str
    reason: str


@dataclass(frozen=True)
class ProviderComparisonResult:
    suite: str
    reports: list[str]
    comparison: str
    skipped: list[SkippedProvider]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


def run_provider_comparison(
    suite_path: Path,
    presets: list[str],
    config: HarnessConfig,
    output_dir: Path,
    comparison_output: Path,
    skip_missing_keys: bool = True,
) -> ProviderComparisonResult:
    reports: list[EvalReport] = []
    report_paths: list[str] = []
    skipped: list[SkippedProvider] = []
    for preset in presets:
        model = apply_preset(preset, config.model)
        if skip_missing_keys and model.provider != "mock" and not os.environ.get(model.api_key_env):
            skipped.append(SkippedProvider(preset=preset, reason=f"missing {model.api_key_env}"))
            continue
        run_config = HarnessConfig(
            model=model,
            agent=config.agent,
            permissions=config.permissions,
            mcp_tools=config.mcp_tools,
            mcp_servers=config.mcp_servers,
        )
        report = run_eval_suite(suite_path, run_config, output_dir, run_label=preset)
        reports.append(report)
        report_paths.append(_report_path(report))

    comparison_output.parent.mkdir(parents=True, exist_ok=True)
    markdown = _render_provider_comparison(reports, skipped)
    comparison_output.write_text(markdown, encoding="utf-8")
    manifest = ProviderComparisonResult(
        suite=str(suite_path),
        reports=report_paths,
        comparison=str(comparison_output),
        skipped=skipped,
    )
    comparison_output.with_suffix(".json").write_text(manifest.to_json(), encoding="utf-8")
    return manifest


def _render_provider_comparison(reports: list[EvalReport], skipped: list[SkippedProvider]) -> str:
    lines: list[str] = []
    if reports:
        lines.append(compare_eval_reports(reports).rstrip())
    else:
        lines.extend(["# Eval Report Comparison", "", "No provider runs were executed."])
    if skipped:
        lines.extend(["", "## Skipped Providers", "", "| Preset | Reason |", "| --- | --- |"])
        for item in skipped:
            lines.append(f"| {item.preset} | {item.reason} |")
    return "\n".join(lines).rstrip() + "\n"


def _report_path(report: EvalReport) -> str:
    if not report.results:
        return ""
    return str(Path(report.results[0].trace).parent / "report.json")
