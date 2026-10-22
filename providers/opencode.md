---
layout: default
title: 'opencode free tier: limits, free models, verified 2026-10-22'
description: 'Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK. Free models: big-pickle, mimo-v2.5, nemotron-3-ultra, nemotron-3.5-lightning, mimo-v2.6-flash, longcat-2.5-preview. Free models work only inside…'
permalink: /providers/opencode/
last_modified_at: 2026-10-22
crumb: opencode
---

{% raw %}

# opencode free tier

🤖 Coding agents & CLIs · no card · **live** — last verified by a probe on 2026-10-22 · [opencode.ai](https://opencode.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK

## Free models

`big-pickle`, [`mimo-v2.5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2.5/), [`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/), [`nemotron-3.5-lightning`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3.5-lightning/), [`mimo-v2.6-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2.6-flash/), [`longcat-2.5-preview`](https://mvalentsev.github.io/awesome-free-ai-coding/models/longcat-2.5-preview/)

## Limits, in the vendor's words

Free model usage: Usage allowance: amount not published (period not published); scope not published

Free models work only inside OpenCode; other clients receive `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Use `opencode/<model-id>` and select the Free variant. Offers rotate; each named free offer is "available on OpenCode for a limited time". Collected free-model data may improve models; NVIDIA offers are trial-only and exclude personal or confidential data. Beam Free's provider does not train on inputs and retains them for 30 days; its listed territorial exclusions include Russia. Official 1.19.0 and 2.0.28 builds also returned that 403 in isolated runs on 2026-10-15.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://opencode.ai/legal/terms-of-service), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “During its free period, collected data may be used to improve the model.” ([source](https://opencode.ai/v2/docs/console/models/)).

## Connect

- No API endpoint to paste: this row is a tool you install or sign in to.

## Evidence

- Probe: the page at <https://opencode.ai/v2/docs/console/models/>, anchored on `big pickle`, `mimo-v2.5-free`
- Source: <https://opencode.ai/v2/docs/console/models/>
- Source: <https://opencode.ai/docs/>
- Source: <https://github.com/anomalyco/opencode/issues/49590#issuecomment-5723721001>
- Source: <https://dev.meta.ai/docs/reasoning.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-19` — Free models changed: dropped muse-spark-1.3-contributor
- `2026-10-15` — Free models changed: dropped ling-3.0-flash-fin
- `2026-10-11` — Free models changed: added longcat-2.5-preview
- `2026-10-06` — Free models changed: added mimo-v2.6-flash
- `2026-09-16` — Free models changed: added muse-spark-1.3-contributor
- `2026-09-14` — Free models changed: dropped muse-spark-1.2
- `2026-08-30` — Free models changed: added ling-3.0-flash-fin; dropped hy3
- `2026-08-20` — Free models changed: added muse-spark-1.2; dropped deepseek-v4-flash, laguna-s-2.1
- `2026-08-14` — Free models changed: added hy3, laguna-s-2.1, nemotron-3.5-lightning
- `2026-07-19` — Free models changed: added big-pickle, deepseek-v4-flash, mimo-v2.5, nemotron-3-ultra
- `2026-07-19` — Added: Open-source TUI agent, BYOK or free models via OpenRouter

---

Generated from `registry.yaml` on 2026-10-22 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
