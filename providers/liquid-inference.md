---
layout: default
title: 'Liquid Inference free tier: limits, free models, verified 2026-11-05'
description: Inference exchange where providers compete to serve API requests, with a no-card starting credit for new workspaces. The initial credit amount and expiry are not published. A separate first top-up of at least $10 earns $2; that purchase is not required for the starting credit. Each request…
permalink: /providers/liquid-inference/
last_modified_at: 2026-11-05
crumb: Liquid Inference
---

{% raw %}

# Liquid Inference free tier

🎁 Trials (no card when possible) · no card · not offered in mainland China, Russia, Iran and 3 more places · provisional — added on 2026-11-03, a regular row from the first probe it passes on or after 2026-11-17 · **live** — last verified by a probe on 2026-11-05 · [inference.ai.exchange](https://inference.ai.exchange) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Inference exchange where providers compete to serve API requests, with a no-card starting credit for new workspaces

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

New workspace credit: One-time USD allowance: amount not published; scope not published

The initial credit amount and expiry are not published. A separate first top-up of at least $10 earns $2; that purchase is not required for the starting credit. Each request reserves a price cap, then settles actual usage and the exchange fee. The winning provider sees the request under its own published terms and data policy. The exchange stores usage receipts and saved workloads; optional caches and the Auto classifier have separate handling. Four named regions of Ukraine are excluded in addition to the listed countries. Grant activation and authenticated generation have not been checked here.

## Where it is offered

Not offered in mainland China, Russia, Iran, Syria, Cuba and North Korea ([source](https://inference.ai.exchange/docs/availability.md), read 2026-11-03). That leaves out 8.3% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1).

## Connect

- Base URL: `https://router.inference.ai.exchange/v1`
- Key: `LIQUID_INFERENCE_API_KEY` — get one at <https://inference.ai.exchange>
- Callable ids: `gpt-oss-120b`
- Note: Use a workspace API key. gpt-oss-120b is a documented example and currently advertises tools; inspect /models for current supported parameters. Provider availability and capabilities vary. An explicit retention_policy of none also prevents the Auto classifier from receiving prompts.

Try it from your terminal with your key in `LIQUID_INFERENCE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://router.inference.ai.exchange/v1/chat/completions \
  -H "Authorization: Bearer $LIQUID_INFERENCE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-oss-120b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://inference.ai.exchange/docs/quickstart.md>, anchored on `A new workspace gets a starting credit`, `without a card`, `/v1/chat/completions`
- Source: <https://inference.ai.exchange/docs/quickstart.md>
- Source: <https://inference.ai.exchange/docs/fees.md>
- Source: <https://inference.ai.exchange/docs/data-handling.md>
- Source: <https://inference.ai.exchange/docs/availability.md>
- Source: <https://inference.ai.exchange/docs/provider.md>
- Source: <https://inference.ai.exchange/docs/keys.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-03` — Added: Inference exchange where providers compete to serve API requests, with a no-card starting credit for new workspaces

---

Generated from `registry.yaml` on 2026-11-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
