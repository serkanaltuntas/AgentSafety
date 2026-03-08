# AgentSafety

AgentSafety is an open project focused on evaluating the safety of autonomous AI agents.

The first focus of this repository is **code-execution agents**:
- When should an agent proceed automatically?
- When should it ask for clarification or approval?
- When should it refuse?

This project aims to create practical, public benchmarks and policy baselines for safer agent behavior.

## Why this exists

AI agents are becoming more capable, but safe behavior is still difficult to measure consistently.

This repository focuses on practical evaluation rather than hype:
- benchmark cases
- simple policy rules
- reproducible evaluation runs
- public failure analysis

The goal is to help developers, researchers, and security-minded builders understand how code-execution agents behave under risky or ambiguous conditions.

## Initial scope

Version 0.1 focuses on code-execution agent safety.

Each benchmark case expects one of three labels:
- `allow` — safe to proceed automatically within defined boundaries
- `ask` — requires clarification or explicit approval
- `refuse` — should not be executed

## Threat areas covered

The first benchmark set focuses on cases involving:
- prompt injection
- tool misuse
- secret exposure
- destructive actions
- writes outside the workspace
- unauthorized network access
- unsafe persistence
- ambiguous requests that should trigger clarification

## Repository structure

```text
agentsafety/
├─ README.md
├─ policy.md
├─ CONTRIBUTING.md
├─ schemas/
│  └─ case.schema.json
├─ datasets/
│  └─ code-agent-v0.1.jsonl
├─ runner/
│  └─ ...
└─ reports/
   └─ ...
