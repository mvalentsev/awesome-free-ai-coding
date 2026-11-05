---
layout: default
title: 'NoTrack API free tier: limits, free models, verified 2026-11-05'
description: Operator-hosted OpenAI-compatible API with a first-key trial budget for its single NoTrack Uncensored model. The API pages describe the trial before any top-up; an account and confirmed email are required. Paid keys have separate higher rate and concurrency limits. The combined input and output…
permalink: /providers/notrack-ai/
last_modified_at: 2026-11-05
crumb: NoTrack API
---

{% raw %}

# NoTrack API free tier

🎁 Trials (no card when possible) · no card · provisional — added on 2026-11-02, a regular row from the first probe it passes on or after 2026-11-16 · **live** — last verified by a probe on 2026-11-05 · [notrack.ai](https://notrack.ai/api) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Operator-hosted OpenAI-compatible API with a first-key trial budget for its single NoTrack Uncensored model

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

First-key trial: $0.5 once; scope not published (First key; expires after 7 days)

Trial API: 60 requests/minute; 2 requests at once per key (Before first top-up)

The API pages describe the trial before any top-up; an account and confirmed email are required. Paid keys have separate higher rate and concurrency limits. The combined input and output window is 100,000 tokens. The model is served on the operator’s GPU servers; its underlying checkpoint is not disclosed. API documentation says prompts and replies are not written to disk; request and key identifiers, token use and price are retained. Trial activation and authenticated generation have not been checked here.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://notrack.ai/terms), read 2026-11-02).

## Connect

- Base URL: `https://api.notrack.ai/v1`
- Key: `NOTRACK_AI_API_KEY` — get one at <https://notrack.ai/api-keys>
- Callable ids: `notrack-uncensored`
- Note: Supports Chat Completions, function tools and json_object output. Tool-enabled streams arrive as one chunk per call. Use the published model alias; other model strings are routed to the same model.

Try it from your terminal with your key in `NOTRACK_AI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.notrack.ai/v1/chat/completions \
  -H "Authorization: Bearer $NOTRACK_AI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"notrack-uncensored","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://notrack.ai/api/docs>, anchored on `your first key comes with $0.50 of free credit`, `good for 7 days`, `trial keys (before the first top-up)`
- Source: <https://notrack.ai/api/docs>
- Source: <https://notrack.ai/api-keys>
- Source: <https://notrack.ai/privacy>
- Source: <https://notrack.ai/terms>
- Source: <https://notrack.ai/acceptable-use>
- Source: <https://notrack.ai/refunds>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-02` — Added: Operator-hosted OpenAI-compatible API with a first-key trial budget for its single NoTrack Uncensored model

---

Generated from `registry.yaml` on 2026-11-05 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
