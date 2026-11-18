---
layout: default
title: 'Upstage (Solar API) free tier: limits, free models, verified 2026-11-09'
description: 'Approved schools, universities, hospitals and nonprofits get free API model access for up to one year. Free models: solar-pro-4. Institutional approval is required; apply to the program and receive instructions by email. Access lasts up to one year within the program usage period ending March 31…'
permalink: /providers/upstage/
last_modified_at: 2026-11-17
crumb: Upstage (Solar API)
---

{% raw %}

# Upstage (Solar API) free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-11-09; the 2 probes since have not found that evidence, and 3 misses in a row archive the row · [upstage.ai](https://www.upstage.ai/events/ai-initiative-2025-en) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Approved schools, universities, hospitals and nonprofits get free API model access for up to one year

## Free models

[`solar-pro-4`](https://mvalentsev.github.io/awesome-free-ai-coding/models/solar-pro-4/) (until 2027-03-31)

## Limits, in the vendor's words

Approved institutional access: Usage allowance: amount not published (period not published); scope not published (up to one year within the program usage period, after approval)

Institutional approval is required; apply to the program and receive instructions by email. Access lasts up to one year within the program usage period ending March 31, 2027. Numerical usage limits are not published. General API signup credit is unconfirmed; browser-only free testing and document-agent runs are separate from coding-model API access.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.upstage.ai/terms-of-service), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “The Company shall not use Member Input/Output Data for service improvement or for training artificial intelligence models.” ([source](https://www.upstage.ai/terms-of-service)).

## Connect

- Base URL: `https://api.upstage.ai/v1`
- Key: `UPSTAGE_API_KEY` — get one at <https://console.upstage.ai/api-keys>
- Callable ids: `solar-pro4`
- `solar-pro4`: free until 2027-03-31 23:00+09:00 ([conditions](https://www.upstage.ai/events/ai-initiative-2025-en))

Try it from your terminal with your key in `UPSTAGE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.upstage.ai/v1/chat/completions \
  -H "Authorization: Bearer $UPSTAGE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"solar-pro4","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.upstage.ai/events/ai-initiative-2025-en>, anchored on `Free access to AI models`, `Solar Pro 4`, `internal review and approval`, `March 31, 2027`
- Source: <https://console.upstage.ai/docs/getting-started>
- Source: <https://console.upstage.ai/>
- Source: <https://www.upstage.ai/events/ai-initiative-2025-en>
- Source: <https://www.upstage.ai/pricing>
- Source: <https://console.upstage.ai/docs/resources/faq>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-17` — Free models changed: added solar-pro-4
- `2026-09-25` — Free models changed: dropped solar-mini, solar-pro-3
- `2026-07-19` — Free models changed: added solar-mini, solar-pro-3
- `2026-07-19` — Added: Upstage Solar LLM API; $10 free credit on signup, no card

---

Generated from `registry.yaml` on 2026-11-18 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
