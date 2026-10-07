---
layout: default
title: 'Hugging Face Inference Providers free tier: limits, free models, verified 2026-10-05'
description: Routed access to 200+ models across providers (Groq, Cerebras, Together, etc.) with a free HF account. Credits apply only to HF-routed requests and their amount is subject to change. They spend at each provider's own rates across the router's catalog; a spending balance does not make any…
permalink: /providers/huggingface-inference/
last_modified_at: 2026-10-05
crumb: Hugging Face Inference Providers
---

{% raw %}

# Hugging Face Inference Providers free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-05 · [huggingface.co](https://huggingface.co/docs/inference-providers) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Routed access to 200+ models across providers (Groq, Cerebras, Together, etc.) with a free HF account

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

HF-routed usage: $0.1/month per account

Credits apply only to HF-routed requests and their amount is subject to change. They spend at each provider's own rates across the router's catalog; a spending balance does not make any individual model free.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://huggingface.co/terms-of-service), read 2026-09-26).

## Connect

- Base URL: `https://router.huggingface.co/v1`
- Key: `HUGGINGFACE_INFERENCE_API_KEY` — get one at <https://huggingface.co/settings/tokens>
- Codex CLI: [`configs/codex/huggingface-inference.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/huggingface-inference.config.toml) — copy it to `~/.codex/`, then `codex -p huggingface-inference`; set up on the lane by the vendor's own page, <https://huggingface.co/docs/inference-providers/integrations/codex>: "all Codex requests are routed through Inference Providers"
- Callable ids: `openai/gpt-oss-120b`, `Qwen/Qwen3.8-27B`, `zai-org/GLM-5.3-Flash`
- Note: Chat-only; use namespaced model IDs. The listed IDs are examples, and the monthly credit can be spent across routed models.

Try it from your terminal with your key in `HUGGINGFACE_INFERENCE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://router.huggingface.co/v1/chat/completions \
  -H "Authorization: Bearer $HUGGINGFACE_INFERENCE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"openai/gpt-oss-120b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://huggingface.co/docs/inference-providers/pricing>, anchored on `monthly credits`, `$0.10, subject to change`; ids checked in <https://router.huggingface.co/v1/models>
- Source: <https://huggingface.co/docs/inference-providers/pricing>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-08-14` — Free models changed: dropped deepseek, qwen3
- `2026-07-19` — Added: Routed access to 200+ models across providers (Groq, Cerebras, Together, etc.) with a free HF account

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
