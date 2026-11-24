---
layout: default
title: 'IteraCompute free tier: limits, free models, verified 2026-11-23'
description: 'OpenAI-compatible API with retained monthly free model usage for eligible existing accounts. Free models: qwen3.8-27b. Positive net recharge had to complete before 2026-11-24 08:00 UTC to retain shared free access; registration alone and later top-ups do not qualify. "Users with positive net…'
permalink: /providers/iteracompute/
last_modified_at: 2026-11-24
crumb: IteraCompute
---

{% raw %}

# IteraCompute free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-11-23 · [iteracompute.com](https://iteracompute.com/free/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible API with retained monthly free model usage for eligible existing accounts

## Free models

[`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/)

## Limits, in the vendor's words

Retained Free allowance below Starter: 30,000,000 tokens/month per account (for eligible pre-cutoff recharge users below Starter); for `qwen/qwen3.8-27b`, `Auto`

Retained Starter allowance: 100,000,000 tokens/month per account (for eligible pre-cutoff recharge users); for `qwen/qwen3.8-27b`, `Auto`

Retained Pro allowance: 300,000,000 tokens/month per account (for eligible pre-cutoff recharge users); for `qwen/qwen3.8-27b`, `Auto`

Shared free-model slot: 1 request at once per account; for `qwen/qwen3.8-27b`, `Auto`

Positive net recharge had to complete before 2026-11-24 08:00 UTC to retain shared free access; registration alone and later top-ups do not qualify. "Users with positive net recharge completed before this cutoff retain their existing free tier." Active plans separately allow Auto; purchased plan tokens and shared free benefits have separate ledgers. Spending the balance preserves the retained tier; refunds may change it. Input and output, including reasoning, count across all account keys and free routes. "Context includes input and requested output; output is capped at 8,192 tokens." Free and Starter context is 128K; Pro is 256K. No RPM, TPM or daily token cap. Requests reserve maximum usage and settle actual usage; exhausted quota returns 429 without automatic paid overage. Shared capacity may queue; honor Retry-After. No SLA. New external payments add an 8% fee. Zero data retention requires a separate signed agreement. "Allowances reset on the first of each month at 00:00 UTC (08:00 Beijing time); unused tokens do not roll over."

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://iteracompute.com/terms.html), read 2026-10-18).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Without your explicit authorization, we will not use your Model API call data, Interaction Data or Usage Data to train, fine-tune or optimize general-purpose foundation models offered to unspecified users.” ([source](https://iteracompute.com/privacy.html)).

## Connect

- Base URL: `https://api.iteracompute.com/v1`
- Key: `ITERACOMPUTE_API_KEY` — get one at <https://platform.iteracompute.com/api-keys>
- Callable ids: `qwen/qwen3.8-27b`, `Auto`
- Note: Use qwen/qwen3.8-27b for the named model or Auto for the changing pool. Both use the retained shared allowance for qualifying pre-cutoff recharge accounts. An active plan separately permits Auto; check its purchased and shared allowances in your account. Create an API key and use Chat Completions. Auto does not pin model weights or precision. Other catalog routes have independent prices and eligibility.

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
- Source: <https://iteracompute.com/models/auto/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-21` — Free models changed: added qwen3.8-27b
- `2026-10-18` — Added: OpenAI-compatible API with a recurring free token allowance on a self-hosted open model, without a card or balance top-up

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
