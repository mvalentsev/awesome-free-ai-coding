---
layout: default
title: 'Kiosapi.id free tier: limits, free models, verified 2026-11-09'
description: Indonesian OpenAI-compatible gateway from PT Mura Teras Kreatif with a daily free allowance on selected open models, independent of its prepaid models. A verified email is required. Free requests do not spend prepaid credit and need no top-up. The daily allowance is shared across Free models. Free…
permalink: /providers/kiosapi-id/
last_modified_at: 2026-11-09
crumb: Kiosapi.id
---

{% raw %}

# Kiosapi.id free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-11-02, a regular row from the first probe it passes on or after 2026-11-16 · **live** — last verified by a probe on 2026-11-09 · [kiosapi.id](https://kiosapi.id) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Indonesian OpenAI-compatible gateway from PT Mura Teras Kreatif with a daily free allowance on selected open models, independent of its prepaid models

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Free models: 50 requests/day per account; for `zai/glm-4.7-flash`, `qwen/qwen3-30b`, `google/gemma-4-26b`, `meta/llama-3.1-8b`, `aisingapore/sea-lion-27b`. 07:00 WIB

Free rate limit: 5 requests/minute; scope not published

A verified email is required. Free requests do not spend prepaid credit and need no top-up. The daily allowance is shared across Free models. Free requests have approximately 24k input characters and 2,048 output tokens. Paid models spend the separate rupiah balance. Free inference uses Cloudflare Workers AI; upstream data policies apply. Encrypted web-chat storage does not encrypt inference processing.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://kiosapi.id/terms), read 2026-11-02).

## Connect

- Base URL: `https://api.kiosapi.id/v1`
- Key: `KIOSAPI_ID_API_KEY` — get one at <https://kiosapi.id/dashboard/keys>
- Callable ids: `zai/glm-4.7-flash`, `qwen/qwen3-30b`, `google/gemma-4-26b`, `meta/llama-3.1-8b`, `aisingapore/sea-lion-27b`
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

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-02` — Added: Indonesian OpenAI-compatible gateway from PT Mura Teras Kreatif with a daily free allowance on selected open models, independent of its prepaid models

---

Generated from `registry.yaml` on 2026-11-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
