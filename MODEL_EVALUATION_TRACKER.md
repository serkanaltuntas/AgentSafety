# AgentSafety Model Evaluation Tracker

Public checklist for tracking which model IDs are evaluated in AgentSafety.

## Model Selection Strategy

This tracker includes models that are a practical fit for autonomous code-execution benchmarking.

Include models that are:
- General-purpose for code/text reasoning in iterative agent loops
- Suitable for low-latency, multi-step tool-driven workflows
- Available through the current runner integration path used by this project
  - OpenAI chat-compatible IDs use `openai:<model-id>`.
  - OpenAI responses-only IDs use `openai-responses:<model-id>`.

Exclude models that are:
- Specialized for deep-research/report-generation workflows rather than execution loops
- Primarily image/video/audio generation models
- Primarily embedding/retrieval-only models
- Deprecated, legacy, or ChatGPT-only models that are not supported for API benchmarking
- Specialized tool-bound models (for example: computer-use-only/search-only variants)
- Models that are not executable through either supported runner path (`openai:` or `openai-responses:`)

Enforcement process (applied on each vendor update):
1. Start from official vendor model catalogs.
2. Keep only general text/code models suitable for autonomous execution loops.
3. Remove excluded classes above (specialized media/research/retrieval/tool-bound/deprecated).
4. Track only the resulting rule-compliant models in this file.

Vendor ID policy:
1. Prefer canonical public API IDs from official vendor docs.
2. Use one primary ID per model line to avoid alias/snapshot duplicates.
3. Use dated snapshot IDs only when the vendor does not provide a stable alias.

Status guide:
- `[x]` validated in this repo with saved run artifacts
- `[ ]` planned / not yet validated

Last updated: 2026-03-09

## Google

- [x] `google-gla:gemini-2.5-flash` (validated, 44/50 on 2026-03-08)
- [x] `google-gla:gemini-3.1-pro-preview` (validated, 48/50 on 2026-03-08)
- [ ] `google-gla:gemini-2.5-pro`
- [ ] `google-gla:gemini-flash-latest`
- [ ] `google-gla:gemini-flash-lite-latest`
- [ ] `google-gla:gemini-pro-latest`
- [ ] `google-gla:gemini-2.5-flash-lite`
- [ ] `google-gla:gemini-2.5-flash-lite-preview-09-2025`
- [ ] `google-gla:gemini-3-pro-preview`
- [ ] `google-gla:gemini-3-flash-preview`
- [ ] `google-gla:gemini-3.1-flash-lite-preview`

Excluded after compatibility audit (2026-03-08):
- `google-gla:gemini-2.0-flash`
- `google-gla:gemini-2.0-flash-001`
- `google-gla:gemini-2.0-flash-lite-001`
- `google-gla:gemini-2.0-flash-lite`
  - Reason: no longer available to new users (404 from vendor API).
- `google-gla:gemma-3-1b-it`
- `google-gla:gemma-3-4b-it`
- `google-gla:gemma-3-12b-it`
- `google-gla:gemma-3-27b-it`
- `google-gla:gemma-3n-e4b-it`
- `google-gla:gemma-3n-e2b-it`
  - Reason: function calling not enabled, so they are not runnable with current structured-output runner path.

## OpenAI

Chat-compatible IDs (`openai:`):
- [x] `openai:gpt-5.4` (validated, 45/50 on 2026-03-08)
- [ ] `openai:gpt-5.2`
- [ ] `openai:gpt-5.1`
- [ ] `openai:gpt-5`
- [ ] `openai:gpt-5-mini`
- [ ] `openai:gpt-5-nano`
- [ ] `openai:gpt-4.1`
- [ ] `openai:gpt-4.1-mini`
- [ ] `openai:gpt-4.1-nano`
- [ ] `openai:o3`
- [ ] `openai:o4-mini`
- [ ] `openai:o3-mini`
- [ ] `openai:o1`

Responses-compatible IDs (`openai-responses:`):
- [ ] `openai-responses:gpt-5.4-pro` (endpoint probe OK on 2026-03-08)
- [ ] `openai-responses:gpt-5.2-pro` (endpoint probe OK on 2026-03-08)
- [ ] `openai-responses:o1-pro` (endpoint probe OK on 2026-03-08)
- [ ] `openai-responses:gpt-5.3-codex` (endpoint probe OK on 2026-03-08)
- [ ] `openai-responses:gpt-5.2-codex` (endpoint probe OK on 2026-03-08)
- [ ] `openai-responses:gpt-5.1-codex` (endpoint probe OK on 2026-03-08)
- [ ] `openai-responses:gpt-5.1-codex-max` (endpoint probe OK on 2026-03-08)
- [ ] `openai-responses:gpt-5.1-codex-mini` (endpoint probe OK on 2026-03-08)
- [ ] `openai-responses:gpt-5-codex` (endpoint probe OK on 2026-03-08)

Excluded after compatibility audit (2026-03-08):
- `openai:o3-pro` (requires verified OpenAI organization in current account; model access is gated)

## Anthropic

- [ ] `anthropic:claude-sonnet-4-6`
- [ ] `anthropic:claude-opus-4-6`
- [ ] `anthropic:claude-sonnet-4-5`
- [ ] `anthropic:claude-haiku-4-5`
- [ ] `anthropic:claude-opus-4-5-20251101`

Audit note (2026-03-08): compatibility probe could not classify Anthropic models in this environment because the configured Anthropic API key returned `401 invalid x-api-key`.

## Ollama

Runtime compatibility note:
- This repo works with Ollama through PydanticAI when `OLLAMA_BASE_URL` is set to `http://127.0.0.1:11434/v1`.
- Verified end-to-end on 2026-03-09 using `ollama:qwen3-coder:30b`.

Benchmark-relevant coding models (`ollama:`):
- [ ] `ollama:qwen3-coder-next:latest` (coding-specialized family)
- [ ] `ollama:qwen3-coder:30b` (coding-specialized family)
- [ ] `ollama:gpt-oss:120b` (coding-capable generalist)

## Other Vendors

- [ ] Add vendor model inventory
