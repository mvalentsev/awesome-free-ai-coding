---
layout: default
title: 'Hugging Face Inference Providers free tier: limits, free models, verified 2026-09-03'
description: Routed access to 200+ models across providers (Groq, Cerebras, Together, etc.) with a free HF account. Free users get $0.10/month credits (subject to change); credits apply only on HF-routed requests. There is no free model list to publish — the credit is spent at each provider's own rate across…
permalink: /providers/huggingface-inference/
---

{% raw %}

# Hugging Face Inference Providers

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-03 · [huggingface.co](https://huggingface.co/docs/inference-providers) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Routed access to 200+ models across providers (Groq, Cerebras, Together, etc.) with a free HF account

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Free users get $0.10/month credits (subject to change); credits apply only on HF-routed requests. There is no free model list to publish — the credit is spent at each provider's own rate across everything the router reaches, so which models it buys depends on their price, not on a tier (read 2026-08-14)

## Connect

- Base URL: `https://router.huggingface.co/v1`
- Key: `HUGGINGFACE_INFERENCE_API_KEY` — get one at <https://huggingface.co/settings/tokens>
- Note: chat-only; model ids namespaced (openai/gpt-oss-120b)

## Evidence

- Probe: the page at <https://huggingface.co/docs/inference-providers/pricing>, anchored on `monthly credits`, `$0.10, subject to change`
- Source: <https://huggingface.co/docs/inference-providers/pricing>

## History

- `2026-08-17` — Free models changed: dropped deepseek, qwen3
- `2026-07-19` — Added to the list: Routed access to 200+ models across providers (Groq, Cerebras, Together, etc.) with a free HF account

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
