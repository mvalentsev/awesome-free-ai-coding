---
layout: default
title: 'Poolside Platform free tier: limits, free models, verified 2026-09-24'
description: Free self-serve developer access to the Laguna coding models, direct from the vendor whose models this list already carries second-hand through OpenRouter and Kilo Gateway. Poolside publishes none. Its quickstart offers "fast, free developer access" as the recommended of four access paths, with…
permalink: /providers/poolside/
last_modified_at: 2026-09-24
crumb: Poolside Platform
---

{% raw %}

# Poolside Platform free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-24 · [poolside.ai](https://poolside.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free self-serve developer access to the Laguna coding models, direct from the vendor whose models this list already carries second-hand through OpenRouter and Kilo Gateway

## Free models

The vendor does not say which models the free part reaches, so the column names none.

## Limits, in the vendor's words

Poolside publishes none. Its quickstart offers "fast, free developer access" as the recommended of four access paths, with the organisation's own deployment a separate enterprise one, but poolside.ai/pricing is a 404 and no page on the docs site states a quota, a rate limit or a duration. Treat it as unquantified rather than as generous

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “We may use your Content to provide, maintain, improve, and develop the Products and other Poolside offerings, including training our models, unless you opt-out. … you may opt-out of Poolside using your Content for training by selecting the Training Opt-Out under User Settings” ([source](https://poolside.ai/legal/eula)).

## Connect

- Base URL: `https://inference.poolside.ai/v1`
- Key: `POOLSIDE_API_KEY` — get one at <https://platform.poolside.ai>
- Callable ids: `poolside/laguna-s-2.1`, `poolside/laguna-xs-2.1`
- Note: the two ids come from docs.poolside.ai/api/overview, a different page from the one the probe reads — the vendor documents no free-versus-paid split for Platform keys anywhere, so this row claims no free models and names none in its column. The key is created by signing in to Poolside Platform, whose dashboard sits behind a Cloudflare check no probe can read

## Evidence

- Probe: the page at <https://docs.poolside.ai/get-started/quickstart>, anchored on `Choose this option for fast, free developer access`, `fastest way to get a free Poolside API key`
- Source: <https://docs.poolside.ai/get-started/quickstart>
- Source: <https://docs.poolside.ai/api/overview>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-08-14` — Added: Free self-serve developer access to the Laguna coding models, direct from the vendor whose models this list already carries second-hand through OpenRouter and Kilo Gateway

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
