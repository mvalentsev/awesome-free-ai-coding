---
layout: default
title: '1min.AI free tier: limits, free models, verified 2026-11-09'
description: Multi-provider AI platform with a no-card Free plan, credits obtainable without purchase, and an OpenAI-compatible API that spends the same credit balance. Free credits never expire and can be obtained through daily visits and other published activities; their amount is not published. API use…
permalink: /providers/onemin-ai/
last_modified_at: 2026-11-09
crumb: 1min.AI
---

{% raw %}

# 1min.AI free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-11-02, a regular row from the first probe it passes on or after 2026-11-16 · **live** — last verified by a probe on 2026-11-09 · [1min.ai](https://1min.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Multi-provider AI platform with a no-card Free plan, credits obtainable without purchase, and an OpenAI-compatible API that spends the same credit balance

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

Free credits: Credits allowance: amount not published (period not published) per account

Compatible API: 60 requests/minute per person (Shared across API keys)

Free credits never expire and can be obtained through daily visits and other published activities; their amount is not published. API use draws from the key owner team balance and member allowance. Credits are reserved for estimated input and maximum output before generation. The compatible endpoint is text-only, supports function tools on its documented models, and has a 32,768-token output ceiling (16,384 for GPT-4o). Inputs, tool data, outputs and usage evidence are retained under the existing retention policy. Text is also sent to OpenAI for moderation, regardless of the generation provider. The generic 180-RPM specification is separate from the compatible endpoint limit.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://1min.ai/terms), read 2026-11-02).

## Connect

- Base URL: `https://api.1min.ai/openai/v1`
- Key: `ONEMIN_AI_API_KEY` — get one at <https://app.1min.ai/>
- Callable ids: `gpt-4.1-mini`
- Note: Use a 1min.AI key as a bearer token. gpt-4.1-mini is the documented SDK example; inspect the authenticated /models catalog for current access. This endpoint supports Chat Completions, not Responses; the application has models and features outside this adapter.

Try it from your terminal with your key in `ONEMIN_AI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.1min.ai/openai/v1/chat/completions \
  -H "Authorization: Bearer $ONEMIN_AI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-4.1-mini","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://1min.ai/free-credits>, anchored on `obtain free credits without making a purchase`, `these credits never expire`
- Source: <https://1min.ai/pricing>
- Source: <https://1min.ai/free-credits>
- Source: <https://docs.1min.ai/docs/api/create-api-key>
- Source: <https://docs.1min.ai/docs/api/specifications/credits-limits>
- Source: <https://docs.1min.ai/docs/api/specifications/rate-limits>
- Source: <https://docs.1min.ai/docs/api/openai-compatible>
- Source: <https://1min.ai/terms>
- Source: <https://1min.ai/privacy>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-02` — Added: Multi-provider AI platform with a no-card Free plan, credits obtainable without purchase, and an OpenAI-compatible API that spends the same credit balance

---

Generated from `registry.yaml` on 2026-11-11 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
