---
layout: default
title: 'IteraCompute free tier: limits, free models, verified 2026-11-24'
description: An OpenAI-compatible Auto router with a retained monthly token allowance for eligible existing accounts. Eligibility depends on the positive balance of top-ups completed before the promotion ended, after refunds. Later top-ups cannot unlock or increase that allowance. The billing dashboard…
permalink: /providers/iteracompute/
last_modified_at: 2026-11-26
crumb: IteraCompute
---

{% raw %}

# IteraCompute free tier

🔌 LLM APIs with free tier · no card · requires a qualifying prior top-up · **live** — last verified by a probe on 2026-11-24 · [iteracompute.com](https://iteracompute.com/free/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

An OpenAI-compatible Auto router with a retained monthly token allowance for eligible existing accounts.

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

Retained Auto allowance: Monthly tokens allowance: see your account for values per account

Eligibility depends on the positive balance of top-ups completed before the promotion ended, after refunds. Later top-ups cannot unlock or increase that allowance. The billing dashboard separates retained tokens, plan tokens and promotional rewards. Pay-as-you-go wallet billing is off by default.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://iteracompute.com/terms.html), read 2026-10-18).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Without your explicit authorization, we will not use your Model API call data, Interaction Data or Usage Data to train, fine-tune or optimize general-purpose foundation models offered to unspecified users.” ([source](https://iteracompute.com/privacy.html)).

## Connect

- Base URL: `https://api.iteracompute.com/v1`
- Key: `ITERACOMPUTE_API_KEY` — get one at <https://platform.iteracompute.com/api-keys>
- Callable ids: `Auto`
- Note: Auto selects from the currently listed models using demand, cost and spare capacity. Create a key that permits Auto and check your available tokens in Billing. The named Qwen3.8-27B route has retired.

Try it from your terminal with your key in `ITERACOMPUTE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.iteracompute.com/v1/chat/completions \
  -H "Authorization: Bearer $ITERACOMPUTE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"Auto","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://iteracompute.com/free-tier-terms/>, anchored on `monthly Auto allowance`, `Later top-ups cannot unlock or increase this allowance`; ids checked in <https://api.iteracompute.com/v1/models>
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
- Source: <https://iteracompute.com/models/auto/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-26` — Free models changed: dropped qwen3.8-27b
- `2026-10-21` — Free models changed: added qwen3.8-27b
- `2026-10-18` — Added: OpenAI-compatible API with a recurring free token allowance on a self-hosted open model, without a card or balance top-up

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
