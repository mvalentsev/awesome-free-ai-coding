---
layout: default
title: 'Sarvam AI free tier: limits, free models, verified 2026-10-26'
description: India's Sarvam AI grants verified users ₹100 in credits that never expire, spendable across its APIs, including Sarvam-105B chat through an OpenAI-compatible endpoint. Signup credit requires a verified user, applies across APIs and never expires; its value is in INR, with no guaranteed token…
permalink: /providers/sarvam/
last_modified_at: 2026-10-26
crumb: Sarvam AI
---

{% raw %}

# Sarvam AI free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-26 · [sarvam.ai](https://www.sarvam.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

India's Sarvam AI grants verified users ₹100 in credits that never expire, spendable across its APIs, including Sarvam-105B chat through an OpenAI-compatible endpoint

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

₹100 once per account

Pay-as-you-go Sarvam-105B: 60 requests/minute per account (Shared by all API keys under the account); for `sarvam-105b`

Signup credit requires a verified user, applies across APIs and never expires; its value is in INR, with no guaranteed token conversion. Rate limits apply per account across its keys, with separate pools by API. The listed Pay-as-you-go rate covers Sarvam-105B. The v2 chat and Responses APIs are generally available for the documented open models; the pricing page still labels some other models beta. No page read mentions a card.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.sarvam.ai/terms-of-service), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “We use Your content (including inputs, uploads, prompts, or generated outputs) to train, fine-tune, and/ or improve our AI models unless you explicitly opt-out through your account settings” ([source](https://www.sarvam.ai/privacy-policy)).

## Connect

- Base URL: `https://api.sarvam.ai/v1`
- Key: `SARVAM_API_KEY` — get one at <https://indus.sarvam.ai/key-management>
- Callable ids: `sarvam-105b`
- Note: The vendor accepts api-subscription-key and Authorization: Bearer. This configuration uses /v1/chat/completions for sarvam-105b; the conversations variant is omitted. The separate /v2/chat/completions and /v2/responses routes are generally available for their listed models. Prices are in rupees.

Try it from your terminal with your key in `SARVAM_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.sarvam.ai/v1/chat/completions \
  -H "Authorization: Bearer $SARVAM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"sarvam-105b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.sarvam.ai/api/getting-started/pricing.md>, anchored on `Every verified user receives ₹100 in credits`
- Source: <https://docs.sarvam.ai/api/getting-started/pricing.md>
- Source: <https://docs.sarvam.ai/api/getting-started/models.md>
- Source: <https://docs.sarvam.ai/api/getting-started/ratelimits.md>
- Source: <https://docs.sarvam.ai/api-reference/authentication.md>
- Source: <https://docs.sarvam.ai/api-reference/beta-apis.md>
- Source: <https://api.sarvam.ai/v2/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: dropped sarvam-105b
- `2026-09-16` — Free models changed: dropped deepseek-v4-flash, glm-5.3-flash
- `2026-09-05` — Added: India's Sarvam AI credits every new account ₹100 to spend on any of its APIs — its own Sarvam-105B chat model beside hosted DeepSeek V4 Flash, GLM 5.3 Flash and Gemma 4 — through an OpenAI-shaped chat endpoint

---

Generated from `registry.yaml` on 2026-10-29 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
