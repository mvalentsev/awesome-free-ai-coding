---
layout: default
title: 'Sarvam AI free tier: limits, free models, verified 2026-09-05'
description: India's Sarvam AI credits every new account ₹100 to spend on any of its APIs — its own Sarvam-105B chat model beside hosted DeepSeek V4 Flash, GLM 5.3 Flash and Gemma 4 — through an OpenAI-shaped chat endpoint. "Every new user receives ₹100 worth of free credits to explore all our APIs" — about…
permalink: /providers/sarvam/
---

{% raw %}

# Sarvam AI

🎁 Trials (no card when possible) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-05 · [sarvam.ai](https://www.sarvam.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

India's Sarvam AI credits every new account ₹100 to spend on any of its APIs — its own Sarvam-105B chat model beside hosted DeepSeek V4 Flash, GLM 5.3 Flash and Gemma 4 — through an OpenAI-shaped chat endpoint

## Free models

`sarvam-105b`, `deepseek-v4-flash`, `glm-5.3-flash`

## Limits, in the vendor's words

"Every new user receives ₹100 worth of free credits to explore all our APIs" — about $1.15 — and the credits page adds that they "are universal and never expire". Per-million-token prices on the same pricing page (read 2026-09-05): sarvam-105b ₹29.28 in / ₹73.2 out, deepseekv4-flash ₹19.8 / ₹59.4, glm5.3-flash ₹13.5 / ₹45, gemma4 ₹36.6 / ₹91.5, glm5.2 and glm5.3 around ₹127 / ₹400 — so the grant is roughly 3 million input tokens of the flagship or 7 million of GLM 5.3 Flash. The Starter plan is rate-limited to 60 chat requests a minute on the default models and 40 on sarvam-105b. Sign-up is an account on the dashboard; no card is mentioned on any page read

## Connect

- Base URL: `https://api.sarvam.ai/v1`
- Key: `SARVAM_API_KEY` — get one at <https://dashboard.sarvam.ai>
- Callable ids: `sarvam-105b`, `deepseekv4-flash`, `glm5.3-flash`
- Note: the vendor's own header is api-subscription-key, and the same key is accepted as "Authorization: Bearer" on every endpoint — the docs name that form as the one for "OpenAI-compatible tooling pointed at the Chat Completions endpoint". Ids write the version without its hyphen (deepseekv4-flash, glm5.3-flash); a newer /v2/chat/completions adds 512K context and tool calling on GLM-5.2 and image input on Gemma 4 31B. Prices are in rupees

## Evidence

- Probe: the page at <https://docs.sarvam.ai/api/getting-started/pricing.md>, anchored on `₹100 worth of free credits`
- Source: <https://docs.sarvam.ai/api/getting-started/pricing.md>
- Source: <https://docs.sarvam.ai/api/getting-started/ratelimits.md>
- Source: <https://docs.sarvam.ai/api-reference/authentication.md>

## History

No recorded event yet — the first scheduled run after a row lands writes its `added` line.

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
