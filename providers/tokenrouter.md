---
layout: default
title: 'TokenRouter (PaleBlueDot) free tier: limits, free models, verified 2026-10-01'
description: 'OpenAI-compatible gateway with a zero-priced free-model route in its default group beside metered models. Free models: nemotron-3-nano-omni. The free route is in the default group, with no published request cap. Other catalog routes are metered, apart from an unmarked zero-priced stealth route.'
permalink: /providers/tokenrouter/
last_modified_at: 2026-10-01
crumb: TokenRouter (PaleBlueDot)
---

{% raw %}

# TokenRouter (PaleBlueDot) free tier

🧭 Aggregators (one key, many providers) · no card · not offered in Russia, Iran, Belarus and 3 more places · **live** — last verified by a probe on 2026-10-01 · [tokenrouter.com](https://www.tokenrouter.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway with a zero-priced free-model route in its default group beside metered models

## Free models

[`nemotron-3-nano-omni`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-omni/)

## Limits, in the vendor's words

The free route is in the default group, with no published request cap. Other catalog routes are metered, apart from an unmarked zero-priced stealth route.

## Where it is offered

Not offered in Russia, Iran, Belarus, Syria, Cuba and North Korea ([source](https://www.tokenrouter.com/docs/conditions-of-use/), read 2026-09-26). That leaves out 2.7% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “for or on behalf of parties located in, headquartered in, or having a parent company headquartered in Russia, Belarus, Iran, North Korea, Cuba, or the occupied regions of Ukraine”.

## Connect

- Base URL: `https://api.tokenrouter.com/v1`
- Key: `TOKENROUTER_API_KEY` — get one at <https://www.tokenrouter.com/console/token>
- Callable ids: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`
- Note: Use the zero-priced free-model ID in the default group. PaleBlueDot AI runs tokenrouter.com; similarly named gateways on other TLDs are separate services and their keys do not work here.

Try it from your terminal with your key in `TOKENROUTER_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.tokenrouter.com/v1/chat/completions \
  -H "Authorization: Bearer $TOKENROUTER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.tokenrouter.com/api/pricing>, free rows carrying `free`, each listed family checked for a zero price
- Source: <https://api.tokenrouter.com/api/pricing>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-08-14` — Free models changed: dropped kimi-k3
- `2026-08-05` — Added: Zero-priced Kimi K3 on the gateway's own deployment, plus a free Nemotron lane, inside a 121-model paid catalog

---

Generated from `registry.yaml` on 2026-10-01 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
