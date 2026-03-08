.PHONY: help sync run run-default run-model run-openai-gpt54 run-anthropic-sonnet46 run-gemini-pro run-ollama report report-latest report-all review-logs meta-report meta-report-all meta-report-check check test clean-generated

PYTHONPATH ?= .
UV_RUN ?= uv run
DATASET ?= datasets/code-agent-v0.1.jsonl
MODEL ?= openai:gpt-5.3-instant
RESULTS_GLOB ?= reports/results-*.json
RAW_LOG ?=

help:
	@echo "AgentSafety main commands"
	@echo ""
	@echo "Setup"
	@echo "  make sync"
	@echo ""
	@echo "Benchmark runs"
	@echo "  make run-default"
	@echo "  make run-model MODEL=<vendor:model-id> [DATASET=<path>]"
	@echo "  make run-openai-gpt54"
	@echo "  make run-anthropic-sonnet46"
	@echo "  make run-gemini-pro"
	@echo "  make run-ollama"
	@echo ""
	@echo "Reports"
	@echo "  make report-latest"
	@echo "  make report-all"
	@echo "  make review-logs [RAW_LOG=<reports/raw-...json>]"
	@echo "  make meta-report"
	@echo "  make meta-report-all"
	@echo "  make meta-report-check"
	@echo ""
	@echo "Validation"
	@echo "  make check"
	@echo "  make test"
	@echo ""
	@echo "Cleanup"
	@echo "  make clean-generated"

sync:
	$(UV_RUN) sync

run: run-default

run-default:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/main.py --dataset $(DATASET)

run-model:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/main.py --dataset $(DATASET) --model $(MODEL)

run-openai-gpt54:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/main.py --dataset $(DATASET) --model openai:gpt-5.4

run-anthropic-sonnet46:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/main.py --dataset $(DATASET) --model anthropic:claude-sonnet-4-6

run-gemini-pro:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/main.py --dataset $(DATASET) --model google-gla:gemini-3.1-pro-preview

run-ollama:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/main.py --dataset $(DATASET) --model ollama:llama3.1

report: report-latest

report-latest:
	@latest_file=$$(ls -1t reports/results-*.json 2>/dev/null | head -n 1); \
	if [ -z "$$latest_file" ]; then \
		echo "No structured results found under reports/results-*.json"; \
		exit 1; \
	fi; \
	echo "Using $$latest_file"; \
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/report.py "$$latest_file"

report-all:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/report.py $(RESULTS_GLOB)

review-logs:
	@raw_file="$(RAW_LOG)"; \
	if [ -z "$$raw_file" ]; then \
		raw_file=$$(ls -1t reports/raw-*.json 2>/dev/null | head -n 1); \
	fi; \
	if [ -z "$$raw_file" ]; then \
		echo "No raw logs found under reports/raw-*.json"; \
		exit 1; \
	fi; \
	echo "Using $$raw_file"; \
	jq '.[] | select(.passed == false) | {case_id, title, expected, actual, reasoning, error}' "$$raw_file"

meta-report:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/meta_report.py

meta-report-all:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/meta_report.py --all-runs

meta-report-check:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/meta_report.py --check

check:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python -m py_compile runner/main.py runner/report.py runner/meta_report.py
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python runner/meta_report.py --check

test:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) pytest -q

clean-generated:
	rm -f reports/raw-*.json reports/results-*.json reports/report-*.md reports/meta-report.md
