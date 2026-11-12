---
layout: default
title: 'PLaMo API (Preferred Networks) free tier: limits, free models, verified 2026-11-09'
description: Preferred Networks model API with a Free plan for eligible users in Japan. Registration and use are limited to adults resident in Japan or Japanese entities. Free inputs and outputs are stored and used for training; personal information must not be submitted. Usage and rate limits apply; the…
permalink: /providers/plamo/
last_modified_at: 2026-11-09
crumb: PLaMo API (Preferred Networks)
---

{% raw %}

# PLaMo API (Preferred Networks) free tier

🔌 LLM APIs with free tier · no card · offered only in Japan · provisional — added on 2026-11-08, a regular row from the first probe it passes on or after 2026-11-22 · **live** — last verified by a probe on 2026-11-09 · [plamo.preferredai.jp](https://plamo.preferredai.jp/api) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Preferred Networks model API with a Free plan for eligible users in Japan

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Registration and use are limited to adults resident in Japan or Japanese entities. Free inputs and outputs are stored and used for training; personal information must not be submitted. Usage and rate limits apply; the public limits table does not separate Free-plan amounts. The web-search campaign is a separate allowance.

## Where it is offered

Offered only in Japan ([source](https://plamo.preferredai.jp/info/terms), read 2026-11-09). That leaves out 96.7% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “On the Free plan, input and output are stored and used for training in every feature.” ([source](https://docs.plamo.preferredai.jp/en/pricing)).

## Connect

- Base URL: `https://api.platform.preferredai.jp/v1`
- Key: `PLAMO_API_KEY` — get one at <https://console.platform.preferredai.jp/>
- Callable ids: `plamo-3.0-prime`, `plamo-3.1-prime`
- Note: Select the Free API plan, then create a key in the Console. Prefer the current model ID. The API reference states that the older ID will switch to the current model after January 31, 2027.

Try it from your terminal with your key in `PLAMO_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.platform.preferredai.jp/v1/chat/completions \
  -H "Authorization: Bearer $PLAMO_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"plamo-3.1-prime","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.plamo.preferredai.jp/en/pricing>, anchored on `On the Free plan, input and output are stored and used for training in every feature`
- Source: <https://docs.plamo.preferredai.jp/en/pricing>
- Source: <https://docs.plamo.preferredai.jp/en/getting-started>
- Source: <https://docs.plamo.preferredai.jp/en/api>
- Source: <https://docs.plamo.preferredai.jp/en/limit>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-08` — Added: Preferred Networks model API with a Free plan for eligible users in Japan

---

Generated from `registry.yaml` on 2026-11-12 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
