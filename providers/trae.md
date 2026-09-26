---
layout: default
title: 'TRAE (TraeCode) free tier: limits, free models, verified 2026-09-24'
description: TRAE's AI IDE, TraeCode, whose Free plan runs Auto mode only — no model choice — on a monthly Basic usage allowance of a few dollars and 5,000 autocompletions. Trae publishes the Free plan as words — "Auto mode only", "Limited usage", "Limited Autocomplete", "Autocompletion 5000 / month",…
permalink: /providers/trae/
last_modified_at: 2026-09-26
crumb: TRAE (TraeCode)
---

{% raw %}

# TRAE (TraeCode) free tier

🎁 Trials (no card when possible) · no card · not offered in mainland China, Russia, Canada and 11 more places · **live** — last verified by a probe on 2026-09-24 · [trae.ai](https://www.trae.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

TRAE's AI IDE, TraeCode, whose Free plan runs Auto mode only — no model choice — on a monthly Basic usage allowance of a few dollars and 5,000 autocompletions

## Free models

The vendor does not say which models the free part reaches, so the column names none.

## Limits, in the vendor's words

Trae publishes the Free plan as words — "Auto mode only", "Limited usage", "Limited Autocomplete", "Autocompletion 5000 / month", "Concurrent Cloud Tasks 2" — and as numbers in the page payload, where basic_usage_limit is the dollar figure the paid plans print as "$20 usage / month". That figure depends on where the page is served: on 2026-09-16 a GitHub runner read $3 of Basic usage on Free and another network $1, with different paid-plan figures and prices too. Both versions carry 5,000 autocompletions and 1,000 advanced-model requests on Free. Auto mode picks the model, and which models it routes to is published nowhere. The probe reads the payload because trae.ai renders per request and its table can arrive without the Free column

## Where it is offered

Offered in the 235 countries and territories its list names, not in mainland China, Russia, Canada, Hong Kong, Taiwan, Egypt, Iran, Belarus and 6 more places ([source](https://docs.trae.ai/ide/supported-countries-and-regions), read 2026-09-26). That leaves out 14.4% of the developers GitHub counts, beyond the embargoed countries most offers leave out ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “TRAE is currently available in the following countries and regions”.

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “When you use TraeCode's services, your information like your chat interactions, including related code snippets and AI-generated outputs, may be used for analytics, product improvement, and model training. … When Privacy mode is enabled, TraeCode will not use any of your chat interactions, including related code snippets and AI-generated outputs, for the above-mentioned purposes.” ([source](https://docs.trae.ai/ide/privacy-mode)).

## Connect

- No API endpoint to paste: this row is a tool you install or sign in to.

## Evidence

- Probe: the page at <https://www.trae.ai/pricing>, anchored on `"name":"Free"`, `"auto_completion_limit":5000`, `"advanced_model_request_limit":1000` in the page's own data
- Source: <https://www.trae.ai/pricing>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-07-19` — Added: Free access to frontier models in IDE

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
