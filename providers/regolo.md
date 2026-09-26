---
layout: default
title: 'Regolo AI free tier: limits, free models, verified 2026-09-24'
description: 'EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card. "Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), "1M tokens per day" and…'
permalink: /providers/regolo/
last_modified_at: 2026-09-25
crumb: Regolo AI
---

{% raw %}

# Regolo AI free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-24 · [regolo.ai](https://regolo.ai/pricing/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

## Free models

[`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/), [`gpt-oss-120b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-oss-120b/), [`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/), `apertus-70b`

## Limits, in the vendor's words

"Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), "1M tokens per day" and "Stricter rate limits" with "Fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. One model is priced at €0.00 in and out outside any trial, brick-v1-beta, and it is not one to code with: its own page calls it "a lightweight prompt-complexity classifier designed for LLM routing pipelines", a Qwen3.5-0.8B LoRA that labels a prompt easy, medium or hard for Regolo's Brick router (read 2026-09-21)

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Zero Data Retention means Regolo does not store, log, or retain any of the data you send through our APIs — including prompts, completions, and any attached files. … It is never used for model training, analytics, or any other purpose.” ([source](https://regolo.ai/faq/)).

## Connect

- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `glm5.2`, `gpt-oss-120b`, `qwen3.8-27b`, `apertus-70b`, `brick-v1-beta`
- Note: GET /v1/models is public and needs no key, but it publishes ids only — the prices and the trial terms are on the pricing page this row probes. brick-v1-beta is the one id priced at zero on that page, and it is Brick's prompt-complexity classifier rather than a coding model

## Evidence

- Probe: the page at <https://regolo.ai/pricing/>, anchored on `1M tokens per day`, `No credit card required, no commitment`; ids checked in <https://api.regolo.ai/v1/models>
- Source: <https://api.regolo.ai/v1/models>
- Source: <https://docs.regolo.ai/>
- Source: <https://regolo.ai/models-archive/brick-v1-beta/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: added gpt-oss-120b; dropped gpt-oss
- `2026-09-22` — Free models changed: added glm-5.2; dropped glm-5
- `2026-09-21` — Free models changed: dropped llama-3.3
- `2026-09-17` — Free models changed: added qwen3.8-27b; dropped qwen3.8
- `2026-08-30` — Added: EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
