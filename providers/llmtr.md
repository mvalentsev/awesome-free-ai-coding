---
layout: default
title: 'LLMTR free tier: limits, free models, verified 2026-09-17'
description: 'Turkish OpenAI-compatible gateway whose free rows answer on a zero balance — thirteen zero-priced chat ids on 2026-09-16, Nemotron 3 Ultra, Qwen3.6 27B and Agnes 3.0 Flash among them. A new account calls the free rows before any top-up: the migration guide says "Model kataloğunda ücretsiz olarak…'
permalink: /providers/llmtr/
---

{% raw %}

# LLMTR

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-17 · [llmtr.com](https://llmtr.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Turkish OpenAI-compatible gateway whose free rows answer on a zero balance — thirteen zero-priced chat ids on 2026-09-16, Nemotron 3 Ultra, Qwen3.6 27B and Agnes 3.0 Flash among them

## Free models

`nemotron-3-ultra`, `qwen3.6`

## Limits, in the vendor's words

A new account calls the free rows before any top-up: the migration guide says "Model kataloğunda ücretsiz olarak işaretlenen bir chat modelini seçin" (pick a chat model marked free in the catalog), and "Bu adım, sıfır bakiye ile gateway ve kullanım kaydı akışının çalıştığını doğrular" (this step checks that the gateway and usage logging work on a zero balance). Four free rows carry a daily quota whose figure is published nowhere (Nemotron 3 Ultra and Super, Qwen3.6 27B, Ling 3.0 Flash Fin); Laguna XS 2.1 is free because "Poolside serves these models free on its own inference API", with "no extra token allowance to track"; three rows are free "22 Eylul 2026'ya kadar" (until 22 September 2026), and dots-3-note-preview closes on 30 September 2026. Paid use is prepaid credit: "An 8% platform margin is added on top of the requested top-up amount" and "We never modify model prices". The privacy page says prompt and response bodies are not written permanently to its usage and billing database ("kalıcı olarak yazılmaz"). Read 2026-09-16

## Connect

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.6-27b-free`, `poolside/laguna-xs-2.1`, `inclusionai/ling-3.0-flash-fin`, `dots-studio/dots-3-note-preview`, `openai/gpt-oss-safeguard-20b`, `qwen/qwen3.8-flash-free`, `inclusionai/ling-3.0-flash-vl`, `inclusionai/ling-3.0-flash-sante`, `agnes/agnes-3.0-flash`, `agnes/agnes-2.5-flash`, `motif/motif-3`
- Note: the thirteen ids are every chat row the public catalog prices at 0 on 2026-09-16, motif/motif-3 created that evening. qwen/qwen3.8-flash-free, inclusionai/ling-3.0-flash-vl and inclusionai/ling-3.0-flash-sante are free only until 22 September 2026, and dots-studio/dots-3-note-preview closes on 30 September 2026. nvidia/nemotron-3-ultra-550b-a55b is the free daily-quota row and its -262k twin the metered one; openai/gpt-oss-safeguard-20b is a content classifier rather than a coding model. liquid/lfm-2.5-embedding-350m-free is ignored as an embeddings row

## Evidence

- Probe: the models catalog at <https://llmtr.com/v1/models>, every listed family required at a zero price
- Source: <https://llmtr.com/docs/migration/openai-openrouter/>
- Source: <https://llmtr.com/docs/en/billing/>
- Source: <https://llmtr.com/docs/en/gateway/poolside-laguna/>
- Source: <https://llmtr.com/privacy>
- Source: <https://llmtr.com/v1/models>

## History

- `2026-09-10` — Free models changed: dropped mercury-2
- `2026-09-07` — Free models changed: dropped minimax-m3
- `2026-09-03` — Added to the list: Turkish OpenAI-compatible gateway with a daily-quota free lane that answers on a zero balance — eleven zero-priced ids on 2026-09-02, MiniMax M3, Nemotron 3 Ultra, Qwen3.6 27B and Mercury 2 among them

---

Generated from `registry.yaml` on 2026-09-19 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
