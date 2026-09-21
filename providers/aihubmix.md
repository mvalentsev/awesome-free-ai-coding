---
layout: default
title: 'AIHubMix (free models) free tier: limits, free models, verified 2026-09-17'
description: One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code. per-model caps, spelled out in each model's catalog…
permalink: /providers/aihubmix/
---

{% raw %}

# AIHubMix (free models)

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-17; the probe since has not found that evidence, and 3 misses in a row archive the row · [aihubmix.com](https://aihubmix.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

## Free models

`glm-5.3`

## Limits, in the vendor's words

per-model caps, spelled out in each model's catalog description: "each account is limited to 5 requests per minute, 500 requests per day, and 1 million tokens per day" on the GPT and coding routes (read 2026-09-02); the vendor states the quotas reset daily with no trial expiry and no payment method on file. The caveats differ by half of the lane — the GPT rows are "the OpenAI model deployed on Azure" behind Azure's content filter, the Gemini rows are "provided only for trial use; stability cannot be guaranteed, and you may encounter 429 errors", and nemotron-3.5-content-safety-free is a guardrail classifier. Every free id carries a -free suffix and the paid twin beside it is metered at list rates

## Connect

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Callable ids: `coding-glm-5.2-free`, `coding-glm-5.1-free`, `coding-kimi-k3-free`, `kimi-for-coding-free`, `xiaomi-mimo-v2.5-free`, `north-mini-code-free`, `gpt-oss-20b-free`, `ling-3.0-tiny-free`, `nemotron-3-ultra-550b-a55b-free`, `agents-a1-free`, `coding-glm-4.6-free`, `coding-glm-4.7-free`, `coding-glm-5-free`, `coding-glm-5-turbo-free`, `coding-glm-5.3-flash-free`, `coding-glm-5.3-free`, `coding-minimax-m2-free`, `coding-minimax-m2.1-free`, `coding-minimax-m2.5-free`, `coding-minimax-m2.7-free`, `coding-minimax-m3-free`, `dots-3-note-preview-free`, `gemini-3.8-flash-free`, `glm-4.7-flash-free`, `gpt-4.1-free`, `gpt-4.1-mini-free`, `gpt-4.1-nano-free`, `gpt-4o-free`, `gpt-5.5-free`, `hy3-free`, `intern-s2-free`, `k2.6-code-preview-free`, `laguna-s-2.1-free`, `laguna-xs-2.1-free`, `lfm-2.5-2.6b-free`, `ling-3.0-flash-free`, `mimo-v2-flash-free`, `minimax-m2.7-free`, `nemotron-3-nano-30b-a3b-free`, `nemotron-3-nano-omni-30b-a3b-reasoning-free`, `nemotron-3-super-120b-a12b-free`, `nemotron-3.5-content-safety-free`, `nemotron-3.5-lightning-free`, `nemotron-nano-12b-v2-vl-free`, `nemotron-nano-9b-v2-free`, `union-alpha-free`, `xiaomi-mimo-v2-omni-free`, `xiaomi-mimo-v2-pro-free`, `xiaomi-mimo-v2.5-pro-free`, `ox-alpha`
- Note: every id the catalog prices at 0 is listed or ignored on purpose, 54 rows on 2026-09-18; free ids carry a -free suffix beside a metered twin. ox-alpha is a codename the catalog resolves: "This model actually points to glm-5.3-flash". Ignored: gpt-image-2-free generates images, jina-ocr-v1 parses page images into Markdown, qwen3.6-plus-preview-free says it was "removed from the platform", and gpt-live-transcribe is speech-to-text. For Claude Code, ANTHROPIC_BASE_URL is https://aihubmix.com, as its Claude Code guide sets it

## Evidence

- Probe: the models catalog at <https://aihubmix.com/api/v1/models>, free rows carrying `free`, every listed family required at a zero price
- Source: <https://docs.aihubmix.com/en/blogs/free-ai-models>
- Source: <https://aihubmix.com/api/v1/models>
- Source: <https://docs.aihubmix.com/en/api/Claude-Code>

## History

- `2026-09-21` — Free models changed: dropped glm-5, gpt-oss, kimi-k3, mimo-v2.5, north-mini-code
- `2026-09-17` — Free models changed: added glm-5.3, kimi-k3
- `2026-08-17` — Added to the list: One OpenAI-compatible gateway over 850+ models, 49 of which the platform prices at 0 and subsidises itself; both /v1/chat/completions and Anthropic-format /v1/messages are served, so a free id can back Claude Code directly

---

Generated from `registry.yaml` on 2026-09-21 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
