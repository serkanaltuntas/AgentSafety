# AgentSafety

**AgentSafety** is an open benchmark for evaluating whether autonomous code agents make safe decisions: `allow`, `ask`, or `refuse`.

Created and maintained by [Serkan Altuntas](https://github.com/serkanaltuntas), this project focuses on a practical problem in AI: measuring the safety posture of code-execution agents.

Rather than chasing generalized "safe superintelligence," AgentSafety provides a concrete, operational decision framework, public refusal/approval baselines, and reproducible failure reports.

## 📊 Latest Findings Snapshot

- Meta comparison report (committed): [`reports/meta-report.md`](reports/meta-report.md)
- Model inventory/tracker: [`MODEL_EVALUATION_TRACKER.md`](MODEL_EVALUATION_TRACKER.md)
- Refresh via script only:
  ```bash
  PYTHONPATH=. uv run python runner/meta_report.py
  ```
- Verify it is up-to-date before commit:
  ```bash
  PYTHONPATH=. uv run python runner/meta_report.py --check
  ```

---

## 🚀 The Core Idea

A capable AI agent is not useful unless it can make safe decisions.

Instead of scoring an agent solely on "did it complete the task?", AgentSafety scores it on whether it chose the correct safety posture. The benchmark uses three straightforward labels:
- **`allow`**: The action is safe to proceed automatically within defined boundaries.
- **`ask`**: The action may be legitimate, but requires clarification or explicit approval (e.g., installing third-party packages).
- **`refuse`**: The action crosses a clear safety boundary and should not be executed (e.g., executing prompt injection, modifying global system files).

Read our full framework in the [Safety Policy Baseline](policy.md).

## 🛡️ Addressed Risk Vectors

Version 0.1 of our benchmark dataset (`datasets/code-agent-v0.1.jsonl`) tests agents against:
- Prompt injection & instructions hidden inside uploaded documents
- Tool misuse and destructive file operations
- Secret exposure and credential access
- Arbitrary code execution (`curl | bash`)
- Writing outside the workspace boundary
- Modification of critical system profiles (`.bashrc`, SSH configs)
- Ambiguous user intent
- Execution of untrusted dependencies

## 📂 Repository Structure

```text
agentsafety/
├─ README.md                # Project Overview & Setup
├─ policy.md                # Safety Boundaries & Decision Model
├─ CONTRIBUTING.md          # Project Philosophy & Contribution Guide
├─ MODEL_EVALUATION_TRACKER.md # Vendor/model coverage checklist
├─ LICENSE                  # Apache 2.0 License
├─ schemas/
│  └─ case.schema.json      # JSON Schema for benchmark cases
├─ datasets/
│  └─ code-agent-v0.1.jsonl # Active benchmark dataset
├─ runner/
│  ├─ main.py               # Benchmark execution script
│  └─ meta_report.py        # Aggregates saved result JSONs into a meta markdown report
└─ reports/                 # Templates and generated evaluation outputs
   ├─ meta-report.md        # Committed cross-run comparison report
   └─ report-v0.1-template.md
```

## 🛠️ Setup & Execution

To run the AgentSafety benchmark locally and test an autonomous agent, follow these steps:

### 1. Prerequisites
- Python 3.10+
- (Optional but Recommended) A Docker environment or isolated Sandbox VM for safe agent execution.

### 2. Installation
Clone the repository and install the dependencies using [uv](https://docs.astral.sh/uv/), the extremely fast Python package and project manager:
```bash
git clone https://github.com/serkanaltuntas/agentsafety.git
cd agentsafety

# Install dependencies and sync the environment
uv sync
```

### 3. Environment Configuration
Copy the sample environment file and add the necessary API keys for the agents/models you intend to test:
```bash
cp .env.example .env
# Edit .env and supply OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.
```

### 4. Running the Benchmark
AgentSafety uses [PydanticAI](https://ai.pydantic.dev/) as its evaluation wrapper, meaning you can plug and play almost any major LLM provider without writing new integration code.

Use the minimal runner to evaluate an agent against the active dataset. Using `uv run` ensures it runs in the isolated project environment. By default, it runs `openai:gpt-5.3-instant`.

Each run now writes **three timestamped artifacts** to `reports/` automatically:
- `raw-<model>-<benchmark>-<timestamp>.json`
- `results-<model>-<benchmark>-<timestamp>.json`
- `report-<model>-<benchmark>-<timestamp>.md`

**Examples for different models:**

```bash
# Test OpenAI (Default)
uv run python runner/main.py --dataset datasets/code-agent-v0.1.jsonl

# Test OpenAI with a specific model (GPT-5.4)
uv run python runner/main.py --dataset datasets/code-agent-v0.1.jsonl --model openai:gpt-5.4

# Test Anthropic (Claude 4.6 Sonnet)
uv run python runner/main.py --dataset datasets/code-agent-v0.1.jsonl --model anthropic:claude-sonnet-4-6

# Test Google Gemini 3.1 Pro (preview model id)
uv run python runner/main.py --dataset datasets/code-agent-v0.1.jsonl --model google-gla:gemini-3.1-pro-preview

# Test a Local Model via Ollama (No API Key Required)
uv run python runner/main.py --dataset datasets/code-agent-v0.1.jsonl --model ollama:llama3.1
```
_Note: Ensure the corresponding API key (e.g., `OPENAI_API_KEY`, `GEMINI_API_KEY`) is present in your `.env` file before running cloud models._

### 5. Generating the Meta Comparison Report
After one or more benchmark runs, generate (or refresh) the committed markdown meta report:

```bash
PYTHONPATH=. uv run python runner/meta_report.py
```

Optional: compare all historical runs instead of latest-per-model only:

```bash
PYTHONPATH=. uv run python runner/meta_report.py --all-runs
```

Optional: enforce freshness in CI/pre-commit (fails if `reports/meta-report.md` is stale):

```bash
PYTHONPATH=. uv run python runner/meta_report.py --check
```

## 🤝 Contributing

We are looking for high-quality, realistic risk scenarios for code-execution agents.

We choose **better cases over more cases**. Please refer to the [Contributing Validation Guidelines](CONTRIBUTING.md) to understand how you can submit new benchmark challenges.

---
_AgentSafety is an open project by Serkan Altuntas. Licensed under the Apache License 2.0._
