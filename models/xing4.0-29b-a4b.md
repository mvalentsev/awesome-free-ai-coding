---
layout: default
title: 'xing4.0-29b-a4b free: 3 providers, limits and ids, provider probes 2026-11-12'
description: xing4.0-29b-a4b is served free by Kilo Code, AIHubMix (free models) and SiliconFlow (China). None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/xing4.0-29b-a4b/
last_modified_at: 2026-11-12
crumb: xing4.0-29b-a4b
---

{% raw %}

# Where xing4.0-29b-a4b is free

**3 rows on the list serve `xing4.0-29b-a4b` free:** Kilo Code, AIHubMix (free models) and SiliconFlow (China). None asks for a card; Kilo Code answers with no account at all. The providers' last scheduled probes were on 2026-11-12; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · last probe 2026-11-12 · listed since 2026-10-31

Open-source coding agent with an Auto Free mode and a keyless OpenAI-compatible gateway, alongside BYOK and local models

- Limits, in the vendor's words: 200 requests/hour per IP

The free-model lineup rotates. Auto Free routes over the free models in the catalog's autoRouting list. Other models use pay-as-you-go credits or a Kilo Pass subscription.
- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code`
- Callable ids: `openrouter/free`
- `openrouter/free`: the router chooses the model ([conditions](https://openrouter.ai/api/v1/models))
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-12 · listed since 2026-11-09

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m xing4.0-29b-a4b-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `xing4.0-29b-a4b-free`

### [SiliconFlow (China)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/siliconflow-cn/)

🔌 LLM APIs with free tier · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · last probe 2026-11-12 · listed since 2026-10-31

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

- [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/) — listed 2026-10-31 to 2026-11-12

---

Generated from `registry.yaml` on 2026-11-12 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
