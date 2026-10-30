---
layout: default
title: 'Haimaker free tier: limits, free models, verified 2026-10-30'
description: 'OpenAI-compatible API gateway with a limited-time free model promotion, no card required. Free models: glm-5.3, deepseek-v4.1-flash, minimax-m3. Create an account and an API key. Free capacity is best effort and shared across the wave; paid requests have priority. No numerical allowance is…'
permalink: /providers/haimaker/
last_modified_at: 2026-10-30
crumb: Haimaker
---

{% raw %}

# Haimaker free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-10-30, a regular row from the first probe it passes on or after 2026-11-13 · **live** — last verified by a probe on 2026-10-30 · [haimaker.ai](https://haimaker.ai/free/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible API gateway with a limited-time free model promotion, no card required

## Free models

[`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) (until 2026-11-01), [`deepseek-v4.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4.1-flash/) (until 2026-11-01), [`minimax-m3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m3/) (until 2026-11-01)

## Limits, in the vendor's words

Usage allowance: amount not published (period not published); scope not published

Create an account and an API key. Free capacity is best effort and shared across the wave; paid requests have priority. No numerical allowance is published. After the promotion, the same IDs and key return to paid token pricing. Prompts and responses are logged by default; opt out in API key settings. Logged contents are deleted after 30 days. Haimaker says "We do not use the content of your API requests to train AI models." Upstream providers apply their own data policies; their training practices are not established here. Its terms restrict competing-product development and comparative benchmarking without permission.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://haimaker.ai/terms-and-conditions/), read 2026-10-30).

## What happens to what you send

Training policy not established. In the vendor's words: “haimaker does not control and is not responsible for how Third-Party Model providers collect, use, store, process, retain, disclose, or train on data you submit when routing to their models.” ([source](https://haimaker.ai/terms-and-conditions/)).

## Connect

- Base URL: `https://api.haimaker.ai/v1`
- Key: `HAIMAKER_API_KEY` — get one at <https://app.haimaker.ai/sign-up>
- Callable ids: `z-ai/glm-5.3`, `deepseek/deepseek-v4.1-flash`, `minimax/minimax-m3`
- `z-ai/glm-5.3`: free until 2026-11-01 14:00+00:00 ([conditions](https://haimaker.ai/free/))
- `deepseek/deepseek-v4.1-flash`: free until 2026-11-01 14:00+00:00 ([conditions](https://haimaker.ai/free/))
- `minimax/minimax-m3`: free until 2026-11-01 14:00+00:00 ([conditions](https://haimaker.ai/free/))
- Note: Use an API key as a bearer token with Chat Completions. The advertised free window ends November 1 at 14:00 UTC; these same IDs are metered afterward.

Try it from your terminal with your key in `HAIMAKER_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.haimaker.ai/v1/chat/completions \
  -H "Authorization: Bearer $HAIMAKER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"z-ai/glm-5.3","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.haimaker.ai/public/model_hub>, each listed family checked for a zero price
- Source: <https://api.haimaker.ai/public/model_hub>
- Source: <https://haimaker.ai/llms.txt>
- Source: <https://haimaker.ai/privacy-policy/>
- Source: <https://haimaker.ai/terms-and-conditions/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-30` — Added: OpenAI-compatible API gateway with a limited-time free model promotion, no card required

---

Generated from `registry.yaml` on 2026-10-31 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
