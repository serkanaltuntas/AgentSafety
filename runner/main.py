import json
import argparse
import os
import sys
import asyncio
from datetime import datetime
from typing import Iterator, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

from runner.agent_wrapper import ask_model_for_decision
from runner.report import generate_report

BENCHMARK_VERSION = "v0.1"


def model_slug(model_id: str) -> str:
    """Creates a filesystem-safe model slug for output filenames."""
    base = model_id.split(":")[-1] if ":" in model_id else model_id
    return "".join(c if c.isalnum() or c in "-._" else "-" for c in base)


def is_ollama_model(model_id: str) -> bool:
    """Returns True if the model uses the Ollama provider."""
    return model_id.startswith("ollama:")


def classify_ollama_error(error_text: str) -> str:
    """
    Classifies Ollama errors.

    runtime_unavailable:
        Local runtime/configuration failure that should stop the benchmark immediately.
    evaluation_error:
        Model-level response quality/validation error for a single case.
    """
    text = error_text.lower()
    runtime_markers = (
        "404 page not found",
        "connection refused",
        "cannot connect",
        "operation not permitted",
        "context deadline exceeded",
        "timed out",
        "timeout",
        "broken pipe",
        "connection reset",
        "unexpected eof",
        "insufficient memory",
        "not enough memory",
        "status_code: 500",
        "status_code: 502",
        "status_code: 503",
        "status_code: 504",
    )
    if any(marker in text for marker in runtime_markers):
        return "runtime_unavailable"
    return "evaluation_error"


async def preflight_ollama(model_id: str) -> None:
    """Performs a one-shot check to ensure Ollama is reachable before the benchmark starts."""
    base_url = (os.getenv("OLLAMA_BASE_URL") or "").strip()
    if not base_url:
        raise RuntimeError(
            "OLLAMA_BASE_URL is not set. "
            "Set it to your Ollama OpenAI-compatible endpoint, e.g. http://127.0.0.1:11434/v1."
        )

    prompt = (
        "Connectivity preflight: This is a safe request to classify. "
        "Return the correct safety label."
    )
    try:
        await ask_model_for_decision(model_id, prompt)
    except Exception as e:
        raise RuntimeError(
            f"Ollama preflight failed for model '{model_id}' with OLLAMA_BASE_URL='{base_url}'. "
            f"Underlying error: {e}"
        ) from e


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
            "error": None,
            "error_kind": None,
        }
    except Exception as e:
        error_text = str(e)
        print(f"  [Error] Evaluation failed for case {case.get('id')}: {error_text}", file=sys.stderr)
        error_kind = "evaluation_error"
        if is_ollama_model(model_id):
            error_kind = classify_ollama_error(error_text)
        return {
            "case_id": case.get("id"),
            "domain": case.get("domain"),
            "title": case.get("title"),
            "expected": case.get("expected_label"),
            "actual": None,
            "reasoning": None,
            "passed": False,
            "error": error_text,
            "error_kind": error_kind,
        }


def build_report(
    results: List[Dict[str, Any]],
    model_id: str,
    dataset_path: str,
    run_date: str,
    run_timestamp: str,
) -> Dict[str, Any]:
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
            "run_date": run_date,
            "run_timestamp": run_timestamp,
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
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional raw results path. Defaults to a timestamped file in reports/.",
    )
    parser.add_argument("--model", type=str, default="openai:gpt-5.3-instant", help="The PydanticAI model string (e.g., openai:gpt-5.4, anthropic:claude-4-6-sonnet-latest)")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Error: Dataset not found at {args.dataset}", file=sys.stderr)
        sys.exit(1)

    results: List[Dict[str, Any]] = []
    passed_count = 0
    total_count = 0
    error_count = 0

    if is_ollama_model(args.model):
        print("\nRunning Ollama preflight...")
        try:
            await preflight_ollama(args.model)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            print(
                "Guard triggered: benchmark aborted and no report files were generated.",
                file=sys.stderr,
            )
            sys.exit(2)
        print("Ollama preflight passed.")

    print("\nStarting evaluation...")
    for case in stream_dataset(args.dataset):
        total_count += 1
        result = await evaluate_agent(case, args.model)
        results.append(result)

        if result.get("error"):
            if is_ollama_model(args.model) and result.get("error_kind") == "runtime_unavailable":
                print(
                    f"Error: Ollama runtime failed during case {result.get('case_id')}: "
                    f"{result.get('error')}",
                    file=sys.stderr,
                )
                print(
                    "Guard triggered: benchmark aborted and no report files were generated.",
                    file=sys.stderr,
                )
                sys.exit(2)
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

    run_dt = datetime.now().astimezone()
    run_date = run_dt.date().isoformat()
    run_timestamp = run_dt.isoformat(timespec="seconds")
    ts = run_dt.strftime("%Y%m%d-%H%M%S")
    model_short = model_slug(args.model)

    raw_output_path = args.output or os.path.join(
        "reports",
        f"raw-{model_short}-{BENCHMARK_VERSION}-{ts}.json",
    )
    output_dir = os.path.dirname(raw_output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = "."

    # Save raw results
    with open(raw_output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Raw results saved to {raw_output_path}")

    # Generate and save structured JSON report
    report = build_report(results, args.model, args.dataset, run_date, run_timestamp)
    report_path = os.path.join(
        output_dir,
        f"results-{model_short}-{BENCHMARK_VERSION}-{ts}.json"
    )
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Structured report saved to {report_path}")

    # Generate and save markdown report from this run
    markdown_path = os.path.join(
        output_dir,
        f"report-{model_short}-{BENCHMARK_VERSION}-{ts}.md"
    )
    markdown_report = generate_report([report])
    with open(markdown_path, "w") as f:
        f.write(markdown_report)
    print(f"Markdown report saved to {markdown_path}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(async_main())
