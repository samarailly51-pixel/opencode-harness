from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .eval import EvalCaseResult, EvalReport
from .replay import TraceEvent, load_trace, summarize_trace


@dataclass(frozen=True)
class TraceDiagnosis:
    available: bool
    summary: str
    repeated_tool: str | None = None
    marker_status: str | None = None
    last_tools: tuple[str, ...] = ()
    failed_tools: int = 0
    no_finish_event: bool = False


@dataclass(frozen=True)
class DiagnosisMetrics:
    label: str
    reports: int
    total: int
    passed: int
    failure_types: Counter[str]
    patterns: Counter[str]
    repeated_tail_cases: int
    failed_tool_cases: int
    marker_missing_cases: int
    no_finish_cases: int


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


def compare_diagnosis_reports(
    before_reports: list[EvalReport],
    after_reports: list[EvalReport],
    before_label: str = "Before",
    after_label: str = "After",
) -> str:
    before = _diagnosis_metrics(before_label, before_reports)
    after = _diagnosis_metrics(after_label, after_reports)
    lines = [
        "# Before/After Diagnosis Comparison",
        "",
        "This report compares two sets of OpenCode Harness eval reports and their linked traces.",
        "Use it after an agent-loop, prompt, tool-policy, or provider change to see whether failure modes moved.",
        "",
    ]
    lines.extend(_before_after_snapshot(before, after))
    lines.extend(_counter_delta_section("Failure Type Delta", before.failure_types, after.failure_types))
    lines.extend(_counter_delta_section("Pattern Delta", before.patterns, after.patterns))
    lines.extend(_trace_signal_delta_section(before, after))
    lines.extend(_case_change_section(before_reports, after_reports))
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
        "| Suite | Case | Failure | Finished | Steps | Pattern | Trace Signals | Suggested Next Action |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for report, result in failures:
        trace_diagnosis = _diagnose_trace(result)
        pattern = _infer_pattern(report, result)
        action = _suggest_action(pattern, result, trace_diagnosis)
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
                    _md_escape(trace_diagnosis.summary),
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
    trace_diagnoses = [_diagnose_trace(result) for _, result in failures]
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
    if any(diagnosis.repeated_tool for diagnosis in trace_diagnoses):
        fixes.append(
            "Add loop-break rules for repeated tool calls when the last trace events show the same tool pattern."
        )
    if any(diagnosis.failed_tools for diagnosis in trace_diagnoses):
        fixes.append(
            "Inspect failed tool outputs and permission decisions before treating the result as a pure model failure."
        )
    if any(diagnosis.marker_status == "missing" for diagnosis in trace_diagnoses):
        fixes.append(
            "Treat marker-missing finished cases as finalization failures before changing the task assertions."
        )
    if not fixes:
        fixes.append("Open the trace and session files for each failed case, then add a narrower failure label if needed.")

    lines = ["## Recommended Fixes", ""]
    for index, fix in enumerate(dict.fromkeys(fixes), start=1):
        lines.append(f"{index}. {fix}")
    lines.append("")
    return lines


def _diagnosis_metrics(label: str, reports: list[EvalReport]) -> DiagnosisMetrics:
    failures = [(report, result) for report in reports for result in report.results if not result.ok]
    trace_diagnoses = [_diagnose_trace(result) for _, result in failures]
    return DiagnosisMetrics(
        label=label,
        reports=len(reports),
        total=sum(report.total for report in reports),
        passed=sum(report.passed for report in reports),
        failure_types=Counter(result.failure_type or "unknown" for _, result in failures),
        patterns=Counter(_infer_pattern(report, result) for report, result in failures),
        repeated_tail_cases=sum(1 for diagnosis in trace_diagnoses if diagnosis.repeated_tool),
        failed_tool_cases=sum(1 for diagnosis in trace_diagnoses if diagnosis.failed_tools),
        marker_missing_cases=sum(1 for diagnosis in trace_diagnoses if diagnosis.marker_status == "missing"),
        no_finish_cases=sum(1 for diagnosis in trace_diagnoses if diagnosis.no_finish_event),
    )


