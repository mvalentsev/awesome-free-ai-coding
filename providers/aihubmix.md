---
layout: default
title: 'AIHubMix (free models) free tier: limits, free models, verified 2026-09-03'
description: 'One OpenAI-compatible gateway over 800+ models, 56 of which the platform prices at 0 and subsidises itself; both /v1/chat/completions and Anthropic-format /v1/messages are served, so a free id can back Claude Code directly. per-model caps, spelled out in each model''s catalog description: "each…'
permalink: /providers/aihubmix/
---

{% raw %}

# AIHubMix (free models)

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-03 · [aihubmix.com](https://aihubmix.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One OpenAI-compatible gateway over 800+ models, 56 of which the platform prices at 0 and subsidises itself; both /v1/chat/completions and Anthropic-format /v1/messages are served, so a free id can back Claude Code directly

## Free models

`glm-5`, `mimo-v2.5`, `north-mini-code`, `gpt-oss`

## Limits, in the vendor's words

per-model caps, spelled out in each model's catalog description: "each account is limited to 5 requests per minute, 500 requests per day, and 1 million tokens per day" on the GPT and coding routes (read 2026-09-02); the vendor states the quotas reset daily with no trial expiry and no payment method on file. The caveats differ by half of the lane — the GPT rows are "the OpenAI model deployed on Azure" behind Azure's content filter, the Gemini rows are "provided only for trial use; stability cannot be guaranteed, and you may encounter 429 errors", and nemotron-3.5-content-safety-free is a guardrail classifier. Every free id carries a -free suffix and the paid twin beside it is metered at list rates

## Connect

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Callable ids: `coding-glm-5.2-free`, `coding-glm-5.1-free`, `coding-kimi-k3-free`, `kimi-for-coding-free`, `xiaomi-mimo-v2.5-free`, `north-mini-code-free`, `gpt-oss-20b-free`, `ling-3.0-tiny-free`, `nemotron-3-ultra-550b-a55b-free`, `gemma-4-31b-it-free`, `coding-glm-4.6-free`, `coding-glm-4.7-free`, `coding-glm-5-free`, `coding-glm-5-turbo-free`, `coding-glm-5.3-flash-free`, `coding-glm-5.3-free`, `coding-minimax-m2-free`, `coding-minimax-m2.1-free`, `coding-minimax-m2.5-free`, `coding-minimax-m2.7-free`, `coding-minimax-m3-free`, `dots-3-note-preview-free`, `gemini-3-flash-preview-free`, `gemini-3.5-flash-lite-free`, `gemini-3.6-flash-free`, `gemini-3.7-flash-free`, `gemini-3.8-flash-free`, `gemma-4-26b-a4b-it-free`, `glm-4.7-flash-free`, `gpt-4.1-free`, `gpt-4.1-mini-free`, `gpt-4.1-nano-free`, `gpt-4o-free`, `gpt-5.5-free`, `hy3-free`, `k2.6-code-preview-free`, `laguna-s-2.1-free`, `laguna-xs-2.1-free`, `lfm-2.5-2.6b-free`, `ling-3.0-flash-free`, `mimo-v2-flash-free`, `minimax-m2.7-free`, `minimax-m3-free`, `nemotron-3-nano-30b-a3b-free`, `nemotron-3-nano-omni-30b-a3b-reasoning-free`, `nemotron-3-super-120b-a12b-free`, `nemotron-3.5-content-safety-free`, `nemotron-3.5-lightning-free`, `nemotron-nano-12b-v2-vl-free`, `nemotron-nano-9b-v2-free`, `xiaomi-mimo-v2-omni-free`, `xiaomi-mimo-v2-pro-free`, `xiaomi-mimo-v2.5-pro-free`
- Note: every -free id the catalog prices at 0 is listed: 53 on 2026-09-03, 52 the day before — gemini-3.8-flash-free is the one that joined, priced 0 in and out and carrying the same trial-use caveat as the two Gemini Flash rows already here; against ten picked as the coding-relevant half of 49 on 2026-08-14 with the proprietary rows left out as likely to rotate — gpt-5.5-free, gpt-4.1-free and gemini-3.7-flash-free, the three named then, all stood nineteen days later, so the list is now the lane and the probe reports whatever joins or leaves it. Ignored on purpose: gpt-image-2-free and gemini-3.1-flash-image-preview-free generate images, and qwen3.6-plus-preview-free describes itself as "removed from the platform". `model_id` is the callable string; `model_name` beside it is a display title The Claude Code guide verifies the setup with a curl to https://aihubmix.com/v1/messages carrying x-api-key and anthropic-version, so ANTHROPIC_BASE_URL is https://aihubmix.com — a -free id there backs Claude Code on the subsidised lane

## Evidence

- Probe: the models catalog at <https://aihubmix.com/api/v1/models>, free rows carrying `free`, every listed family required at a zero price
- Source: <https://docs.aihubmix.com/en/blogs/free-ai-models>
- Source: <https://aihubmix.com/api/v1/models>
- Source: <https://docs.aihubmix.com/en/api/Claude-Code>

## History

- `2026-08-17` — Added to the list: One OpenAI-compatible gateway over 850+ models, 49 of which the platform prices at 0 and subsidises itself; both /v1/chat/completions and Anthropic-format /v1/messages are served, so a free id can back Claude Code directly

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
