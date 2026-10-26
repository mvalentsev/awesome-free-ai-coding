---
layout: default
title: 'SimpleLLM free tier: limits, free models, verified 2026-10-26'
description: OpenAI-compatible chat API from Stage One Solutions UG in Germany, with enabled zero-price aliases usable without credit. An account and API key are required. Request and token budgets depend on configuration; the authenticated rate-limit endpoint reports current minute, hourly and daily counters…
permalink: /providers/simplellm/
last_modified_at: 2026-10-26
crumb: SimpleLLM
---

{% raw %}

# SimpleLLM free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-10-14, a regular row from the first probe it passes on or after 2026-10-28 · **live** — last verified by a probe on 2026-10-26 · [simplellm.eu](https://simplellm.eu) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible chat API from Stage One Solutions UG in Germany, with enabled zero-price aliases usable without credit

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

General: Per-minute requests allowance: see your account for values; scope not published

Free models: Hourly requests allowance: see your account for values; Daily requests allowance: see your account for values; Hourly tokens allowance: see your account for values; Daily tokens allowance: see your account for values; scope not published

An account and API key are required. Request and token budgets depend on configuration; the authenticated rate-limit endpoint reports current minute, hourly and daily counters. The docs do not establish one shared scope for every key, model and upstream limit. The public catalog can list an enabled alias whose backend is disabled, so listing does not prove a successful completion. Planned or disabled rows are excluded. Numeric free limits and reset times are not publicly fixed.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://simplellm.eu/agb), read 2026-10-14).

## Connect

- Base URL: `https://api.simplellm.eu/v1`
- Key: `SIMPLELLM_API_KEY` — get one at <https://simplellm.eu/docs/>
- Callable ids: `free-gemma-4-E4B`, `free-Llama-3.1-8B-Instruct`
- Note: Use the exact free-prefixed IDs. The public catalog gives both ordinary token prices in SimpleCredits; enabled/status and both prices are rechecked. V1 documents chat completions and SSE; tools depend on the model. Responses is undocumented and the Anthropic adapter is outside the supported V1 contract, so Codex uses the existing LiteLLM bridge. Authenticated generation has not been checked here.

Try it from your terminal with your key in `SIMPLELLM_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.simplellm.eu/v1/chat/completions \
  -H "Authorization: Bearer $SIMPLELLM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"free-gemma-4-E4B","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://simplellm.eu/api/models>, each listed family checked for a zero price
- Source: <https://simplellm.eu/docs/models.md>
- Source: <https://simplellm.eu/docs/limits.md>
- Source: <https://simplellm.eu/docs/compatibility.md>
- Source: <https://simplellm.eu/docs/billing.md>
- Source: <https://simplellm.eu/agb>
- Source: <https://simplellm.eu/impressum>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-14` — Added: OpenAI-compatible chat API from Stage One Solutions UG in Germany, with enabled zero-price aliases usable without credit

---

Generated from `registry.yaml` on 2026-10-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