def _before_after_snapshot(before: DiagnosisMetrics, after: DiagnosisMetrics) -> list[str]:
    lines = [
        "## Snapshot",
        "",
        "| Label | Reports | Passed | Pass Rate | Failed |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in [before, after]:
        failed = item.total - item.passed
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_escape(item.label),
                    str(item.reports),
                    f"{item.passed}/{item.total}",
                    _rate(item.passed, item.total),
                    str(failed),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Net Change",
            "",
            "| Metric | Before | After | Delta |",
            "| --- | ---: | ---: | ---: |",
            _delta_row("Passed", before.passed, after.passed),
            _delta_row("Failed", before.total - before.passed, after.total - after.passed, lower_is_better=True),
            _rate_delta_row("Pass Rate", _rate_value(before.passed, before.total), _rate_value(after.passed, after.total)),
            "",
        ]
    )
    return lines


def _counter_delta_section(title: str, before: Counter[str], after: Counter[str]) -> list[str]:
    keys = sorted(set(before) | set(after))
    lines = [f"## {title}", ""]
    if not keys:
        lines.extend(["No failures in either report set.", ""])
        return lines
    lines.extend(["| Name | Before | After | Delta |", "| --- | ---: | ---: | ---: |"])
    for key in keys:
        lines.append(_delta_row(f"`{_md_escape(key)}`", before.get(key, 0), after.get(key, 0), lower_is_better=True))
    lines.append("")
    return lines


def _trace_signal_delta_section(before: DiagnosisMetrics, after: DiagnosisMetrics) -> list[str]:
    return [
        "## Trace Signal Delta",
        "",
        "| Signal | Before | After | Delta |",
        "| --- | ---: | ---: | ---: |",
        _delta_row("Repeated tail tool cases", before.repeated_tail_cases, after.repeated_tail_cases, lower_is_better=True),
        _delta_row("Failed-tool cases", before.failed_tool_cases, after.failed_tool_cases, lower_is_better=True),
        _delta_row("Marker-missing cases", before.marker_missing_cases, after.marker_missing_cases, lower_is_better=True),
        _delta_row("No-finish cases", before.no_finish_cases, after.no_finish_cases, lower_is_better=True),
        "",
    ]


def _case_change_section(before_reports: list[EvalReport], after_reports: list[EvalReport]) -> list[str]:
    before_cases = _case_index(before_reports)
    after_cases = _case_index(after_reports)
    case_ids = sorted(set(before_cases) | set(after_cases))
    lines = [
        "## Case Outcome Changes",
        "",
        "| Case | Before | After | Change |",
        "| --- | --- | --- | --- |",
    ]
    for case_id in case_ids:
        before_item = before_cases.get(case_id)
        after_item = after_cases.get(case_id)
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_escape(case_id),
                    _md_escape(_case_status(before_item)),
                    _md_escape(_case_status(after_item)),
                    _md_escape(_case_change(before_item, after_item)),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _case_index(reports: list[EvalReport]) -> dict[str, tuple[EvalReport, EvalCaseResult]]:
    items = {}
    for report in reports:
        for result in report.results:
            items[f"{report.suite}::{result.id}"] = (report, result)
    return items


def _case_status(item: tuple[EvalReport, EvalCaseResult] | None) -> str:
    if item is None:
        return "-"
    report, result = item
    if result.ok:
        return f"PASS ({result.steps} steps)"
    pattern = _infer_pattern(report, result)
    trace = _diagnose_trace(result)
    trace_hint = ""
    if trace.repeated_tool:
        trace_hint = f", repeated={trace.repeated_tool}"
    elif trace.failed_tools:
        trace_hint = f", failed_tools={trace.failed_tools}"
    elif trace.no_finish_event:
        trace_hint = ", no_finish"
    return f"FAIL:{result.failure_type or 'unknown'} / {pattern} ({result.steps} steps{trace_hint})"


def _case_change(
    before_item: tuple[EvalReport, EvalCaseResult] | None,
    after_item: tuple[EvalReport, EvalCaseResult] | None,
) -> str:
    if before_item is None:
        return "added"
    if after_item is None:
        return "removed"
    _, before = before_item
    _, after = after_item
    if not before.ok and after.ok:
        return "fixed"
    if before.ok and not after.ok:
        return "regressed"
    if before.ok and after.ok:
        return "still passing"
    if before.failure_type != after.failure_type:
        return f"failure changed: {before.failure_type or 'unknown'} -> {after.failure_type or 'unknown'}"
    if after.steps < before.steps:
        return "same failure, fewer steps"
    if after.steps > before.steps:
        return "same failure, more steps"
    return "unchanged failure"


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


