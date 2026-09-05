---
layout: default
title: 'TokenRouter (PaleBlueDot) free tier: limits, free models, verified 2026-09-03'
description: Two zero-priced ids — Nemotron 3 Nano Omni and GLM 5.3, in the default group — inside a 134-row catalog metered at list rates. both free ids sit in the default group and publish no request cap; of the other 132 rows on 2026-09-02, 131 are metered at list rates and stealth/ox-alpha is priced 0…
permalink: /providers/tokenrouter/
---

{% raw %}

# TokenRouter (PaleBlueDot)

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-03 · [tokenrouter.com](https://www.tokenrouter.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Two zero-priced ids — Nemotron 3 Nano Omni and GLM 5.3, in the default group — inside a 134-row catalog metered at list rates

## Free models

`nemotron-3-nano-omni`

## Limits, in the vendor's words

both free ids sit in the default group and publish no request cap; of the other 132 rows on 2026-09-02, 131 are metered at list rates and stealth/ox-alpha is priced 0 without the free marker the lane is read by. The zero-priced Kimi K3 this entry was registered for is gone — moonshotai/kimi-k3-free had left the catalog by 2026-08-14 and only the paid moonshotai/kimi-k3 remains

## Connect

- Base URL: `https://api.tokenrouter.com/v1`
- Key: `TOKENROUTER_API_KEY` — get one at <https://www.tokenrouter.com/console/token>
- Callable ids: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `z-ai/glm-5.3-free`
- Note: two ids in the catalog are priced 0 and they are the whole free lane here — nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free alone on 2026-08-14, z-ai/glm-5.3-free beside it by 2026-09-02. PaleBlueDot AI runs this gateway on tokenrouter.com; same-name gateways on other TLDs are separate services and their keys do not work here

## Evidence

- Probe: the models catalog at <https://api.tokenrouter.com/api/pricing>, free rows carrying `free`, every listed family required at a zero price
- Source: <https://api.tokenrouter.com/api/pricing>

## History

- `2026-08-14` — Free models changed: dropped kimi-k3
- `2026-08-05` — Added to the list: Zero-priced Kimi K3 on the gateway's own deployment, plus a free Nemotron lane, inside a 121-model paid catalog

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
