---
layout: default
title: 'BeatAPI (free models) free tier: limits, free models, verified 2026-11-08'
description: A no-top-up API for free text-model variants. Free calls are counted separately from paid rate limits, but can also be refused when the ordinary account limit is exhausted. Availability can change without notice and no daily allowance is promised. Free model contexts, output limits and reasoning…
permalink: /providers/beatapi/
last_modified_at: 2026-11-08
crumb: BeatAPI (free models)
---

{% raw %}

# BeatAPI (free models) free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-11-08, a regular row from the first probe it passes on or after 2026-11-22 · **live** — last verified by a probe on 2026-11-08 · [beatapi.io](https://beatapi.io) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A no-top-up API for free text-model variants

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

1 request/minute per account (before the first top-up)

10 requests/minute per account (after any top-up)

Free calls are counted separately from paid rate limits, but can also be refused when the ordinary account limit is exhausted. Availability can change without notice and no daily allowance is promised. Free model contexts, output limits and reasoning settings are not those of the paid siblings.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://beatapi.io/terms-of-service), read 2026-11-08).

## Connect

- Base URL: `https://api.beatapi.io/v1`
- Key: `BEATAPI_API_KEY` — get one at <https://beatapi.io/dashboard/apikeys>
- Callable ids: `glm-5.3-flash-free`, `deepseek-v4.1-flash-free`, `hy4-free`
- Note: Use a key in the default auto group and the exact -free ID. A zero balance is allowed. All three listed Free IDs support Chat Completions; the Free catalog does not promise Responses. Reasoning consumes the output budget; the Free guide recommends "2000 or more" tokens.

Try it from your terminal with your key in `BEATAPI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.beatapi.io/v1/chat/completions \
  -H "Authorization: Bearer $BEATAPI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"glm-5.3-flash-free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.beatapi.io/free-models>, anchored on `A zero balance is fine, and so is an account that has never topped up`, `glm-5.3-flash-free`, `deepseek-v4.1-flash-free`, `hy4-free`; ids checked in <https://api.beatapi.io/v1/text/models>
- Source: <https://beatapi.io/pricing>
- Source: <https://beatapi.io/terms-of-service>
- Source: <https://docs.beatapi.io/free-models>
- Source: <https://docs.beatapi.io/faq/account-billing>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-08` — Added: A no-top-up API for free text-model variants

---

Generated from `registry.yaml` on 2026-11-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
