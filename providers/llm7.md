---
layout: default
title: 'LLM7.io free tier: limits, free models, verified 2026-10-01'
description: 'OpenAI-compatible API with a free dashboard token and a recurring allowance of 100,000 input plus output tokens per day on eligible turbo models. The limits page now lists Free token and Pro, with no anonymous plan: a free token allows 1 request a second, 60 a minute, 250 an hour and "100,000…'
permalink: /providers/llm7/
last_modified_at: 2026-10-01
crumb: LLM7.io
---

{% raw %}

# LLM7.io free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-01 · [llm7.io](https://llm7.io) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible API with a free dashboard token and a recurring allowance of 100,000 input plus output tokens per day on eligible turbo models

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The limits page now lists Free token and Pro, with no anonymous plan: a free token allows 1 request a second, 60 a minute, 250 an hour and "100,000 tokens per 24 hours". "Free-token quotas are provided at no charge and may be reduced without notice". The quickstart requires a token from dash.llm7.io. "`turbo` models are fast models available with free API tokens", while the Models API defines usage_based_only as paid usage; turbo alone does not establish free eligibility. Pro is $12 a month. The operator publishes terms, last updated 9 August 2026, and names no upstream for any model. Read 2026-10-01

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://github.com/chigwell/llm7.io/blob/main/TERMS.md), read 2026-09-26).

## Connect

- Base URL: `https://api.llm7.io/v1`
- Key: `LLM7_API_KEY` — get one at <https://dash.llm7.io>
- Callable ids: `codestral-latest`, `mistral-Nemo-Instruct-2407`, `minimax-m2.7`
- Note: get a free token at dash.llm7.io; current docs require it. The three ids remain turbo with usage_based_only false on 2026-10-01. Their anonymous completions were observed on 2026-09-29, but current authenticated access was not called without a personal token. They stay out of the Models column: the limits probe names no model and the catalog publishes balance-accounting prices. The former anonymous allowance is no longer documented

Try it from your terminal with your key in `LLM7_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.llm7.io/v1/chat/completions \
  -H "Authorization: Bearer $LLM7_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"codestral-latest","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.llm7.io/limits.md>, anchored on `Free token`, `100,000 tokens per 24 hours`, `provided at no charge`; ids checked in <https://api.llm7.io/v1/models>
- Source: <https://docs.llm7.io/limits.md>
- Source: <https://docs.llm7.io/guides/models.md>
- Source: <https://docs.llm7.io/quickstart.md>
- Source: <https://github.com/chigwell/llm7.io/blob/main/TERMS.md>
- Source: <https://docs.llm7.io/guides/models-api.md>
- Source: <https://api.llm7.io/v1/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-16` — Added: OpenAI-compatible API with an anonymous tier — no account, no key — of 500,000 tokens a day on its turbo models, GLM 5.3 Flash, MiniMax M2.7 and Codestral among them; a free token doubles it

---

Generated from `registry.yaml` on 2026-10-01 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
