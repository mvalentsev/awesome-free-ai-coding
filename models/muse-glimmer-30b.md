---
layout: default
title: 'muse-glimmer-30b free: 3 providers, limits and ids, verified 2026-09-24'
description: muse-glimmer-30b is served free by Requesty, NVIDIA NIM (build.nvidia.com) and Routeway. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/muse-glimmer-30b/
last_modified_at: 2026-09-26
crumb: muse-glimmer-30b
---

{% raw %}

# Where muse-glimmer-30b is free

**3 rows on the list serve `muse-glimmer-30b` free:** Requesty, NVIDIA NIM (build.nvidia.com) and Routeway. None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/muse-glimmer), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Requesty](https://mvalentsev.github.io/awesome-free-ai-coding/providers/requesty/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-17

OpenAI-compatible router over a 690+ model catalog with routing, caching and fallbacks; twelve rows in it are priced 0 and the free plan is the same gateway restricted to those

- Limits, in the vendor's words: Free plan is $0 with no credit card — 200 requests a day, free models only, with routing, caching, fallbacks, spend tracking and EU data residency included; past that the same key moves to pay-as-you-go
- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `nvidia/muse-glimmer-30b`
- What you send may be used to train or improve models ([the vendor's words](https://www.requesty.ai/privacy)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · verified 2026-09-24 · listed since 2026-09-24

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

- Limits, in the vendor's words: No card; the API key needs a free NVIDIA Developer Program account verified by a code sent to your phone, and on 2026-09-25 build.nvidia.com's own list kept fourteen countries out of that step: Afghanistan, Bangladesh, Belarus, Cuba, Iran, Kazakhstan, Kyrgyzstan, North Korea, Pakistan, Russia, Syria, Tajikistan, Tanzania and Uzbekistan. The ceiling is a rate, not credits: NVIDIA's site puts it at "Up to 40 rpm" and "10,000 requests per day", adding that "Rate limits may vary by model and traffic from other users may cause throttling"; NVIDIA staff call 40 RPM "the published free-tier cap" that "is not adjustable on a per-account basis". A key can also be issued and still not answer: since June 2026 the vendor's forum has carried thread after thread of new personal keys that list the catalog and get 404 on every chat call, and NVIDIA's pinned note on account access says verification "has been challenging for both the community and NVIDIA", sending such cases to help@build.nvidia.com. Each model's page states whether its free endpoint is available or deprecated, and NVIDIA renames ids without notice, so copy them from the catalog. Read 2026-09-25
- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `meta/muse-glimmer-30b`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-14

OpenAI-compatible gateway whose :free lane rotates — three zero-priced chat models on 2026-09-23, Meta's Muse Glimmer 30B, DeepSeek V4 Flash and MiniMax M2.7 — beside 269 metered rows in the same catalog

- Limits, in the vendor's words: Free models — every id ending :free — are capped at 5 requests per minute and 200 per day and answer 429 past either; the pay-as-you-go ids beside them have no API-level rate limits, only edge DDoS protection (docs.routeway.ai, read 2026-08-30). The lane itself rotates, ids joining and leaving within days while their metered twins stay. The gateway publishes no legal entity or terms of service and is supported through Discord alone: a fallback lane, not a dependency
- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Callable ids: `muse-glimmer-30b:free`

## Related models

- [`muse-spark-1.3-contributor`](https://mvalentsev.github.io/awesome-free-ai-coding/models/muse-spark-1.3-contributor/) — free at opencode and Cline
- [`muse-spark-1.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/muse-spark-1.2/) — free at Freebuff

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
