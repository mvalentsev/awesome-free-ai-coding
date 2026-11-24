---
layout: default
title: 'cheapllm.shop free tier: limits, free models, verified 2026-11-23'
description: 'OpenAI- and Anthropic-compatible model API with free beta access and a permanent hourly Free tier. Free models: deepseek-v4.1-flash-1017. Email registration and an API key are required; no card. "During the beta it is free and has no rate limit." The beta has no published end date. Requests may…'
permalink: /providers/cheapllm-shop/
last_modified_at: 2026-11-24
crumb: cheapllm.shop
---

{% raw %}

# cheapllm.shop free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-11-10, a regular row from the first probe it passes on or after 2026-11-24 · **live** — last verified by a probe on 2026-11-23 · [cheapllm.shop](https://cheapllm.shop) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI- and Anthropic-compatible model API with free beta access and a permanent hourly Free tier

## Free models

[`deepseek-v4.1-flash-1017`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4.1-flash-1017/)

## Limits, in the vendor's words

Minimum after-beta Free allowance: 5,000 input tokens/rolling hour; 1,000 output tokens/rolling hour per account (after the beta ends)

Email registration and an API key are required; no card. "During the beta it is free and has no rate limit." The beta has no published end date. Requests may queue for 30 seconds before a 503 with Retry-After. Charges require adding a payment method. "Free requests are for your own use only: no reselling, no proxy or pool of keys for people without their own account." Optional priority credit pays for "going ahead in the line". The operator says API prompts and answers are not stored; request metadata is retained. Signed-in browser-chat conversations are stored separately.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://cheapllm.shop/terms), read 2026-11-10).

## Connect

- Base URL: `https://cheapllm.shop/v1`
- Key: `CHEAPLLM_SHOP_API_KEY` — get one at <https://cheapllm.shop/signup>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://cheapllm.shop`
- Codex CLI: [`configs/codex/cheapllm-shop.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/cheapllm-shop.config.toml) — copy it to `~/.codex/`, then `codex -p cheapllm-shop`; set up on the lane by the vendor's own page, <https://cheapllm.shop/docs>: "Tools built for the OpenAI Responses API (Codex CLI, recent OpenAI SDK code) can call POST /v1/responses"
- Callable ids: `deepseek-v4.1-flash-1017`
- Note: Use the exact model ID with your own account key. Chat Completions supports tools and streaming; Messages and Responses adapters are documented. Responses is stateless: store and previous_response_id are not retained.

Try it from your terminal with your key in `CHEAPLLM_SHOP_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://cheapllm.shop/v1/chat/completions \
  -H "Authorization: Bearer $CHEAPLLM_SHOP_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4.1-flash-1017","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://cheapllm.shop/docs>, anchored on `Free during the beta.`, `permanent free tier`, `deepseek-v4.1-flash-1017`, `per account over a rolling hour`
- Source: <https://cheapllm.shop/docs>
- Source: <https://cheapllm.shop/integrations>
- Source: <https://cheapllm.shop/terms>
- Source: <https://cheapllm.shop/v1/models>
- Source: <https://cheapllm.shop/privacy>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-24` — Free models changed: added deepseek-v4.1-flash-1017
- `2026-11-10` — Added: OpenAI- and Anthropic-compatible model API with free beta access and a permanent hourly Free tier

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
