---
layout: default
title: 'Kilo Code free tier: limits, free models, verified 2026-09-14'
description: Open-source VS Code / JetBrains / CLI agent; its $0 plan routes "Auto Free" to the zero-priced models the Kilo Gateway carries, and the same gateway answers any OpenAI client directly, without a key for the free ids, with BYOK and local models (Ollama, LM Studio) alongside. $0/mo, no hosted…
permalink: /providers/kilo-code/
---

{% raw %}

# Kilo Code

🤖 Coding agents & CLIs · no card · **live** — last verified by a probe on 2026-09-14 · [kilo.ai](https://kilo.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source VS Code / JetBrains / CLI agent; its $0 plan routes "Auto Free" to the zero-priced models the Kilo Gateway carries, and the same gateway answers any OpenAI client directly, without a key for the free ids, with BYOK and local models (Ollama, LM Studio) alongside

## Free models

`nemotron-3-ultra`, `nemotron-3-super`, `north-mini-code`, `step-3.7-flash`, `laguna-s-2.1`, `laguna-xs-2.1`

## Limits, in the vendor's words

$0/mo, no hosted credit required, and no account either for the free lane: "The gateway allows unauthenticated access for free models only. Anonymous requests are identified by IP address and are subject to rate limiting (200 requests per hour per IP)", Kilo's gateway docs say, and a keyless call to kilo-auto/free and to nvidia/nemotron-3-ultra-550b-a55b:free answered on 2026-09-16. The lane is a rotating set of the ids the gateway itself marks isFree, 20 of them on 2026-09-16 (19 on 2026-09-12, 20 on 2026-09-10, 17 on 2026-09-08, 19 on 2026-09-05, 18 by the evening of 2026-09-02, 19 that morning, 13 on 2026-08-14), with Nemotron 3 Ultra and Nex-N2.5-Pro among them; everything else runs on pay-as-you-go credits or a Kilo Pass subscription. The lane costs something other than money: all 20 carry mayTrainOnYourPrompts, while 353 of the 358 metered ids do not — the five exceptions are stealth/* models struck under the same bargain. Two metered rows are priced 0 and marked isFree false, Google's Lyria 3 music previews, so a price of zero is not the lane here either. Auto Free routes over five of the twenty, named in the catalog's own autoRouting list — dots-3-note-preview, ling-3.0-flash-vl, nex-n2.5-pro, nemotron-3-ultra and laguna-s-2.1 on 2026-09-16 as on 2026-09-12, where step-3.7-flash held the fifth slot on 2026-09-10. The rotation is quick, which is why the ids that come and go stay out of the Models column: Ling 3.0 Flash left in 2026-08, ling-3.0-tiny:free stood in for three days and was gone by 2026-08-14, liquid/lfm-2.5-2.6b:free arrived instead, and by 2026-09-02 tencent/hy3:free had been demoted to the metered tencent/hy3 while MiniMax M3 and M2.7, Ling 3.0 Flash Fin, Dots3-Note and both Inkling sizes had arrived; LongCat 2.0 was marked isFree on the morning of 2026-09-02 and had left the catalog by that evening; Ling 3.0 Flash Sante, the health-tuned sibling of Flash Fin, was marked isFree by 2026-09-05; MiniMax M3 and M2.7 went back to metered on 2026-09-08, the read that took the pair off OpenRouter, LLMTR and Vercel too; Nex-N2.5 in two sizes and Ling 3.0 Flash VL took free slots on 2026-09-10 and wait on a 2026-09-24 bar for a column; Inkling left on 2026-09-12 with Inkling Small staying behind while OpenRouter kept both, a withdrawal on this gateway rather than upstream; and GLM 5.2 joined by 2026-09-16, at a 32,768-token context against the 1,048,576 its metered twin carries, the same read that found it back on OpenRouter, with a 2026-09-30 bar for a column

## Connect

- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Callable ids: `kilo-auto/free`, `openrouter/free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3.5-lightning:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `nvidia/nemotron-3.5-content-safety:free`, `cohere/north-mini-code:free`, `stepfun/step-3.7-flash:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `liquid/lfm-2.5-2.6b:free`, `inclusionai/ling-3.0-flash-fin:free`, `inclusionai/ling-3.0-flash-sante:free`, `dots-studio/dots-3-note-preview:free`, `thinkingmachines/inkling-small:free`, `inclusionai/ling-3.0-flash-vl:free`, `nex-agi/nex-n2.5-pro:free`, `nex-agi/nex-n2.5-mini:free`, `z-ai/glm-5.2:free`
- Note: no key at all for the free ids — "The gateway allows unauthenticated access for free models only", identified by IP address and capped at 200 requests per hour per IP, while a metered id answers 401 `You need to sign in to use this model`. Every id listed is one the catalog marks isFree and mayTrainOnYourPrompts, twenty against 358 metered on 2026-09-16. kilo-auto/free leads because it routes over the five free models the catalog's autoRouting list names; it and openrouter/free are routers and nemotron-3.5-content-safety is a guardrail classifier, so none of the three is a coding model

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

Generated from `registry.yaml` on 2026-09-16 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
