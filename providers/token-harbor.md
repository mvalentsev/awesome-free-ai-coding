---
layout: default
title: 'Token Harbor free tier: limits, free models, verified 2026-09-24'
description: 'OpenAI- and Anthropic-compatible gateway with a standing $0 plan: a rotating lineup of :free ids on a value-based allowance per rolling 7-day period, no card. "Models on permanent free routes carry an explicit :free model ID and are listed under Free on the Models page", and "That set changes as…'
permalink: /providers/token-harbor/
last_modified_at: 2026-09-26
crumb: Token Harbor
---

{% raw %}

# Token Harbor free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-09-16, a regular row from the first probe it passes on or after 2026-09-30 · **live** — last verified by a probe on 2026-09-24 · [tokenharbor.ai](https://tokenharbor.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI- and Anthropic-compatible gateway with a standing $0 plan: a rotating lineup of :free ids on a value-based allowance per rolling 7-day period, no card

## Free models

[`deepseek-v4.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4.1-flash/)

## Limits, in the vendor's words

"Models on permanent free routes carry an explicit :free model ID and are listed under Free on the Models page", and "That set changes as models are added or retired". "Your first free request starts a personal rolling 7×24-hour period; it is not tied to a calendar week or midnight UTC. The allowance is measured by the list-price value of the work rather than a fixed number of requests" — no figure is published, and the dashboard shows only a percentage. "No per-minute request cap"; "Free routes stop accepting new requests when the period allowance is exhausted", and "Free routes never charge your balance". "No card required". "Free routes are disabled by default" until you consent to them, "Token Harbor may retain prompts and responses sent through explicit free routes after you opt in", and "Upstream providers separately process free-route content under their own terms". The operator is Token Harbor PTE. LTD., Singapore. Read 2026-09-18

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://tokenharbor.ai/terms), read 2026-09-26). In the vendor's words: “the Service is restricted and not intended for use in certain jurisdictions”.

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “After you explicitly enable free models, Token Harbor may retain, log, and analyze prompts and responses … Token Harbor may use this data for service diagnostics, safety, optimization, and model or product improvement.” ([source](https://tokenharbor.ai/terms)).

## Connect

- Base URL: `https://tokenharbor.ai/v1`
- Key: `TOKEN_HARBOR_API_KEY` — get one at <https://tokenharbor.ai/dashboard/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://tokenharbor.ai`
- Callable ids: `deepseek-v4.1-flash:free`, `mimo-v2.6-flash:free`, `qwen3.8-flash:free`
- Note: the :free suffix selects the free route, which has to be switched on in the dashboard first; /v1/models needs a key, so the ids are the ones the models page lists under Free, where qwen3.8-flash:free is marked free until 27 September. For Claude Code the docs say "a free account works" and "every gateway model works on both endpoints"

Try it from your terminal with your key in `TOKEN_HARBOR_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://tokenharbor.ai/v1/chat/completions \
  -H "Authorization: Bearer $TOKEN_HARBOR_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4.1-flash:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://tokenharbor.ai/pricing>, anchored on `Try Token Harbor with a free allowance and a rotating model lineup`, `Included every month (4 weeks)`
- Source: <https://tokenharbor.ai/pricing>
- Source: <https://tokenharbor.ai/faq>
- Source: <https://tokenharbor.ai/docs/billing/cashback>
- Source: <https://tokenharbor.ai/models?category=free>
- Source: <https://tokenharbor.ai/docs/integrations/claude-code>
- Source: <https://tokenharbor.ai/docs/api/curl>
- Source: <https://tokenharbor.ai/terms>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-22` — Free models changed: dropped deepseek-v4-flash, mimo-v2.5
- `2026-09-18` — Free models changed: added deepseek-v4-flash
- `2026-09-16` — Added: OpenAI-compatible gateway with a $0 plan: explicit :free ids for DeepSeek V4.1 Flash, DeepSeek V4 Flash and MiMo V2.5 on a value-based allowance, no card

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
