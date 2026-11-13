---
layout: default
title: 'JZS Token free tier: limits, free models, verified 2026-11-12'
description: A temporary free model API with a dedicated key and prepaid account. Credits do not expire and there is no monthly subscription. Any top-up fee is unpublished. The gateway forwards API content to upstream providers under their own policies; its no-content-storage statement covers the gateway…
permalink: /providers/jzstoken/
last_modified_at: 2026-11-12
crumb: JZS Token
---

{% raw %}

# JZS Token free tier

🧭 Aggregators (one key, many providers) · no card · requires $1.5 one-time top-up · provisional — added on 2026-11-08, a regular row from the first probe it passes on or after 2026-11-22 · **live** — last verified by a probe on 2026-11-12 · [jzstoken.com](https://jzstoken.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A temporary free model API with a dedicated key and prepaid account

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Credits do not expire and there is no monthly subscription. Any top-up fee is unpublished. The gateway forwards API content to upstream providers under their own policies; its no-content-storage statement covers the gateway. Per-model output and request limits are unpublished.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://jzstoken.com/terms), read 2026-11-08).

## Connect

- Base URL: `https://jzstoken.com/api/v1`
- Key: `JZSTOKEN_API_KEY` — get one at <https://jzstoken.com/dashboard/keys>
- Callable ids: `jzs-max-3.0`
- `jzs-max-3.0`: free until 2026-11-30 UTC ([conditions](https://jzstoken.com/model-pricing/jzs-max-3.0))
- Note: Create a Dedicated key for this model; a Standard key excludes it. Use /chat/completions. The vendor does not certify streaming, tools, structured output or the Messages format separately for every model. All keys share the account balance.

Try it from your terminal with your key in `JZSTOKEN_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://jzstoken.com/api/v1/chat/completions \
  -H "Authorization: Bearer $JZSTOKEN_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"jzs-max-3.0","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://jzstoken.com/model-pricing/jzs-max-3.0>, anchored on `jzs-max-3.0`, `Free until Nov 30, 2026 (UTC)`, `Calls to this model are billed at $0 during the promotion`
- Source: <https://jzstoken.com/model-pricing/jzs-max-3.0>
- Source: <https://jzstoken.com/docs/quick-start>
- Source: <https://jzstoken.com/docs/faq>
- Source: <https://jzstoken.com/terms>
- Source: <https://jzstoken.com/privacy>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-08` — Added: A temporary free model API with a dedicated key and prepaid account

---

Generated from `registry.yaml` on 2026-11-13 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
