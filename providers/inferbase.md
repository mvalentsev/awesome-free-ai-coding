---
layout: default
title: 'Inferbase free tier: limits, free models, verified 2026-10-26'
description: OpenAI-compatible managed inference on a permanent $0 Free plan, with a shared daily usage budget and no card required. Managed chat, embeddings and rerank share the daily allowance. BYOK requests also count toward the monthly request ceiling, but their tokens are billed by the connected provider…
permalink: /providers/inferbase/
last_modified_at: 2026-10-26
crumb: Inferbase
---

{% raw %}

# Inferbase free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-10-14, a regular row from the first probe it passes on or after 2026-10-28 · **live** — last verified by a probe on 2026-10-26 · [inferbase.ai](https://inferbase.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible managed inference on a permanent $0 Free plan, with a shared daily usage budget and no card required

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

All successful requests: 5,000 requests/month per organization

Managed inference: 100 requests/day; $0.5/day; 10 requests/minute per organization

60 requests/minute per key

Managed chat, embeddings and rerank share the daily allowance. BYOK requests also count toward the monthly request ceiling, but their tokens are billed by the connected provider. Managed requests allow at most 8,192 input and 1,024 output tokens; these are request budgets, not full model context windows. Monthly requests reset on the 1st at 00:00 UTC. Exhausted allowances return 402. Managed image, audio and video generation require Pro.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://inferbase.ai/terms), read 2026-10-14).

## Connect

- Base URL: `https://api.inferbase.ai/v1`
- Key: `INFERBASE_API_KEY` — get one at <https://inferbase.ai/docs/getting-started/quickstart>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.inferbase.ai`
- Callable ids: `auto`
- Note: Create an account and a gateway API key. The auto ID routes among models eligible under the key policy; the response names the model that served the request. Managed usage spends a shared budget, so no model is independently free. The vendor documents OpenAI chat and Anthropic Messages tool loops; authenticated generation has not been checked here.

Try it from your terminal with your key in `INFERBASE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.inferbase.ai/v1/chat/completions \
  -H "Authorization: Bearer $INFERBASE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"auto","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://inferbase.ai/pricing>, anchored on `100 requests and $0.50 of model usage a day`, `no card is required`; ids checked in <https://api.inferbase.ai/v1/models>
- Source: <https://inferbase.ai/pricing>
- Source: <https://inferbase.ai/terms>
- Source: <https://inferbase.ai/subprocessors>
- Source: <https://inferbase.ai/docs/gateway/client-compatibility>
- Source: <https://inferbase.ai/docs/getting-started/quickstart>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-14` — Added: OpenAI-compatible managed inference on a permanent $0 Free plan, with a shared daily usage budget and no card required

---

Generated from `registry.yaml` on 2026-10-31 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
