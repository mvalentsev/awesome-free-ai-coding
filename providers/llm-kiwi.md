---
layout: default
title: 'LLM.kiwi free tier: limits, free models, verified 2026-11-12'
description: Hosted OpenAI-compatible API with a no-card Free plan and an automatic model router. Sign in with Google or GitHub and create a dashboard key. Free allows three active API keys; numerical request and token budgets and reset periods are not published. Capacity, rate limits and fair use apply. The…
permalink: /providers/llm-kiwi/
last_modified_at: 2026-11-12
crumb: LLM.kiwi
---

{% raw %}

# LLM.kiwi free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-11-03, a regular row from the first probe it passes on or after 2026-11-17 · **live** — last verified by a probe on 2026-11-12 · [llm.kiwi](https://llm.kiwi) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Hosted OpenAI-compatible API with a no-card Free plan and an automatic model router

## Free models

The vendor does not identify which models the free offer includes. See Limits for the published conditions.

## Limits, in the vendor's words

Free API allowance: Usage allowance: amount not published (period not published); scope not published

Sign in with Google or GitHub and create a dashboard key. Free allows three active API keys; numerical request and token budgets and reset periods are not published. Capacity, rate limits and fair use apply. The auto router can change its underlying model. Documentation also describes hrllm, but the current public catalog does not list it. Prompts, tool inputs and outputs may be collected to deliver and secure the service; retention varies by data type. No training exclusion is established. Grant activation and authenticated generation have not been checked here.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://llm.kiwi/terms-of-service), read 2026-11-03).

## Connect

- Base URL: `https://api.llm.kiwi/v1`
- Key: `LLM_KIWI_API_KEY` — get one at <https://llm.kiwi/login>
- Callable ids: `auto`
- Note: auto is the documented default and a router, with no fixed underlying model identity. Chat Completions and streaming are documented; function tools, Responses and a fixed context window are not established. Do not assume the account can use every public catalog ID.

Try it from your terminal with your key in `LLM_KIWI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.llm.kiwi/v1/chat/completions \
  -H "Authorization: Bearer $LLM_KIWI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"auto","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.llm.kiwi/limits.md>, anchored on `LLM.kiwi is currently free to use without a credit card.`, `Free access does not mean unlimited capacity.`; ids checked in <https://api.llm.kiwi/v1/models>
- Source: <https://llm.kiwi/pricing>
- Source: <https://docs.llm.kiwi/quickstart.md>
- Source: <https://docs.llm.kiwi/limits.md>
- Source: <https://docs.llm.kiwi/models>
- Source: <https://docs.llm.kiwi/api-reference.md>
- Source: <https://api.llm.kiwi/v1/models>
- Source: <https://llm.kiwi/register>
- Source: <https://llm.kiwi/privacy-policy>
- Source: <https://llm.kiwi/terms-of-service>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-03` — Added: Hosted OpenAI-compatible API with a no-card Free plan and an automatic model router

---

Generated from `registry.yaml` on 2026-11-12 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
