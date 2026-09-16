---
layout: default
title: 'opencode free tier: limits, free models, verified 2026-09-14'
description: Open-source TUI/desktop coding agent with zero-priced models included via the opencode Zen gateway (Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.3 Contributor), which other clients can call too, keyless, with a session header; any provider via…
permalink: /providers/opencode/
---

{% raw %}

# opencode

🤖 Coding agents & CLIs · no card · **live** — last verified by a probe on 2026-09-14 · [opencode.ai](https://opencode.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source TUI/desktop coding agent with zero-priced models included via the opencode Zen gateway (Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.3 Contributor), which other clients can call too, keyless, with a session header; any provider via BYOK too

## Free models

`big-pickle`, `mimo-v2.5`, `ling-3.0-flash-fin`, `nemotron-3-ultra`, `nemotron-3.5-lightning`, `muse-spark-1.3-contributor`

## Limits, in the vendor's words

Zen prices six ids at zero — big-pickle, mimo-v2.5-free, ling-3.0-flash-fin-free, nemotron-3-ultra-free, nemotron-3.5-lightning-free and muse-spark-1.3-contributor-free — and calls every one of them "available on OpenCode for a limited time" while the team collects feedback; a seventh, the stealth model union-alpha, joined the table on 2026-09-16, served on /v1/messages. That feedback is the price: the privacy section exempts each free model from Zen's zero-retention policy ("during its free period, collected data may be used to improve the model"), the two NVIDIA-backed ones are "trial use only — do not submit personal or confidential data", and the Muse Spark one buys its zero with training rights — "heavily discounted token pricing in exchange for permission to use your prompts and completions to train future Meta models", on a row the pricing table still prints as Free in and Free out. Mind the suffix: plain muse-spark-1.3 and muse-spark-1.2 are paid rows at $1.25/$4.25 per 1M tokens, which is why the Models column names muse-spark-1.3-contributor — a bare muse-spark-1.3 would stay named on this page after the free row left it. It joined the column on 2026-09-16, two weeks after Zen added it, and Artificial Analysis scores Muse Spark 1.3 at xhigh — the highest effort Meta's contributor tier allows, since max is "Standard-tier muse-spark-1.3 only" — at 45 on its Intelligence Index, level with Claude Opus 5 at medium. That Muse Spark row is a version newer than it was: Zen's own commits to these docs added muse-spark-1.3-contributor-free on 2026-09-02 and took muse-spark-1.2-contributor-free off the page on 2026-09-05, though the catalog still returns the 1.2 id. deepseek-v4-flash left the free table by the 2026-08-20 read and has been metered at a flat $0.14/$0.28 since the same 2026-09-05 commit dropped peak pricing; its -free id is still in the catalog, while laguna-s-2.1 is off the page and, by 2026-09-14, out of the catalog as well. Since 2026-09-07 every request for them has to carry a stable id for its conversation in the x-opencode-session header: without one Zen answers HTTP 400 MissingSessionID with "OpenCode's free tier can only be used in OpenCode" (read again 2026-09-16). The Zen docs never mention the header — they print every model's endpoint under "You can also access our models through the following API endpoints" — and the rule OpenCode writes down for other clients is on the page of OpenCode Go, its keyed subscription ("Where can I use it?"): a client should "Identify itself with its own user agent" and "Send a stable session ID in x-opencode-session for each conversation", with Hermes, Claude Code, Codex, ZCode, Pi, jcode and Kilo Code CLI listed as validated for Go. OpenCode's team asked Kilo Code for the same header, for its OpenCode Go traffic, on 2026-09-03 ("Any stable UUID per conversation works"), and a Pi report of 2026-09-08 has big-pickle answering 200 with an account key once the header is added. OpenCode sends it for its own provider, where the ids are written opencode/<model-id>. No key is needed either: on 2026-09-16 a keyless request carrying this project's own user agent got 400 MissingSessionID without the header and HTTP 200 from big-pickle with a session id of its own, where a report of 2026-08-14 had the keyless lane answering OpenCode's own user agent alone. Zen documents signup as "sign in to OpenCode Zen, add your billing details, and copy your API key", but the free ids answer without payment details on file — tested by hand rather than read, 2026-08-15. Billing is what the metered ids want, and once it is on, auto-reload tops the balance up by $20 whenever it falls below $5 (read 2026-09-14). The lane has counted six since 2026-08-30, but not always the same six: that day hy3-free was gone from the page altogether — no row in the pricing table, no id in the endpoints table, and not listed under Deprecated models either — while ling-3.0-flash-fin-free had arrived priced Free in, Free out

## Connect

- Base URL: `https://opencode.ai/zen/v1`
- Key: none — the lane is anonymous
- Session header: `x-opencode-session` — a stable id per conversation on every request, which the calling client sends itself; the generated LiteLLM and opencode configs leave this row out
- Callable ids: `ling-3.0-flash-fin-free`, `big-pickle`, `mimo-v2.5-free`, `nemotron-3-ultra-free`, `nemotron-3.5-lightning-free`, `muse-spark-1.3-contributor-free`
- Note: no key needed for the ids Zen prices at zero, as long as every request carries a stable id per conversation in x-opencode-session: without one Zen answers 400 MissingSessionID ("OpenCode's free tier can only be used in OpenCode"), with one ling-3.0-flash-fin-free answered keyless three times out of three on 2026-09-16, while big-pickle and mimo-v2.5-free answered 429 FreeUsageLimitError every time. The client sends the header itself, so the generated LiteLLM and opencode configs leave this row out; inside OpenCode the ids are opencode/<model-id> and the header is sent for you. muse-spark-1.3-contributor-free is served on /v1/responses only (500 on /v1/chat/completions), and the catalog still returns deepseek-v4-flash-free and muse-spark-1.2-contributor-free, which the pricing table no longer lists at zero

## Evidence

- Probe: the page at <https://opencode.ai/docs/zen/>, anchored on `big pickle`, `mimo-v2.5-free`; ids checked in <https://opencode.ai/zen/v1/models>
- Source: <https://opencode.ai/docs/zen/>
- Source: <https://opencode.ai/docs/>
- Source: <https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/llm/request.ts>
- Source: <https://opencode.ai/docs/go/>
- Source: <https://github.com/Kilo-Org/kilocode/issues/13723>

## History

- *next scheduled run* — Free models changed: added muse-spark-1.3-contributor; dropped muse-spark-1.2
- `2026-08-31` — Free models changed: added ling-3.0-flash-fin; dropped hy3
- `2026-08-24` — Free models changed: added muse-spark-1.2; dropped deepseek-v4-flash
- `2026-08-20` — Free models changed: dropped laguna-s-2.1
- `2026-08-17` — Free models changed: added hy3, laguna-s-2.1, nemotron-3.5-lightning
- `2026-07-19` — Free models changed: added big-pickle, deepseek-v4-flash, mimo-v2.5, nemotron-3-ultra
- `2026-07-19` — Added to the list: Open-source TUI agent, BYOK or free models via OpenRouter

---

Generated from `registry.yaml` on 2026-09-16 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
