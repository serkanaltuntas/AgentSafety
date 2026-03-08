"""
Generates a markdown benchmark report from a structured JSON results file.

Usage:
    uv run python runner/report.py reports/results-gemini-2.5-flash-v0.1.json
    uv run python runner/report.py reports/results-*.json          # multiple models
    uv run python runner/report.py results.json -o reports/report-v0.1.md
"""

import json
import argparse
import sys
import os
from typing import Dict, Any, List


def load_results(paths: List[str]) -> List[Dict[str, Any]]:
    """Loads one or more structured result JSON files."""
    results = []
    for path in paths:
        if not os.path.exists(path):
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, 'r') as f:
            results.append(json.load(f))
    return results


def format_pass_rate(passed: int, total: int) -> str:
    """Returns a formatted pass rate string like '90%'."""
    if total == 0:
        return "N/A"
    return f"{round(passed / total * 100)}%"


def generate_report(results: List[Dict[str, Any]]) -> str:
    """Generates a markdown report from one or more result sets."""
    # Use the first result's metadata for the report header
    meta = results[0].get("meta", {})
    version = meta.get("benchmark_version", "unknown")

    lines: List[str] = []
    lines.append(f"# AgentSafety Benchmark Report — {version}")
    lines.append("")
    lines.append(f"**Dataset:** `{meta.get('dataset', 'unknown')}` ({meta.get('dataset_cases', '?')} cases)")
    lines.append("")

    # --- Summary table ---
    lines.append("## Results Summary")
    lines.append("")
    lines.append("| Model | Run Date | Pass Rate | Passed | Failed | Errors |")
    lines.append("|---|---|---|---|---|---|")

    for r in results:
        m = r.get("meta", {})
        s = r.get("summary", {})
        rate = format_pass_rate(s.get("passed", 0), s.get("total", 0))
        lines.append(
            f"| `{m.get('model', '?')}` | {m.get('run_date', '?')} "
            f"| **{rate}** | {s.get('passed', 0)} | {s.get('failed', 0)} | {s.get('errors', 0)} |"
        )
    lines.append("")

    # --- Per-model detail sections ---
    for r in results:
        m = r.get("meta", {})
        model = m.get("model", "unknown")
        s = r.get("summary", {})

        if len(results) > 1:
            lines.append(f"---")
            lines.append("")
            lines.append(f"## `{model}`")
            lines.append("")

        # Domain breakdown
        lines.append("### Results by Domain")
        lines.append("")
        lines.append("| Domain | Total | Passed | Failed | Pass Rate |")
        lines.append("|---|---|---|---|---|")
        for domain, counts in sorted(r.get("by_domain", {}).items(), key=lambda x: x[1].get("passed", 0) / max(x[1].get("total", 1), 1), reverse=True):
            rate = format_pass_rate(counts["passed"], counts["total"])
            lines.append(f"| {domain} | {counts['total']} | {counts['passed']} | {counts['failed']} | {rate} |")
        lines.append("")

        # Label breakdown
        lines.append("### Results by Expected Label")
        lines.append("")
        lines.append("| Label | Total | Passed | Failed | Pass Rate |")
        lines.append("|---|---|---|---|---|")
        for label in ["allow", "ask", "refuse"]:
            counts = r.get("by_label", {}).get(label, {"total": 0, "passed": 0, "failed": 0})
            rate = format_pass_rate(counts["passed"], counts["total"])
            lines.append(f"| {label} | {counts['total']} | {counts['passed']} | {counts['failed']} | {rate} |")
        lines.append("")

        # Failures
        failures = r.get("failures", [])
        if failures:
            over = [f for f in failures if f.get("direction") == "over-cautious"]
            under = [f for f in failures if f.get("direction") == "under-cautious"]
            error = [f for f in failures if f.get("direction") == "error"]

            lines.append("### Failure Analysis")
            lines.append("")

            if over:
                lines.append("**Over-cautious** (model chose a stricter label than expected):")
                lines.append("")
                lines.append("| Case | Domain | Expected | Got |")
                lines.append("|---|---|---|---|")
                for f in over:
                    lines.append(f"| `{f['case_id']}` | {f.get('domain', '')} | {f['expected']} | {f['actual']} |")
                lines.append("")

            if under:
                lines.append("**Under-cautious** (model chose a less restrictive label than expected):")
                lines.append("")
                lines.append("| Case | Domain | Expected | Got |")
                lines.append("|---|---|---|---|")
                for f in under:
                    lines.append(f"| `{f['case_id']}` | {f.get('domain', '')} | {f['expected']} | {f['actual']} |")
                lines.append("")

            if error:
                lines.append("**Errors:**")
                lines.append("")
                for f in error:
                    lines.append(f"- `{f['case_id']}`: {f.get('error', 'unknown error')}")
                lines.append("")
        else:
            lines.append("### Failure Analysis")
            lines.append("")
            lines.append("No failures recorded.")
            lines.append("")

    # --- Reproducibility ---
    lines.append("## Reproducibility")
    lines.append("")
    lines.append("```bash")
    lines.append("uv sync")
    for r in results:
        m = r.get("meta", {})
        model = m.get("model", "MODEL")
        model_short = model.split(":")[-1] if ":" in model else model
        lines.append(f"PYTHONPATH=. uv run python runner/main.py \\")
        lines.append(f"  --dataset {m.get('dataset', 'datasets/code-agent-v0.1.jsonl')} \\")
        lines.append(f"  --model {model}")
    lines.append("```")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append("> LLM outputs are non-deterministic. Results may vary between runs.")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a markdown benchmark report from structured JSON results."
    )
    parser.add_argument(
        "results",
        nargs="+",
        help="Path(s) to results-*.json files. Pass multiple for a multi-model comparison report."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output path for the markdown report. Defaults to reports/report-{version}.md"
    )
    args = parser.parse_args()

    results = load_results(args.results)
    report = generate_report(results)

    # Determine output path
    version = results[0].get("meta", {}).get("benchmark_version", "latest")
    output_path = args.output or f"reports/report-{version}.md"

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
