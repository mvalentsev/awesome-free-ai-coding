---
layout: default
title: 'llama-3.1-8b free: 2 providers, limits and ids, provider probes 2026-11-23'
description: llama-3.1-8b is served free by SimpleLLM and Kiosapi.id. None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/llama-3.1-8b/
last_modified_at: 2026-11-23
crumb: llama-3.1-8b
---

{% raw %}

# Where llama-3.1-8b is free

**2 rows on the list serve `llama-3.1-8b` free:** SimpleLLM and Kiosapi.id. None asks for a card. The providers' last scheduled probes were on 2026-11-23; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [SimpleLLM](https://mvalentsev.github.io/awesome-free-ai-coding/providers/simplellm/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-23 · listed since 2026-10-28

OpenAI-compatible chat API from Stage One Solutions UG in Germany, with enabled zero-price aliases usable without credit

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: All free models: 1 request at once per account

General: Per-minute requests allowance: see your account for values; scope not published

Free models: Hourly requests allowance: see your account for values; Daily requests allowance: see your account for values; Hourly tokens allowance: see your account for values; Daily tokens allowance: see your account for values; scope not published

An account and API key are required. The free request slot is shared across all free models and account keys, for streaming and non-streaming chat; paid requests use separate limits. Other request and token budgets depend on configuration; the authenticated rate-limit endpoint reports current minute, hourly and daily counters. Those counters do not establish one scope for every key, model and upstream limit or show whether the free slot is occupied. The public catalog can list an enabled alias whose backend is disabled, so listing does not prove a successful completion. Planned or disabled rows are excluded. Other numeric budgets and reset times are not publicly fixed.

</details>

- Base URL: `https://api.simplellm.eu/v1`
- Key: `SIMPLELLM_API_KEY` — get one at <https://simplellm.eu/docs/>
- Callable ids: `free-Llama-3.1-8B-Instruct`

### [Kiosapi.id](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kiosapi-id/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-23 · listed since 2026-11-16

Indonesian OpenAI-compatible gateway from PT Mura Teras Kreatif with a daily free allowance on selected open models, independent of its prepaid models

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free models: 50 requests/day per account. 07:00 WIB

Free rate limit: 5 requests/minute; scope not published

A verified email is required. Free requests do not spend prepaid credit and need no top-up. The daily allowance is shared across Free models. Free requests have approximately 24k input characters and 2,048 output tokens. Paid models spend the separate rupiah balance. Free inference uses Cloudflare Workers AI; upstream data policies apply. Encrypted web-chat storage does not encrypt inference processing.

</details>

- Base URL: `https://api.kiosapi.id/v1`
- Key: `KIOSAPI_ID_API_KEY` — get one at <https://kiosapi.id/dashboard/keys>
- Callable ids: `meta/llama-3.1-8b`

---

Generated from `registry.yaml` and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