def _diagnose_trace(result: EvalCaseResult) -> TraceDiagnosis:
    trace_path = Path(result.trace)
    if not trace_path.exists():
        return TraceDiagnosis(available=False, summary="trace unavailable")
    try:
        events = load_trace(trace_path)
    except ValueError:
        return TraceDiagnosis(available=False, summary="trace invalid")
    summary = summarize_trace(events)
    tool_names = _tool_names(events)
    repeated_tool = _repeated_tail_tool(tool_names)
    last_tools = tuple(tool_names[-3:])
    marker_status = _marker_status(events, result.summary)

    signals = [
        f"events={summary.events}",
        f"model_calls={summary.model_calls}",
        f"tool_calls={summary.tool_calls}",
    ]
    if summary.failed_tools:
        signals.append(f"failed_tools={summary.failed_tools}")
    if last_tools:
        signals.append("last_tools=" + " > ".join(last_tools))
    if repeated_tool:
        signals.append(f"repeated_tail={repeated_tool}")
    if marker_status:
        signals.append(f"marker={marker_status}")
    if not summary.finished:
        signals.append("no_finish_event")
    return TraceDiagnosis(
        available=True,
        summary=", ".join(signals),
        repeated_tool=repeated_tool,
        marker_status=marker_status,
        last_tools=last_tools,
        failed_tools=summary.failed_tools,
        no_finish_event=not summary.finished,
    )


def _tool_names(events: list[TraceEvent]) -> list[str]:
    names = []
    for event in events:
        if event.type != "tool.result":
            continue
        tool = event.data.get("tool")
        if tool is not None:
            names.append(str(tool))
    return names


def _repeated_tail_tool(tool_names: list[str]) -> str | None:
    if len(tool_names) < 3:
        return None
    tail = tool_names[-3:]
    if len(set(tail)) == 1:
        return tail[-1]
    return None


def _marker_status(events: list[TraceEvent], summary: str) -> str | None:
    marker = None
    for event in events:
        if event.type != "task.start":
            continue
        value = event.data.get("finish_marker")
        if isinstance(value, str) and value:
            marker = value
    if not marker:
        return None
    return "present" if marker in summary else "missing"


def _suggest_action(pattern: str, result: EvalCaseResult, trace_diagnosis: TraceDiagnosis) -> str:
    if trace_diagnosis.marker_status == "missing":
        return "Inspect whether the final answer satisfied the task but omitted the required finish marker."
    if trace_diagnosis.repeated_tool:
        return f"Review repeated `{trace_diagnosis.repeated_tool}` calls and add a loop-break or synthesis step."
    if trace_diagnosis.failed_tools:
        return "Inspect failed tool outputs before attributing the failure to the model."
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


def _rate(passed: int, total: int) -> str:
    return f"{_rate_value(passed, total):.1f}%"


def _rate_value(passed: int, total: int) -> float:
    return 0.0 if total == 0 else (passed / total) * 100


def _delta_row(label: str, before: int | float, after: int | float, lower_is_better: bool = False, suffix: str = "") -> str:
    delta = after - before
    sign = "+" if delta > 0 else ""
    if isinstance(before, float) or isinstance(after, float):
        before_text = f"{before:.1f}{suffix}"
        after_text = f"{after:.1f}{suffix}"
        delta_text = f"{sign}{delta:.1f}{suffix}"
    else:
        before_text = str(before)
        after_text = str(after)
        delta_text = f"{sign}{delta}"
    if lower_is_better and delta < 0:
        delta_text += " improved"
    elif lower_is_better and delta > 0:
        delta_text += " worse"
    elif not lower_is_better and delta > 0:
        delta_text += " improved"
    elif not lower_is_better and delta < 0:
        delta_text += " worse"
    return f"| {label} | {before_text} | {after_text} | {delta_text} |"


def _rate_delta_row(label: str, before: float, after: float) -> str:
    delta = after - before
    sign = "+" if delta > 0 else ""
    delta_text = f"{sign}{delta:.1f}pp"
    if delta > 0:
        delta_text += " improved"
    elif delta < 0:
        delta_text += " worse"
    return f"| {label} | {before:.1f}% | {after:.1f}% | {delta_text} |"
