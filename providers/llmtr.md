---
layout: default
title: 'LLMTR free tier: limits, free models, verified 2026-10-26'
description: 'Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up. Free models: nemotron-3-ultra, nemotron-3-super, agnes-3.0-flash, agnes-2.5-flash, qwen3.8-27b, jais-3-mova-36b-a4b, k2-horizon-375b-a23b, minimax-m3.1-flash and 5…'
permalink: /providers/llmtr/
last_modified_at: 2026-10-27
crumb: LLMTR
---

{% raw %}

# LLMTR free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-26 · [llmtr.com](https://llmtr.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

## Free models

[`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/), [`nemotron-3-super`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-super/), [`agnes-3.0-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/agnes-3.0-flash/), [`agnes-2.5-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/agnes-2.5-flash/), [`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/), [`jais-3-mova-36b-a4b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/jais-3-mova-36b-a4b/) (until 2026-11-05), [`k2-horizon-375b-a23b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/k2-horizon-375b-a23b/) (until 2026-11-05), [`minimax-m3.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m3.1-flash/) (until 2026-11-02), [`intern-s2-397b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/intern-s2-397b/) (until 2026-10-31), [`atria-dawn`](https://mvalentsev.github.io/awesome-free-ai-coding/models/atria-dawn/) (until 2026-10-31), [`atria-dawn-preview`](https://mvalentsev.github.io/awesome-free-ai-coding/models/atria-dawn-preview/) (until 2026-10-31), [`agents-a1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/agents-a1/) (until 2026-10-31), [`sage-a1.5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/sage-a1.5/) (until 2026-10-31)

## Limits, in the vendor's words

Nemotron Ultra/Super and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`

Heabsy Qwen3.8 27B: Daily usage allowance: amount not published per account; for `heabsy/qwen3.8-27b-heabsy-free`

Nemotron3.5 Super VL: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3.5-super-vl-free`

Jais 3 MoVA: 200,000 tokens/day per account per model (Input and output count together; lower first-day allowance for new accounts); for `ifm/jais-3-mova-36b-a4b`. 00:00'da (TSİ)

K2 Horizon: 200,000 tokens/day per account per model (Input, output and reasoning count together; lower first-day allowance for new accounts); for `ifm/k2-horizon-375b-a23b`. 00:00'da (TSİ)

MiniMax M3.1 Flash: 5,000,000 tokens/day per account per model; for `minimax/minimax-m3.1-flash-free`. 00:00’da (TSİ)

Shanghai AI Lab models: 500,000 tokens/day sharing scope disputed (Per model; model pages say per person, the guide says per account. Input, output and reasoning count; new accounts have a lower first-day allowance.); for `internlm/intern-s2-free`, `internlm/atria-dawn-free`, `internlm/atria-dawn-preview-free`, `internlm/agents-a1-free`, `internlm/sage-a1.5-free`. 00:00'da (TSİ)

Free chat rows can be called on a new account with zero balance before any top-up. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. Heabsy requires provider-specific data-transfer consent: "Heabsy models cannot be called until your account has granted the data-transfer consent for Heabsy". Its stream is buffered until completion, and reasoning_effort is unsupported. For free Nemotron3.5 Super VL, inputs "may be retained by the provider and used to improve the model". Shanghai AI Lab prompts and completions may be logged by the provider and used to improve models.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://llmtr.com/en/terms), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Text, images and videos sent to the free row may be retained by the provider and used to improve the model” ([source](https://llmtr.com/docs/en/gateway/nemotron-3-5-super-vl/)).

## Connect

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`, `agnes/agnes-3.0-flash`, `agnes/agnes-2.5-flash`, `heabsy/qwen3.8-27b-heabsy-free`, `nvidia/nemotron-3.5-super-vl-free`, `ifm/jais-3-mova-36b-a4b`, `ifm/k2-horizon-375b-a23b`, `minimax/minimax-m3.1-flash-free`, `internlm/intern-s2-free`, `internlm/atria-dawn-free`, `internlm/atria-dawn-preview-free`, `internlm/agents-a1-free`, `internlm/sage-a1.5-free`
- `heabsy/qwen3.8-27b-heabsy-free`: free until 2026-11-02 00:00+03:00 ([conditions](https://llmtr.com/models/heabsy/qwen3.8-27b-heabsy-free))
- `ifm/jais-3-mova-36b-a4b`: free until 2026-11-05 23:59+03:00 ([conditions](https://llmtr.com/models/ifm/jais-3-mova-36b-a4b))
- `ifm/k2-horizon-375b-a23b`: free until 2026-11-05 23:59+03:00 ([conditions](https://llmtr.com/models/ifm/k2-horizon-375b-a23b))
- `minimax/minimax-m3.1-flash-free`: free until 2026-11-02 23:59+03:00 ([conditions](https://llmtr.com/models/minimax/minimax-m3.1-flash-free))
- `internlm/intern-s2-free`: free until 2026-10-31 23:59+03:00 ([conditions](https://llmtr.com/models/internlm/intern-s2-free))
- `internlm/atria-dawn-free`: free until 2026-10-31 23:59+03:00 ([conditions](https://llmtr.com/models/internlm/atria-dawn-free))
- `internlm/atria-dawn-preview-free`: free until 2026-10-31 23:59+03:00 ([conditions](https://llmtr.com/models/internlm/atria-dawn-preview-free))
- `internlm/agents-a1-free`: free until 2026-10-31 23:59+03:00 ([conditions](https://llmtr.com/models/internlm/agents-a1-free))
- `internlm/sage-a1.5-free`: free until 2026-10-31 23:59+03:00 ([conditions](https://llmtr.com/models/internlm/sage-a1.5-free))
- Note: New accounts have a lower free allowance for 24 hours. Heabsy needs Settings → Data-transfer consents, buffers streams and rejects reasoning_effort. Nemotron3.5 VL: omit reasoning_effort; reasoning: false disables thinking. Jais 3: low/high (default high), tool_choice: auto. K2 Horizon: medium/high; thinking is mandatory. Shanghai AI Lab: use reasoning: false; omit reasoning_effort. Intern-S2 (397B) requires tool_choice: auto and has no response_format. Include reasoning in max_tokens.

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
- Source: <https://llmtr.com/models/internlm/intern-s2-free>
- Source: <https://llmtr.com/models/internlm/atria-dawn-free>
- Source: <https://llmtr.com/models/internlm/atria-dawn-preview-free>
- Source: <https://llmtr.com/models/internlm/agents-a1-free>
- Source: <https://llmtr.com/models/internlm/sage-a1.5-free>
- Source: <https://llmtr.com/models/baseten/elephant-1-free>
- Source: <https://llmtr.com/models/baseten/mammoth-1-free>
- Source: <https://llmtr.com/blog/shanghai-ai-lab-modelleri-intern-s2-atria-dawn-agents-a1-sage>
- Source: <https://llmtr.com/blog/shanghai-ai-lab-modellerinde-dusunmeyi-kapatma>
- Source: <https://llmtr.com/blog/shanghai-ai-lab-modelleri-1-kasim-2026-sonrasi>
- Source: <https://llmtr.com/blog/arapca-dil-modeli-api-jais-3>
- Source: <https://llmtr.com/blog/k2-horizon-reasoning-effort-max-tokens>
- Source: <https://llmtr.com/blog/jais-3-vs-k2-horizon>
- Source: <https://llmtr.com/models/poolside/laguna-xs-2.1>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-27` — Free models changed: dropped laguna-xs-2.1
- `2026-10-26` — Free models changed: dropped vast-10m-flash
- `2026-10-23` — Free models changed: added agents-a1, atria-dawn, atria-dawn-preview, intern-s2-397b, sage-a1.5
- `2026-10-22` — Free models changed: dropped beam-1.0
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

Generated from `registry.yaml` on 2026-10-28 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
