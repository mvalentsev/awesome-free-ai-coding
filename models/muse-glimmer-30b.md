---
layout: default
title: 'muse-glimmer-30b free: 3 providers, limits and ids, verified 2026-10-08'
description: muse-glimmer-30b is served free by Requesty, NVIDIA NIM (build.nvidia.com) and Routeway. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/muse-glimmer-30b/
last_modified_at: 2026-10-08
crumb: muse-glimmer-30b
---

{% raw %}

# Where muse-glimmer-30b is free

**3 rows on the list serve `muse-glimmer-30b` free:** Requesty, NVIDIA NIM (build.nvidia.com) and Routeway. None asks for a card. The published offers were checked on 2026-10-08 and are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/muse-glimmer), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Requesty](https://mvalentsev.github.io/awesome-free-ai-coding/providers/requesty/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-08 · listed since 2026-09-17

OpenAI-compatible router with free models beside a metered catalog, routing, caching and fallbacks

- Limits, in the vendor's words: 200 requests/day per account

No credit card for the Free plan, which serves free models only. Routing, caching, fallbacks, spend tracking and EU data residency are included. Past the free allowance the same key moves to pay-as-you-go.
- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `nvidia/muse-glimmer-30b`
- What you send may be used to train or improve models ([the vendor's words](https://www.requesty.ai/privacy)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · verified 2026-10-08 · listed since 2026-09-24

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Published ceiling: 40 requests/minute; 10,000 requests/day per account

No card, but an API key requires an NVIDIA Developer Program account and phone verification in a supported country. Published ceilings can vary by model and traffic can cause throttling. Vendor forum reports describe new personal keys that can list models but receive 404 on chat calls; an issued key alone does not establish working inference. Model pages identify available and deprecated endpoints; copy current IDs from the catalog.

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `meta/muse-glimmer-30b`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-08 · listed since 2026-09-14

OpenAI-compatible gateway with a rotating :free chat-model lane beside metered models

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Rate-limits documentation: 5 requests/minute (published sources disagree) per account

FAQ: 20 requests/minute (published sources disagree) per account

Free models: 200 requests/day per account

The FAQ and rate-limit docs disagree on the per-minute cap; both publish the same daily cap. Free IDs end in :free, rotate and may be removed at any time. At a cap they return 429; paid twins require a positive balance. The FAQ describes signup and key creation without payment, but the older terms list a payment method and are behind a bot wall. No legal entity is named; support is email and Discord.

</details>

- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Codex CLI: [`configs/codex/routeway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/routeway.config.toml) — copy it to `~/.codex/`, then `codex -p routeway`; set up on the lane by the vendor's own page, <https://docs.routeway.ai/integrations/agents/codex>: "Use OpenAI’s Codex with Routeway by adding a custom provider"
- Callable ids: `muse-glimmer-30b:free`

## Related models

- [`muse-spark-1.3-contributor`](https://mvalentsev.github.io/awesome-free-ai-coding/models/muse-spark-1.3-contributor/) — free at opencode and Cline

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
