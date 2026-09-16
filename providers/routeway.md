---
layout: default
title: 'Routeway free tier: limits, free models, verified 2026-09-14'
description: OpenAI-compatible gateway whose :free lane rotates — three zero-priced ids on 2026-09-16, Meta's Muse Glimmer 30B, DeepSeek V4 Flash and MiniMax M2.7 — beside 257 metered rows in the same catalog. Free models, meaning every id ending :free, are capped at 5 requests per minute and 200 requests…
permalink: /providers/routeway/
---

{% raw %}

# Routeway

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-14 · [routeway.ai](https://routeway.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway whose :free lane rotates — three zero-priced ids on 2026-09-16, Meta's Muse Glimmer 30B, DeepSeek V4 Flash and MiniMax M2.7 — beside 257 metered rows in the same catalog

## Free models

`deepseek-v4-flash`, `minimax-m2.7`, `muse-glimmer-30b`

## Limits, in the vendor's words

Free models, meaning every id ending :free, are capped at 5 requests per minute and 200 requests per day and return 429 past either; on the pay-as-you-go ids beside them Routeway "does not enforce API-level rate limits", only edge DDoS protection (docs.routeway.ai rate-limits, re-read 2026-08-30). What churns here is the lane rather than the caps: ten zero-priced ids on 2026-08-14, six on 2026-08-28, three on 2026-08-30 — gemma-4-31b-it, gpt-oss-120b and muse-glimmer-30b, with step-3.7-flash and the whole Llama 3.x line gone in the two days before — six again on 2026-09-02, when deepseek-v4-flash, kimi-k2.6 and minimax-m2.7 arrived as :free ids created 2026-08-31 — and four on 2026-09-05, when gemma-4-31b-it:free and gpt-oss-120b:free, the two ids that had stood since 2026-08-14, left the lane while their metered twins stayed at $0.11/$0.33 and $0.04/$0.30 per 1M — and three on 2026-09-14, kimi-k2.6:free having left between the 2026-09-12 and 2026-09-14 reads while the metered kimi-k2.6 stayed at $0.57/$2.85. The gateway publishes no legal entity or terms of service and is supported through Discord alone: a fallback lane, not a dependency

## Connect

- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Callable ids: `muse-glimmer-30b:free`, `deepseek-v4-flash:free`, `minimax-m2.7:free`
- Note: the three :free ids are every zero-priced row in the catalog the probe reads (2026-09-16, the same three as on 2026-09-14), all marked available, and only the :free suffix is zero-priced — the same catalog meters Claude and GPT at list rates. deepseek-v4-flash and minimax-m2.7 were created on 2026-09-01 with a 42,000-token context on the free lane, as was kimi-k2.6, the one of the three that left; muse-glimmer-30b:free, created 2026-08-11, was first read here on 2026-08-28 with 131,072 and has held through every change since, which is what put it in the Models column on 2026-09-14 — Requesty serves the same model free. The other two joined it on 2026-09-16, two weeks after the 2026-09-02 read that first found them, and each is free on another row here too — DeepSeek V4 Flash on Freebuff and FreeInference, MiniMax M2.7 on AIHubMix. The column waits those two weeks because every family in it is a tripwire the api-models probe re-checks on every run, three misses archive the row, and this lane has changed on five of its last seven reads

## Evidence

- Probe: the models catalog at <https://api.routeway.ai/v1/models>, free rows carrying `:free`, every listed family required at a zero price
- Source: <https://api.routeway.ai/v1/models>
- Source: <https://routeway.ai/docs>
- Source: <https://docs.routeway.ai/getting-started/rate-limits>

## History

- *next scheduled run* — Free models changed: added deepseek-v4-flash, minimax-m2.7
- `2026-09-14` — Free models changed: added muse-glimmer-30b
- `2026-09-07` — Free models changed: dropped gemma-4, gpt-oss
- `2026-08-31` — Free models changed: dropped llama-3.3, step-3.7-flash
- `2026-08-11` — Free models changed: dropped ling-3.0-flash
- `2026-08-05` — Free models changed: added gemma-4, llama-3.3
- `2026-08-05` — Added to the list: OpenAI-compatible gateway whose catalog carries eleven live :free ids priced at zero — gpt-oss-120b, Ling 3.0 Flash, Step 3.7 Flash, Gemma 4 and the Llama 3.x line — beside a metered 100+ model catalog

---

Generated from `registry.yaml` on 2026-09-16 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
