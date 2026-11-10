---
layout: default
title: 'glm-4.6v-flash free: 2 providers, limits and ids, provider probes 2026-11-09'
description: glm-4.6v-flash is served free by Z.ai (Zhipu GLM) and NovAI. None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/glm-4.6v-flash/
last_modified_at: 2026-11-09
crumb: glm-4.6v-flash
---

{% raw %}

# Where glm-4.6v-flash is free

**2 rows on the list serve `glm-4.6v-flash` free:** Z.ai (Zhipu GLM) and NovAI. None asks for a card. The providers' last scheduled probes were on 2026-11-09; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Z.ai (Zhipu GLM)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zai-glm/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-09 · listed since 2026-08-14

GLM Flash models free on the API, vision included (OpenAI-compatible at api.z.ai/api/paas/v4)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free Flash models: Usage allowance: amount not published (period not published) per account

GLM-4.7-Flash, GLM-4.5-Flash and GLM-4.6V-Flash have free input and output prices. The flagship rows' limited-time-free cached-storage column does not make their input or output free. No numerical rate or usage allowance is published.

</details>

- Base URL: `https://api.z.ai/api/paas/v4`
- Key: `ZAI_GLM_API_KEY` — get one at <https://z.ai/manage-apikey/apikey-list>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.z.ai/api/anthropic`
- Callable ids: `glm-4.6v-flash`
- What you send is not used to train models ([the vendor's words](https://docs.z.ai/legal-agreement/terms-of-use)).

### [NovAI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/novai/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-11-05

Hong Kong OpenAI-compatible gateway with a recurring free allowance on selected text and vision models, separate from its signup credit

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Shared free-model calls: 10 requests/day per account (before the first completed top-up). 00:00 UTC+8

5 requests/minute per account (before the first completed top-up)

Separate signup credit: $2 once per account (valid for 14 days)

Free chat calls: Unmetered requests per account (after any completed top-up; upstream provider limits still apply)

The daily allowance is shared across free chat, image and video models; media keep separate caps after a top-up. Calls at a cap return 429 until reset. An email account and API key are required. Signup accepts selected email providers and is screened for abuse. Paid models and top-ups are optional. The gateway says it does not store or train on prompts; upstream providers apply their own policies. Users must be at least 18.

</details>

- Base URL: `https://aiapi-pro.com/v1`
- Key: `NOVAI_API_KEY` — get one at <https://aiapi-pro.com/register.html>
- Callable ids: `glm-4.6v-flash`

## Rows that listed it before

- [Vercel AI Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vercel-ai-gateway/) — listed 2026-08-14 to 2026-08-20

## Related models

- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai)
- [`glm-5.3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3-flash/) — free at opencode, NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models), ZCode (Z.ai) and FreeInference (Harvard SEAS)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models), Z.ai (Zhipu GLM), NovAI and MegaNova (requires $1 top-up)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models) and Alibaba Cloud Model Studio (DashScope, international)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international), Regolo AI and AtomCode

---

Generated from `registry.yaml` on 2026-11-10 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
