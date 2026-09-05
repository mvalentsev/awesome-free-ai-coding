---
layout: default
title: 'Regolo AI free tier: limits, free models, verified 2026-09-03'
description: 'EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card. "Start free for one month ... No credit card, no commitment": the trial card names 1 month duration, "1M tokens per day" and "Stricter rate limits — fair usage throttling applies", against…'
permalink: /providers/regolo/
---

{% raw %}

# Regolo AI

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-03 · [regolo.ai](https://regolo.ai/pricing/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

## Free models

`glm-5`, `gpt-oss`, `qwen3.8`, `llama-3.3`, `apertus-70b`

## Limits, in the vendor's words

"Start free for one month ... No credit card, no commitment": the trial card names 1 month duration, "1M tokens per day" and "Stricter rate limits — fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. One model is priced at €0.00 in and out outside any trial, the in-house brick-v1-beta (read 2026-08-30)

## Connect

- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `glm5.2`, `gpt-oss-120b`, `qwen3.8-27b`, `Llama-3.3-70B-Instruct`, `apertus-70b`, `brick-v1-beta`
- Note: GET /v1/models is public and needs no key, but it publishes ids only — the prices and the trial terms are on the pricing page this row probes. brick-v1-beta is the one id priced at zero on that page

## Evidence

- Probe: the page at <https://regolo.ai/pricing/>, anchored on `1M tokens per day`, `No credit card, no commitment`; ids checked in <https://api.regolo.ai/v1/models>
- Source: <https://api.regolo.ai/v1/models>
- Source: <https://docs.regolo.ai/>

## History

- `2026-08-31` — Added to the list: EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
