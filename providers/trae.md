---
layout: default
title: 'Trae free tier: limits, free models, verified 2026-09-14'
description: AI IDE whose Free plan runs Auto mode only — no model choice — on a monthly Basic usage allowance of a few dollars and 5,000 autocompletions. Trae publishes the Free plan as words — "Auto mode only", "Limited usage", "Limited Autocomplete", and in its comparison table "Standard queue",…
permalink: /providers/trae/
---

{% raw %}

# Trae

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-14 · [trae.ai](https://www.trae.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

AI IDE whose Free plan runs Auto mode only — no model choice — on a monthly Basic usage allowance of a few dollars and 5,000 autocompletions

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Trae publishes the Free plan as words — "Auto mode only", "Limited usage", "Limited Autocomplete", and in its comparison table "Standard queue", "Autocompletion 5000 / month" and "Concurrent Cloud Tasks 2" — and as numbers in the payload those words are rendered from, where basic_usage_limit is the field the paid plans print as "$20 usage / month". That figure is not the same on every read: on 2026-09-16 a GitHub runner's read carried 3 on Free beside Pro 20, Pro+ 90 and Ultra 400, and a read from another network carried 1 beside 20, 60 and 200, at different prices, so the Free plan is $1 to $3 of Basic usage a month depending on where the page is served. Both carried auto_completion_limit 5000, advanced_model_request_limit 1000, premium_model_fast_request_limit 10, premium_model_slow_request_limit 50 and no_bonus_quota true, and neither still has the $5 Lite plan that stood beside Pro on 2026-09-10. Auto mode picks the model, and which models it routes to is published nowhere. The probe reads the payload rather than the table: trae.ai answers no-store and renders per request — the scheduled run of 2026-09-10 got a rendered table with no "5000 / month" while the payload carried the Free plan intact, and the runner's page of 2026-09-16 was rendered with an error flag set — so the figures are machinery_keywords with their values attached, and only the ones both served versions carry

## Connect

No API endpoint to paste: this row is a tool you install or sign in to.

## Evidence

- Probe: the page at <https://www.trae.ai/pricing>, anchored on `"name":"Free"`, `"auto_completion_limit":5000`, `"advanced_model_request_limit":1000` in the page's own data
- Source: <https://www.trae.ai/pricing>

## History

- `2026-07-19` — Added to the list: Free access to frontier models in IDE

---

Generated from `registry.yaml` on 2026-09-16 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
