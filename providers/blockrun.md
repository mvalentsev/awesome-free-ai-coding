---
layout: default
title: 'BlockRun (free models) free tier: limits, free models, verified 2026-11-19'
description: Keyless OpenAI-compatible chat and tools. Both IP limits apply across the free lane. The gateway can substitute another free model when an upstream is unavailable. Read the response model and X-Fallback-Model to see which model answered. Paid models use a separate x402 payment flow.
permalink: /providers/blockrun/
last_modified_at: 2026-11-19
crumb: BlockRun (free models)
---

{% raw %}

# BlockRun (free models) free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-11-19, a regular row from the first probe it passes on or after 2026-12-03 · **live** — last verified by a probe on 2026-11-19 · [blockrun.ai](https://blockrun.ai/free) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Keyless OpenAI-compatible chat and tools

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

30 requests/minute; 300 requests/hour per IP

Both IP limits apply across the free lane. The gateway can substitute another free model when an upstream is unavailable. Read the response model and X-Fallback-Model to see which model answered. Paid models use a separate x402 payment flow.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://blockrun.ai/terms), read 2026-11-19).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Free models run on free tiers whose terms may let the host use prompts to improve its service” ([source](https://blockrun.ai/privacy)).

## Connect

- Base URL: `https://blockrun.ai/api/v1`
- Key: none — the lane is anonymous
- Callable ids: `nvidia/muse-glimmer-30b`, `nvidia/nemotron-3.5-bolt`, `poolside/laguna-xs-2.1`
- Note: Use the listed IDs against the BlockRun base URL. The response names the model that handled the request. A 429 can signal an IP limit or exhausted upstream capacity. Follow Retry-After.

Try it from your terminal — the lane takes no key:

```sh
curl -s https://blockrun.ai/api/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"poolside/laguna-xs-2.1","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://blockrun.ai/api/v1/models>, each listed family checked for a zero price
- Source: <https://blockrun.ai/docs/api-reference/models>
- Source: <https://blockrun.ai/docs/api-reference/chat-completions>
- Source: <https://blockrun.ai/docs/api-reference/rate-limits>
- Source: <https://blockrun.ai/docs/getting-started/sdk-developers>
- Source: <https://blockrun.ai/faq>
- Source: <https://blockrun.ai/privacy>
- Source: <https://blockrun.ai/terms>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-19` — Added: Keyless OpenAI-compatible chat and tools

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
