---
layout: default
title: 'Sarvam AI free tier: limits, free models, verified 2026-09-24'
description: India's Sarvam AI credits every new account ₹100 that never expire, spendable on any of its APIs — including its own Sarvam-105B chat model on an OpenAI-shaped endpoint. "Every new user receives ₹100 in credits", usable "across any of our APIs", and the credits "are universal and never expire".…
permalink: /providers/sarvam/
last_modified_at: 2026-09-26
crumb: Sarvam AI
---

{% raw %}

# Sarvam AI free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-24 · [sarvam.ai](https://www.sarvam.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

India's Sarvam AI credits every new account ₹100 that never expire, spendable on any of its APIs — including its own Sarvam-105B chat model on an OpenAI-shaped endpoint

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

"Every new user receives ₹100 in credits", usable "across any of our APIs", and the credits "are universal and never expire". Sarvam-105B costs ₹29.28 in and ₹73.2 out per 1M tokens, so the grant is about 3 million input tokens, and the Starter plan allows 40 chat requests a minute. DeepSeek V4 Flash, GLM 5.3 and Gemma 4 31B are served only on /v2/chat/completions, a beta that is "not enabled by default with standard API subscription keys" and is granted per key on request. No page read mentions a card (2026-09-18)

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.sarvam.ai/terms-of-service), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “We use Your content (including inputs, uploads, prompts, or generated outputs) to train, fine-tune, and/ or improve our AI models unless you explicitly opt-out through your account settings” ([source](https://www.sarvam.ai/privacy-policy)).

## Connect

- Base URL: `https://api.sarvam.ai/v1`
- Key: `SARVAM_API_KEY` — get one at <https://dashboard.sarvam.ai>
- Callable ids: `sarvam-105b`
- Note: the vendor's own header is api-subscription-key, and the same key is accepted as "Authorization: Bearer" on every endpoint. /v1/chat/completions serves only sarvam-105b and its voice-agent variant, sarvam-105b-conversations, which the configs leave out; the open models are on the /v2 beta, whitelisted per key. Prices are in rupees

Try it from your terminal with your key in `SARVAM_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.sarvam.ai/v1/chat/completions \
  -H "Authorization: Bearer $SARVAM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"sarvam-105b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.sarvam.ai/api/getting-started/pricing.md>, anchored on `Every new user receives ₹100 in credits`
- Source: <https://docs.sarvam.ai/api/getting-started/pricing.md>
- Source: <https://docs.sarvam.ai/api/getting-started/models.md>
- Source: <https://docs.sarvam.ai/api/getting-started/ratelimits.md>
- Source: <https://docs.sarvam.ai/api-reference/authentication.md>
- Source: <https://docs.sarvam.ai/api-reference/beta-apis.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: dropped sarvam-105b
- `2026-09-16` — Free models changed: dropped deepseek-v4-flash, glm-5.3-flash
- `2026-09-05` — Added: India's Sarvam AI credits every new account ₹100 to spend on any of its APIs — its own Sarvam-105B chat model beside hosted DeepSeek V4 Flash, GLM 5.3 Flash and Gemma 4 — through an OpenAI-shaped chat endpoint

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
