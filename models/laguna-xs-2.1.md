---
layout: default
title: 'laguna-xs-2.1 free: 1 provider, limits and ids, provider probes 2026-11-02'
description: laguna-xs-2.1 is served free by NVIDIA NIM (build.nvidia.com). It asks for no card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/laguna-xs-2.1/
last_modified_at: 2026-11-02
crumb: laguna-xs-2.1
---

{% raw %}

# Where laguna-xs-2.1 is free

**One row on the list serves `laguna-xs-2.1` free:** NVIDIA NIM (build.nvidia.com). It asks for no card. The provider's last scheduled probe was on 2026-11-02; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · last probe 2026-11-02 · listed since 2026-09-22

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Published ceiling: 40 requests/minute; 10,000 requests/day per account

No card, but an API key requires an NVIDIA Developer Program account and phone verification in a supported country. Published ceilings can vary by model and traffic can cause throttling. Vendor forum reports describe new personal keys that can list models but receive 404 on chat calls; an issued key alone does not establish working inference. Model pages identify available and deprecated endpoints; copy current IDs from the catalog.

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `poolside/laguna-xs-2.1`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

## Rows that listed it before

- [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/) — listed 2026-08-11 to 2026-11-01
- [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/) — listed 2026-09-24 to 2026-11-01
- [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/) — listed 2026-09-24 to 2026-11-01
- [Nous Portal (Hermes Agent)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/) — listed 2026-09-30 to 2026-11-01
- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-09-24 to 2026-10-27

## Related models

- [`laguna-s-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-s-2.1/) — free at Vercel AI Gateway

---

Generated from `registry.yaml` on 2026-11-05 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
