---
layout: default
title: 'Groq free tier: limits, free models, verified 2026-09-03'
description: 'Fast inference against a free plan Groq publishes as a per-model rate table. Groq states the free plan as a table rather than one quota, in RPM / RPD / TPM / TPD: 30 / 14.4K / 6K / 500K on llama-3.1-8b-instant, 30 / 1K / 12K / 100K on llama-3.3-70b-versatile, 30 / 1K / 8K / 200K on…'
permalink: /providers/groq-free/
---

{% raw %}

# Groq

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [groq.com](https://groq.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Fast inference against a free plan Groq publishes as a per-model rate table

## Free models

`llama-3.3`, `gpt-oss`, `qwen3.6`

## Limits, in the vendor's words

Groq states the free plan as a table rather than one quota, in RPM / RPD / TPM / TPD: 30 / 14.4K / 6K / 500K on llama-3.1-8b-instant, 30 / 1K / 12K / 100K on llama-3.3-70b-versatile, 30 / 1K / 8K / 200K on openai/gpt-oss-120b, gpt-oss-20b and qwen/qwen3.6-27b, 30 / 250 / 70K on groq/compound and compound-mini, 20 / 2K on the two whisper models (read 2026-08-14). Those thirteen rows are the whole free plan — no llama-4 among them, though the page carries the id in the API schema it embeds. Groq calls the table "a high level summary and there may be exceptions", and points at the limits page in an account for the exact figures

## Connect

- Base URL: `https://api.groq.com/openai/v1`
- Key: `GROQ_API_KEY` — get one at <https://console.groq.com/keys>
- Callable ids: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.6-27b`
- Note: the ids Groq's own Free Plan Limits table names

## Evidence

- Probe: the page at <https://console.groq.com/docs/rate-limits>, anchored on `free plan limits`, `llama-3.3-70b-versatile`
- Source: <https://console.groq.com/docs/rate-limits>

## History

- `2026-08-17` — Free models changed: added gpt-oss, llama-3.3, qwen3.6; dropped llama-4, qwen3
- `2026-07-19` — Added to the list: Fast inference free tier

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
