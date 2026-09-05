---
layout: default
title: 'opencode free tier: limits, free models, verified 2026-09-03'
description: Open-source TUI/desktop coding agent with six zero-priced models included via the opencode Zen gateway (Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.2 Contributor); any provider via BYOK too. Zen prices six ids at zero — big-pickle,…
permalink: /providers/opencode/
---

{% raw %}

# opencode

🤖 Coding agents & CLIs · no card · **live** — last verified by a probe on 2026-09-03 · [opencode.ai](https://opencode.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source TUI/desktop coding agent with six zero-priced models included via the opencode Zen gateway (Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.2 Contributor); any provider via BYOK too

## Free models

`big-pickle`, `mimo-v2.5`, `ling-3.0-flash-fin`, `nemotron-3-ultra`, `nemotron-3.5-lightning`, `muse-spark-1.2`

## Limits, in the vendor's words

Zen prices six ids at zero — big-pickle, mimo-v2.5-free, ling-3.0-flash-fin-free, nemotron-3-ultra-free, nemotron-3.5-lightning-free and muse-spark-1.2-contributor-free — and calls every one of them "available on OpenCode for a limited time" while the team collects feedback. That feedback is the price: the privacy section exempts each free model from Zen's zero-retention policy ("during its free period, collected data may be used to improve the model"), the two NVIDIA-backed ones are "trial use only — do not submit personal or confidential data", and the newest buys its zero with training rights — "heavily discounted token pricing in exchange for permission to use your prompts and completions to train future Meta models", on a row the pricing table still prints as Free in and Free out. Mind the suffix: plain muse-spark-1.2 is the paid row at $1.25/$4.25 per 1M tokens. Two ids left the free table by the 2026-08-20 read — deepseek-v4-flash is now metered at $0.22/$0.66 off-peak and $0.44/$1.32 peak, and laguna-s-2.1 is off the page entirely — though both -free ids are still in the catalog. Zen documents signup as "sign in to OpenCode Zen, add your billing details, and copy your API key", but the free ids answer without payment details on file — tested by hand rather than read, 2026-08-15. Billing is what the metered ids want, and once it is on, auto-reload tops the balance up by $20 whenever it falls below $5 (read 2026-08-20). The lane still counts six, but not the same six: on 2026-08-30 hy3-free was gone from the page altogether — no row in the pricing table, no id in the endpoints table, and not listed under Deprecated models either — while ling-3.0-flash-fin-free had arrived priced Free in, Free out

## Connect

- Base URL: `https://opencode.ai/zen/v1`
- Key: `OPENCODE_API_KEY` — get one at <https://opencode.ai/auth>
- Callable ids: `big-pickle`, `mimo-v2.5-free`, `ling-3.0-flash-fin-free`, `nemotron-3-ultra-free`, `nemotron-3.5-lightning-free`, `muse-spark-1.2-contributor-free`
- Note: these are the six ids Zen prices at zero; inside an opencode config the same id is written opencode/<model-id>. Every other id on the same base URL is metered. The catalog also still returns deepseek-v4-flash-free and laguna-s-2.1-free, which the pricing table stopped listing at zero — treat them as metered until it says otherwise

## Evidence

- Probe: the page at <https://opencode.ai/docs/zen/>, anchored on `big pickle`, `mimo-v2.5-free`; ids checked in <https://opencode.ai/zen/v1/models>
- Source: <https://opencode.ai/docs/zen/>
- Source: <https://opencode.ai/docs/>

## History

- `2026-08-31` — Free models changed: added ling-3.0-flash-fin; dropped hy3
- `2026-08-24` — Free models changed: added muse-spark-1.2; dropped deepseek-v4-flash
- `2026-08-20` — Free models changed: dropped laguna-s-2.1
- `2026-08-17` — Free models changed: added hy3, laguna-s-2.1, nemotron-3.5-lightning
- `2026-07-19` — Free models changed: added big-pickle, deepseek-v4-flash, mimo-v2.5, nemotron-3-ultra
- `2026-07-19` — Added to the list: Open-source TUI agent, BYOK or free models via OpenRouter

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
