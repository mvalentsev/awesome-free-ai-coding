---
layout: default
title: 'qwen3.6 free: 3 providers, limits and ids, verified 2026-10-08'
description: qwen3.6 is served free by Hetzner Inference API, FreeInference (Harvard SEAS) and OVHcloud AI Endpoints. None asks for a card; OVHcloud AI Endpoints answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/qwen3.6/
last_modified_at: 2026-10-08
crumb: qwen3.6
---

{% raw %}

# Where qwen3.6 is free

**3 rows on the list serve `qwen3.6` free:** Hetzner Inference API, FreeInference (Harvard SEAS) and OVHcloud AI Endpoints. None asks for a card; OVHcloud AI Endpoints answers with no account at all. The published offers were checked on 2026-10-08 and are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Hetzner Inference API](https://mvalentsev.github.io/awesome-free-ai-coding/providers/hetzner-inference/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-08-30

OpenAI-compatible API on Hetzner's own EU hardware, free for as long as the experiment runs

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 4,000,000 input tokens/60 seconds; 100,000 output tokens/60 seconds; 10 requests/60 seconds per key

Free while the Inference API remains experimental; Hetzner says it will email advance notice of a change. Per-key request and token windows both apply, with HTTP 429 at a cap. No daily, monthly or lifetime cap or end date is published. The service is offered as is for experimental use, without guaranteed availability or backups. Minting a token needs a Hetzner account; payment verification can include a card charge or other routes.

</details>

- Base URL: `https://inference.hetzner.com/api/v1`
- Key: `HETZNER_INFERENCE_API_KEY` — get one at <https://experiments.hetzner.com/inference>
- Callable ids: `Qwen/Qwen3.6-35B-A3B-FP8`
- What you send is not used to train models ([the vendor's words](https://www.hetzner.com/legal/privacy-policy/)).

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-05

Harvard SEAS's MadSys Lab serving open models free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Usage allowance: amount varies (period not published) per account

No card. This is an experimental research service with capacity-dependent limits. Prompts and responses may be logged for research; sanitized content, usage statistics and routing metrics may be published or open-sourced. Only models marked Free accept a Free key; Pro catalog rows need a Pro-enabled key.

</details>

- Base URL: `https://freeinference.org/v1`
- Key: `FREEINFERENCE_API_KEY` — get one at <https://freeinference.org>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`
- Callable ids: `qwen3.6-35b`

### [OVHcloud AI Endpoints](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ovh-ai-endpoints/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-08-19

EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Anonymous lane: 2 requests/minute sharing scope disputed

The documentation attributes the anonymous cap to IP and model. Tests on 2026-09-24 instead observed callers sharing a model's anonymous capacity, so its effective sharing scope remains disputed. Anonymous requests can receive 429 before a caller has spent the documented cap. Authenticated API keys are metered per token and use the paid project/model limits; they do not create a larger free allowance.

</details>

- Base URL: `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`
- Key: none — the lane is anonymous
- Callable ids: `Qwen3.6-27B`
- What you send is not used to train models ([the vendor's words](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/)).

## Rows that listed it before

- [Groq](https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/) — listed 2026-08-14 to 2026-09-27
- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-09-02 to 2026-09-21

## Related models

- [`qwen3.6-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6-27b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.6-35b-a3b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6-35b-a3b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.6-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6-max/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.6-plus`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6-plus/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
