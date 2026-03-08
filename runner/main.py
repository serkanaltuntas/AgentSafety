import json
import argparse
import os

def load_dataset(file_path):
    print(f"Loading dataset from {file_path}...")
    dataset = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    dataset.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping malformed JSON at line {len(dataset) + 1}: {e}")
    return dataset

def evaluate_agent(case):
    # This is a placeholder for the actual agent invocation.
    # In a real scenario, this would format the case 'prompt',
    # invoke the LLM or agent framework, and capture the agent's decision.
    print(f"  [Evaluate] Running case: {case['id']} - {case['title']}")
    
    # Placeholder: Returning unexpected label to simulate test failure initially
    # until a real LLM is hooked up.
    return {
        "case_id": case["id"],
        "expected": case["expected_label"],
        "actual": "unknown",
        "passed": False
    }

def main():
    parser = argparse.ArgumentParser(description="AgentSafety Minimal Benchmark Runner")
    parser.add_argument("--dataset", type=str, required=True, help="Path to the JSONL dataset file")
    parser.add_argument("--output", type=str, default="reports/latest_results.json", help="Path to save the results")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Error: Dataset not found at {args.dataset}")
        return

    dataset = load_dataset(args.dataset)
    print(f"Loaded {len(dataset)} cases.")

    results = []
    passed_count = 0

    print("\nStarting evaluation...")
    for case in dataset:
        result = evaluate_agent(case)
        results.append(result)
        if result["passed"]:
            passed_count += 1
            print(f"  Result: PASS")
        else:
            print(f"  Result: FAIL (Expected: {result['expected']}, Got: {result['actual']})")
    
    print("\n--- Evaluation Summary ---")
    print(f"Total Cases: {len(dataset)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {len(dataset) - passed_count}")

    # Save results
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main()
