---
layout: default
title: 'MIAPI free tier: limits, free models, verified 2026-11-12'
description: A monthly free API allowance for web-grounded answers with citations. The Free plan covers all endpoints. Query packs are a separate paid mode and do not expire. Questions are limited to 2,000 characters and output budgets to 50–2,000 tokens; no token-based context limit is published. The public…
permalink: /providers/miapi/
last_modified_at: 2026-11-12
crumb: MIAPI
---

{% raw %}

# MIAPI free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-11-08, a regular row from the first probe it passes on or after 2026-11-22 · **live** — last verified by a probe on 2026-11-12 · [miapi.uk](https://miapi.uk) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A monthly free API allowance for web-grounded answers with citations

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

100 queries/month per account

60 requests/minute; scope not published

The Free plan covers all endpoints. Query packs are a separate paid mode and do not expire. Questions are limited to 2,000 characters and output budgets to 50–2,000 tokens; no token-based context limit is published. The public Playground has separate caps. Upstream model and data conditions are not separately stated. The privacy policy states "Usage logs are retained for up to 90 days."

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://miapi.uk/terms.html), read 2026-11-08).

## Connect

- Base URL: `https://api.miapi.uk/v1`
- Key: `MIAPI_API_KEY` — get one at <https://miapi.uk/signup.html>
- Callable ids: `miapi-grounded`
- Note: Use the grounded-answer alias with /chat/completions. The official OpenAI SDK example uses this endpoint. Set max_tokens between 50 and 2,000 and keep questions within the documented character limit. Streaming is documented; function-tool compatibility is not specified.

Try it from your terminal with your key in `MIAPI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.miapi.uk/v1/chat/completions \
  -H "Authorization: Bearer $MIAPI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"miapi-grounded","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://miapi.uk>, anchored on `100 queries / month`, `miapi-grounded`
- Source: <https://miapi.uk/privacy.html>
- Source: <https://miapi.uk/terms.html>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-08` — Added: A monthly free API allowance for web-grounded answers with citations

---

Generated from `registry.yaml` on 2026-11-13 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
