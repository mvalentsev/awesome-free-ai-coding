---
layout: default
title: 'Ollama Cloud free tier: limits, free models, verified 2026-10-26'
description: Cloud-hosted open models with a monthly starter allowance advertised in the launch announcement; current pricing instead describes pay-as-you-go usage. The August 31 announcement still advertises monthly starter usage for a starter subset, but current pricing and download guidance describe paid…
permalink: /providers/ollama-cloud/
last_modified_at: 2026-10-27
crumb: Ollama Cloud
---

{% raw %}

# Ollama Cloud free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-26 · [ollama.com](https://ollama.com/cloud) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Cloud-hosted open models with a monthly starter allowance advertised in the launch announcement; current pricing instead describes pay-as-you-go usage

## Free models

The vendor does not identify which models the free offer includes. See Limits for the published conditions.

## Limits, in the vendor's words

Advertised starter usage: Monthly credits allowance: amount not published per account

The August 31 announcement still advertises monthly starter usage for a starter subset, but current pricing and download guidance describe paid cloud usage and omit that allowance. Current Free eligibility, amount and model set remain unresolved. The announcement describes signup-date monthly resets without rollover. Confirm the allowance in your account before using a cloud model; per-token prices do not establish starter eligibility. Local model execution is a separate, free use of the software.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://ollama.com/terms), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Prompt or response data is never logged or trained on. … When Ollama partners with providers, we require no logging, no training, and zero data retention policies in place.” ([source](https://ollama.com/pricing)).

## Connect

- Base URL: `https://ollama.com/v1`
- Key: `OLLAMA_CLOUD_API_KEY` — get one at <https://ollama.com/settings/keys>
- Callable ids: none listed — Current pricing and the starter-allowance announcement conflict; confirm the allowance and eligible model IDs in your account.
- Note: An Ollama cloud API key is required. Confirm current free entitlement and select an eligible model in your account before making requests.

Check your key from your terminal — with it in `OLLAMA_CLOUD_API_KEY`, the vendor's catalog lists the models it can call:

```sh
curl -s https://ollama.com/v1/models \
  -H "Authorization: Bearer $OLLAMA_CLOUD_API_KEY"
```

## Evidence

- Probe: the page at <https://ollama.com/blog/transparent-pricing>, anchored on `The free plan now includes a small amount of monthly usage for a set of starter models.`; ids checked in <https://ollama.com/v1/models>
- Source: <https://ollama.com/cloud>
- Source: <https://ollama.com/pricing>
- Source: <https://ollama.com/blog/transparent-pricing>
- Source: <https://docs.ollama.com/cloud>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-08-14` — Free models changed: dropped gpt-oss, minimax-3, nemotron
- `2026-07-20` — Free models changed: added minimax-3, nemotron; dropped qwen3-coder
- `2026-07-19` — Added: Cloud-hosted open models with free usage tier

---

Generated from `registry.yaml` on 2026-10-30 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
