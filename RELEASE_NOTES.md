# Release Notes

## v0.1 (Latest)

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
