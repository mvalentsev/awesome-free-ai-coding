---
layout: default
title: 'AMD Radeon Cloud Token Factory free tier: limits, free models, verified 2026-11-19'
description: Free shared model API on AMD Radeon GPUs, with a recurring account-specific daily usage allowance. China-site AMD AI Developer Program account and API key required. Registration asks for name, email and phone, with email or phone verification; some accounts need approval before receiving a key…
permalink: /providers/amd-token-factory/
last_modified_at: 2026-11-19
crumb: AMD Radeon Cloud Token Factory
---

{% raw %}

# AMD Radeon Cloud Token Factory free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-11-18, a regular row from the first probe it passes on or after 2026-12-02 · **live** — last verified by a probe on 2026-11-19 · [developer.amd.com.cn](https://developer.amd.com.cn/login?source=bjOVsdlfc) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free shared model API on AMD Radeon GPUs, with a recurring account-specific daily usage allowance

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Shared API usage: Daily points allowance: see your account for values per account. 00:00 Beijing time

Typical gateway limit: 20 requests/minute per account (typical; current limits are returned in response headers)

Typical platform limit: 30 requests/minute; 8 requests at once per key (typical; current limits are returned in response headers)

China-site AMD AI Developer Program account and API key required. Registration asks for name, email and phone, with email or phone verification; some accounts need approval before receiving a key. Points meter shared API usage, carry no monetary value and are separate from GPU-instance credits. All models share the daily cap and rate limits; response headers and the usage endpoint report current allowances. For evaluation, prototyping and development; production workloads and reselling access are prohibited. Prompts and outputs are logged for two days, with longer retention for abuse or legal investigations; metadata is retained longer.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://amd-aim.github.io/radeon-cloud-docs/guides/login/), read 2026-11-18).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “We do not train models on your data” ([source](https://amd-aim.github.io/radeon-cloud-docs/api/terms/)).

## Connect

- Base URL: `https://developer.amd.com.cn/radeon/api/v1`
- Key: `AMD_TOKEN_FACTORY_API_KEY` — get one at <https://developer.amd.com.cn/login?source=bjOVsdlfc>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://developer.amd.com.cn/radeon/api`
- Callable ids: `DeepSeek-V4-Flash`, `DeepSeek-V4.1-Flash`, `Gemma-4-31B-IT`, `GLM-5.3-Flash`, `MiMo-V2.6-Flash`, `MiniCPM-V-4.7-1B`, `MiniCPM-V-4.7-35B-A3B`, `MiniCPM5-2B`, `Qwen3.8-27B`
- Note: Use the exact listed model IDs; dated card titles can differ. Chat Completions and Anthropic Messages share the account allowance.

Try it from your terminal with your key in `AMD_TOKEN_FACTORY_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://developer.amd.com.cn/radeon/api/v1/chat/completions \
  -H "Authorization: Bearer $AMD_TOKEN_FACTORY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"MiMo-V2.6-Flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://amd-aim.github.io/radeon-cloud-docs/guides/token-factory/>, anchored on `Token Factory is free, but usage is capped`, `no credits to spend`, `OpenAI-compatible API`, `00:00 Beijing time`
- Source: <https://amd-aim.github.io/radeon-cloud-docs/guides/token-factory/>
- Source: <https://amd-aim.github.io/radeon-cloud-docs/api/rate-limits/>
- Source: <https://amd-aim.github.io/radeon-cloud-docs/api/usage/>
- Source: <https://amd-aim.github.io/radeon-cloud-docs/api/terms/>
- Source: <https://amd-aim.github.io/radeon-cloud-docs/guides/login/>
- Source: <https://amd-aim.github.io/radeon-cloud-docs/api/messages/>
- Source: <https://amd-aim.github.io/radeon-cloud-docs/models/overview/>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3AMiMo-V2.6-Flash>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3ADeepSeek-V4.1-Flash>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3ADeepSeek-V4-Flash>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3AGLM-5.3-Flash>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3AQwen3.8-27B>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3AGemma-4-31B-IT>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3Ad3>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3Ad3-flash>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3AClef>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3AMiniCPM-V-4.7-35B-A3B>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3AMiniCPM-V-4.7-1B>
- Source: <https://developer.amd.com.cn/radeon/api/tokenfactory/model?id=model_gateway%3AMiniCPM5-2B>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-18` — Added: Free shared model API on AMD Radeon GPUs, with a recurring account-specific daily usage allowance

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
