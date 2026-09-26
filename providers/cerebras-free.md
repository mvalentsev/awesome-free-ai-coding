---
layout: default
title: 'Cerebras Inference free tier (archived): what it offered, and why it left the list'
description: 'Very fast inference; $5 in trial credits that expire in 30 days, card required before the API answers at all. Free models: gpt-oss, qwen3.8. Cerebras'' own docs: "New accounts receive $5 in free credits after adding a verified payment method", credits "expire 30 days after they''re granted", and…'
permalink: /providers/cerebras-free/
last_modified_at: 2026-09-16
crumb: Cerebras Inference
---

{% raw %}

# Cerebras Inference free tier (archived)

🎁 Trials (no card when possible) · card required · **archived** — delisted on 2026-09-16: its only free offer was $5 of credit granted after a verified payment method is added, expiring in 30 days — a one-off credit behind a card, which CONTRIBUTING does not admit · [cerebras.ai](https://www.cerebras.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What it offered

Very fast inference; $5 in trial credits that expire in 30 days, card required before the API answers at all

## Free models it listed

`gpt-oss`, `qwen3.8`

## Limits, in the vendor's words

Cerebras' own docs: "New accounts receive $5 in free credits after adding a verified payment method", credits "expire 30 days after they're granted", and "If you skip adding a payment method at sign-up, Playground and API access remain inactive until you do". Asked "Is there a permanently free tier?" the same page answers "No". Free Trial rate limits are per model and the same on both the public catalog now lists — 5 RPM, 30K uncached TPM, 90K total TPM, 1M TPH, 1M TPD each (read 2026-09-03), the two TPM figures being the dual bucket the page describes. That catalog has turned over twice: GLM 4.7 was deprecated on 2026-08-17 exactly as it announced, and Gemma 4 31B left between the 09:55 UTC probe on 2026-09-03, which still found it named, and a re-read eleven hours later — replaced by Qwen 3.8 27B, the one model here that reads images, 2 per request on this tier. The marketing pricing page still promises the credits "after making an account" and mentions no card — that was the old API tier, which accounts opened before the change kept until 2026-08-17 and which is now gone

## Evidence

- Probe: the page at <https://inference-docs.cerebras.ai/support/rate-limits>, anchored on `after adding a verified payment method`, `credits expire 30 days after`
- Source: <https://inference-docs.cerebras.ai/support/rate-limits>
- Source: <https://www.cerebras.ai/pricing>
- Source: <https://inference-docs.cerebras.ai/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-16` — Delisted
- `2026-09-03` — Free models changed: added qwen3.8; dropped gemma-4
- `2026-08-19` — Free models changed: dropped glm-4.7
- `2026-08-14` — Free models changed: added gemma-4, glm-4.7, gpt-oss; dropped qwen3
- `2026-07-19` — Added: Very fast inference, free tier

---

Generated from `registry.yaml` on 2026-09-26. No probe reads this row any more — it left the list for good unless a reviewer brings it back; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
