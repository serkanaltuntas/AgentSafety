# AgentSafety

**AgentSafety** is an open benchmark project for evaluating whether autonomous code agents make safe decisions: `allow`, `ask`, or `refuse`. 

Created and maintained by [Serkan Altuntas](https://github.com/serkanaltuntas), this project focuses on a practical problem in AI: measuring the safety posture of code-execution agents. 

Rather than chasing generalized "safe superintelligence," AgentSafety provides a concrete, operational decision framework, public refusal/approval baselines, and reproducible failure reports.

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
├─ LICENSE                  # Apache 2.0 License
├─ schemas/
│  └─ case.schema.json      # JSON Schema for benchmark cases
├─ datasets/
│  └─ code-agent-v0.1.jsonl # Active benchmark dataset
├─ runner/
│  └─ main.py               # Minimal evaluation script
└─ reports/                 # Templates and outputs from evaluation runs
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
Use the minimal runner to evaluate an agent against the active dataset. Using `uv run` ensures it runs in the isolated project environment:
```bash
uv run python runner/main.py --dataset datasets/code-agent-v0.1.jsonl --output reports/latest_results.json
```
_Note: The initial `runner/main.py` is a skeleton meant to be integrated with your custom LLM framework (e.g., LangChain, AutoGen, or raw API calls). See `CONTRIBUTING.md` for our roadmap on expanding the runner capabilities._

## 🤝 Contributing

We are looking for high-quality, realistic risk scenarios for code-execution agents. 

We choose **better cases over more cases**. Please refer to the [Contributing Validation Guidelines](CONTRIBUTING.md) to understand how you can submit new benchmark challenges.

---
_AgentSafety is an open project by Serkan Altuntas. Licensed under the Apache License 2.0._
