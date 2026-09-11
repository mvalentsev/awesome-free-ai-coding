---
layout: default
title: 'Trae free tier: limits, free models, verified 2026-09-07'
description: 'Free access to frontier models in IDE. Trae publishes the free plan as words in its comparison table — "Limited usage", "Standard queue", "Autocompletion 5000 / month", "Concurrent Cloud Tasks 2" — and as numbers in the payload that table is rendered from: the same basic_usage_limit field that…'
permalink: /providers/trae/
---

{% raw %}

# Trae

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-07 · [trae.ai](https://www.trae.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free access to frontier models in IDE

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Trae publishes the free plan as words in its comparison table — "Limited usage", "Standard queue", "Autocompletion 5000 / month", "Concurrent Cloud Tasks 2" — and as numbers in the payload that table is rendered from: the same basic_usage_limit field that prints "$5 Basic usage" on Lite and "$20" on Pro reads 3 on Free, alongside auto_completion_limit 5000, advanced_model_request_limit 1000, premium_model_fast_request_limit 10, premium_model_slow_request_limit 50 and no_bonus_quota true. So the free plan is $3 of monthly Basic usage with no bonus quota, and the FAQ entry that would define Basic usage is still collapsed with its answer absent from the page (read 2026-08-14, unchanged 2026-09-10). The probe reads the payload rather than the table: the scheduled run of 2026-09-10 got a page whose payload carried the Free plan intact while the rendered table carried no "5000 / month" at all, and trae.ai answers no-store and renders per request, so the table is the half that can arrive missing. The figures are declared as machinery_keywords with their values attached, because a field name on its own outlives the plan it describes and the number the site renders from does not

## Connect

No API endpoint to paste: this row is a tool you install or sign in to.

## Evidence

- Probe: the page at <https://www.trae.ai/pricing>, anchored on `"name":"Free"`, `"basic_usage_limit":3`, `"auto_completion_limit":5000` in the page's own data
- Source: <https://www.trae.ai/pricing>

## History

- `2026-07-19` — Added to the list: Free access to frontier models in IDE

---

Generated from `registry.yaml` on 2026-09-11 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
