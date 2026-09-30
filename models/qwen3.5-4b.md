---
layout: default
title: 'qwen3.5-4b free: 1 provider, limits and ids, verified 2026-09-28'
description: qwen3.5-4b is served free by Mixlayer. It asks for no card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/qwen3.5-4b/
last_modified_at: 2026-09-28
crumb: qwen3.5-4b
---

{% raw %}

# Where qwen3.5-4b is free

**One row on the list serves `qwen3.5-4b` free:** Mixlayer. It asks for no card. A live probe confirmed it on 2026-09-28 and reads it again twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/qwen3-5-4b), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Mixlayer](https://mvalentsev.github.io/awesome-free-ai-coding/providers/mixlayer/)

🔌 LLM APIs with free tier · no card · provisional since 2026-09-17 · verified 2026-09-28 · listed since 2026-09-17

Serverless open models priced per token, one of them at $0 and callable without prepaid credit

- Limits, in the vendor's words: The pricing page says "Free models stay free; pay-as-you-go for everything else." and prices its one free row, qwen/qwen3.5-4b-free, at $0.00 in and out, 131K context, vision and text. The billing docs: "Free models do not require prepaid credit." — a paid model on an empty prepaid balance answers `402`. Rate limits are set per organization and per model, and "Mixlayer does not publish fixed limit values because limits can differ by organization and model". The docs' introduction sends its first request to the free model. The operator is Mixlayer Labs Inc. Read 2026-09-17
- Base URL: `https://models.mixlayer.ai/v1`
- Key: `MIXLAYER_API_KEY` — get one at <https://console.mixlayer.com/app/api-keys>
- Codex CLI: [`configs/codex/mixlayer.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/mixlayer.config.toml) — copy it to `~/.codex/`, then `codex -p mixlayer`; set up on the lane by the vendor's own page, <https://docs.mixlayer.com/codex-cli>: "A separate profile keeps Mixlayer isolated from your default Codex configuration"
- Callable ids: `qwen/qwen3.5-4b-free`
- What you send is not used to train models ([the vendor's words](https://www.mixlayer.com/privacy-policy)).

## Related models

- [`qwen3.5-122b-a10b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-122b-a10b/) — free at Alibaba Cloud Model Studio (DashScope, international) and Regolo AI
- [`qwen3.5-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-27b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.5-35b-a3b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-35b-a3b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.5-397b-a17b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-397b-a17b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.5-9b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-9b/) — free at Regolo AI

---

Generated from `registry.yaml` on 2026-09-30 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
