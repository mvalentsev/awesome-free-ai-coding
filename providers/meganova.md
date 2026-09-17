---
layout: default
title: 'MegaNova free tier: limits, free models, verified 2026-09-17'
description: OpenAI-compatible gateway whose no-card Tier 1 account gets 50 free requests a day on each of Mistral Small 3.2 and the house Manta routers — 550 a day across its free rows. Tier 1 is "Free registration — no credit card required", with "Free Access Models (<100B), including Manta Mini". The Free…
permalink: /providers/meganova/
---

{% raw %}

# MegaNova

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-17 · [meganova.ai](https://meganova.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway whose no-card Tier 1 account gets 50 free requests a day on each of Mistral Small 3.2 and the house Manta routers — 550 a day across its free rows

## Free models

`mistral-small-3.2`

## Limits, in the vendor's words

Tier 1 is "Free registration — no credit card required", with "Free Access Models (<100B), including Manta Mini". The Free Model Quota table gives a Tier 1 account 50 requests a day ("50 RPD (Requests Per Day)") on each of Mistral-Small-3.2-24B, Manta Mini and Manta Flash, and on several roleplay fine-tunes, an embedding model and a reranker — "Total Free Quota per day 550", with a "daily reset at 00:00 UTC" — and 0 on GLM-4.7-Flash and Manta Pro until a "$1 deposit" moves the account to Tier 2. The terms say "Free modules are for evaluation and interactive use only and are not designed for production or unattended batch workloads". The operator is Nebula Nova Inc., a Delaware corporation. Read 2026-09-16

## Connect

- Base URL: `https://api.meganova.ai/v1`
- Key: `MEGANOVA_API_KEY` — get one at <https://www.meganova.ai/api-keys>
- Callable ids: `mistralai/Mistral-Small-3.2-24B-Instruct-2506`, `meganova-ai/manta-mini-1.0`, `meganova-ai/manta-flash-1.0`
- Note: the three ids listed are the chat rows a Tier 1 account can call for free; ten more zero-priced rows are ignored on purpose — zai-org/GLM-4.7-Flash and manta-pro-1.0 have a Tier 1 quota of 0, faster-whisper, Qwen3-Embedding-8B and bge-reranker-v2-m3 are not chat models, and five are roleplay fine-tunes (four of Llama, one of Mistral NeMo). Manta Mini and Manta Flash are MegaNova's own routers, tagged best_role_play in the catalog, so Mistral Small 3.2, at 8,192 tokens of context, is the one named coding model on the lane

## Evidence

- Probe: the models catalog at <https://api.meganova.ai/v1/models>, every listed family required at a zero price
- Source: <https://docs.meganova.ai/free-model-quota>
- Source: <https://docs.meganova.ai/tiers/tier-1.md>
- Source: <https://docs.meganova.ai/legal-docs/terms-of-service.md>
- Source: <https://api.meganova.ai/v1/models>

## History

- `2026-09-03` — Added to the list: OpenAI-compatible gateway whose no-card Tier 1 account gets a daily free quota on Mistral Small 3.2 and the house Manta routers — 50 a day per model, 550 across the lane

---

Generated from `registry.yaml` on 2026-09-17 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
