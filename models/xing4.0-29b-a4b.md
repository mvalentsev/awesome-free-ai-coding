---
layout: default
title: 'xing4.0-29b-a4b free: 2 providers, limits and ids, provider probes 2026-11-16'
description: xing4.0-29b-a4b is served free by Kilo Code and SiliconFlow (China). None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/xing4.0-29b-a4b/
last_modified_at: 2026-11-16
crumb: xing4.0-29b-a4b
---

{% raw %}

# Where xing4.0-29b-a4b is free

**2 rows on the list serve `xing4.0-29b-a4b` free:** Kilo Code and SiliconFlow (China). None asks for a card; Kilo Code answers with no account at all. The providers' last scheduled probes were on 2026-11-16; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · last probe 2026-11-16 · listed since 2026-10-31

Open-source coding agent with an Auto Free mode and a keyless OpenAI-compatible gateway, alongside BYOK and local models

- Limits, in the vendor's words: 200 requests/hour per IP

The free-model lineup rotates. Auto Free routes over the free models in the catalog's autoRouting list. Other models use pay-as-you-go credits or a Kilo Pass subscription.
- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code`
- Callable ids: `openrouter/free`
- `openrouter/free`: the router chooses the model ([conditions](https://openrouter.ai/api/v1/models))
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [SiliconFlow (China)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/siliconflow-cn/)

🔌 LLM APIs with free tier · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · last probe 2026-11-16 · listed since 2026-10-31

Zero-priced small chat models on SiliconFlow China, after real-name verification with accepted mainland, Hong Kong, Macau or Taiwan documents

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Verified free models: Usage allowance: see your account for values (period not published) per account per model

Free models are zero-priced but require real-name verification. Online verification uses an Alipay face scan and accepted mainland, Hong Kong, Macau, Taiwan or Chinese permanent-residence documents; other applicants must contact staff. Sign in by SMS or email. Per-model fixed rate values are shown in the client-rendered model square, rather than public docs.

</details>

- Base URL: `https://api.siliconflow.cn/v1`
- Key: `SILICONFLOW_CN_API_KEY` — get one at <https://cloud.siliconflow.cn/account/ak>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.siliconflow.cn`
- Callable ids: `XingChenAGI/Xing4.0-29B`
- What you send is not used to train models ([the vendor's words](https://docs.siliconflow.cn/docs/legals/privacy-policy)).

## Rows that listed it before

- [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/) — listed 2026-10-31 to 2026-11-16
- [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/) — listed 2026-11-09 to 2026-11-13

---

Generated from `registry.yaml` on 2026-11-16 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
