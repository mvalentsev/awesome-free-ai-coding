---
layout: default
title: 'Moark (Gitee AI) free tier: limits, free models, verified 2026-09-21'
description: 'Gitee''s model platform, formerly Gitee AI — 200+ open models behind OpenAI- and Anthropic-compatible APIs — whose free experience token gives every user 100 calls a day across its featured models, with nothing bought. The FAQ: 选择“免费体验访问令牌”即可享受免费体验，每位用户每日拥有 100 次免费调用次数 — take the free experience…'
permalink: /providers/moark/
---

{% raw %}

# Moark (Gitee AI)

🧭 Aggregators (one key, many providers) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-21 · [moark.com](https://moark.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Gitee's model platform, formerly Gitee AI — 200+ open models behind OpenAI- and Anthropic-compatible APIs — whose free experience token gives every user 100 calls a day across its featured models, with nothing bought

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The FAQ: 选择“免费体验访问令牌”即可享受免费体验，每位用户每日拥有 100 次免费调用次数 — take the free experience token and every user has 100 free calls a day — and a token past that answers `400` `已达到最大当日免费 API 使用次数，请购买资源后继续使用 API`. The Claude Code guide offers the same token to developers who have bought nothing, 仅供体验，每日调用次数有限 (for trying out, daily calls limited), and configures deepseek-v4-flash-0731. Which models the token reaches, 所有精选模型 (all featured models), is listed only on the client-rendered model square; the models marked 免费 there are another matter, needing a purchased resource package of any amount. Sign-in is with a Gitee account, and no page read says whether one can be opened with a phone number from outside mainland China. Read 2026-09-17

## Connect

- Base URL: `https://api.moark.com/v1`
- Key: `MOARK_API_KEY` — get one at <https://moark.com/dashboard/tokens>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://moark.com/anthropic`
- Callable ids: `deepseek-v4-flash-0731`
- Note: the FAQ gives the OpenAI base as https://api.moark.com/v1 and the Anthropic one as https://moark.com/anthropic, which the Claude Code guide sets as ANTHROPIC_BASE_URL with deepseek-v4-flash-0731 in every model slot; the id is checked against the keyless catalog at api.moark.com/v1/models

## Evidence

- Probe: the page at <https://moark.com/docs/FAQ>, anchored on `每位用户每日拥有 100 次免费调用次数`; ids checked in <https://api.moark.com/v1/models>
- Source: <https://moark.com/docs/FAQ>
- Source: <https://moark.com/docs/getting-started>
- Source: <https://moark.com/docs/integrations/Development-Tools/claude_code>

## History

- `2026-09-21` — Added to the list: Gitee's model platform, formerly Gitee AI — 200+ open models behind OpenAI- and Anthropic-compatible APIs — whose free experience token gives every user 100 calls a day across its featured models, with nothing bought

---

Generated from `registry.yaml` on 2026-09-21 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
