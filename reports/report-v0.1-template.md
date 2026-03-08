# AgentSafety Evaluation Report v0.1

**Date:** YYYY-MM-DD
**Evaluator/Agent Tested:** [e.g., CodeAgent-v1.2, Base GPT-4 Setup, etc.]
**Dataset:** `datasets/code-agent-v0.1.jsonl`

## Summary

- **Total Cases Executed:** 0
- **Total Passed:** 0 (0%)
- **Total Failed:** 0 (0%)

## Benchmark Breakdown

| Domain | Total | Passed | Failed | Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| `bash-execution` | 0 | 0 | 0 | 0% |
| `file-operations` | 0 | 0 | 0 | 0% |
| `dependency-resolution`| 0 | 0 | 0 | 0% |
| `network-access` | 0 | 0 | 0 | 0% |
| `credential-access` | 0 | 0 | 0 | 0% |
| `prompt-injection` | 0 | 0 | 0 | 0% |

## Detailed Failure Analysis

*(Provide a qualitative breakdown of why the agent failed certain tasks. What were its blind spots? Did it falsely `allow` destructive actions or falsely `refuse` safe local actions?)*

### False `allow` (Safety Breaches)
- **`case_id`**: Description of what the agent did instead of asking/refusing.

### False `ask` (Overly Cautious)
- **`case_id`**: Description of why the agent hesitated on a safe workflow.

### False `refuse` (Workflow Blockers)
- **`case_id`**: Description of why the agent refused a legitimate `allow` or `ask` action.

## Reproducibility Notes
- **System Prompt Used:** [Insert minimal system prompt]
- **Environment:** [e.g., Docker container with simulated project]
- **API Versions:** [e.g., anthropics/claude-3-opus-20240229]
