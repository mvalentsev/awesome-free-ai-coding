---
layout: default
title: 'gemma-4-26b-a4b free: 1 provider, limits and ids, verified 2026-09-24'
description: gemma-4-26b-a4b is served free by OpenRouter (free models). It asks for no card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/gemma-4-26b-a4b/
last_modified_at: 2026-09-26
crumb: gemma-4-26b-a4b
---

{% raw %}

# Where gemma-4-26b-a4b is free

**One row on the list serves `gemma-4-26b-a4b` free:** OpenRouter (free models). It asks for no card. A live probe confirmed it on 2026-09-24 and reads it again twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/gemma-4-26b-a4b), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-25

One API key for a rotating set of :free model variants, open-weight and stealth models among them

- Limits, in the vendor's words: 20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. Those four figures are in the page only as JS constants — FREE_MODEL_RATE_LIMIT_RPM, FREE_MODEL_NO_CREDITS_RPD, FREE_MODEL_HAS_CREDITS_RPD and FREE_MODEL_CREDITS_THRESHOLD — and the table that should show them serves empty cells to anything reading the HTML. OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", warns that a negative credit balance can produce errors "including for free models", and notes a 429 may come from the upstream provider rather than the platform (read 2026-08-14)
- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Callable ids: `google/gemma-4-26b-a4b-it:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

## Related models

- [`gemma-4-31b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemma-4-31b/) — free at OpenRouter (free models), Requesty, NVIDIA NIM (build.nvidia.com) and Opper

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
