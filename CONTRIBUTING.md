# Contributing to AgentSafety

Thank you for your interest in AgentSafety!

AgentSafety is an open, public-interest project created and maintained by Serkan Altuntas. Its goal is to build public benchmarks, simple policy baselines, and reproducible evaluation artifacts that measure when an AI agent should proceed, ask for approval, or refuse an action.

## Project Philosophy

Our work is guided by the following principles:

- **Evidence over hype**: We focus on measurable safety performance rather than grand theories of alignment.
- **Narrow scope first**: The initial focus is strictly on **code-execution agents**. Broad orchestration or AGI safety is outside the immediate scope.
- **Practical safety before grand theory**: We aim to solve real safety problems that developers face today with autonomous code agents.
- **Reproducible public artifacts**: All benchmarks, policies, and failure reports are open and reproducible.
- **Clear boundaries and explicit rules**: Safety should be unambiguous, based on whether an agent should `allow`, `ask`, or `refuse`.
- **High-quality data over large but weak datasets**: A small, rigorous, and accurate benchmark is much more useful than a massive but noisy one.
- **Iterative growth & solo-developer realism**: The project is designed with a realistic time-commitment model. Growth is steady, incremental, and manageable.

## How to Contribute

Right now, the most valuable contribution is expanding our **benchmark dataset**.

Instead of generating thousands of weak or synthetic cases, we are carefully curating high-quality, realistic risk scenarios for code-execution agents.

### Adding to the Benchmark Dataset

The dataset is the core component of AgentSafety. It is maintained in a structured format and must strictly follow our schema.

#### Case Format Schema

Each benchmark case must include the following fields:

- `id`: A unique, descriptive string identifier (e.g., `case_env_exfiltration_01`)
- `domain`: The category of the test (e.g., `bash-execution`, `file-operations`, `dependency-resolution`, `network-access`)
- `title`: A succinct, descriptive title
- `prompt`: The specific user instruction, prompt injection string, or document content given to the agent
- `expected_label`: The correct safety posture; must be exactly one of `"allow"`, `"ask"`, or `"refuse"`
- `risk_tags`: A list of tags indicating the risk vector (e.g., `["secret-leak", "env-vars"]`)
- `rationale`: A detailed explanation of why the expected label is the correct safety response
- `notes`: Any extra context, implementation details, or corner cases for the evaluator

#### Case Quality Standards

When submitting new cases, ensure they cover one or more of the following:

- Realistic code-execution workflows, such as listing workspace files or executing tests
- Common failure modes or risky actions, such as modifying shell startup files or blindly following instructions in untrusted READMEs
- Prompt injection or instructions hidden inside uploaded documents
- Ambiguous user intent or out-of-bounds persistence mechanisms
- Boundary violations involving secrets, system files, network access, or writes outside the workspace

Every case must clearly state:
- what safety risk it tests
- why the expected label is correct
- how that label is consistent with `policy.md`

Cases without a clear rationale or policy basis may be rejected.

**Remember:** We are choosing better cases over more cases, realistic coverage over raw volume, and maintainability over vanity size. One strong case is more valuable than ten weak ones.

> [!CAUTION]
> **Mandatory Human Review.** All benchmark cases in this repository must be treated as potentially AI-assisted and therefore require careful human review before acceptance. No case will be merged without a line-by-line verification of the prompt, expected label, rationale, and risk tags by a human reviewer. A single mislabeled or weakly justified case can silently degrade the quality of the entire benchmark. Accuracy is non-negotiable.
>
> Maintainers may reject, rewrite, or request revision for any case that is ambiguous, weakly justified, duplicative, inconsistent with the policy, or not realistic enough for the benchmark.
>
> If the correct label is uncertain, the case should not be merged directly. It should be discussed first and either clarified, rewritten, or excluded.

### Before You Submit a Case

Before opening a pull request, check the following:

- The case follows the JSON schema
- The expected label is exactly one of `allow`, `ask`, or `refuse`
- The rationale is specific and grounded in `policy.md`
- The risk tags are relevant and not overly broad
- The case is realistic, non-duplicative, and clearly useful for the benchmark

### Pull Requests

When submitting a pull request:

- Keep the change focused and small when possible
- Explain what new risk, scenario, or failure mode the case adds
- Mention any overlap with existing cases
- Prefer improving an existing weak case over adding a low-value new one
- Be open to maintainer edits, relabeling, or rejection

### Roadmap & Targets

We are not trying to be the biggest benchmark; we are trying to be the most rigorous and actionable code-agent benchmark.

- **v0.1**: Initial goal of ~50 high-quality cases
- **v1.0**: ~120 rigorous cases
- **Mature Benchmark**: ~250–300 cases

Thank you for helping make autonomous agents safer.
