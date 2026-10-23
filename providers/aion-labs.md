---
layout: default
title: 'Aion Labs free tier: limits, free models, verified 2026-10-22'
description: OpenAI-compatible text-model API with a daily credit allowance on its $0 Free tier, no card required. The reset timezone is unpublished. Request and token ceilings apply separately from the credit balance; completions are billed at each model's price. An account and API key are required. The Terms…
permalink: /providers/aion-labs/
last_modified_at: 2026-10-22
crumb: Aion Labs
---

{% raw %}

# Aion Labs free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-10-10, a regular row from the first probe it passes on or after 2026-10-24 · **live** — last verified by a probe on 2026-10-22 · [aionlabs.ai](https://www.aionlabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible text-model API with a daily credit allowance on its $0 Free tier, no card required

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

Daily credits allowance: amount not published; 15 requests/minute; 20,000 tokens/minute; 20,000 tokens/day per account

The reset timezone is unpublished. Request and token ceilings apply separately from the credit balance; completions are billed at each model's price. An account and API key are required. The Terms call free use before purchase a courtesy that may be changed or withdrawn.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.aionlabs.ai/terms/), read 2026-10-10).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “We do not use your Input or Output to train models and we do not sell them.” ([source](https://www.aionlabs.ai/terms/)).

## Connect

- Base URL: `https://api.aionlabs.ai/v1`
- Key: `AION_LABS_API_KEY` — get one at <https://www.aionlabs.ai/app/api-keys/>
- Callable ids: `aion-labs/aion-3.5`, `aion-labs/aion-3.5-mini`, `aion-labs/aion-3.0-mini`, `aion-labs/aion-3.0`, `aion-labs/aion-2.0`, `aion-labs/aion-rp-llama-3.1-8b`
- Note: Create an API key in the dashboard and send it as a bearer token with the OpenAI Chat Completions format.

Try it from your terminal with your key in `AION_LABS_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.aionlabs.ai/v1/chat/completions \
  -H "Authorization: Bearer $AION_LABS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"aion-labs/aion-3.5","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.aionlabs.ai/pricing/>, anchored on `A daily credit allowance to try agent jobs, the API, and browser chat`, `No card required`; ids checked in <https://api.aionlabs.ai/v1/models>
- Source: <https://www.aionlabs.ai/pricing/>
- Source: <https://www.aionlabs.ai/docs/>
- Source: <https://www.aionlabs.ai/docs/quickstart/>
- Source: <https://www.aionlabs.ai/docs/rate-limits/>
- Source: <https://api.aionlabs.ai/v1/models>
- Source: <https://www.aionlabs.ai/terms/>
- Source: <https://www.aionlabs.ai/privacy/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-10` — Added: OpenAI-compatible text-model API with a daily credit allowance on its $0 Free tier, no card required

---

Generated from `registry.yaml` on 2026-10-23 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
