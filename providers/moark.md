---
layout: default
title: 'Moark (Gitee AI) free tier: limits, free models, verified 2026-10-08'
description: Gitee's model platform, formerly Gitee AI — 200+ open models behind OpenAI- and Anthropic-compatible APIs — whose free experience token gives every user 100 calls a day across its featured models, with nothing bought. Choose the free experience token; it can be used without buying a resource…
permalink: /providers/moark/
last_modified_at: 2026-10-08
crumb: Moark (Gitee AI)
---

{% raw %}

# Moark (Gitee AI) free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-08 · [moark.com](https://moark.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Gitee's model platform, formerly Gitee AI — 200+ open models behind OpenAI- and Anthropic-compatible APIs — whose free experience token gives every user 100 calls a day across its featured models, with nothing bought

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

100 requests/day per account

Choose the free experience token; it can be used without buying a resource package. At the daily cap it returns `400 已达到最大当日免费 API 使用次数，请购买资源后继续使用 API`. Featured models are listed in the client-rendered model square. Its separately marked free models require a purchased resource package. Sign in through Gitee; acceptance of non-mainland phone numbers is unverified.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://moark.com/docs/appendix/terms), read 2026-09-26). In the vendor's words: “您必须提交自身合法、真实、有效的身份信息完成真实身份的核验”.

## What happens to what you send

What you send is not used to train models. In the vendor's words: “对于您在我们的网站上发布的内容或以其他方式提供的内容，…在此明确，未经您的允许，我们不会使用您的内容作为人工智能模型训练的输入。” ([source](https://moark.com/docs/appendix/terms)).

## Connect

- Base URL: `https://api.moark.com/v1`
- Key: `MOARK_API_KEY` — get one at <https://moark.com/dashboard/tokens>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://moark.com/anthropic`
- Codex CLI: [`configs/codex/moark.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/moark.config.toml) — copy it to `~/.codex/`, then `codex -p moark`; Codex's base is `https://moark.com/v1`; set up on the lane by the vendor's own page, <https://moark.com/docs/integrations/Development-Tools/Codex>: "模力方舟提供对 Codex 的原生支持"
- Callable ids: `deepseek-v4-flash-0731`
- Note: Use the free experience access token. For Claude Code, set ANTHROPIC_BASE_URL=https://moark.com/anthropic; its guide uses deepseek-v4-flash-0731 in every model slot. The featured models available to the free token are listed in the model square.

Try it from your terminal with your key in `MOARK_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.moark.com/v1/chat/completions \
  -H "Authorization: Bearer $MOARK_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-flash-0731","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://moark.com/docs/FAQ>, anchored on `每位用户每日拥有 100 次免费调用次数`; ids checked in <https://api.moark.com/v1/models>
- Source: <https://moark.com/docs/FAQ>
- Source: <https://moark.com/docs/getting-started>
- Source: <https://moark.com/docs/integrations/Development-Tools/claude_code>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: Gitee's model platform, formerly Gitee AI — 200+ open models behind OpenAI- and Anthropic-compatible APIs — whose free experience token gives every user 100 calls a day across its featured models, with nothing bought

---

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
