---
layout: default
title: 'Groq free tier: limits, free models, verified 2026-09-10'
description: 'Fast inference against a free plan Groq publishes as a per-model rate table. Groq states the free plan as a table rather than one quota, in RPM / RPD / TPM / TPD: 30 / 1K / 8K / 200K on openai/gpt-oss-120b, gpt-oss-20b, gpt-oss-safeguard-20b, qwen/qwen3.6-27b and qwen/qwen3.8-27b, 30 / 14.4K /…'
permalink: /providers/groq-free/
---

{% raw %}

# Groq

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-10 · [groq.com](https://groq.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Fast inference against a free plan Groq publishes as a per-model rate table

## Free models

`gpt-oss`, `qwen3.6`, `qwen3.8`

## Limits, in the vendor's words

Groq states the free plan as a table rather than one quota, in RPM / RPD / TPM / TPD: 30 / 1K / 8K / 200K on openai/gpt-oss-120b, gpt-oss-20b, gpt-oss-safeguard-20b, qwen/qwen3.6-27b and qwen/qwen3.8-27b, 30 / 14.4K / 15K / 500K on the two meta-llama/llama-prompt-guard classifiers, 30 / 250 / 70K on groq/compound and compound-mini, 20 / 2K on the two whisper models and 10 / 100 / 1.2K / 3.6K on the two canopylabs/orpheus voices (read 2026-09-08). Those thirteen rows are the whole free plan, and no Llama is among them any more: llama-3.3-70b-versatile and llama-3.1-8b-instant were both in the table on 2026-08-14 and are gone from it now, surviving only inside the OpenAPI schema and the response samples the page embeds — where llama-4 has always been, and where this row's old anchor keyword was matching. Groq calls the table "a high level summary and there may be exceptions", and points at the limits page in an account for the exact figures

## Connect

- Base URL: `https://api.groq.com/openai/v1`
- Key: `GROQ_API_KEY` — get one at <https://console.groq.com/keys>
- Callable ids: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.6-27b`
- Note: the ids Groq's own Free Plan Limits table names

## Evidence

- Probe: the page at <https://console.groq.com/docs/rate-limits>, anchored on `free plan limits`, `qwen/qwen3.8-27b`
- Source: <https://console.groq.com/docs/rate-limits>

## History

- `2026-09-10` — Free models changed: added qwen3.8; dropped llama-3.3
- `2026-08-17` — Free models changed: added gpt-oss, llama-3.3, qwen3.6; dropped llama-4, qwen3
- `2026-07-19` — Added to the list: Fast inference free tier

---

Generated from `registry.yaml` on 2026-09-12 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
