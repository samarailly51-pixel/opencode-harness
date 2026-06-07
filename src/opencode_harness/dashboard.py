from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import os

from .eval import EvalReport, load_eval_report


@dataclass(frozen=True)
class DashboardItem:
    path: Path
    report: EvalReport


def discover_eval_reports(paths: list[Path]) -> list[DashboardItem]:
    candidates: list[Path] = []
    for path in paths:
        if path.is_file():
            candidates.append(path)
        elif path.is_dir():
            report = path / "report.json"
            if report.exists():
                candidates.append(report)
            else:
                candidates.extend(sorted(path.rglob("report.json")))
    seen: set[Path] = set()
    items: list[DashboardItem] = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        items.append(DashboardItem(path=candidate, report=load_eval_report(candidate)))
    return sorted(items, key=lambda item: item.report.started_at, reverse=True)


def render_eval_dashboard(items: list[DashboardItem], output_path: Path | None = None) -> str:
    total_runs = len(items)
    total_cases = sum(item.report.total for item in items)
    total_passed = sum(item.report.passed for item in items)
    total_failed = total_cases - total_passed
    pass_rate = 0 if total_cases == 0 else (total_passed / total_cases) * 100
    rows = []
    for item in items:
        report = item.report
        run_rate = 0 if report.total == 0 else (report.passed / report.total) * 100
        report_html = item.path.with_name("report.html")
        report_link = report_html if report_html.exists() else item.path
        rows.append(
            "<tr>"
            f"<td>{escape(report.started_at)}</td>"
            f"<td>{escape(report.suite)}</td>"
            f"<td>{escape(report.model_provider)}</td>"
            f"<td>{escape(report.model_name)}</td>"
            f"<td class=\"num\">{report.passed}/{report.total}</td>"
            f"<td class=\"num\">{run_rate:.1f}%</td>"
            f"<td>{escape(_failure_breakdown(report))}</td>"
            f"<td><a href=\"{escape(_link(report_link, output_path))}\">report</a></td>"
            "</tr>"
        )
    body = "".join(rows) if rows else "<tr><td colspan=\"8\">No eval reports found.</td></tr>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OpenCode Harness Eval Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #202124; background: #f6f8fb; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px; }}
    h1 {{ margin: 0 0 18px; font-size: 1.8rem; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-bottom: 20px; }}
    .metric {{ background: #fff; border: 1px solid #dfe3ea; border-radius: 8px; padding: 12px; }}
    .metric strong {{ display: block; color: #5f6368; font-size: 0.78rem; text-transform: uppercase; margin-bottom: 4px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #dfe3ea; border-radius: 8px; overflow: hidden; }}
    th, td {{ border-bottom: 1px solid #e8eaed; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #eef3f8; font-weight: 700; }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    a {{ color: #174ea6; }}
  </style>
</head>
<body>
<main>
  <h1>OpenCode Harness Eval Dashboard</h1>
  <section class="metrics">
    <div class="metric"><strong>Runs</strong>{total_runs}</div>
    <div class="metric"><strong>Cases</strong>{total_cases}</div>
    <div class="metric"><strong>Passed</strong>{total_passed}</div>
    <div class="metric"><strong>Failed</strong>{total_failed}</div>
    <div class="metric"><strong>Pass Rate</strong>{pass_rate:.1f}%</div>
  </section>
  <table>
    <thead>
      <tr><th>Started</th><th>Suite</th><th>Provider</th><th>Model</th><th>Passed</th><th>Rate</th><th>Failures</th><th>Report</th></tr>
    </thead>
    <tbody>
      {body}
    </tbody>
  </table>
</main>
</body>
</html>
"""


def write_eval_dashboard(items: list[DashboardItem], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_eval_dashboard(items, output_path=output_path), encoding="utf-8")


def _failure_breakdown(report: EvalReport) -> str:
    counts: dict[str, int] = {}
    for result in report.results:
        if result.ok:
            continue
        failure = result.failure_type or "unknown"
        counts[failure] = counts.get(failure, 0) + 1
    if not counts:
        return "-"
    return ", ".join(f"{name}={count}" for name, count in sorted(counts.items()))


def _link(path: Path, output_path: Path | None) -> str:
    if output_path is None:
        return path.as_posix()
    try:
        return Path(os.path.relpath(path, output_path.parent)).as_posix()
    except ValueError:
        return path.as_posix()
