---
layout: default
title: 'ling-3.0-flash free: 1 provider, limits and ids, verified 2026-10-05'
description: ling-3.0-flash is served free by AIHubMix (free models). It asks for no card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/ling-3.0-flash/
last_modified_at: 2026-10-06
crumb: ling-3.0-flash
---

{% raw %}

# Where ling-3.0-flash is free

**One row on the list serves `ling-3.0-flash` free:** AIHubMix (free models). It asks for no card. The published offer was checked on 2026-10-05 and is rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/ling-3-0-flash), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself, with an Anthropic-format /v1/messages too, so a free id can back Claude Code

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex CLI"
- Callable ids: `ling-3.0-flash-free`

## Rows that listed it before

- [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/) — listed 2026-08-05 to 2026-08-11
- [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/) — listed 2026-08-05 to 2026-08-11

## Related models

- [`ling-3.0-flash-sante`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash-sante/) — free at OpenRouter (free models), Kilo Code and Nous Portal (Hermes Agent)
- [`ling-3.0-flash-fin`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash-fin/) — free at opencode and Nous Portal (Hermes Agent)
- [`ling-3.0-tiny`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-tiny/) — free at Requesty and AIHubMix (free models)
- [`ling-3.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.1-flash/) — free at LLMTR (until 2026-10-13)

---

Generated from `registry.yaml` on 2026-10-06 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
