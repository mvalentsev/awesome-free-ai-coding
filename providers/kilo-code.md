---
layout: default
title: 'Kilo Code free tier: limits, free models, verified 2026-09-21'
description: 'Open-source VS Code / JetBrains / CLI agent whose $0 plan routes "Auto Free" to the models the Kilo Gateway marks free; the same gateway serves them to any OpenAI client without a key, with BYOK and local models alongside. $0 a month, and no account for the free lane: "The gateway allows…'
permalink: /providers/kilo-code/
---

{% raw %}

# Kilo Code

🤖 Coding agents & CLIs · no card · **live** — last verified by a probe on 2026-09-21 · [kilo.ai](https://kilo.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source VS Code / JetBrains / CLI agent whose $0 plan routes "Auto Free" to the models the Kilo Gateway marks free; the same gateway serves them to any OpenAI client without a key, with BYOK and local models alongside

## Free models

`nemotron-3-ultra`, `nemotron-3-super`, `north-mini-code`, `step-3.7-flash`, `laguna-s-2.1`, `laguna-xs-2.1`

## Limits, in the vendor's words

$0 a month, and no account for the free lane: "The gateway allows unauthenticated access for free models only. Anonymous requests are identified by IP address and are subject to rate limiting (200 requests per hour per IP)". The lane is whatever the gateway marks isFree — 21 ids on 2026-09-21, Nemotron 3 Ultra, Step 3.7 Flash and Laguna S 2.1 among them — and it rotates within days, so an id waits two weeks before it joins the Models column. It costs something other than money: every free id carries mayTrainOnYourPrompts, which almost no metered id does. Auto Free routes over the free models the catalog's autoRouting list names. Everything else runs on pay-as-you-go credits or a Kilo Pass subscription. Read 2026-09-21

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Prompts may be logged by the upstream provider and used to improve their services.” ([source](https://api.kilo.ai/api/gateway/models)).

## Connect

- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Callable ids: `kilo-auto/free`, `openrouter/free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3.5-lightning:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `nvidia/nemotron-3.5-content-safety:free`, `cohere/north-mini-code:free`, `stepfun/step-3.7-flash:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `liquid/lfm-2.5-2.6b:free`, `inclusionai/ling-3.0-flash-fin:free`, `inclusionai/ling-3.0-flash-sante:free`, `dots-studio/dots-3-note-preview:free`, `thinkingmachines/inkling-small:free`, `inclusionai/ling-3.0-flash-vl:free`, `nex-agi/nex-n2.5-pro:free`, `nex-agi/nex-n2.5-mini:free`, `z-ai/glm-5.2:free`, `qwen/qwen3.8-27b:free`
- Note: no key at all for the free ids, capped at 200 requests per hour per IP; a metered id answers 401 `You need to sign in to use this model`. Every id listed is one the catalog marks isFree and mayTrainOnYourPrompts. kilo-auto/free leads because it routes over the free models the catalog's autoRouting list names; it and openrouter/free are routers and nemotron-3.5-content-safety is a guardrail classifier, so none of the three is a coding model

## Evidence

- Probe: the models catalog at <https://api.kilo.ai/api/gateway/models>, free rows carrying `:free`, every listed family required at a zero price
- Source: <https://kilo.ai/pricing>
- Source: <https://api.kilo.ai/api/gateway/models>
- Source: <https://kilo.ai/docs/gateway/authentication>
- Source: <https://kilocode.ai>

## History

- `2026-08-14` — Free models changed: dropped ling-3.0-tiny
- `2026-08-11` — Free models changed: added laguna-xs-2.1, ling-3.0-tiny, nemotron-3-super
- `2026-08-11` — Free models changed: added laguna-s-2.1, step-3.7-flash; dropped ling-3.0-flash
- `2026-08-05` — Free models changed: added ling-3.0-flash, nemotron-3-ultra, north-mini-code
- `2026-07-19` — Free models changed: dropped claude-sonnet-5, gemini-3.1-pro, gpt-5.5
- `2026-07-19` — Free models changed: added claude-sonnet-5, gemini-3.1-pro, gpt-5.5
- `2026-07-19` — Added to the list: VS Code agent extension with free starter credits

---

Generated from `registry.yaml` on 2026-09-22 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
