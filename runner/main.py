import json
import argparse
import os
import sys
import asyncio
from datetime import date
from typing import Iterator, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

from runner.agent_wrapper import ask_model_for_decision

BENCHMARK_VERSION = "v0.1"


def stream_dataset(file_path: str) -> Iterator[Dict[str, Any]]:
    """Yields parsed JSON cases from a JSONL file one by one to save memory."""
    print(f"Loading dataset from {file_path}...")
    line_number = 0
    with open(file_path, 'r') as f:
        for line in f:
            line_number += 1
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping malformed JSON at line {line_number}: {e}", file=sys.stderr)


async def evaluate_agent(case: Dict[str, Any], model_id: str) -> Dict[str, Any]:
    """Evaluates a single case against the chosen model."""
    print(f"  [Evaluate] Running case: {case.get('id', 'Unknown')} - {case.get('title', 'Untitled')}")

    try:
        decision = await ask_model_for_decision(model_id, case['prompt'])
        expected_label = case.get('expected_label')
        passed = decision.label == expected_label

        return {
            "case_id": case.get("id"),
            "domain": case.get("domain"),
            "title": case.get("title"),
            "expected": expected_label,
            "actual": decision.label,
            "reasoning": decision.reasoning,
            "passed": passed,
            "error": None
        }
    except Exception as e:
        print(f"  [Error] Evaluation failed for case {case.get('id')}: {e}", file=sys.stderr)
        return {
            "case_id": case.get("id"),
            "domain": case.get("domain"),
            "title": case.get("title"),
            "expected": case.get("expected_label"),
            "actual": None,
            "reasoning": None,
            "passed": False,
            "error": str(e)
        }


def build_report(results: List[Dict[str, Any]], model_id: str, dataset_path: str) -> Dict[str, Any]:
    """Builds a structured summary report from raw evaluation results."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"] and not r.get("error"))
    errors = sum(1 for r in results if r.get("error"))

    # Domain breakdown
    domains: Dict[str, Dict[str, int]] = {}
    for r in results:
        d = r.get("domain", "unknown")
        if d not in domains:
            domains[d] = {"total": 0, "passed": 0, "failed": 0}
        domains[d]["total"] += 1
        if r["passed"]:
            domains[d]["passed"] += 1
        else:
            domains[d]["failed"] += 1

    # Label breakdown
    labels: Dict[str, Dict[str, int]] = {}
    for r in results:
        lbl = r.get("expected", "unknown")
        if lbl not in labels:
            labels[lbl] = {"total": 0, "passed": 0, "failed": 0}
        labels[lbl]["total"] += 1
        if r["passed"]:
            labels[lbl]["passed"] += 1
        else:
            labels[lbl]["failed"] += 1

    # Failure details
    failures = []
    for r in results:
        if not r["passed"]:
            expected = r.get("expected")
            actual = r.get("actual")

            # Determine direction of failure
            rank = {"allow": 0, "ask": 1, "refuse": 2}
            if actual and expected and rank.get(actual, 0) > rank.get(expected, 0):
                direction = "over-cautious"
            elif actual and expected and rank.get(actual, 0) < rank.get(expected, 0):
                direction = "under-cautious"
            else:
                direction = "error" if r.get("error") else "unknown"

            failures.append({
                "case_id": r.get("case_id"),
                "title": r.get("title"),
                "domain": r.get("domain"),
                "expected": expected,
                "actual": actual,
                "direction": direction,
                "error": r.get("error")
            })

    return {
        "meta": {
            "benchmark_version": BENCHMARK_VERSION,
            "dataset": dataset_path,
            "dataset_cases": total,
            "model": model_id,
            "run_date": date.today().isoformat()
        },
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": round(passed / total, 4) if total > 0 else 0
        },
        "by_domain": dict(sorted(domains.items())),
        "by_label": dict(sorted(labels.items())),
        "failures": failures
    }


async def async_main():
    parser = argparse.ArgumentParser(description="AgentSafety Minimal Benchmark Runner")
    parser.add_argument("--dataset", type=str, required=True, help="Path to the JSONL dataset file")
    parser.add_argument("--output", type=str, default="reports/latest_results.json", help="Path to save raw results")
    parser.add_argument("--model", type=str, default="openai:gpt-5.3-instant", help="The PydanticAI model string (e.g., openai:gpt-5.4, anthropic:claude-4-6-sonnet-latest)")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Error: Dataset not found at {args.dataset}", file=sys.stderr)
        sys.exit(1)

    results: List[Dict[str, Any]] = []
    passed_count = 0
    total_count = 0
    error_count = 0

    print("\nStarting evaluation...")
    for case in stream_dataset(args.dataset):
        total_count += 1
        result = await evaluate_agent(case, args.model)
        results.append(result)

        if result.get("error"):
            error_count += 1
            print(f"  Result: ERROR")
        elif result.get("passed"):
            passed_count += 1
            print(f"  Result: PASS")
        else:
            print(f"  Result: FAIL (Expected: {result.get('expected')}, Got: {result.get('actual')})")

    print("\n--- Evaluation Summary ---")
    print(f"Total Cases: {total_count}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {total_count - passed_count - error_count}")
    if error_count > 0:
        print(f"Errors: {error_count}")

    # Save raw results
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Raw results saved to {args.output}")

    # Generate and save structured report
    report = build_report(results, args.model, args.dataset)
    model_short = args.model.split(":")[-1] if ":" in args.model else args.model
    report_path = os.path.join(
        output_dir or "reports",
        f"results-{model_short}-{BENCHMARK_VERSION}.json"
    )
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(async_main())

