---
layout: default
title: 'IteraCompute free tier: limits, free models, verified 2026-10-26'
description: 'OpenAI-compatible API with recurring free usage on a self-hosted open model. Free models: qwen3.8-27b. Register and verify an email, or sign in with Google. Input and output, including reasoning, count across all account keys. "Context includes input and requested output; output is capped at 8,192…'
permalink: /providers/iteracompute/
last_modified_at: 2026-10-26
crumb: IteraCompute
---

{% raw %}

# IteraCompute free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-10-18, a regular row from the first probe it passes on or after 2026-11-01 · **live** — last verified by a probe on 2026-10-26 · [iteracompute.com](https://iteracompute.com/free/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible API with recurring free usage on a self-hosted open model

## Free models

[`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/)

## Limits, in the vendor's words

Qwen Free tier: 30,000,000 tokens/month per account; for `qwen/qwen3.8-27b`. Allowances reset on the first of each month at 00:00 UTC (08:00 Beijing time); unused tokens do not roll over.

Qwen Free tier: 160,000 tokens/minute per account; for `qwen/qwen3.8-27b`

Register and verify an email, or sign in with Google. Input and output, including reasoning, count across all account keys. "Context includes input and requested output; output is capped at 8,192 tokens." Free total context is 128K. Requests reserve maximum usage, then settle actual usage. Exhausted quota returns 429 without automatic paid overage. No recharge is required; optional cumulative $10/$50 top-ups unlock larger allowances. Recharge thresholds use completed principal minus refunds, excluding grants and fees. Spending the balance keeps the tier; refunds may lower it. Shared capacity may queue; honor Retry-After. No SLA. Zero data retention requires a separate signed agreement.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://iteracompute.com/terms.html), read 2026-10-18).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Without your explicit authorization, we will not use your Model API call data, Interaction Data or Usage Data to train, fine-tune or optimize general-purpose foundation models offered to unspecified users.” ([source](https://iteracompute.com/privacy.html)).

## Connect

- Base URL: `https://api.iteracompute.com/v1`
- Key: `ITERACOMPUTE_API_KEY` — get one at <https://platform.iteracompute.com/api-keys>
- Callable ids: `qwen/qwen3.8-27b`
- Note: The published no-recharge Free allowance covers Qwen. Create a key scoped to qwen/qwen3.8-27b. Other zero-priced catalog routes have no published access conditions. Use Chat Completions and the Free context/output budgets on the provider page. Authenticated generation has not been checked here.

Try it from your terminal with your key in `ITERACOMPUTE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.iteracompute.com/v1/chat/completions \
  -H "Authorization: Bearer $ITERACOMPUTE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen/qwen3.8-27b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.iteracompute.com/v1/models>, each listed family checked for a zero price
- Source: <https://iteracompute.com/pricing/>
- Source: <https://iteracompute.com/free-tier-terms/>
- Source: <https://iteracompute.com/docs.html>
- Source: <https://iteracompute.com/integrations/opencode/>
- Source: <https://iteracompute.com/models/qwen3-8-27b/>
- Source: <https://iteracompute.com/subprocessors/>
- Source: <https://iteracompute.com/changelog/>
- Source: <https://iteracompute.com/about/>
- Source: <https://iteracompute.com/terms.html>
- Source: <https://iteracompute.com/privacy.html>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-21` — Free models changed: added qwen3.8-27b
- `2026-10-18` — Added: OpenAI-compatible API with a recurring free token allowance on a self-hosted open model, without a card or balance top-up

---

Generated from `registry.yaml` on 2026-10-27 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
