---
layout: default
title: 'Together AI (free model) free tier: limits, free models, verified 2026-11-19'
description: 'Zero-priced serverless chat after activation. Free models: ternary-bonsai-27b. Together documents prepaid activation for new organizations and suspends API access at zero balance. Funding can use a card or US bank account. The catalog prices other serverless models separately.'
permalink: /providers/together-ai/
last_modified_at: 2026-11-19
crumb: Together AI (free model)
---

{% raw %}

# Together AI (free model) free tier

🔌 LLM APIs with free tier · no card · requires $15 one-time top-up · provisional — added on 2026-11-19, a regular row from the first probe it passes on or after 2026-12-03 · **live** — last verified by a probe on 2026-11-19 · [together.ai](https://www.together.ai/models/prism-ml-ternary-bonsai-27b) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Zero-priced serverless chat after activation

## Free models

`ternary-bonsai-27b` (requires $15 top-up)

## Limits, in the vendor's words

Together documents prepaid activation for new organizations and suspends API access at zero balance. Funding can use a card or US bank account. The catalog prices other serverless models separately.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.together.ai/terms-of-service), read 2026-11-19).

## Connect

- Base URL: `https://api.together.xyz/v1`
- Key: `TOGETHER_AI_API_KEY` — get one at <https://api.together.ai/settings/api-keys>
- Callable ids: `Prism-ML/Ternary-Bonsai-27B`
- Note: Use the serverless ID as printed. The named variant is based on Qwen3.6 27B and supports function calling according to the catalog.

Try it from your terminal with your key in `TOGETHER_AI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.together.xyz/v1/chat/completions \
  -H "Authorization: Bearer $TOGETHER_AI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"Prism-ML/Ternary-Bonsai-27B","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.together.ai/docs/serverless/models>, anchored on `Prism-ML/Ternary-Bonsai-27B`
- Source: <https://www.together.ai/pricing>
- Source: <https://www.together.ai/models/prism-ml-ternary-bonsai-27b>
- Source: <https://docs.together.ai/docs/serverless/models>
- Source: <https://docs.together.ai/docs/billing-credits>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-19` — Added: Zero-priced serverless chat after activation

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
