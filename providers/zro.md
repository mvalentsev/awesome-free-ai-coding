---
layout: default
title: 'Zro (MoonMath) free tier: limits, free models, verified 2026-11-05'
description: OpenAI-compatible inference for coding agents from MoonMath, with a recurring Free plan on selected Flash models. The Free plan covers the two named Flash models with a daily allowance; its amount, pooling scope, reset time and rate limits are not published. An account and API key are required…
permalink: /providers/zro/
last_modified_at: 2026-11-05
crumb: Zro (MoonMath)
---

{% raw %}

# Zro (MoonMath) free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-11-01, a regular row from the first probe it passes on or after 2026-11-15 · **live** — last verified by a probe on 2026-11-05 · [zro.moonmath.ai](https://zro.moonmath.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible inference for coding agents from MoonMath, with a recurring Free plan on selected Flash models

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Free plan: Daily usage allowance: amount not published; scope not published

The Free plan covers the two named Flash models with a daily allowance; its amount, pooling scope, reset time and rate limits are not published. An account and API key are required. The pricing page offers Free separately from paid plans and usage packs; the general quickstart still asks for a subscription or usage pack. Inference passes through an EU gateway and runs in Europe, the US, or both as selected per key; unavailable allowed regions fail rather than falling back elsewhere. Zro says it retains no request bodies and uses no requests or logs for training without separate explicit consent; account, billing and operational metadata are retained. Inference providers follow their own operational logging terms. Optional agent tools have separate prices.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://zro.moonmath.ai/terms), read 2026-10-31).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “We do not use customer requests or logs for training, fine-tuning, evaluations, analytics, or other secondary purposes unless you separately and explicitly agree” ([source](https://zro.moonmath.ai/privacy)).

## Connect

- Base URL: `https://zro.moonmath.ai/v1`
- Key: `ZRO_API_KEY` — get one at <https://zro.moonmath.ai/get-started?plan=free>
- Callable ids: `glm-5.3-flash`, `deepseek-v4.1-flash`
- Note: Create an account and API key for the Free plan and select either listed Flash ID. Other models and auto routing use metered rates. The vendor documents Chat Completions, Responses and Messages; these configurations use Chat Completions. Authenticated generation and Free activation have not been checked here.

Try it from your terminal with your key in `ZRO_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://zro.moonmath.ai/v1/chat/completions \
  -H "Authorization: Bearer $ZRO_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"glm-5.3-flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://zro.moonmath.ai/pricing>, anchored on `Free daily usage on GLM-5.3 Flash and DeepSeek V4.1 Flash.`, `Resets every day.`, `OpenAI-compatible API`, `Free plan for Flash models. $0 per month`
- Source: <https://zro.moonmath.ai/pricing>
- Source: <https://zro.moonmath.ai/docs/models>
- Source: <https://zro.moonmath.ai/docs/quickstart>
- Source: <https://zro.moonmath.ai/docs/api>
- Source: <https://zro.moonmath.ai/privacy>
- Source: <https://zro.moonmath.ai/terms>
- Source: <https://zro.moonmath.ai/docs/regions>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-01` — Added: OpenAI-compatible inference for coding agents from MoonMath, with a recurring Free plan on selected Flash models

---

Generated from `registry.yaml` on 2026-11-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
