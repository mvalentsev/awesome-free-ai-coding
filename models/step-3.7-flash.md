---
layout: default
title: 'step-3.7-flash free: 2 providers, limits and ids, verified 2026-09-24'
description: step-3.7-flash is served free by Kilo Code and Nous Portal (Hermes Agent). None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/step-3.7-flash/
last_modified_at: 2026-09-26
crumb: step-3.7-flash
---

{% raw %}

# Where step-3.7-flash is free

**2 rows on the list serve `step-3.7-flash` free:** Kilo Code and Nous Portal (Hermes Agent). None asks for a card; Kilo Code answers with no account at all. A live probe confirmed each one on 2026-09-24 and reads them again twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/step-3-7-flash), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · verified 2026-09-24 · listed since 2026-08-11

Open-source VS Code / JetBrains / CLI agent whose $0 plan routes "Auto Free" to the models the Kilo Gateway marks free; the same gateway serves them to any OpenAI client without a key, with BYOK and local models alongside

- Limits, in the vendor's words: $0 a month, and no account for the free lane: "The gateway allows unauthenticated access for free models only. Anonymous requests are identified by IP address and are subject to rate limiting (200 requests per hour per IP)". The lane is whatever the gateway marks isFree — 21 ids on 2026-09-24, Nemotron 3 Ultra, Step 3.7 Flash and Laguna S 2.1 among them — and it rotates within days, so an id waits two weeks before it joins the Models column. It costs something other than money: every free id carries mayTrainOnYourPrompts, which almost no metered id does. Auto Free routes over the free models the catalog's autoRouting list names. Everything else runs on pay-as-you-go credits or a Kilo Pass subscription. Read 2026-09-21
- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Callable ids: `stepfun/step-3.7-flash:free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [Nous Portal (Hermes Agent)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/)

🧭 Aggregators (one key, many providers) · no card · provisional since 2026-09-16 · verified 2026-09-24 · listed since 2026-09-16

Nous Research's inference portal behind its Hermes Agent: a $0 Free plan limited to the models it prices at zero — seven on 2026-09-18, Step 3.7 Flash and Laguna S 2.1 among them — on an OpenAI-compatible API

- Limits, in the vendor's words: The portal's plan table reads "Free $0 Free models only Standard rate limits $0 monthly credits Try Hermes", and the Hermes Agent guide has you "create a Nous Portal account (or sign in), choose the Free plan, and authorize Hermes" — "The :free tag is what keeps it on the no-cost plan". No rate-limit figure is published and no page read mentions a card. The keyless catalog prices seven rows at zero; a call without a key answers HTTP 402 with a payment offer, so the free models want the portal's key. Read 2026-09-18
- Base URL: `https://inference-api.nousresearch.com/v1`
- Key: `NOUS_PORTAL_API_KEY` — get one at <https://portal.nousresearch.com>
- Callable ids: `stepfun/step-3.7-flash:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://portal.nousresearch.com/privacy)).

## Rows that listed it before

- [Kenari](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kenari/) — listed 2026-09-02 to 2026-09-16; the row itself is archived
- [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/) — listed 2026-08-05 to 2026-08-30

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
