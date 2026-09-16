---
layout: default
title: 'Sarvam AI free tier: limits, free models, verified 2026-09-14'
description: India's Sarvam AI credits every new account ₹100 that never expire, spendable on any of its APIs — including its own Sarvam-105B chat model on an OpenAI-shaped endpoint. "Every new user receives ₹100 worth of free credits to explore all our APIs", and the credits "are universal and never…
permalink: /providers/sarvam/
---

{% raw %}

# Sarvam AI

🎁 Trials (no card when possible) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-14 · [sarvam.ai](https://www.sarvam.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

India's Sarvam AI credits every new account ₹100 that never expire, spendable on any of its APIs — including its own Sarvam-105B chat model on an OpenAI-shaped endpoint

## Free models

`sarvam-105b`

## Limits, in the vendor's words

"Every new user receives ₹100 worth of free credits to explore all our APIs", and the credits "are universal and never expire". Sarvam-105B costs ₹29.28 in and ₹73.2 out per 1M tokens, so the grant is about 3 million input tokens, and the Starter plan allows 40 chat requests a minute. DeepSeek V4 Flash, GLM 5.3 and Gemma 4 31B are served only on /v2/chat/completions, a beta that is "not enabled by default with standard API subscription keys" and is granted per key on request. No page read mentions a card (2026-09-16)

## Connect

- Base URL: `https://api.sarvam.ai/v1`
- Key: `SARVAM_API_KEY` — get one at <https://dashboard.sarvam.ai>
- Callable ids: `sarvam-105b`, `sarvam-105b-conversations`
- Note: the vendor's own header is api-subscription-key, and the same key is accepted as "Authorization: Bearer" on every endpoint. /v1/chat/completions serves only sarvam-105b and sarvam-105b-conversations; the open models are on the /v2 beta, whitelisted per key. Prices are in rupees

## Evidence

- Probe: the page at <https://docs.sarvam.ai/api/getting-started/pricing.md>, anchored on `₹100 worth of free credits`
- Source: <https://docs.sarvam.ai/api/getting-started/pricing.md>
- Source: <https://docs.sarvam.ai/api/getting-started/ratelimits.md>
- Source: <https://docs.sarvam.ai/api-reference/authentication.md>
- Source: <https://docs.sarvam.ai/api-reference/beta-apis.md>

## History

- *next scheduled run* — Free models changed: dropped deepseek-v4-flash, glm-5.3-flash
- `2026-09-07` — Added to the list: India's Sarvam AI credits every new account ₹100 to spend on any of its APIs — its own Sarvam-105B chat model beside hosted DeepSeek V4 Flash, GLM 5.3 Flash and Gemma 4 — through an OpenAI-shaped chat endpoint

---

Generated from `registry.yaml` on 2026-09-16 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
