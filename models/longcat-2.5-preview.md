---
layout: default
title: 'longcat-2.5-preview free: 2 providers, limits and ids, provider probes 2026-10-22'
description: longcat-2.5-preview is served free by opencode and Nous Portal (Hermes Agent). None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/longcat-2.5-preview/
last_modified_at: 2026-10-22
crumb: longcat-2.5-preview
---

{% raw %}

# Where longcat-2.5-preview is free

**2 rows on the list serve `longcat-2.5-preview` free:** opencode and Nous Portal (Hermes Agent). None asks for a card. The providers' last scheduled probes were on 2026-10-22; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/)

🤖 Coding agents & CLIs · no card · last probe 2026-10-22 · listed since 2026-10-11

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model usage: Usage allowance: amount not published (period not published); scope not published

Free models work only inside OpenCode; other clients receive `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Use `opencode/<model-id>` and select the Free variant. Offers rotate; each named free offer is "available on OpenCode for a limited time". Collected free-model data may improve models; NVIDIA offers are trial-only and exclude personal or confidential data. Beam Free's provider does not train on inputs and retains them for 30 days; its listed territorial exclusions include Russia.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models ([the vendor's words](https://opencode.ai/v2/docs/console/models/)).

### [Nous Portal (Hermes Agent)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-22 · listed since 2026-10-13

Nous Research's inference portal with a $0 Free plan for :free models, accessible through an OpenAI-compatible API and Hermes Agent

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free models: Usage allowance: amount not published (period not published) per account

Choose the Free plan and use exact :free IDs; they are zero-priced, while metered routes are outside it. Use a portal key with ordinary API clients; the catalog itself is public. The Free plan publishes no card requirement or numerical rate cap.

</details>

- Base URL: `https://inference-api.nousresearch.com/v1`
- Key: `NOUS_PORTAL_API_KEY` — get one at <https://portal.nousresearch.com>
- Callable ids: `meituan/longcat-2.5-preview:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://portal.nousresearch.com/privacy)).

## Related models

- [`longcat-2.0`](https://mvalentsev.github.io/awesome-free-ai-coding/models/longcat-2.0/) — free at Nous Portal (Hermes Agent)

---

Generated from `registry.yaml` on 2026-10-24 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
