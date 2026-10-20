---
layout: default
title: 'Upstage (Solar API) free tier: limits, free models, verified 2026-10-19'
description: Upstage Solar LLM API; $10 free credit on signup, no card. See the console for credit validity. After the signup credit is spent, continue with prepaid credit or pay-as-you-go billing.
permalink: /providers/upstage/
last_modified_at: 2026-10-19
crumb: Upstage (Solar API)
---

{% raw %}

# Upstage (Solar API) free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-19 · [console.upstage.ai](https://console.upstage.ai/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Upstage Solar LLM API; $10 free credit on signup, no card

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

Signup credit: $10 once per account

See the console for credit validity. After the signup credit is spent, continue with prepaid credit or pay-as-you-go billing.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.upstage.ai/terms-of-service), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “The Company shall not use Member Input/Output Data for service improvement or for training artificial intelligence models.” ([source](https://www.upstage.ai/terms-of-service)).

## Connect

- Base URL: `https://api.upstage.ai/v1`
- Key: `UPSTAGE_API_KEY` — get one at <https://console.upstage.ai/api-keys>
- Callable ids: `solar-pro4`, `solar-mini4`

Try it from your terminal with your key in `UPSTAGE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.upstage.ai/v1/chat/completions \
  -H "Authorization: Bearer $UPSTAGE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"solar-pro4","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://console.upstage.ai/docs/getting-started>, anchored on `$10 in free credit` in the page's own data
- Source: <https://console.upstage.ai/docs/getting-started>
- Source: <https://console.upstage.ai/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: dropped solar-mini, solar-pro-3
- `2026-07-19` — Free models changed: added solar-mini, solar-pro-3
- `2026-07-19` — Added: Upstage Solar LLM API; $10 free credit on signup, no card

---

Generated from `registry.yaml` on 2026-10-20 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
