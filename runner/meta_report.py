"""
Generates a markdown meta report by comparing structured benchmark result files.

Usage:
    PYTHONPATH=. uv run python runner/meta_report.py
    PYTHONPATH=. uv run python runner/meta_report.py --all-runs
    PYTHONPATH=. uv run python runner/meta_report.py \
      --results-glob "reports/results-*.json" \
      --output reports/meta-report.md
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


TIMESTAMP_RE = re.compile(r"-(\d{8}-\d{6})\.json$")
EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)


@dataclass
class ResultBundle:
    path: str
    model: str
    run_time: datetime
    payload: Dict[str, Any]


def parse_run_time(payload: Dict[str, Any], path: str) -> datetime:
    """Parses a run timestamp from payload metadata with filename fallback."""
    meta = payload.get("meta", {})

    run_ts = meta.get("run_timestamp")
    if isinstance(run_ts, str) and run_ts:
        try:
            dt = datetime.fromisoformat(run_ts)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    run_date = meta.get("run_date")
    if isinstance(run_date, str) and run_date:
        try:
            dt = datetime.fromisoformat(run_date)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    match = TIMESTAMP_RE.search(path)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y%m%d-%H%M%S").replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    return EPOCH_UTC


def load_bundles(paths: List[str]) -> List[ResultBundle]:
    """Loads result files and converts them into sortable bundles."""
    bundles: List[ResultBundle] = []
    for path in paths:
        with open(path, "r") as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            print(f"Warning: Skipping non-object report: {path}", file=sys.stderr)
            continue
        model = payload.get("meta", {}).get("model", "unknown")
        run_time = parse_run_time(payload, path)
        bundles.append(ResultBundle(path=path, model=model, run_time=run_time, payload=payload))
    return bundles


def choose_latest_per_model(bundles: List[ResultBundle]) -> List[ResultBundle]:
    """Selects the most recent run per model ID."""
    latest: Dict[str, ResultBundle] = {}
    for b in bundles:
        current = latest.get(b.model)
        if current is None or b.run_time > current.run_time:
            latest[b.model] = b
    return list(latest.values())


def pct(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "N/A"
    return f"{(numerator / denominator) * 100:.1f}%"


def format_run_time(bundle: ResultBundle) -> str:
    meta = bundle.payload.get("meta", {})
    run_ts = meta.get("run_timestamp")
    if isinstance(run_ts, str) and run_ts:
        return run_ts
    run_date = meta.get("run_date")
    if isinstance(run_date, str) and run_date:
        return run_date
    if bundle.run_time != EPOCH_UTC:
        return bundle.run_time.isoformat(timespec="seconds")
    return "unknown"


def failure_posture_counts(bundle: ResultBundle) -> Tuple[int, int, int]:
    failures = bundle.payload.get("failures", [])
    over = sum(1 for f in failures if f.get("direction") == "over-cautious")
    under = sum(1 for f in failures if f.get("direction") == "under-cautious")
    error = sum(1 for f in failures if f.get("direction") == "error")
    return over, under, error


def build_meta_report(
    selected: List[ResultBundle],
    all_paths: List[str],
    latest_only: bool,
    max_case_rows: int,
    datasets: List[str],
    benchmark_versions: List[str],
) -> str:
    selected_sorted = sorted(
        selected,
        key=lambda b: (
            -(b.payload.get("summary", {}).get("pass_rate", 0)),
            b.model,
        ),
    )

    domains = sorted(
        {
            domain
            for b in selected_sorted
            for domain in b.payload.get("by_domain", {}).keys()
        }
    )

    lines: List[str] = []
    lines.append("# AgentSafety Meta Report")
    lines.append("")
    snapshot_time = max((b.run_time for b in selected_sorted), default=EPOCH_UTC)
    snapshot_label = (
        snapshot_time.isoformat(timespec="seconds")
        if snapshot_time != EPOCH_UTC
        else "unknown"
    )
    lines.append(f"Data snapshot time: `{snapshot_label}`")
    lines.append(f"Selection mode: `{'latest per model' if latest_only else 'all runs'}`")
    lines.append(f"Source files scanned: `{len(all_paths)}`")
    lines.append(f"Result sets compared: `{len(selected_sorted)}`")
    lines.append("")

    if not selected_sorted:
        lines.append("No structured results found. Run benchmark first.")
        lines.append("")
        return "\n".join(lines)

    if len(datasets) == 1:
        lines.append(f"Dataset: `{datasets[0]}`")
    else:
        lines.append("Datasets:")
        for dataset in datasets:
            lines.append(f"- `{dataset}`")
    if len(benchmark_versions) == 1:
        lines.append(f"Benchmark version: `{benchmark_versions[0]}`")
    else:
        lines.append("Benchmark versions:")
        for version in benchmark_versions:
            lines.append(f"- `{version}`")
    lines.append("")

    # Global comparison
    lines.append("## Model Comparison")
    lines.append("")
    lines.append("| Rank | Model | Run Time | Pass Rate | Passed | Failed | Errors |")
    lines.append("|---|---|---|---|---|---|---|")
    for idx, b in enumerate(selected_sorted, start=1):
        summary = b.payload.get("summary", {})
        lines.append(
            f"| {idx} | `{b.model}` | {format_run_time(b)} | "
            f"**{pct(summary.get('passed', 0), summary.get('total', 0))}** | "
            f"{summary.get('passed', 0)} | {summary.get('failed', 0)} | {summary.get('errors', 0)} |"
        )
    lines.append("")

    # Safety posture comparison
    lines.append("## Safety Posture Comparison")
    lines.append("")
    lines.append("| Model | Over-cautious | Under-cautious | Error Failures |")
    lines.append("|---|---|---|---|")
    for b in selected_sorted:
        over, under, err = failure_posture_counts(b)
        lines.append(f"| `{b.model}` | {over} | {under} | {err} |")
    lines.append("")

    # Domain comparison
    lines.append("## Domain Pass Rates")
    lines.append("")
    header = "| Model | " + " | ".join(domains) + " |"
    sep = "|---|" + "---|" * len(domains)
    lines.append(header)
    lines.append(sep)
    for b in selected_sorted:
        by_domain = b.payload.get("by_domain", {})
        domain_cells: List[str] = []
        for domain in domains:
            stats = by_domain.get(domain, {})
            cell = pct(stats.get("passed", 0), stats.get("total", 0))
            domain_cells.append(cell)
        lines.append(f"| `{b.model}` | " + " | ".join(domain_cells) + " |")
    lines.append("")

    # Repeated failure cases across compared models
    fail_counter: Counter[str] = Counter()
    fail_details: Dict[str, Dict[str, Any]] = {}
    for b in selected_sorted:
        for f in b.payload.get("failures", []):
            case_id = f.get("case_id")
            if not case_id:
                continue
            fail_counter[case_id] += 1
            fail_details.setdefault(case_id, f)

    repeated = [(case, count) for case, count in fail_counter.items() if count > 1]
    repeated.sort(key=lambda item: (-item[1], item[0]))

    lines.append("## Repeated Failure Cases")
    lines.append("")
    if repeated:
        lines.append("| Case ID | Domain | Expected | Count |")
        lines.append("|---|---|---|---|")
        for case_id, count in repeated[:max_case_rows]:
            info = fail_details.get(case_id, {})
            lines.append(
                f"| `{case_id}` | {info.get('domain', '')} | "
                f"{info.get('expected', '')} | {count} |"
            )
    else:
        lines.append("No repeated failure cases across compared model runs.")
    lines.append("")

    # Source traceability
    lines.append("## Included Result Files")
    lines.append("")
    for b in sorted(selected, key=lambda x: x.path):
        lines.append(f"- `{b.path}`")
    lines.append("")

    lines.append("> [!NOTE]")
    lines.append("> This file is auto-generated from `reports/results-*.json`. Do not edit manually.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a meta comparison markdown report from benchmark result JSON files."
    )
    parser.add_argument(
        "--results-glob",
        type=str,
        default="reports/results-*.json",
        help="Glob pattern for structured result files.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/meta-report.md",
        help="Output markdown path.",
    )
    parser.add_argument(
        "--all-runs",
        action="store_true",
        help="Compare all matching runs. Default is latest run per model.",
    )
    parser.add_argument(
        "--max-repeated-cases",
        type=int,
        default=10,
        help="Maximum repeated failure cases to list.",
    )
    parser.add_argument(
        "--allow-mixed",
        action="store_true",
        help="Allow comparing multiple datasets/benchmark versions in one report.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether output file is up to date without writing changes.",
    )
    args = parser.parse_args()

    all_paths = sorted(glob.glob(args.results_glob))
    bundles = load_bundles(all_paths)
    selected = bundles if args.all_runs else choose_latest_per_model(bundles)

    datasets = sorted(
        {
            str(b.payload.get("meta", {}).get("dataset", "unknown"))
            for b in selected
        }
    )
    benchmark_versions = sorted(
        {
            str(b.payload.get("meta", {}).get("benchmark_version", "unknown"))
            for b in selected
        }
    )

    if not args.allow_mixed and (len(datasets) > 1 or len(benchmark_versions) > 1):
        print(
            "Error: Mixed datasets or benchmark versions detected. "
            "Use --allow-mixed if this is intentional.",
            file=sys.stderr,
        )
        print(f"Datasets: {datasets}", file=sys.stderr)
        print(f"Benchmark versions: {benchmark_versions}", file=sys.stderr)
        sys.exit(1)

    markdown = build_meta_report(
        selected=selected,
        all_paths=all_paths,
        latest_only=(not args.all_runs),
        max_case_rows=args.max_repeated_cases,
        datasets=datasets,
        benchmark_versions=benchmark_versions,
    )

    if args.check:
        if not os.path.exists(args.output):
            print(f"Meta report is missing: {args.output}", file=sys.stderr)
            sys.exit(1)
        with open(args.output, "r") as f:
            current = f.read()
        if current != markdown:
            print(
                f"Meta report is stale: {args.output}\n"
                f"Run: PYTHONPATH=. uv run python runner/meta_report.py",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Meta report is up to date: {args.output}")
        return

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w") as f:
        f.write(markdown)

    print(f"Meta report written to {args.output}")


if __name__ == "__main__":
    main()
