---
layout: default
title: 'Bytez free tier: limits, free models, verified 2026-09-24'
description: Serverless API over open models, whose Free plan grants $1 of credit every four weeks for open models of up to 7B parameters, one request at a time, with no billing. The billing page's Free card reads "$0 / month - Get $1 in free credits", "Run open models up to 7B parameters", "1 concurrent…
permalink: /providers/bytez/
last_modified_at: 2026-09-24
crumb: Bytez
---

{% raw %}

# Bytez free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-09-17, a regular row from the first probe it passes on or after 2026-10-01 · **live** — last verified by a probe on 2026-09-24 · [bytez.com](https://bytez.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Serverless API over open models, whose Free plan grants $1 of credit every four weeks for open models of up to 7B parameters, one request at a time, with no billing

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

The billing page's Free card reads "$0 / month - Get $1 in free credits", "Run open models up to 7B parameters", "1 concurrent request (open models)" and "Credits refresh every 4 weeks", and the billing cycle adds that "Credits expire 4 weeks after grant", with no billing on the plan. The card also lists "Access all closed model providers", but the get-started guide says a closed-source model needs "an account with the model provider" and is "billed directly by the provider", so the free dollar reaches only the open models of 7B parameters or fewer — Qwen3 4B, the docs' own example, is one. An open model above 7B needs at least $10 of credit bought in the last four weeks, on the $3 a month plan. Read 2026-09-17

## Connect

- Base URL: `https://api.bytez.com/models/v2/openai/v1`
- Key: `BYTEZ_API_KEY` — get one at <https://bytez.com/api>
- Callable ids: `Qwen/Qwen3-4B`
- Note: model ids are Hugging Face ids, Qwen/Qwen3-4B being the docs' example; the OpenAI SDK examples pass the key as the api key and the docs' curl sends it bare in Authorization. /v1/models answers 401 without a key, and closed-source models need a provider key of your own

## Evidence

- Probe: the page at <https://docs.bytez.com/model-api/docs/billing.md>, anchored on `$0 / month - Get $1 in free credits`, `Run open models up to 7B parameters`
- Source: <https://docs.bytez.com/model-api/docs/billing.md>
- Source: <https://docs.bytez.com/model-api/docs/billing>
- Source: <https://docs.bytez.com/model-api/docs/get-started.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: Serverless API over open models, whose Free plan grants $1 of credit every four weeks for open models of up to 7B parameters, one request at a time, with no billing

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
