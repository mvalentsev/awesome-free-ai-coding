---
layout: default
title: 'agnes-3.0-flash free: 2 providers, limits and ids, provider probes 2026-10-13'
description: agnes-3.0-flash is served free by LLMTR and Agnes AI. None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/agnes-3.0-flash/
last_modified_at: 2026-10-14
crumb: agnes-3.0-flash
---

{% raw %}

# Where agnes-3.0-flash is free

**2 rows on the list serve `agnes-3.0-flash` free:** LLMTR and Agnes AI. None asks for a card. The providers' last scheduled probes were on 2026-10-13; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-13 · listed since 2026-09-28

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Nemotron Ultra/Super and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`

DeepSeek V4.1 Flash: Daily usage allowance: amount not published per account per model; for `deepseek/deepseek-v4.1-flash-free`

Heabsy Qwen3.8 27B: Daily usage allowance: amount not published per account; for `heabsy/qwen3.8-27b-heabsy-free`

Free chat rows can be called on a new account with zero balance before any top-up. Laguna XS 2.1 follows Poolside's free inference offer, without a token allowance to track. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. Heabsy requires provider-specific data-transfer consent: "Heabsy models cannot be called until your account has granted the data-transfer consent for Heabsy". Its stream is buffered until completion, and reasoning_effort is unsupported.

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `agnes/agnes-3.0-flash`
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

### [Agnes AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/agnes-ai/)

🔌 LLM APIs with free tier · no card · last probe 2026-10-13 · listed since 2026-09-14

Agnes AI's own models behind an OpenAI-compatible API, with its Flash text models charged at zero today and image generation free beside them

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Published allowed rate: 30 requests/minute per account

Effective rate: 10 requests/minute per account

The Flash models' input, cached input and output are currently zero-priced; Pro remains metered. Zero pricing is promotional: "Promotional end dates are subject to Agnes AI platform announcements and your account bill". Allowed and effective text RPM are separate ceilings for the default user class; the account's keys share them. Image rates are separate. No daily budget is published.

</details>

- Base URL: `https://apihub.agnes-ai.com/v1`
- Key: `AGNES_AI_API_KEY` — get one at <https://platform.agnes-ai.com>
- Callable ids: `agnes-3.0-flash`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://wiki.agnes-ai.com/en/docs/privacy-policy)).

## Related models

- [`agnes-2.5-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/agnes-2.5-flash/) — free at LLMTR and Agnes AI

---

Generated from `registry.yaml` on 2026-10-15 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
