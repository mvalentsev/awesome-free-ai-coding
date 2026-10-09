---
layout: default
title: 'qwen3.5-4b free: 2 providers, limits and ids, verified 2026-10-08'
description: qwen3.5-4b is served free by Mixlayer and SiliconFlow (China). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/qwen3.5-4b/
last_modified_at: 2026-10-08
crumb: qwen3.5-4b
---

{% raw %}

# Where qwen3.5-4b is free

**2 rows on the list serve `qwen3.5-4b` free:** Mixlayer and SiliconFlow (China). None asks for a card. The published offers were checked on 2026-10-08 and are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/qwen3-5-4b), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Mixlayer](https://mvalentsev.github.io/awesome-free-ai-coding/providers/mixlayer/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-17

Serverless open models priced per token, one of them at $0 and callable without prepaid credit

- Limits, in the vendor's words: Usage allowance: see your account for values (period not published) per organization per model

Free models do not need prepaid credit; paid models return 402 when the balance is empty. The zero-priced Qwen route is separate from metered models. Rate limits are set per organization and model, with actual values unpublished. The operator is Mixlayer Labs Inc.
- Base URL: `https://models.mixlayer.ai/v1`
- Key: `MIXLAYER_API_KEY` — get one at <https://console.mixlayer.com/app/api-keys>
- Codex CLI: [`configs/codex/mixlayer.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/mixlayer.config.toml) — copy it to `~/.codex/`, then `codex -p mixlayer`; set up on the lane by the vendor's own page, <https://docs.mixlayer.com/codex-cli>: "A separate profile keeps Mixlayer isolated from your default Codex configuration"
- Callable ids: `qwen/qwen3.5-4b-free`
- What you send is not used to train models ([the vendor's words](https://www.mixlayer.com/privacy-policy)).

### [SiliconFlow (China)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/siliconflow-cn/)

🔌 LLM APIs with free tier · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · verified 2026-10-08 · listed since 2026-10-03

China's SiliconFlow prices eight small chat models at ¥0 for an account verified with Chinese, Hong Kong, Macau or Taiwan papers

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Verified free models: Usage allowance: see your account for values (period not published) per account per model

Free models are zero-priced but require real-name verification. Online verification uses an Alipay face scan and accepted mainland, Hong Kong, Macau, Taiwan or Chinese permanent-residence documents; other applicants must contact staff. Sign in by SMS or email. Per-model fixed rate values are shown in the client-rendered model square, rather than public docs.

</details>

- Base URL: `https://api.siliconflow.cn/v1`
- Key: `SILICONFLOW_CN_API_KEY` — get one at <https://cloud.siliconflow.cn/account/ak>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.siliconflow.cn`
- Callable ids: `Qwen/Qwen3.5-4B`
- What you send is not used to train models ([the vendor's words](https://docs.siliconflow.cn/docs/legals/privacy-policy)).

## Related models

- [`qwen3.5-122b-a10b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-122b-a10b/) — free at Alibaba Cloud Model Studio (DashScope, international) and Regolo AI
- [`qwen3.5-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-27b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.5-35b-a3b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-35b-a3b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.5-397b-a17b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-397b-a17b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.5-9b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-9b/) — free at Regolo AI

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
