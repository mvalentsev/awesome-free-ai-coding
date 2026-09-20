---
layout: default
title: 'Trae free tier: limits, free models, verified 2026-09-17'
description: AI IDE whose Free plan runs Auto mode only — no model choice — on a monthly Basic usage allowance of a few dollars and 5,000 autocompletions. Trae publishes the Free plan as words — "Auto mode only", "Limited usage", "Limited Autocomplete", "Autocompletion 5000 / month", "Concurrent Cloud Tasks…
permalink: /providers/trae/
---

{% raw %}

# Trae

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-17 · [trae.ai](https://www.trae.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

AI IDE whose Free plan runs Auto mode only — no model choice — on a monthly Basic usage allowance of a few dollars and 5,000 autocompletions

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Trae publishes the Free plan as words — "Auto mode only", "Limited usage", "Limited Autocomplete", "Autocompletion 5000 / month", "Concurrent Cloud Tasks 2" — and as numbers in the page payload, where basic_usage_limit is the dollar figure the paid plans print as "$20 usage / month". That figure depends on where the page is served: on 2026-09-16 a GitHub runner read $3 of Basic usage on Free and another network $1, with different paid-plan figures and prices too. Both versions carry 5,000 autocompletions and 1,000 advanced-model requests on Free. Auto mode picks the model, and which models it routes to is published nowhere. The probe reads the payload because trae.ai renders per request and its table can arrive without the Free column

## Connect

No API endpoint to paste: this row is a tool you install or sign in to.

## Evidence

- Probe: the page at <https://www.trae.ai/pricing>, anchored on `"name":"Free"`, `"auto_completion_limit":5000`, `"advanced_model_request_limit":1000` in the page's own data
- Source: <https://www.trae.ai/pricing>

## History

- `2026-07-19` — Added to the list: Free access to frontier models in IDE

---

Generated from `registry.yaml` on 2026-09-20 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
