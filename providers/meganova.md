---
layout: default
title: 'MegaNova free tier: limits, free models, verified 2026-09-03'
description: 'OpenAI-compatible gateway whose no-card Tier 1 account gets a daily free quota on Mistral Small 3.2 and the house Manta routers — 50 a day per model, 550 across the lane. Tier 1 is "Free, no credit card required" with "Free Models: <100B parameters (including Manta Mini)" and "Limited free model…'
permalink: /providers/meganova/
---

{% raw %}

# MegaNova

🧭 Aggregators (one key, many providers) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-03 · [meganova.ai](https://meganova.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway whose no-card Tier 1 account gets a daily free quota on Mistral Small 3.2 and the house Manta routers — 50 a day per model, 550 across the lane

## Free models

`mistral-small-3.2`

## Limits, in the vendor's words

Tier 1 is "Free, no credit card required" with "Free Models: <100B parameters (including Manta Mini)" and "Limited free model access"; the Free Model Quota page grants it per account with a "daily reset at 00:00 UTC": 50 a day each on Mistral-Small-3.2-24B, Manta-Mini, Manta-Flash, five community Llama fine-tunes, Qwen3-Embedding-8B and BGE-Reranker, "Total Free Quota per day 550", and 0 on GLM-4.7-Flash and Manta-Pro until Tier 2 ("$1 deposit to unlock"). The page never names the unit; its nearest sentence is "Each request reports: Remaining free quota". Past the quota "usage continues based on the account's billing configuration (if the charge switch is turned on)". Mistral Small 3.2 is served at 8,192 tokens of context here, Manta Flash at 16,384. The Website Terms say the Service Terms "typically prohibit production or high-throughput use of free modules", against the quota page's own "lightweight production use"; the operator is Nebula Nova Inc., a Delaware corporation, and its privacy policy lists prompts among the content it collects (read 2026-09-02)

## Connect

- Base URL: `https://api.meganova.ai/v1`
- Key: `MEGANOVA_API_KEY` — get one at <https://www.meganova.ai/api-keys>
- Callable ids: `mistralai/Mistral-Small-3.2-24B-Instruct-2506`, `meganova-ai/manta-mini-1.0`, `meganova-ai/manta-flash-1.0`
- Note: the three ids listed are the chat rows a Tier 1 account can call for free; ten more zero-priced rows are ignored on purpose — zai-org/GLM-4.7-Flash and manta-pro-1.0 have a Tier 1 quota of 0, faster-whisper, Qwen3-Embedding-8B and bge-reranker-v2-m3 are not chat models, and five are roleplay fine-tunes of Llama (Sapphira, Violet Lotus, Nevoria, Euryale, Stheno). Manta Mini and Manta Flash are MegaNova's own routers over open models, tagged best_role_play in the catalog, so Mistral Small 3.2 is the one named coding model on the lane

## Evidence

- Probe: the models catalog at <https://api.meganova.ai/v1/models>, every listed family required at a zero price
- Source: <https://docs.meganova.ai/free-model-quota>
- Source: <https://docs.meganova.ai/tiers>
- Source: <https://api.meganova.ai/v1/models>

## History

- `2026-09-03` — Added to the list: OpenAI-compatible gateway whose no-card Tier 1 account gets a daily free quota on Mistral Small 3.2 and the house Manta routers — 50 a day per model, 550 across the lane

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
