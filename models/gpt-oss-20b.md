---
layout: default
title: 'gpt-oss-20b free: 3 providers, limits and ids, verified 2026-09-24'
description: gpt-oss-20b is served free by Groq, NVIDIA NIM (build.nvidia.com) and Pollinations.AI. None asks for a card; Pollinations.AI answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/gpt-oss-20b/
last_modified_at: 2026-09-26
crumb: gpt-oss-20b
---

{% raw %}

# Where gpt-oss-20b is free

**3 rows on the list serve `gpt-oss-20b` free:** Groq, NVIDIA NIM (build.nvidia.com) and Pollinations.AI. None asks for a card; Pollinations.AI answers with no account at all. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Groq](https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/)

🔌 LLM APIs with free tier · no card · verified 2026-09-24 · listed since 2026-09-25

Fast inference against a free plan Groq publishes as a per-model rate table

- Limits, in the vendor's words: Groq states the free plan as a table rather than one quota, in RPM / RPD / TPM / TPD: 30 / 1K / 8K / 200K on openai/gpt-oss-120b, gpt-oss-20b, gpt-oss-safeguard-20b, qwen/qwen3.6-27b and qwen/qwen3.8-27b, 30 / 14.4K / 15K / 500K on the two meta-llama/llama-prompt-guard classifiers, 30 / 250 / 70K on groq/compound and compound-mini, 20 / 2K on the two whisper models and 10 / 100 / 1.2K / 3.6K on the two canopylabs/orpheus voices (read 2026-09-08). Those thirteen rows are the whole free plan, with no Llama among them — the Llama ids in the page's API samples are not on it. Groq calls the table "a high level summary and there may be exceptions", and points at the limits page in an account for the exact figures
- Base URL: `https://api.groq.com/openai/v1`
- Key: `GROQ_API_KEY` — get one at <https://console.groq.com/keys>
- Callable ids: `openai/gpt-oss-20b`
- What you send is not used to train models ([the vendor's words](https://console.groq.com/docs/legal/services-agreement)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · verified 2026-09-24 · listed since 2026-09-24

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

- Limits, in the vendor's words: No card; the API key needs a free NVIDIA Developer Program account verified by a code sent to your phone, and on 2026-09-25 build.nvidia.com's own list kept fourteen countries out of that step: Afghanistan, Bangladesh, Belarus, Cuba, Iran, Kazakhstan, Kyrgyzstan, North Korea, Pakistan, Russia, Syria, Tajikistan, Tanzania and Uzbekistan. The ceiling is a rate, not credits: NVIDIA's site puts it at "Up to 40 rpm" and "10,000 requests per day", adding that "Rate limits may vary by model and traffic from other users may cause throttling"; NVIDIA staff call 40 RPM "the published free-tier cap" that "is not adjustable on a per-account basis". A key can also be issued and still not answer: since June 2026 the vendor's forum has carried thread after thread of new personal keys that list the catalog and get 404 on every chat call, and NVIDIA's pinned note on account access says verification "has been challenging for both the community and NVIDIA", sending such cases to help@build.nvidia.com. Each model's page states whether its free endpoint is available or deprecated, and NVIDIA renames ids without notice, so copy them from the catalog. Read 2026-09-25
- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `openai/gpt-oss-20b`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [Pollinations.AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/pollinations/)

🔌 LLM APIs with free tier · no card · verified 2026-09-24 · listed since 2026-09-25

Legacy open text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai), on one model

- Limits, in the vendor's words: The keyless catalog publishes exactly one model and tags it with the tier it belongs to — "openai-fast", described as "GPT-OSS 20B Reasoning LLM (OVH)", tier "anonymous", aliased to openai / gpt-oss / gpt-oss-20b — and a POST with no key answered it on 2026-09-21. It is the legacy host, and the only place the offer is stated now: the API docs on the vendor's working branch describe gen.pollinations.ai alone — "Get an API key" at enter.pollinations.ai, usage billed in Pollen credits — and a keyless call there answers 401. The 1 request per 15 seconds this row used to quote came from docs on a branch the vendor stopped updating on 2026-08-04, and no current page states an anonymous rate
- Base URL: `https://text.pollinations.ai/openai`
- Key: none — the lane is anonymous
- Callable ids: `gpt-oss-20b`

## Related models

- [`gpt-oss-120b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-oss-120b/) — free at Groq, Google Antigravity, Regolo AI and OVHcloud AI Endpoints
- [`gpt-5.6-luna`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-5.6-luna/) — free at Zed

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
