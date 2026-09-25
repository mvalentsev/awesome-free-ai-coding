---
layout: default
title: 'opencode free tier: limits, free models, verified 2026-09-24'
description: Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.3 Contributor — inside OpenCode only, no sign-in; any provider via BYOK. The free ids work inside…
permalink: /providers/opencode/
---

{% raw %}

# opencode

🤖 Coding agents & CLIs · no card · **live** — last verified by a probe on 2026-09-24 · [opencode.ai](https://opencode.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.3 Contributor — inside OpenCode only, no sign-in; any provider via BYOK

## Free models

`big-pickle`, `mimo-v2.5`, `ling-3.0-flash-fin`, `nemotron-3-ultra`, `nemotron-3.5-lightning`, `muse-spark-1.3-contributor`

## Limits, in the vendor's words

The free ids work inside OpenCode and nowhere else. Since 2026-09-17 Zen has answered every other client with `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`, and on 2026-09-18 an OpenCode maintainer wrote "You cannot use the free tier in other harnesses (this is only a limitation for the free tier nothing else)", so this row publishes no base URL. Inside OpenCode the ids are `opencode/<model-id>`, and all six answered the official 1.18.31 CLI, signed out, on 2026-09-18. Zen calls each one "available on OpenCode for a limited time", and the price is data: of the free models "collected data may be used to improve the model", the NVIDIA-backed ones are "Trial use only — do not submit personal or confidential data", and Muse Spark 1.3 Contributor trades "heavily discounted token pricing in exchange for permission to use your prompts and completions to train future Meta models". Mind the suffix: plain muse-spark-1.3 is a paid row; the contributor id's best allowed effort, xhigh, scores 45 on the Artificial Analysis Intelligence Index — max is "Standard-tier `muse-spark-1.3` only". Billing is for the metered ids. Read 2026-09-18

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “During its free period, collected data may be used to improve the model.” ([source](https://opencode.ai/docs/zen/)).

## Connect

No API endpoint to paste: this row is a tool you install or sign in to.

## Evidence

- Probe: the page at <https://opencode.ai/docs/zen/>, anchored on `big pickle`, `mimo-v2.5-free`
- Source: <https://opencode.ai/docs/zen/>
- Source: <https://opencode.ai/docs/>
- Source: <https://github.com/anomalyco/opencode/issues/49590#issuecomment-5723721001>
- Source: <https://dev.meta.ai/docs/reasoning.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-16` — Free models changed: added muse-spark-1.3-contributor
- `2026-09-14` — Free models changed: dropped muse-spark-1.2
- `2026-08-30` — Free models changed: added ling-3.0-flash-fin; dropped hy3
- `2026-08-20` — Free models changed: added muse-spark-1.2; dropped deepseek-v4-flash, laguna-s-2.1
- `2026-08-14` — Free models changed: added hy3, laguna-s-2.1, nemotron-3.5-lightning
- `2026-07-19` — Free models changed: added big-pickle, deepseek-v4-flash, mimo-v2.5, nemotron-3-ultra
- `2026-07-19` — Added: Open-source TUI agent, BYOK or free models via OpenRouter

---

Generated from `registry.yaml` on 2026-09-25 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
