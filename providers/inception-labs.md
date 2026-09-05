---
layout: default
title: 'Inception Labs (Mercury) free tier: limits, free models, verified 2026-09-03'
description: A signup grant on the Mercury diffusion models, one for chat and one built for fill-in-the-middle and code edits — the second is the reason this row is here, since an FIM endpoint is what an IDE completion plugin actually calls. 100 million tokens on every new account, no payment details…
permalink: /providers/inception-labs/
---

{% raw %}

# Inception Labs (Mercury)

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-03 · [platform.inceptionlabs.ai](https://platform.inceptionlabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A signup grant on the Mercury diffusion models, one for chat and one built for fill-in-the-middle and code edits — the second is the reason this row is here, since an FIM endpoint is what an IDE completion plugin actually calls

## Free models

`mercury-2`, `mercury-edit-2`

## Limits, in the vendor's words

100 million tokens on every new account, no payment details required, and the grant does not refill — past it the account moves to pay-as-you-go at $0.25 per 1M input and $0.75 per 1M output. The Free tier is rate-limited separately at 100-1,000 requests, 100,000-1,000,000 input tokens and 10,000-100,000 output tokens per minute

## Connect

- Base URL: `https://api.inceptionlabs.ai/v1`
- Key: `INCEPTION_LABS_API_KEY` — get one at <https://platform.inceptionlabs.ai>
- Callable ids: `mercury-2`, `mercury-edit-2`
- Note: mercury-2 answers /v1/chat/completions; mercury-edit-2 answers /v1/fim/completions and /v1/edit/completions instead, so an OpenAI-shaped chat client cannot call it — point an autocomplete plugin at it, not a chat agent

## Evidence

- Probe: the page at <https://docs.inceptionlabs.ai/get-started/models>, anchored on `100 million free tokens`, `mercury-2`, `mercury-edit-2`
- Source: <https://docs.inceptionlabs.ai/get-started/models>
- Source: <https://docs.inceptionlabs.ai/get-started/rate-limits>

## History

- `2026-08-17` — Added to the list: A signup grant on the Mercury diffusion models, one for chat and one built for fill-in-the-middle and code edits — the second is the reason this row is here, since an FIM endpoint is what an IDE completion plugin actually calls

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
