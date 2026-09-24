---
layout: default
title: 'LLMTR free tier: limits, free models, verified 2026-09-21'
description: 'Turkish OpenAI-compatible gateway whose free rows answer on a zero balance — nine zero-priced chat ids on 2026-09-23, Nemotron 3 Ultra, Qwen3.8 27B and Agnes 3.0 Flash among them. A new account calls the free rows before any top-up: the migration guide says "Model kataloğunda ücretsiz olarak…'
permalink: /providers/llmtr/
---

{% raw %}

# LLMTR

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-21 · [llmtr.com](https://llmtr.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Turkish OpenAI-compatible gateway whose free rows answer on a zero balance — nine zero-priced chat ids on 2026-09-23, Nemotron 3 Ultra, Qwen3.8 27B and Agnes 3.0 Flash among them

## Free models

`nemotron-3-ultra`

## Limits, in the vendor's words

A new account calls the free rows before any top-up: the migration guide says "Model kataloğunda ücretsiz olarak işaretlenen bir chat modelini seçin" (pick a chat model marked free in the catalog), and "Bu adım, sıfır bakiye ile gateway ve kullanım kaydı akışının çalıştığını doğrular" (this step checks that the gateway and usage logging work on a zero balance). Four free rows carry a daily quota whose figure is published nowhere (Nemotron 3 Ultra and Super, Qwen3.8 27B, Ling 3.0 Flash Fin); Laguna XS 2.1 is free because "Poolside serves these models free on its own inference API", with "no extra token allowance to track"; dots-3-note-preview closes on 30 September 2026. Paid use is prepaid credit: "An 8% platform margin is added on top of the requested top-up amount" and "We never modify model prices". The privacy page says prompt and response bodies are not written permanently to its usage and billing database ("kalıcı olarak yazılmaz"). Read 2026-09-21

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Poolside states that prompts and completions on free access may be logged and used to improve its products.” ([source](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

## Connect

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`, `poolside/laguna-xs-2.1`, `inclusionai/ling-3.0-flash-fin`, `dots-studio/dots-3-note-preview`, `agnes/agnes-3.0-flash`, `agnes/agnes-2.5-flash`, `motif/motif-3`
- Note: the nine ids are every chat row the public catalog prices at 0 on 2026-09-23 outside the evren/* rows; dots-studio/dots-3-note-preview closes on 30 September. nvidia/nemotron-3-ultra-550b-a55b is the free daily-quota row, its -262k twin the metered one. Ignored: an embeddings row, openai/gpt-oss-safeguard-20b, a content classifier, and five evren/* rows priced 0 because each "kendi EVREN anahtarınızla çalışır" (runs on your own EVREN key)

## Evidence

- Probe: the models catalog at <https://llmtr.com/v1/models>, each listed family checked for a zero price
- Source: <https://llmtr.com/docs/migration/openai-openrouter/>
- Source: <https://llmtr.com/docs/en/billing/>
- Source: <https://llmtr.com/docs/en/gateway/poolside-laguna/>
- Source: <https://llmtr.com/privacy>
- Source: <https://llmtr.com/v1/models>

## History

- *next scheduled run* — Free models changed: dropped qwen3.6
- `2026-09-10` — Free models changed: dropped mercury-2
- `2026-09-07` — Free models changed: dropped minimax-m3
- `2026-09-03` — Added to the list: Turkish OpenAI-compatible gateway with a daily-quota free lane that answers on a zero balance — eleven zero-priced ids on 2026-09-02, MiniMax M3, Nemotron 3 Ultra, Qwen3.6 27B and Mercury 2 among them

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
