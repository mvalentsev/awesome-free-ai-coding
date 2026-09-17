---
layout: default
title: 'opencode free tier: limits, free models, verified 2026-09-14'
description: Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.3 Contributor — callable from other clients too, keyless, with a session header; any provider via BYOK.…
permalink: /providers/opencode/
---

{% raw %}

# opencode

🤖 Coding agents & CLIs · no card · **live** — last verified by a probe on 2026-09-14; the probe since has not found that evidence, and 3 misses in a row archive the row · [opencode.ai](https://opencode.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.3 Contributor — callable from other clients too, keyless, with a session header; any provider via BYOK

## Free models

`big-pickle`, `mimo-v2.5`, `ling-3.0-flash-fin`, `nemotron-3-ultra`, `nemotron-3.5-lightning`, `muse-spark-1.3-contributor`

## Limits, in the vendor's words

Zen prices its free ids at zero and calls each one "available on OpenCode for a limited time". The price is data: the privacy section says of the free models that "collected data may be used to improve the model", the NVIDIA-backed ones are "Trial use only — do not submit personal or confidential data", and Muse Spark 1.3 Contributor trades "heavily discounted token pricing in exchange for permission to use your prompts and completions to train future Meta models". Mind the suffix: plain muse-spark-1.3 is a paid row, so the Models column names the contributor id, whose best allowed effort, xhigh, scores 45 on the Artificial Analysis Intelligence Index — max is "Standard-tier `muse-spark-1.3` only". Since 2026-09-07 every request for a free id must carry a stable id per conversation in x-opencode-session, a header OpenCode documents for other clients on the page of OpenCode Go, its keyed subscription: "Send a stable session ID in x-opencode-session for each conversation". The free ids need no key and no billing details; billing is for the metered ids. Read 2026-09-16

## Connect

- Base URL: `https://opencode.ai/zen/v1`
- Key: none — the lane is anonymous
- Session header: `x-opencode-session` — a stable id per conversation on every request, which the calling client sends itself; the generated LiteLLM and opencode configs leave this row out
- Callable ids: `ling-3.0-flash-fin-free`, `big-pickle`, `mimo-v2.5-free`, `nemotron-3-ultra-free`, `nemotron-3.5-lightning-free`, `muse-spark-1.3-contributor-free`
- Note: no key needed for the free ids as long as every request carries a stable id per conversation in x-opencode-session; ling-3.0-flash-fin-free answered keyless three times out of three on 2026-09-16 while big-pickle and mimo-v2.5-free answered 429 FreeUsageLimitError every time. Clients send the header themselves, so the generated LiteLLM and opencode configs leave this row out; inside OpenCode the ids are opencode/<model-id>. muse-spark-1.3-contributor-free is served on /v1/responses only

## Evidence

- Probe: the page at <https://opencode.ai/docs/zen/>, anchored on `big pickle`, `mimo-v2.5-free`; ids checked in <https://opencode.ai/zen/v1/models>
- Source: <https://opencode.ai/docs/zen/>
- Source: <https://opencode.ai/docs/>
- Source: <https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/llm/request.ts>
- Source: <https://opencode.ai/docs/go/>
- Source: <https://github.com/Kilo-Org/kilocode/issues/13723>
- Source: <https://dev.meta.ai/docs/reasoning.md>

## History

- `2026-09-17` — Free models changed: added muse-spark-1.3-contributor; dropped muse-spark-1.2
- `2026-08-31` — Free models changed: added ling-3.0-flash-fin; dropped hy3
- `2026-08-24` — Free models changed: added muse-spark-1.2; dropped deepseek-v4-flash
- `2026-08-20` — Free models changed: dropped laguna-s-2.1
- `2026-08-17` — Free models changed: added hy3, laguna-s-2.1, nemotron-3.5-lightning
- `2026-07-19` — Free models changed: added big-pickle, deepseek-v4-flash, mimo-v2.5, nemotron-3-ultra
- `2026-07-19` — Added to the list: Open-source TUI agent, BYOK or free models via OpenRouter

---

Generated from `registry.yaml` on 2026-09-17 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
