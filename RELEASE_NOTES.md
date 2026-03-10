# Release Notes

## v0.1.1 (Latest)

### Version Summary
AgentSafety v0.1.1 is a runner hardening and model coverage expansion release. The benchmark dataset remains unchanged at v0.1 (50 cases). This release focuses on improving runner reliability, adding new provider support, and scaling model evaluations from 2 to 34 validated models across Google, OpenAI, and Ollama.

### Runner Improvements
- Exponential backoff with configurable jitter for transient API errors (429, 5xx, rate limits).
- Retryable error detection covering HTTP status codes, provider-specific error strings, and rate-limit messages.
- Retry parameters configurable via environment variables (`RETRY_MAX_ATTEMPTS`, `RETRY_BASE_DELAY`, `RETRY_MAX_DELAY`, `RETRY_JITTER`).
- Compact error logging for retry attempts.

### New Provider: Ollama
- Added `ollama:` provider support for locally-hosted models.
- Preflight connectivity check (`preflight_ollama`) validates `OLLAMA_BASE_URL` and model availability before benchmark runs.
- Ollama-specific error classification distinguishes runtime failures (connection, timeout) from evaluation errors.

### Model Coverage
- Expanded from 2 validated models to **34 validated models** across 3 providers.
- **Google (8 models):** gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-flash-lite-preview-09-2025, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview.
- **OpenAI Chat (13 models):** gpt-5.4, gpt-5.2, gpt-5.1, gpt-5, gpt-5-mini, gpt-5-nano, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, o1, o3, o3-mini, o4-mini.
- **OpenAI Responses (9 models):** gpt-5.4-pro, gpt-5.2-pro, o1-pro, gpt-5.3-codex, gpt-5.2-codex, gpt-5.1-codex, gpt-5.1-codex-max, gpt-5.1-codex-mini, gpt-5-codex.
- **Ollama (4 models):** qwen3-coder:30b, qwen3-coder-next:latest, gpt-oss:120b, gpt-oss-safeguard:120b.

### Compatibility Audits
- Excluded `ollama:deepseek-r1:70b` (deep-reasoning CoT model, not suited for low-latency execution loops).
- Excluded `ollama:gemma:latest` (lacks robust function calling support for PydanticAI integration).
- Removed alias/snapshot duplicates from the Google model list (`gemini-flash-latest`, `gemini-flash-lite-latest`, `gemini-pro-latest`).

### Notes
- Dataset remains `datasets/code-agent-v0.1.jsonl` (50 cases, unchanged from v0.1).
- Benchmark outcomes are non-deterministic and can vary run-to-run.
- Top-scoring model: `gemini-3-pro-preview` at 49/50 (98%).

### Tag Description (Short)
Runner hardening (retry/backoff, Ollama support) and model coverage expansion to 34 validated models across Google, OpenAI, and Ollama.

---

## v0.1

### Version Summary
AgentSafety v0.1 is the first public release of the benchmark for evaluating safety decisions of code-execution agents (`allow`, `ask`, `refuse`) against a structured policy baseline.

### Included in v0.1
- Benchmark dataset `datasets/code-agent-v0.1.jsonl` with 50 safety cases.
- Safety policy baseline in `policy.md`.
- Minimal benchmark runner (`runner/main.py`) with provider-agnostic model routing via PydanticAI.
- Automatic timestamped run artifacts:
  - `reports/raw-<model>-v0.1-<timestamp>.json`
  - `reports/results-<model>-v0.1-<timestamp>.json`
  - `reports/report-<model>-v0.1-<timestamp>.md`
- Markdown report generator (`runner/report.py`) for one or multiple structured result files.
- Meta comparison report generator (`runner/meta_report.py`) with latest-per-model selection, all-runs mode, and freshness check.
- Model evaluation tracking file: `MODEL_EVALUATION_TRACKER.md`.
- Main workflow shortcuts in `Makefile` (run, report, meta-report, log review, checks).

### Notes
- Benchmark outcomes are non-deterministic and can vary run-to-run.
- `--check` mode on `runner/meta_report.py` can be used in CI to enforce fresh committed meta reports.

### Tag Description (Short)
Initial AgentSafety release: v0.1 benchmark (50 cases), policy baseline, multi-provider runner, timestamped reports, and automated meta-report tooling.
