---
layout: default
title: 'beam-1.0 free: 1 provider, limits and ids, provider probes 2026-10-19'
description: beam-1.0 is served free by LLMTR. It asks for no card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/beam-1.0/
last_modified_at: 2026-10-19
crumb: beam-1.0
---

{% raw %}

# Where beam-1.0 is free

**One row on the list serves `beam-1.0` free:** LLMTR. It asks for no card. The provider's last scheduled probe was on 2026-10-19; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-19 · listed since 2026-10-17

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Nemotron Ultra/Super and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`

Heabsy Qwen3.8 27B: Daily usage allowance: amount not published per account; for `heabsy/qwen3.8-27b-heabsy-free`

Nemotron3.5 Super VL: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3.5-super-vl-free`

Beam 1.0: Daily usage allowance: amount not published; scope not published; for `reflection/beam-1.0-501b-a23b`

Jais 3 MoVA: Daily tokens allowance: amount not published; scope not published; for `ifm/jais-3-mova-36b-a4b`

K2 Horizon: Daily tokens allowance: amount not published; scope not published; for `ifm/k2-horizon-375b-a23b`

Free chat rows can be called on a new account with zero balance before any top-up. Laguna XS 2.1 follows Poolside's free inference offer, without a token allowance to track. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. Heabsy requires provider-specific data-transfer consent: "Heabsy models cannot be called until your account has granted the data-transfer consent for Heabsy". Its stream is buffered until completion, and reasoning_effort is unsupported. For free Nemotron3.5 Super VL, inputs "may be retained by the provider and used to improve the model".

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `reflection/beam-1.0-501b-a23b`
- `reflection/beam-1.0-501b-a23b`: free until 2026-10-22 23:59+03:00 ([conditions](https://llmtr.com/models/reflection/beam-1.0-501b-a23b))
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

---

Generated from `registry.yaml` on 2026-10-19 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
