---
layout: default
title: 'MegaNova free tier: limits, free models, verified 2026-10-05'
description: 'OpenAI-compatible gateway with daily free model quotas: no-card Tier 1, plus additional free access after a one-time deposit. Free models: mistral-small-3.2, glm-4.7-flash. Tier 1 is "Free registration — no credit card required", with "Free Access Models (<100B), including Manta Mini". The Free…'
permalink: /providers/meganova/
last_modified_at: 2026-10-05
crumb: MegaNova
---

{% raw %}

# MegaNova free tier

🧭 Aggregators (one key, many providers) · no card · not offered in Hong Kong, Venezuela, Azerbaijan and 40 more places · **live** — last verified by a probe on 2026-10-05 · [meganova.ai](https://meganova.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway with daily free model quotas: no-card Tier 1, plus additional free access after a one-time deposit

## Free models

`mistral-small-3.2`, [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) (requires $1 top-up)

## Limits, in the vendor's words

Tier 1 is "Free registration — no credit card required", with "Free Access Models (<100B), including Manta Mini". The Free Model Quota table gives a Tier 1 account 50 requests a day ("50 RPD (Requests Per Day)") on each of Mistral-Small-3.2-24B, Manta Mini and Manta Flash, and on several roleplay fine-tunes, an embedding model and a reranker — "Total Free Quota per day 550", with a "daily reset at 00:00 UTC" — and 0 on GLM-4.7-Flash and Manta Pro until a "$1 deposit" moves the account to Tier 2. The terms say "Free modules are for evaluation and interactive use only and are not designed for production or unattended batch workloads". The operator is Nebula Nova Inc., a Delaware corporation. Read 2026-09-16

## Where it is offered

Offered in the 187 countries and territories its list names, not in Hong Kong, Venezuela, Azerbaijan, Yemen, Côte d'Ivoire, Puerto Rico, DR Congo, Afghanistan and 35 more places ([source](https://docs.meganova.ai/faq/supported-countries.md), read 2026-09-26). That leaves out 2.4% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “We provide the following list of countries and territories where … services are officially supported”.

## Connect

- Base URL: `https://api.meganova.ai/v1`
- Key: `MEGANOVA_API_KEY` — get one at <https://www.meganova.ai/api-keys>
- Callable ids: `mistralai/Mistral-Small-3.2-24B-Instruct-2506`, `meganova-ai/manta-mini-1.0`, `meganova-ai/manta-flash-1.0`, `zai-org/GLM-4.7-Flash`, `meganova-ai/manta-pro-1.0`
- `zai-org/GLM-4.7-Flash`: requires $1 one-time top-up ([conditions](https://docs.meganova.ai/tiers/tier-2.md))
- `meganova-ai/manta-pro-1.0`: requires $1 one-time top-up ([conditions](https://docs.meganova.ai/tiers/tier-2.md))
- Note: Free quota is used first; paid continuation requires enabling the charge switch. Mistral tool execution failed in the tested OpenCode setup, and its LiteLLM-to-Responses path failed in Codex CLI. Manta routers may return tool requests as plain text.

Try it from your terminal with your key in `MEGANOVA_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.meganova.ai/v1/chat/completions \
  -H "Authorization: Bearer $MEGANOVA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"mistralai/Mistral-Small-3.2-24B-Instruct-2506","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.meganova.ai/v1/models>, each listed family checked for a zero price
- Source: <https://docs.meganova.ai/free-model-quota>
- Source: <https://docs.meganova.ai/tiers/tier-1.md>
- Source: <https://docs.meganova.ai/legal-docs/terms-of-service.md>
- Source: <https://api.meganova.ai/v1/models>
- Source: <https://docs.meganova.ai/tiers/tier-2.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-01` — Free models changed: added glm-4.7-flash
- `2026-09-02` — Added: OpenAI-compatible gateway whose no-card Tier 1 account gets a daily free quota on Mistral Small 3.2 and the house Manta routers — 50 a day per model, 550 across the lane

---

Generated from `registry.yaml` on 2026-10-05 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
