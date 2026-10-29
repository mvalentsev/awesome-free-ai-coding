---
layout: default
title: 'atria-dawn-preview free: 1 provider, limits and ids, provider probes 2026-10-26'
description: atria-dawn-preview is served free by LLMTR. It asks for no card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/atria-dawn-preview/
last_modified_at: 2026-10-29
crumb: atria-dawn-preview
---

{% raw %}

# Where atria-dawn-preview is free

**One row on the list serves `atria-dawn-preview` free:** LLMTR. It asks for no card. The provider's last scheduled probe was on 2026-10-26; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-10-23

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Nemotron Ultra and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `qwen/qwen3.8-27b-free`

Heabsy Qwen3.8 27B: Daily usage allowance: amount not published per account; for `heabsy/qwen3.8-27b-heabsy-free`

Nemotron3.5 Super VL: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3.5-super-vl-free`

Jais 3 MoVA: 200,000 tokens/day per account per model (Input and output count together; lower first-day allowance for new accounts); for `ifm/jais-3-mova-36b-a4b`. 00:00'da (TSİ)

K2 Horizon: 200,000 tokens/day per account per model (Input, output and reasoning count together; lower first-day allowance for new accounts); for `ifm/k2-horizon-375b-a23b`. 00:00'da (TSİ)

MiniMax M3.1 Flash: 5,000,000 tokens/day per account per model; for `minimax/minimax-m3.1-flash-free`. 00:00’da (TSİ)

Shanghai AI Lab models: 500,000 tokens/day sharing scope disputed (Per model; model pages say per person, the guide says per account. Input, output and reasoning count; new accounts have a lower first-day allowance.); for `internlm/intern-s2-free`, `internlm/atria-dawn-free`, `internlm/atria-dawn-preview-free`, `internlm/agents-a1-free`, `internlm/sage-a1.5-free`. 00:00'da (TSİ)

Free chat rows can be called on a new account with zero balance before any top-up. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. Heabsy requires provider-specific data-transfer consent: "Heabsy models cannot be called until your account has granted the data-transfer consent for Heabsy". Its stream is buffered until completion, and reasoning_effort is unsupported. For free Nemotron3.5 Super VL, inputs "may be retained by the provider and used to improve the model". Shanghai AI Lab prompts and completions may be logged by the provider and used to improve models.

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `internlm/atria-dawn-preview-free`
- `internlm/atria-dawn-preview-free`: free until 2026-10-31 23:59+03:00 ([conditions](https://llmtr.com/models/internlm/atria-dawn-preview-free))
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/nemotron-3-5-super-vl/)).

## Related models

- [`atria-dawn`](https://mvalentsev.github.io/awesome-free-ai-coding/models/atria-dawn/) — free at LLMTR (until 2026-10-31)

---

Generated from `registry.yaml` on 2026-10-29 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
