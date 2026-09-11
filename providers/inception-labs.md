---
layout: default
title: 'Inception Labs (Mercury) free tier: limits, free models, verified 2026-09-07'
description: A signup grant on the Mercury diffusion models — Mercury 2.5 and Mercury 2 for chat, Mercury Edit 2 for fill-in-the-middle and code edits; the last is the reason this row is here, since an FIM endpoint is what an IDE completion plugin actually calls. 100 million tokens on every new account, no…
permalink: /providers/inception-labs/
---

{% raw %}

# Inception Labs (Mercury)

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-07 · [platform.inceptionlabs.ai](https://platform.inceptionlabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A signup grant on the Mercury diffusion models — Mercury 2.5 and Mercury 2 for chat, Mercury Edit 2 for fill-in-the-middle and code edits; the last is the reason this row is here, since an FIM endpoint is what an IDE completion plugin actually calls

## Free models

`mercury-2.5`, `mercury-2`, `mercury-edit-2`

## Limits, in the vendor's words

100 million tokens on every new account, no payment details required, and the grant does not refill. The FAQ calls it a one-time credit "shared across all models rather than granted per model", so Mercury 2.5 spends the same balance as Mercury 2. Past it the account moves to pay-as-you-go: $0.25 per 1M input and $0.75 per 1M output on Mercury 2 and Mercury Edit 2, a list $0.20/$0.75 on Mercury 2.5 that the launch promotion is discounting 80% to $0.04/$0.15 (2026-09-10). The Free tier's own ceiling is per minute rather than per month — 1,000 requests, 1,000,000 input tokens and 100,000 output tokens

## Connect

- Base URL: `https://api.inceptionlabs.ai/v1`
- Key: `INCEPTION_LABS_API_KEY` — get one at <https://platform.inceptionlabs.ai>
- Callable ids: `mercury-2.5`, `mercury-2`, `mercury-edit-2`
- Note: mercury-2.5 and mercury-2 answer /v1/chat/completions and are the two ids /v1/models lists; mercury-edit-2 answers /v1/fim/completions and /v1/edit/completions instead and is absent from that catalog by design, so an OpenAI-shaped chat client cannot call it — point an autocomplete plugin at it, not a chat agent

## Evidence

- Probe: the page at <https://docs.inceptionlabs.ai/get-started>, anchored on `100 million free tokens`, `no payment details required`
- Source: <https://docs.inceptionlabs.ai/get-started>
- Source: <https://docs.inceptionlabs.ai/resources/faq>
- Source: <https://docs.inceptionlabs.ai/get-started/models>
- Source: <https://docs.inceptionlabs.ai/get-started/rate-limits>

## History

- `2026-08-17` — Added to the list: A signup grant on the Mercury diffusion models, one for chat and one built for fill-in-the-middle and code edits — the second is the reason this row is here, since an FIM endpoint is what an IDE completion plugin actually calls

---

Generated from `registry.yaml` on 2026-09-11 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
