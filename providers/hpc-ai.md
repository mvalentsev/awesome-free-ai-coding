---
layout: default
title: 'HPC-AI Model APIs free tier: limits, free models, verified 2026-10-05'
description: OpenAI-compatible APIs over 24 models, GLM 5.3 Flash, Kimi K3 and MiniMax M3 among them, with $2 of free credit for every user — $4 with the vendor's invite code — at 5 requests a minute until a first deposit. The invite-code grant is the total signup balance, not an extra amount added to the…
permalink: /providers/hpc-ai/
last_modified_at: 2026-10-05
crumb: HPC-AI Model APIs
---

{% raw %}

# HPC-AI Model APIs free tier

🎁 Trials (no card when possible) · no card · not offered in mainland China · **live** — last verified by a probe on 2026-10-05 · [hpc-ai.com](https://www.hpc-ai.com/model-apis) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible APIs over 24 models, GLM 5.3 Flash, Kimi K3 and MiniMax M3 among them, with $2 of free credit for every user — $4 with the vendor's invite code — at 5 requests a minute until a first deposit

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

Standard signup grant: $2 once per account

Signup grant with invite code: $4 once per account (Use invite code HPCAI-MAPI)

L0 before first deposit: 5 requests/minute per account per model; for `zai-org/glm-5.3-flash`, `moonshotai/kimi-k2.7-code`, `zai-org/glm-5.3`, `deepseek/deepseek-v4-flash`, `anthropic/claude-fable-5`, `anthropic/claude-opus-4.7`, `anthropic/claude-opus-4.8`, `anthropic/claude-opus-5`, `moonshotai/kimi-k3`, `openai/gpt-5.5`, `openai/gpt-oss-120b`, `qwen/qwen3.8-2.4t-a95b`, `qwen/qwen3.8-max`, `zai-org/glm-5.2`, `anthropic/claude-opus-4.6`, `xiaomi/mimo-v2.5-pro`, `xiaomi/mimo-v2.5`, `moonshotai/kimi-k2.6`, `nvidia/nemotron-3-ultra-550b-a55b`, `minimax/minimax-m3`, `qwen/qwen-3.5-397b-a17b`, `qwen/qwen-3.5-35b-a3b`, `qwen/qwen-3.5-27b`

Standard L0 models: 2,000,000 tokens/minute per account per model; for `zai-org/glm-5.3-flash`, `moonshotai/kimi-k2.7-code`, `zai-org/glm-5.3`, `deepseek/deepseek-v4-flash`, `anthropic/claude-fable-5`, `anthropic/claude-opus-4.7`, `anthropic/claude-opus-4.8`, `anthropic/claude-opus-5`, `moonshotai/kimi-k3`, `openai/gpt-5.5`, `openai/gpt-oss-120b`, `qwen/qwen3.8-2.4t-a95b`, `qwen/qwen3.8-max`, `zai-org/glm-5.2`, `xiaomi/mimo-v2.5-pro`, `xiaomi/mimo-v2.5`, `moonshotai/kimi-k2.6`, `nvidia/nemotron-3-ultra-550b-a55b`, `minimax/minimax-m3`, `qwen/qwen-3.5-397b-a17b`, `qwen/qwen-3.5-35b-a3b`, `qwen/qwen-3.5-27b`

L0: Claude Opus 4.6: 10,000,000 tokens/minute per account per model; for `anthropic/claude-opus-4.6`

The invite-code grant is the total signup balance, not an extra amount added to the standard grant; supplies are limited. Credit spends at model list prices. L0 applies before the first deposit; spending alone does not promote an account to L1. Claude Opus 4.6 has a higher token rate than the other positive-RPM L0 models; DeepSeek V4 Pro has zero L0 RPM. No card requirement or credit expiry is published.

## Where it is offered

Not offered in mainland China ([source](https://www.hpc-ai.com/agreement/service), read 2026-09-26). That leaves out 5.9% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “The Services are intended for users outside Mainland China and are not available to individuals or entities located in Mainland China”.

## What happens to what you send

What you send is not used to train models. In the vendor's words: “No customer request data is used for model training unless explicitly agreed otherwise.” ([source](https://www.hpc-ai.com/model-apis)).

## Connect

- Base URL: `https://api.hpc-ai.com/inference/v1`
- Key: `HPC_AI_API_KEY` — get one at <https://www.hpc-ai.com/models-console/api-key>
- Codex CLI: [`configs/codex/hpc-ai.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/hpc-ai.config.toml) — copy it to `~/.codex/`, then `codex -p hpc-ai`; set up on the lane by the vendor's own page, <https://www.hpc-ai.com/doc/docs/Model-APIs/Integration/Codex/>: "Codex CLI and the Codex IDE extension share the same config.toml layers"
- Callable ids: `zai-org/glm-5.3-flash`, `moonshotai/kimi-k2.7-code`, `minimax/minimax-m3`
- Note: ids are the keyless model list's at www.hpc-ai.com/api/maas/v1/models, 2026-09-17, the quick start's own example being moonshotai/kimi-k2.7-code

Try it from your terminal with your key in `HPC_AI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.hpc-ai.com/inference/v1/chat/completions \
  -H "Authorization: Bearer $HPC_AI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"zai-org/glm-5.3-flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.hpc-ai.com/model-apis>, anchored on `Do you offer a free trial for users?` and `in free credits. New accounts using the invite code` in the page's own data; ids checked in <https://www.hpc-ai.com/api/maas/v1/models>
- Source: <https://www.hpc-ai.com/model-apis>
- Source: <https://www.hpc-ai.com/doc/docs/Model-APIs/User-Guides/Rate-Limit/>
- Source: <https://www.hpc-ai.com/doc/docs/Model-APIs/User-Guides/QuickStart/>
- Source: <https://www.hpc-ai.com/api/maas/v1/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: OpenAI-compatible APIs over 24 models, GLM 5.3 Flash, Kimi K3 and MiniMax M3 among them, with $2 of free credit for every user — $4 with the vendor's invite code — at 5 requests a minute until a first deposit

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
