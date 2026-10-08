---
layout: default
title: 'abliteration.ai free tier: limits, free models, verified 2026-10-08'
description: OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card. Sign in to use the preview without a card. A preview credit's fiat value is unpublished even though the organization balance…
permalink: /providers/abliteration-ai/
last_modified_at: 2026-10-08
crumb: abliteration.ai
---

{% raw %}

# abliteration.ai free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-08 · [abliteration.ai](https://abliteration.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

1 credits once per organization

Sign in to use the preview without a card. A preview credit's fiat value is unpublished even though the organization balance endpoint uses USD; no conversion is inferred. Further usage needs prepaid credit or a paid plan and is billed per token. The models stream, call tools and think before answering by default.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://abliteration.ai/terms-of-service), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Prompts, completions, and images are processed in memory and never stored by default. They are never used to train or fine-tune any model.” ([source](https://abliteration.ai/data-handling)).

## Connect

- Base URL: `https://api.abliteration.ai/v1`
- Key: `ABLITERATION_AI_API_KEY` — get one at <https://abliteration.ai/console>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.abliteration.ai`
- Codex CLI: [`configs/codex/abliteration-ai.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/abliteration-ai.config.toml) — copy it to `~/.codex/`, then `codex -p abliteration-ai`; set up on the lane by the vendor's own page, <https://docs.abliteration.ai/integrations/codex>: "To use Codex with abliteration.ai, register a custom model provider"
- Callable ids: `abliterated-model-large-v2`, `abliterated-model`, `abliterated-model-large`
- Note: ids are the three the docs' models page serves, read 2026-09-23 — abliterated-model-large the previous large model, from GLM-5.2; /v1/models answers 401 without a key. The Claude Code guide sets ANTHROPIC_BASE_URL=https://api.abliteration.ai with an ak_ key as ANTHROPIC_AUTH_TOKEN, the client appending /v1/messages

Try it from your terminal with your key in `ABLITERATION_AI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.abliteration.ai/v1/chat/completions \
  -H "Authorization: Bearer $ABLITERATION_AI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"abliterated-model-large-v2","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://abliteration.ai/pricing>, anchored on `You can start with a one-credit free preview and no credit card`
- Source: <https://abliteration.ai/pricing>
- Source: <https://docs.abliteration.ai/models.md>
- Source: <https://docs.abliteration.ai/pricing.md>
- Source: <https://docs.abliteration.ai/api-reference/credits/get-the-credit-balance-for-the-api-keys-organization.md>
- Source: <https://docs.abliteration.ai/integrations/claude-code.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card

---

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
