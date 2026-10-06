---
layout: default
title: 'qwen3.5-4b free: 2 providers, limits and ids, verified 2026-10-05'
description: qwen3.5-4b is served free by Mixlayer and SiliconFlow (China). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/qwen3.5-4b/
last_modified_at: 2026-10-05
crumb: qwen3.5-4b
---

{% raw %}

# Where qwen3.5-4b is free

**2 rows on the list serve `qwen3.5-4b` free:** Mixlayer and SiliconFlow (China). None asks for a card. The published offers were checked on 2026-10-05 and are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/qwen3-5-4b), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Mixlayer](https://mvalentsev.github.io/awesome-free-ai-coding/providers/mixlayer/)

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-09-17

Serverless open models priced per token, one of them at $0 and callable without prepaid credit

- Limits, in the vendor's words: The pricing page says "Free models stay free; pay-as-you-go for everything else." and prices its one free row, qwen/qwen3.5-4b-free, at $0.00 in and out, 131K context, vision and text. The billing docs: "Free models do not require prepaid credit." — a paid model on an empty prepaid balance answers `402`. Rate limits are set per organization and per model, and "Mixlayer does not publish fixed limit values because limits can differ by organization and model". The docs' introduction sends its first request to the free model. The operator is Mixlayer Labs Inc. Read 2026-09-17
- Base URL: `https://models.mixlayer.ai/v1`
- Key: `MIXLAYER_API_KEY` — get one at <https://console.mixlayer.com/app/api-keys>
- Codex CLI: [`configs/codex/mixlayer.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/mixlayer.config.toml) — copy it to `~/.codex/`, then `codex -p mixlayer`; set up on the lane by the vendor's own page, <https://docs.mixlayer.com/codex-cli>: "A separate profile keeps Mixlayer isolated from your default Codex configuration"
- Callable ids: `qwen/qwen3.5-4b-free`
- What you send is not used to train models ([the vendor's words](https://www.mixlayer.com/privacy-policy)).

### [SiliconFlow (China)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/siliconflow-cn/)

🔌 LLM APIs with free tier · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · verified 2026-10-05 · listed since 2026-10-03

China's SiliconFlow prices eight small chat models at ¥0 for an account verified with Chinese, Hong Kong, Macau or Taiwan papers

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: The rate-limit FAQ: free models cost nothing ("免费模型调用免费", billed at 0), their limits are fixed per model ("免费模型的 Rate Limits 固定", shown in the client-rendered model square), and "实名认证后使用全部的免费模型" — they open only after real-name verification. That is an Alipay face scan taking a mainland ID card, a Hong Kong, Macau or Taiwan travel or residence permit, or China's permanent-residence card for foreigners; without one "暂时不支持线上个人认证", and the FAQ offers a form to the staff instead. Sign-in is by SMS or email. The free rows are in the price list's own data, each at ¥0 in and out: Qwen3-8B, GLM-4-9B-0414, GLM-Z1-9B-0414, Qwen2.5-7B-Instruct, Qwen3.5-4B, DeepSeek-R1-0528-Qwen3-8B, Hunyuan-MT-7B and Xing4.0-29B, the last two also marked 免费 in the table the page renders. Read 2026-09-18

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

Generated from `registry.yaml` on 2026-10-06 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
