---
layout: default
title: 'OrcaRouter (free models) free tier: limits, free models, verified 2026-11-12'
description: Free model APIs for accounts with established GitHub linkage. The workspace owner must link a GitHub account registered for some time, unless lifetime spend exempts the workspace. The lowest tier also has a small unpublished per-request prompt cap. Day buckets reset at 00:00 UTC. Free models never…
permalink: /providers/orcarouter/
last_modified_at: 2026-11-12
crumb: OrcaRouter (free models)
---

{% raw %}

# OrcaRouter (free models) free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-11-08, a regular row from the first probe it passes on or after 2026-11-22 · **live** — last verified by a probe on 2026-11-12 · [orcarouter.ai](https://www.orcarouter.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free model APIs for accounts with established GitHub linkage

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

10 requests/minute; 50 requests/day per workspace (before any top-up)

20 requests/minute; 800 requests/day per workspace ($20 lifetime spend)

The workspace owner must link a GitHub account registered for some time, unless lifetime spend exempts the workspace. The lowest tier also has a small unpublished per-request prompt cap. Day buckets reset at 00:00 UTC. Free models never fall back to a paid model; availability and limits can change. Requests are routed to upstream providers under their own policies. The rate-limit guide states "OrcaRouter rate-limits at the workspace level, not per API key."

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.orcarouter.ai/terms.html), read 2026-11-08).

## Connect

- Base URL: `https://api.orcarouter.ai/v1`
- Key: `ORCAROUTER_API_KEY` — get one at <https://www.orcarouter.ai>
- Callable ids: `deepseek/deepseek-v4-flash-free`, `deepseek/deepseek-v4.1-flash-free`, `z-ai/glm-5.3-flash-free`
- Note: Create an OrcaRouter key and keep the exact -free ID. The listed variants declare Chat Completions in the public catalog. Paid siblings and the separately gated Security Research models have different access conditions. Read the error reason: rate windows, capacity, prompt size and GitHub eligibility are different failures.

Try it from your terminal with your key in `ORCAROUTER_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.orcarouter.ai/v1/chat/completions \
  -H "Authorization: Bearer $ORCAROUTER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek/deepseek-v4-flash-free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.orcarouter.ai/v1/models>, free rows carrying `-free`, each listed family checked for a zero price
- Source: <https://docs.orcarouter.ai/routing/free-models.md>
- Source: <https://api.orcarouter.ai/api/free-package/public>
- Source: <https://docs.orcarouter.ai/getting-started/quickstart.md>
- Source: <https://www.orcarouter.ai/terms.html>
- Source: <https://www.orcarouter.ai/privacy.html>
- Source: <https://docs.orcarouter.ai/operations/rate-limits.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-08` — Added: Free model APIs for accounts with established GitHub linkage

---

Generated from `registry.yaml` on 2026-11-14 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
