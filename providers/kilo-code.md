---
layout: default
title: 'Kilo Code free tier: limits, free models, verified 2026-09-03'
description: Open-source VS Code / JetBrains / CLI agent; its $0 plan routes "Auto Free" to the zero-priced models the Kilo Gateway carries, and the same gateway answers any OpenAI client directly, with BYOK and local models (Ollama, LM Studio) alongside. $0/mo, no hosted credit required — the free lane is a…
permalink: /providers/kilo-code/
---

{% raw %}

# Kilo Code

🤖 Coding agents & CLIs · no card · **live** — last verified by a probe on 2026-09-03 · [kilo.ai](https://kilo.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source VS Code / JetBrains / CLI agent; its $0 plan routes "Auto Free" to the zero-priced models the Kilo Gateway carries, and the same gateway answers any OpenAI client directly, with BYOK and local models (Ollama, LM Studio) alongside

## Free models

`nemotron-3-ultra`, `nemotron-3-super`, `north-mini-code`, `step-3.7-flash`, `laguna-s-2.1`, `laguna-xs-2.1`

## Limits, in the vendor's words

$0/mo, no hosted credit required — the free lane is a rotating set of the ids the gateway itself marks isFree, 19 of them on 2026-09-05 (18 by the evening of 2026-09-02, 19 that morning, 13 on 2026-08-14), with Nemotron 3 Ultra and MiniMax M3 among them; everything else runs on pay-as-you-go credits or a Kilo Pass subscription. The lane costs something other than money: all 19 carry mayTrainOnYourPrompts, while 347 of the 352 metered ids do not — the five exceptions are stealth/* models struck under the same bargain. Two metered rows are priced 0 and marked isFree false, Google's Lyria 3 music previews, so a price of zero is not the lane here either. The rotation is quick: Ling 3.0 Flash left in 2026-08, ling-3.0-tiny:free stood in for three days and was gone by 2026-08-14, liquid/lfm-2.5-2.6b:free arrived instead, and by 2026-09-02 tencent/hy3:free had been demoted to the metered tencent/hy3 while MiniMax M3 and M2.7, Ling 3.0 Flash Fin, Dots3-Note and both Inkling sizes had arrived, LongCat 2.0 came and went inside 2026-09-02 itself, and Ling 3.0 Flash Sante, the health-tuned sibling of Flash Fin, was marked isFree by 2026-09-05

## Connect

- Base URL: `https://api.kilo.ai/api/gateway`
- Key: `KILO_CODE_API_KEY` — get one at <https://app.kilo.ai/profile>
- Callable ids: `kilo-auto/free`, `openrouter/free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3.5-lightning:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `nvidia/nemotron-3.5-content-safety:free`, `cohere/north-mini-code:free`, `stepfun/step-3.7-flash:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `liquid/lfm-2.5-2.6b:free`, `minimax/minimax-m3:free`, `minimax/minimax-m2.7:free`, `inclusionai/ling-3.0-flash-fin:free`, `inclusionai/ling-3.0-flash-sante:free`, `dots-studio/dots-3-note-preview:free`, `thinkingmachines/inkling:free`, `thinkingmachines/inkling-small:free`
- Note: every id listed is one the catalog marks isFree — the same catalog meters 352 more (2026-09-05). kilo-auto/free and openrouter/free are routers and nemotron-3.5-content-safety is a guardrail classifier, so none of the three is a coding model. These ids come and go faster than the offer does, which is why they stay here and out of the Models column — meituan/longcat-2.0-free was marked isFree on the morning of 2026-09-02 and had left the catalog by a second read that evening

## Evidence

- Probe: the models catalog at <https://api.kilo.ai/api/gateway/models>, free rows carrying `:free`, every listed family required at a zero price
- Source: <https://kilo.ai/pricing>
- Source: <https://api.kilo.ai/api/gateway/models>
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

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
