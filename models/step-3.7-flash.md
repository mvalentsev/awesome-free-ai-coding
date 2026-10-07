---
layout: default
title: 'step-3.7-flash free: 2 providers, limits and ids, verified 2026-10-05'
description: step-3.7-flash is served free by Kilo Code and Nous Portal (Hermes Agent). None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/step-3.7-flash/
last_modified_at: 2026-10-05
crumb: step-3.7-flash
---

{% raw %}

# Where step-3.7-flash is free

**2 rows on the list serve `step-3.7-flash` free:** Kilo Code and Nous Portal (Hermes Agent). None asks for a card; Kilo Code answers with no account at all. The published offers were checked on 2026-10-05 and are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/step-3-7-flash), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · verified 2026-10-05 · listed since 2026-08-11

Open-source VS Code / JetBrains / CLI agent whose $0 plan routes "Auto Free" to the models the Kilo Gateway marks free; the same gateway serves them to any OpenAI client without a key, with BYOK and local models alongside

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 200 requests/hour per IP

$0 a month; no account for the free lane.  The lane is whatever the gateway marks isFree and the free-model lineup rotates. It costs something other than money: every free id carries mayTrainOnYourPrompts, which almost no metered id does. Auto Free routes over the free models the catalog's autoRouting list names. Everything else runs on pay-as-you-go credits or a Kilo Pass subscription. Read 2026-09-21

</details>

- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code`
- Callable ids: `stepfun/step-3.7-flash:free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [Nous Portal (Hermes Agent)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-16

Nous Research's inference portal with a $0 Free plan for :free models, accessible through an OpenAI-compatible API and Hermes Agent

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free models: Usage allowance: amount not published (period not published) per account

Choose the Free plan and use exact :free IDs; they are zero-priced, while metered routes are outside it. A portal key is required: a keyless chat call returns 402 even though the public catalog is readable. No page read mentions a card or a numerical rate cap.

</details>

- Base URL: `https://inference-api.nousresearch.com/v1`
- Key: `NOUS_PORTAL_API_KEY` — get one at <https://portal.nousresearch.com>
- Callable ids: `stepfun/step-3.7-flash:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://portal.nousresearch.com/privacy)).

## Rows that listed it before

- [Kenari](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kenari/) — listed 2026-09-02 to 2026-09-16; the row itself is archived
- [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/) — listed 2026-08-05 to 2026-08-30

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
