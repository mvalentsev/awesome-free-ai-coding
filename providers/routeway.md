---
layout: default
title: 'Routeway free tier: limits, free models, verified 2026-09-03'
description: OpenAI-compatible gateway whose :free lane rotates — four zero-priced ids on 2026-09-05, Meta's Muse Glimmer 30B, DeepSeek V4 Flash, Kimi K2.6 and MiniMax M2.7 — beside 241 metered rows in the same catalog. Free models, meaning every id ending :free, are capped at 5 requests per minute and 200…
permalink: /providers/routeway/
---

{% raw %}

# Routeway

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-03 · [routeway.ai](https://routeway.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway whose :free lane rotates — four zero-priced ids on 2026-09-05, Meta's Muse Glimmer 30B, DeepSeek V4 Flash, Kimi K2.6 and MiniMax M2.7 — beside 241 metered rows in the same catalog

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Free models, meaning every id ending :free, are capped at 5 requests per minute and 200 requests per day and return 429 past either; on the pay-as-you-go ids beside them Routeway "does not enforce API-level rate limits", only edge DDoS protection (docs.routeway.ai rate-limits, re-read 2026-08-30). What churns here is the lane rather than the caps: ten zero-priced ids on 2026-08-14, six on 2026-08-28, three on 2026-08-30 — gemma-4-31b-it, gpt-oss-120b and muse-glimmer-30b, with step-3.7-flash and the whole Llama 3.x line gone in the two days before — six again on 2026-09-02, when deepseek-v4-flash, kimi-k2.6 and minimax-m2.7 arrived as :free ids created 2026-08-31 — and four on 2026-09-05, when gemma-4-31b-it:free and gpt-oss-120b:free, the two ids that had stood since 2026-08-14, left the lane while their metered twins stayed at $0.11/$0.33 and $0.04/$0.30 per 1M. The gateway publishes no legal entity or terms of service and is supported through Discord alone: a fallback lane, not a dependency

## Connect

- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Callable ids: `muse-glimmer-30b:free`, `deepseek-v4-flash:free`, `kimi-k2.6:free`, `minimax-m2.7:free`
- Note: the four :free ids are every zero-priced row in the catalog the probe reads (2026-09-05), all marked available, and only the :free suffix is zero-priced — the same catalog meters Claude and GPT at list rates. deepseek-v4-flash, kimi-k2.6 and minimax-m2.7 were created on 2026-08-31 with a 42,000-token context on the free lane; muse-glimmer-30b:free, created 2026-08-11, was first read here on 2026-08-28 with 131,072. The Models column is empty on purpose: gemma-4 and gpt-oss were its two families and both left on 2026-09-05, and nothing on the lane has yet stood the two weeks the column asks for — every family in it is a tripwire the api-models probe re-checks on every run, three misses archive the row, and this lane has changed on five of its last seven reads. The ids live here, and in the generated configs, until one of them stands

## Evidence

- Probe: the models catalog at <https://api.routeway.ai/v1/models>, free rows carrying `:free`, every listed family required at a zero price
- Source: <https://api.routeway.ai/v1/models>
- Source: <https://routeway.ai/docs>
- Source: <https://docs.routeway.ai/getting-started/rate-limits>

## History

- `2026-08-31` — Free models changed: dropped llama-3.3, step-3.7-flash
- `2026-08-11` — Free models changed: dropped ling-3.0-flash
- `2026-08-05` — Free models changed: added gemma-4, llama-3.3
- `2026-08-05` — Added to the list: OpenAI-compatible gateway whose catalog carries eleven live :free ids priced at zero — gpt-oss-120b, Ling 3.0 Flash, Step 3.7 Flash, Gemma 4 and the Llama 3.x line — beside a metered 100+ model catalog

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
