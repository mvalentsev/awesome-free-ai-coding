---
layout: default
title: 'Kiosapi.id free tier: limits, free models, verified 2026-11-16'
description: 'Indonesian OpenAI-compatible gateway from PT Mura Teras Kreatif with a daily free allowance on selected open models, independent of its prepaid models. Free models: gemma-4-26b-a4b, glm-4.7-flash, llama-3.1-8b, qwen3-30b, sea-lion-27b. A verified email is required. Free requests do not spend…'
permalink: /providers/kiosapi-id/
last_modified_at: 2026-11-16
crumb: Kiosapi.id
model_sort: true
---

{% raw %}

# Kiosapi.id free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-11-16 · [kiosapi.id](https://kiosapi.id) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Indonesian OpenAI-compatible gateway from PT Mura Teras Kreatif with a daily free allowance on selected open models, independent of its prepaid models

## Free models

<span data-model-sort-inline><span data-model-family="gemma-4-26b-a4b">[`gemma-4-26b-a4b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemma-4-26b-a4b/)</span>, <span data-model-family="glm-4.7-flash">[`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/)</span>, <span data-model-family="llama-3.1-8b">[`llama-3.1-8b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/llama-3.1-8b/)</span>, <span data-model-family="qwen3-30b">`qwen3-30b`</span>, <span data-model-family="sea-lion-27b">`sea-lion-27b`</span></span>

## Limits, in the vendor's words

Free models: 50 requests/day per account. 07:00 WIB

Free rate limit: 5 requests/minute; scope not published

A verified email is required. Free requests do not spend prepaid credit and need no top-up. The daily allowance is shared across Free models. Free requests have approximately 24k input characters and 2,048 output tokens. Paid models spend the separate rupiah balance. Free inference uses Cloudflare Workers AI; upstream data policies apply. Encrypted web-chat storage does not encrypt inference processing.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://kiosapi.id/terms), read 2026-11-02).

## Connect

- Base URL: `https://api.kiosapi.id/v1`
- Key: `KIOSAPI_ID_API_KEY` — get one at <https://kiosapi.id/dashboard/keys>
- Callable ids: `google/gemma-4-26b`, `zai/glm-4.7-flash`, `meta/llama-3.1-8b`, `qwen/qwen3-30b`, `aisingapore/sea-lion-27b`
- Note: Use a live key. Test keys return fixed mock responses without calling a model. The hosted Agents API accepts paid models only; ordinary Free Chat Completions is separate. The public catalog marks function tools available on GLM, Qwen and Gemma, but not Llama or SEA-LION.

Try it from your terminal with your key in `KIOSAPI_ID_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.kiosapi.id/v1/chat/completions \
  -H "Authorization: Bearer $KIOSAPI_ID_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"zai/glm-4.7-flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.kiosapi.id/v1/models>, each listed family checked for a zero price
- Source: <https://kiosapi.id/docs>
- Source: <https://kiosapi.id/pricing>
- Source: <https://kiosapi.id/docs/agents>
- Source: <https://kiosapi.id/terms>
- Source: <https://kiosapi.id/privacy>
- Source: <https://ai.google.dev/gemma/docs/core/model_card_4>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-16` — Free models changed: added gemma-4-26b-a4b, glm-4.7-flash, llama-3.1-8b, qwen3-30b, sea-lion-27b
- `2026-11-02` — Added: Indonesian OpenAI-compatible gateway from PT Mura Teras Kreatif with a daily free allowance on selected open models, independent of its prepaid models

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
