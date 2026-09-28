---
layout: default
title: 'qwen3.6 free: 3 providers, limits and ids, verified 2026-09-28'
description: qwen3.6 is served free by Hetzner Inference API, FreeInference (Harvard SEAS) and OVHcloud AI Endpoints. None asks for a card; OVHcloud AI Endpoints answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/qwen3.6/
last_modified_at: 2026-09-28
crumb: qwen3.6
---

{% raw %}

# Where qwen3.6 is free

**3 rows on the list serve `qwen3.6` free:** Hetzner Inference API, FreeInference (Harvard SEAS) and OVHcloud AI Endpoints. None asks for a card; OVHcloud AI Endpoints answers with no account at all. A live probe confirmed each one on 2026-09-28 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Hetzner Inference API](https://mvalentsev.github.io/awesome-free-ai-coding/providers/hetzner-inference/)

🔌 LLM APIs with free tier · no card · verified 2026-09-28 · listed since 2026-08-30

OpenAI-compatible API on Hetzner's own EU hardware, free for as long as the experiment runs

- Limits, in the vendor's words: Hetzner answers it in its own FAQ: "As long as the Inference API remains in experimental status, it is free of charge. Should this status change, we will notify you in advance via email with detailed information." Published per API key: 4M input and 100k output tokens per 60s, plus 10 requests per 60s, HTTP 429 over either. No daily, monthly or lifetime cap is published and no end date is named — the same page calls the service experimental, "provided for experimental purposes only" and offered as is, with performance and availability not guaranteed and no backups. A Hetzner account is needed to mint a token and the docs do not say whether a payment method is required; Hetzner's own fraud-prevention page offers a card charge as one of several verification routes (read 2026-08-30)
- Base URL: `https://inference.hetzner.com/api/v1`
- Key: `HETZNER_INFERENCE_API_KEY` — get one at <https://experiments.hetzner.com/inference>
- Callable ids: `Qwen/Qwen3.6-35B-A3B-FP8`
- What you send is not used to train models ([the vendor's words](https://www.hetzner.com/legal/privacy-policy/)).

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · verified 2026-09-28 · listed since 2026-09-05

Harvard SEAS's MadSys Lab serving open models free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

- Limits, in the vendor's words: No quota figure is published: the landing page says "Free to use", "No credit card required" and "Generous quota for research and prototyping", and the terms say "Quotas, rate limits, model access, and usage limits may change based on usage, demand, infrastructure capacity, abuse prevention, operational needs, and individual or aggregate activity". It is "an experimental research service", and prompts are not private: "All prompts and responses may be logged for research purposes" and "sanitized prompts and responses, usage statistics, and routing metrics — may be published or open-sourced". The models page splits the catalog: "Free accounts can use models marked Free. Models marked Pro require a Pro-enabled key" — seven chat ids Free and three Pro (glm-5.2, glm-5.3, kimi-k2.7-code), read 2026-09-05
- Base URL: `https://freeinference.org/v1`
- Key: `FREEINFERENCE_API_KEY` — get one at <https://freeinference.org>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`
- Callable ids: `qwen3.6-35b`

### [OVHcloud AI Endpoints](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ovh-ai-endpoints/)

🔌 LLM APIs with free tier · no card · verified 2026-09-28 · listed since 2026-08-19

EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller

- Limits, in the vendor's words: OVHcloud documents the anonymous lane: "Anonymous: 2 requests per minute, per IP and per model. Authenticated with an API access key: 400 requests per minute, per PCI project and per model", and its product page says "Test all our models for free in a sandbox or via the API". It is not counted per IP in practice: on 2026-09-24 one call a minute to Qwen3.8-27B from an address nothing else used answered twice in five, and each answer left `ratelimit-remaining: 0`, another caller having spent the minute's other request; the first call of a minute on six ids, and every call from a GitHub runner that morning, answered 429. The two requests a minute per model are shared by every anonymous caller. A key bills every chat model per token, Qwen3.8-27B at "0.4 € / Mtoken(input)" and "2.7 € / Mtoken(output)". Read 2026-09-24
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

Generated from `registry.yaml` on 2026-09-28 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
