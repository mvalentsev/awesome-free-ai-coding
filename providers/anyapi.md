---
layout: default
title: 'AnyAPI free tier: limits, free models, verified 2026-11-08'
description: A free model API with a separate daily AnyToken allowance. AnyTokens are internal billing units, not model tokens. The daily wallet does not carry over and is limited to one account per person or legal entity. Browser Playground access is a separate mode. Requests go to third-party providers with…
permalink: /providers/anyapi/
last_modified_at: 2026-11-08
crumb: AnyAPI
---

{% raw %}

# AnyAPI free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-11-08, a regular row from the first probe it passes on or after 2026-11-22 · **live** — last verified by a probe on 2026-11-08 · [anyapi.ai](https://anyapi.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A free model API with a separate daily AnyToken allowance

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

100,000 AnyTokens/day per account. midnight UTC

AnyTokens are internal billing units, not model tokens. The daily wallet does not carry over and is limited to one account per person or legal entity. Browser Playground access is a separate mode. Requests go to third-party providers with their own data policies; the documentation offers provider-selection controls.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://anyapi.ai/terms-of-service), read 2026-11-08).

## Connect

- Base URL: `https://api.anyapi.ai/v1`
- Key: `ANYAPI_API_KEY` — get one at <https://dash.anyapi.ai/?page=api-keys>
- Callable ids: `qwen/qwen3.8-27b:free`, `inclusionai/ling-3.0-flash-fin:free`, `inclusionai/ling-3.0-flash-sante:free`
- Note: Create a Free account and an API key in the Dashboard. Use the exact provider/model:free ID with /chat/completions. The daily AnyToken wallet and each zero-priced variant have separate scopes; paid models require a different plan.

Try it from your terminal with your key in `ANYAPI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.anyapi.ai/v1/chat/completions \
  -H "Authorization: Bearer $ANYAPI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen/qwen3.8-27b:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://anyapi.ai/pricing>, anchored on `100K / day`, `No credit card required`
- Source: <https://anyapi.ai/pricing>
- Source: <https://anyapi.ai/terms-of-service>
- Source: <https://anyapi.ai/ai-models>
- Source: <https://docs.anyapi.ai/get-started/quick-start.md>
- Source: <https://docs.anyapi.ai/features/privacy-logging.md>
- Source: <https://anyapi.ai/ai-models/qwen-qwen3-8-27b-free>
- Source: <https://anyapi.ai/ai-models/inclusionai-ling-3-0-flash-fin-free>
- Source: <https://anyapi.ai/ai-models/inclusionai-ling-3-0-flash-sante-free>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-08` — Added: A free model API with a separate daily AnyToken allowance

---

Generated from `registry.yaml` on 2026-11-08 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
