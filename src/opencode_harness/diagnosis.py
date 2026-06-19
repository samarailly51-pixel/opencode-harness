from __future__ import annotations

from collections import Counter

from .eval import EvalCaseResult, EvalReport


def diagnose_eval_reports(reports: list[EvalReport]) -> str:
    lines = [
        "# Failure-Mode Diagnosis",
        "",
        "This report summarizes failed eval cases from existing OpenCode Harness `report.json` files.",
        "It is intended for agent-loop debugging, provider comparison, and product-facing case studies.",
        "",
    ]
    if not reports:
        lines.extend(["No eval reports were provided.", ""])
        return "\n".join(lines)

    lines.extend(_snapshot_table(reports))
    failures = [(report, result) for report in reports for result in report.results if not result.ok]
    if not failures:
        lines.extend(["## Summary", "", "No failed eval cases were found.", ""])
        return "\n".join(lines)

    lines.extend(_failure_breakdown_section(failures))
    lines.extend(_case_diagnostics_section(failures))
    lines.extend(_recommended_fixes_section(failures))
    return "\n".join(lines).rstrip() + "\n"


def _snapshot_table(reports: list[EvalReport]) -> list[str]:
    lines = [
        "## Report Snapshot",
        "",
        "| Suite | Provider | Model | Passed | Pass Rate | Failed Cases |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for report in reports:
        pass_rate = 0 if report.total == 0 else (report.passed / report.total) * 100
        failed = report.total - report.passed
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_escape(report.suite),
                    _md_escape(report.model_provider),
                    _md_escape(report.model_name),
                    f"{report.passed}/{report.total}",
                    f"{pass_rate:.1f}%",
                    str(failed),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _failure_breakdown_section(failures: list[tuple[EvalReport, EvalCaseResult]]) -> list[str]:
    counts = Counter(result.failure_type or "unknown" for _, result in failures)
    lines = ["## Failure Type Breakdown", "", "| Failure Type | Count |", "| --- | ---: |"]
    for failure_type, count in sorted(counts.items()):
        lines.append(f"| `{_md_escape(failure_type)}` | {count} |")
    lines.append("")
    return lines


def _case_diagnostics_section(failures: list[tuple[EvalReport, EvalCaseResult]]) -> list[str]:
    lines = [
        "## Case Diagnostics",
        "",
        "| Suite | Case | Failure | Finished | Steps | Pattern | Suggested Next Action |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for report, result in failures:
        pattern = _infer_pattern(report, result)
        action = _suggest_action(pattern, result)
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_escape(report.suite),
                    _md_escape(result.id),
                    f"`{_md_escape(result.failure_type or 'unknown')}`",
                    str(result.finished),
                    str(result.steps),
                    _md_escape(pattern),
                    _md_escape(action),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _recommended_fixes_section(failures: list[tuple[EvalReport, EvalCaseResult]]) -> list[str]:
    failure_types = {result.failure_type or "unknown" for _, result in failures}
    patterns = {_infer_pattern(report, result) for report, result in failures}
    fixes = []
    if "expectation_mismatch" in failure_types:
        fixes.append(
            "Separate marker-missing failures from genuinely wrong answers by inspecting the final summary and trace."
        )
        fixes.append(
            "Keep the eval finish marker visible in the task and after tool observations so models know when to close."
        )
    if "max_steps" in failure_types:
        fixes.append(
            "Inspect the last two tool calls before increasing `max_steps`; if enough evidence exists, tighten the finish policy."
        )
    if "verification_failure" in failure_types:
        fixes.append(
            "Surface verifier stdout/stderr in the task loop and require the agent to rerun verification before finishing."
        )
    if any("Repair" in pattern for pattern in patterns):
        fixes.append(
            "For repair tasks, prefer copied fixture workspaces, explicit test commands, and a required pass marker."
        )
    if any("Long-context" in pattern for pattern in patterns):
        fixes.append(
            "For long-context tasks, split evidence gathering from synthesis and reduce unrelated repository context."
        )
    if not fixes:
        fixes.append("Open the trace and session files for each failed case, then add a narrower failure label if needed.")

    lines = ["## Recommended Fixes", ""]
    for index, fix in enumerate(dict.fromkeys(fixes), start=1):
        lines.append(f"{index}. {fix}")
    lines.append("")
    return lines


def _infer_pattern(report: EvalReport, result: EvalCaseResult) -> str:
    failure_type = result.failure_type or "unknown"
    suite_case = f"{report.suite} {result.id}".lower()
    summary = result.summary.lower()
    text = f"{suite_case} {summary}"
    if failure_type == "max_steps":
        return "Tool-loop overrun / missing finalization"
    if failure_type == "verification_failure":
        return "Verification failure after attempted repair"
    if failure_type == "tool_failure":
        return "Unrecovered tool failure"
    if failure_type == "recovered_tool_failure":
        return "Recovered tool error"
    if failure_type == "exception":
        return "Runtime exception"
    if failure_type == "expectation_mismatch":
        if "repair" in suite_case or any(token in summary for token in ["fixed", "patched", "applied patch"]):
            return "Repair finalization gap"
        if any(token in suite_case for token in ["long-context", "long context", "repo-wide", "cross-file"]):
            return "Long-context synthesis or marker drift"
        return "Finish-marker drift"
    return "Unclassified failure"


def _suggest_action(pattern: str, result: EvalCaseResult) -> str:
    if pattern.startswith("Tool-loop"):
        return "Review the final trace events and add stronger finish pressure before raising step budget."
    if pattern.startswith("Verification"):
        return "Expose verifier output to the agent and rerun the case with write permissions enabled."
    if pattern.startswith("Unrecovered tool"):
        return "Check permission policy, workspace path, and tool arguments in the trace."
    if pattern.startswith("Recovered tool"):
        return "Keep the pass but inspect whether retries hide a provider/tool schema issue."
    if pattern.startswith("Runtime"):
        return "Fix the exception path before comparing model quality."
    if pattern.startswith("Repair"):
        return "Require test rerun evidence and a final pass marker in the finish summary."
    if pattern.startswith("Long-context"):
        return "Reduce context noise or split the task into evidence and synthesis phases."
    if result.finished:
        return "Check whether the summary missed only the marker or missed the task requirement."
    return "Open trace and session artifacts for manual triage."


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")
