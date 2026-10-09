---
layout: default
title: 'LLMTR free tier: limits, free models, verified 2026-10-08'
description: 'Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up. Free models: nemotron-3-ultra, nemotron-3-super, laguna-xs-2.1, agnes-3.0-flash, agnes-2.5-flash, ling-3.1-flash, qwen3.8-27b, kolibri-1 and 1 more. Free chat rows can…'
permalink: /providers/llmtr/
last_modified_at: 2026-10-08
crumb: LLMTR
---

{% raw %}

# LLMTR free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-08 · [llmtr.com](https://llmtr.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

## Free models

[`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/), [`nemotron-3-super`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-super/), [`laguna-xs-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-xs-2.1/), [`agnes-3.0-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/agnes-3.0-flash/), [`agnes-2.5-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/agnes-2.5-flash/), [`ling-3.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.1-flash/) (until 2026-10-13), [`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/), [`kolibri-1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/kolibri-1/) (until 2026-10-09), [`apodex-1.1-mini`](https://mvalentsev.github.io/awesome-free-ai-coding/models/apodex-1.1-mini/) (until 2026-10-10)

## Limits, in the vendor's words

Nemotron Ultra/Super and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`

Apodex 1.1 Mini: Daily usage allowance: amount not published per account per model; for `apodex/apodex-1.1-mini-free`

Free chat rows can be called on a new account with zero balance before any top-up. Laguna XS 2.1 follows Poolside's free inference offer, without a token allowance to track. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. Apodex Mini can close before its recorded deadline if the promotion pool runs out.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://llmtr.com/en/terms), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Poolside states that prompts and completions on free access may be logged and used to improve its products.” ([source](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

## Connect

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`, `poolside/laguna-xs-2.1`, `inclusionai/ling-3.1-flash`, `agnes/agnes-3.0-flash`, `agnes/agnes-2.5-flash`, `tesseracted/kolibri-1`, `apodex/apodex-1.1-mini-free`
- `inclusionai/ling-3.1-flash`: free until 2026-10-13 19:00+03:00 ([conditions](https://llmtr.com/models/inclusionai/ling-3.1-flash))
- `tesseracted/kolibri-1`: free until 2026-10-09 23:59+03:00 ([conditions](https://llmtr.com/models/tesseracted/kolibri-1))
- `apodex/apodex-1.1-mini-free`: free until 2026-10-10 23:59+03:00 ([conditions](https://llmtr.com/models/apodex/apodex-1.1-mini-free))
- Note: New accounts have a reduced shared free-model allowance during their first 24 hours. Nemotron Ultra's -262k variant is metered. Checked 2026-10-05: Qwen ordinary, streaming and small tool cycles completed, but full Codex and OpenCode requests returned provider_error. Ling completed an OpenCode tool turn; Codex via LiteLLM did not complete with either model.

Try it from your terminal with your key in `LLMTR_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://llmtr.com/v1/chat/completions \
  -H "Authorization: Bearer $LLMTR_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"nvidia/nemotron-3-ultra-550b-a55b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://llmtr.com/v1/models>, each listed family checked for a zero price
- Source: <https://llmtr.com/docs/migration/openai-openrouter/>
- Source: <https://llmtr.com/docs/en/billing/>
- Source: <https://llmtr.com/docs/en/gateway/poolside-laguna/>
- Source: <https://llmtr.com/privacy>
- Source: <https://llmtr.com/v1/models>
- Source: <https://llmtr.com/models/minimax/minimax-m3.1-flash-preview>
- Source: <https://llmtr.com/models/inclusionai/ling-3.1-flash>
- Source: <https://llmtr.com/models/motif/motif-3>
- Source: <https://llmtr.com/models/tesseracted/kolibri-1>
- Source: <https://llmtr.com/models/qwen/qwen3.8-27b-free>
- Source: <https://llmtr.com/models/apodex/apodex-1.1-mini-free>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-06` — Free models changed: dropped minimax-m3.1-flash-preview
- `2026-10-06` — Free models changed: added apodex-1.1-mini
- `2026-10-05` — Free models changed: added kolibri-1, qwen3.8-27b
- `2026-10-04` — Free models changed: dropped motif-3
- `2026-10-01` — Free models changed: added ling-3.1-flash, minimax-m3.1-flash-preview
- `2026-10-01` — Free models changed: dropped ling-3.0-flash-fin
- `2026-09-30` — Free models changed: added motif-3
- `2026-09-28` — Free models changed: added agnes-2.5-flash, agnes-3.0-flash
- `2026-09-24` — Free models changed: added laguna-xs-2.1, ling-3.0-flash-fin, nemotron-3-super
- `2026-09-21` — Free models changed: dropped qwen3.6
- `2026-09-07` — Free models changed: dropped mercury-2
- `2026-09-07` — Free models changed: dropped minimax-m3
- `2026-09-02` — Added: Turkish OpenAI-compatible gateway with a daily-quota free lane that answers on a zero balance — eleven zero-priced ids on 2026-09-02, MiniMax M3, Nemotron 3 Ultra, Qwen3.6 27B and Mercury 2 among them

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
