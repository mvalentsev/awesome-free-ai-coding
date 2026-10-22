---
layout: default
title: 'LLMTR free tier: limits, free models, verified 2026-10-22'
description: 'Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up. Free models: nemotron-3-ultra, nemotron-3-super, laguna-xs-2.1, agnes-3.0-flash, agnes-2.5-flash, qwen3.8-27b, beam-1.0, jais-3-mova-36b-a4b and 3 more. Free chat rows…'
permalink: /providers/llmtr/
last_modified_at: 2026-10-22
crumb: LLMTR
---

{% raw %}

# LLMTR free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-22 · [llmtr.com](https://llmtr.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

## Free models

[`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/), [`nemotron-3-super`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-super/), [`laguna-xs-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-xs-2.1/), [`agnes-3.0-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/agnes-3.0-flash/), [`agnes-2.5-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/agnes-2.5-flash/), [`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/), [`beam-1.0`](https://mvalentsev.github.io/awesome-free-ai-coding/models/beam-1.0/) (until 2026-10-22), [`jais-3-mova-36b-a4b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/jais-3-mova-36b-a4b/) (until 2026-11-05), [`k2-horizon-375b-a23b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/k2-horizon-375b-a23b/) (until 2026-11-05), [`minimax-m3.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m3.1-flash/) (until 2026-10-26), [`vast-10m-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/vast-10m-flash/) (until 2026-10-26)

## Limits, in the vendor's words

Nemotron Ultra/Super and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`

Heabsy Qwen3.8 27B: Daily usage allowance: amount not published per account; for `heabsy/qwen3.8-27b-heabsy-free`

Nemotron3.5 Super VL: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3.5-super-vl-free`

Beam 1.0: Daily usage allowance: amount not published; scope not published; for `reflection/beam-1.0-501b-a23b`

Jais 3 MoVA: Daily tokens allowance: amount not published; scope not published; for `ifm/jais-3-mova-36b-a4b`

K2 Horizon: Daily tokens allowance: amount not published; scope not published; for `ifm/k2-horizon-375b-a23b`

MiniMax M3.1 Flash: 5,000,000 tokens/day per account per model; for `minimax/minimax-m3.1-flash-free`. 00:00’da (TSİ)

Vast-10M Flash: 10,000,000 tokens/day per person; for `voltropy/vast-10m-flash-free`

Free chat rows can be called on a new account with zero balance before any top-up. Laguna XS 2.1 follows Poolside's free inference offer, without a token allowance to track. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. Heabsy requires provider-specific data-transfer consent: "Heabsy models cannot be called until your account has granted the data-transfer consent for Heabsy". Its stream is buffered until completion, and reasoning_effort is unsupported. For free Nemotron3.5 Super VL, inputs "may be retained by the provider and used to improve the model".

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://llmtr.com/en/terms), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Poolside states that prompts and completions on free access may be logged and used to improve its products.” ([source](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

## Connect

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`, `poolside/laguna-xs-2.1`, `agnes/agnes-3.0-flash`, `agnes/agnes-2.5-flash`, `heabsy/qwen3.8-27b-heabsy-free`, `nvidia/nemotron-3.5-super-vl-free`, `reflection/beam-1.0-501b-a23b`, `ifm/jais-3-mova-36b-a4b`, `ifm/k2-horizon-375b-a23b`, `minimax/minimax-m3.1-flash-free`, `voltropy/vast-10m-flash-free`
- `heabsy/qwen3.8-27b-heabsy-free`: free until 2026-11-02 00:00+03:00 ([conditions](https://llmtr.com/models/heabsy/qwen3.8-27b-heabsy-free))
- `reflection/beam-1.0-501b-a23b`: free until 2026-10-22 23:59+03:00 ([conditions](https://llmtr.com/models/reflection/beam-1.0-501b-a23b))
- `ifm/jais-3-mova-36b-a4b`: free until 2026-11-05 23:59+03:00 ([conditions](https://llmtr.com/models/ifm/jais-3-mova-36b-a4b))
- `ifm/k2-horizon-375b-a23b`: free until 2026-11-05 23:59+03:00 ([conditions](https://llmtr.com/models/ifm/k2-horizon-375b-a23b))
- `minimax/minimax-m3.1-flash-free`: free until 2026-10-26 23:59+03:00 ([conditions](https://llmtr.com/models/minimax/minimax-m3.1-flash-free))
- `voltropy/vast-10m-flash-free`: free until 2026-10-26 23:59+03:00 ([conditions](https://llmtr.com/models/voltropy/vast-10m-flash-free))
- Note: New accounts share a reduced free allowance for 24 hours. Heabsy needs Settings → Data-transfer consents; streams buffer and reasoning_effort is unsupported. Omit reasoning_effort for Nemotron3.5 Super VL; reasoning: false disables thinking. Beam always reasons (low/medium/high/xhigh/max; default max). Jais 3 accepts low/high (default high); use tool_choice: auto. K2 Horizon always reasons (medium/high). Set max_tokens for the answer and reasoning. Vast supports tools and JSON schema without reasoning; long prompts can delay the first token for minutes. Use streaming and a long timeout.

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
- Source: <https://llmtr.com/models/anthropic/claude-haiku-5.5-free>
- Source: <https://llmtr.com/docs/en/gateway/system-one/>
- Source: <https://llmtr.com/models/nace/drex-v1.0-free>
- Source: <https://llmtr.com/models/nace/drex-v1.5-free>
- Source: <https://llmtr.com/models/deepseek/deepseek-v4.1-flash-free>
- Source: <https://llmtr.com/models/heabsy/qwen3.8-27b-heabsy-free>
- Source: <https://llmtr.com/docs/en/gateway/heabsy/>
- Source: <https://llmtr.com/models/scaledown/summarize-free>
- Source: <https://llmtr.com/models/scaledown/extract-free>
- Source: <https://llmtr.com/models/scaledown/classify-free>
- Source: <https://llmtr.com/models/nvidia/nemotron-3.5-super-vl-free>
- Source: <https://llmtr.com/docs/en/gateway/nemotron-3-5-super-vl/>
- Source: <https://llmtr.com/models/reflection/beam-1.0-501b-a23b>
- Source: <https://llmtr.com/models/ifm/jais-3-mova-36b-a4b>
- Source: <https://llmtr.com/models/ifm/k2-horizon-375b-a23b>
- Source: <https://llmtr.com/models/nace/drex-max-free>
- Source: <https://llmtr.com/models/minimax/minimax-m3.1-flash-free>
- Source: <https://llmtr.com/models/voltropy/vast-10m-flash-free>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-22` — Free models changed: added minimax-m3.1-flash, vast-10m-flash
- `2026-10-19` — Free models changed: added jais-3-mova-36b-a4b, k2-horizon-375b-a23b
- `2026-10-17` — Free models changed: added beam-1.0
- `2026-10-16` — Free models changed: dropped deepseek-v4.1-flash
- `2026-10-14` — Free models changed: dropped claude-haiku-5.5
- `2026-10-13` — Free models changed: dropped ling-3.1-flash
- `2026-10-12` — Free models changed: added deepseek-v4.1-flash
- `2026-10-11` — Free models changed: added claude-haiku-5.5
- `2026-10-10` — Free models changed: dropped apodex-1.1-mini
- `2026-10-10` — Free models changed: dropped kolibri-1
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

Generated from `registry.yaml` on 2026-10-22 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
