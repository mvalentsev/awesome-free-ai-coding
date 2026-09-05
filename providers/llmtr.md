---
layout: default
title: 'LLMTR free tier: limits, free models, verified 2026-09-03'
description: Turkish OpenAI-compatible gateway with a daily-quota free lane that answers on a zero balance — twelve zero-priced ids on 2026-09-05, MiniMax M3, Nemotron 3 Ultra, Qwen3.6 27B and Mercury 2 among them. The migration guide has a new account send its first request on a free model before any…
permalink: /providers/llmtr/
---

{% raw %}

# LLMTR

🧭 Aggregators (one key, many providers) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-03 · [llmtr.com](https://llmtr.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Turkish OpenAI-compatible gateway with a daily-quota free lane that answers on a zero balance — twelve zero-priced ids on 2026-09-05, MiniMax M3, Nemotron 3 Ultra, Qwen3.6 27B and Mercury 2 among them

## Free models

`nemotron-3-ultra`, `minimax-m3`, `qwen3.6`, `mercury-2`

## Limits, in the vendor's words

The migration guide has a new account send its first request on a free model before any top-up: "Model kataloğunda ücretsiz olarak işaretlenen bir chat modelini seçin … Bu adım, sıfır bakiye ile gateway akışının çalıştığını doğrular" — pick a chat model marked free in the catalog; this step verifies the gateway flow works with a zero balance. Every free row's own description says it is free with a daily quota ("günlük kotayla ücretsiz"), and the figure is published nowhere the docs reach: the Nemotron page sets "nvidia/nemotron-3-ultra-550b-a55b — Ücretsiz, günlük kota" against the metered -262k twin and says only that when the quota is full the free row limits requests. The lane churns and the vendor writes it down — the provider "removed the free tier behind openai/gpt-oss-20b on 24 August 2026 and that model id was retired", and dots-3-note-preview's row says it closes on 30 September 2026. Paid use is a credit balance: "An 8% platform margin is added on top of the requested top-up amount", "We never modify model prices". "Prompt ve yanıt içeriği saklanmaz" — prompt and response content are not stored. Docs are Turkish with an English subset (quickstart, billing, authentication); /v1/models is public and cached (read 2026-09-02)

## Connect

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `minimax/minimax-m3-free`, `minimax/minimax-m2.7-free`, `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.6-27b-free`, `inception/mercury-2-free`, `poolside/laguna-xs-2.1`, `inclusionai/ling-3.0-flash-fin`, `dots-studio/dots-3-note-preview`, `openai/gpt-oss-safeguard-20b`, `openai/gpt-6-astra-free`
- Note: the eleven ids listed are every chat row the public catalog prices at 0 on 2026-09-05: the ten of 2026-09-02 — eight described as free with a daily quota, plus poolside/laguna-xs-2.1 and openai/gpt-oss-safeguard-20b, a content classifier — and openai/gpt-6-astra-free, which arrived by 2026-09-05 carrying its own end date, "10 Eylül 2026'ya kadar günlük kotayla ücretsiz" (free with a daily quota until 10 September 2026), beside the metered openai/gpt-6-astra at $10/$50 per 1M, the price OpenRouter lists it at too. It is listed for the days it has, and the stale-ids check reports it the run after it goes; liquid/lfm-2.5-embedding-350m-free is ignored on purpose as an embeddings row. nvidia/nemotron-3-ultra-550b-a55b is the free daily-quota row and nvidia/nemotron-3-ultra-550b-a55b-262k the metered one — same checkpoint, different products, the vendor's own page says

## Evidence

- Probe: the models catalog at <https://llmtr.com/v1/models>, every listed family required at a zero price
- Source: <https://llmtr.com/docs/migration/openai-openrouter/>
- Source: <https://llmtr.com/docs/en/billing/>
- Source: <https://llmtr.com/v1/models>

## History

- `2026-09-03` — Added to the list: Turkish OpenAI-compatible gateway with a daily-quota free lane that answers on a zero balance — eleven zero-priced ids on 2026-09-02, MiniMax M3, Nemotron 3 Ultra, Qwen3.6 27B and Mercury 2 among them

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
