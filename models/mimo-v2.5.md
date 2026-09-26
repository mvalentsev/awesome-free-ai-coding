---
layout: default
title: 'mimo-v2.5 free: 2 providers, limits and ids, verified 2026-09-24'
description: mimo-v2.5 is served free by opencode and AIHubMix (free models). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/mimo-v2.5/
last_modified_at: 2026-09-25
crumb: mimo-v2.5
---

{% raw %}

# Where mimo-v2.5 is free

**2 rows on the list serve `mimo-v2.5` free:** opencode and AIHubMix (free models). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/)

🤖 Coding agents & CLIs · no card · verified 2026-09-24 · listed since 2026-07-19

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.3 Contributor — inside OpenCode only, no sign-in; any provider via BYOK

- Limits, in the vendor's words: The free ids work inside OpenCode and nowhere else. Since 2026-09-17 Zen has answered every other client with `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`, and on 2026-09-18 an OpenCode maintainer wrote "You cannot use the free tier in other harnesses (this is only a limitation for the free tier nothing else)", so this row publishes no base URL. Inside OpenCode the ids are `opencode/<model-id>`, and all six answered the official 1.18.31 CLI, signed out, on 2026-09-18. Zen calls each one "available on OpenCode for a limited time", and the price is data: of the free models "collected data may be used to improve the model", the NVIDIA-backed ones are "Trial use only — do not submit personal or confidential data", and Muse Spark 1.3 Contributor trades "heavily discounted token pricing in exchange for permission to use your prompts and completions to train future Meta models". Mind the suffix: plain muse-spark-1.3 is a paid row; the contributor id's best allowed effort, xhigh, scores 45 on the Artificial Analysis Intelligence Index — max is "Standard-tier `muse-spark-1.3` only". Billing is for the metered ids. Read 2026-09-18
- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models ([the vendor's words](https://opencode.ai/docs/zen/)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-08-14

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Callable ids: `xiaomi-mimo-v2.5-free`, `xiaomi-mimo-v2.5-pro-free`

## Rows that listed it before

- [Freebuff](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/) — listed 2026-09-02 to 2026-09-22
- [Token Harbor](https://mvalentsev.github.io/awesome-free-ai-coding/providers/token-harbor/) — listed 2026-09-16 to 2026-09-22
- [MiMo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/mimo-code/) — listed 2026-07-20 to 2026-07-27; the row itself is archived

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
