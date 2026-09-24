---
layout: default
title: 'Kenari free tier (archived): what it offered, and why it left the list'
description: Indonesian OpenAI- and Anthropic-compatible gateway whose :free ids are billed Rp 0 behind a per-minute and a daily cap — sixteen on 2026-09-16, GLM-4.7-Flash, Nemotron 3 Ultra, Hy3 and Mistral Medium 3.5 among them. "Models with the :free suffix, for example step-3-7-flash:free, are billed at…
permalink: /providers/kenari/
---

{% raw %}

# Kenari

🧭 Aggregators (one key, many providers) · no card · **archived** — delisted on 2026-09-16: rejected for cause — the operator's own JavaScript bundle showed its capacity coming from pooled ChatGPT and Codex OAuth credentials, captcha solvers and a proxy pool that multiplies per-IP free quotas · `kenari.id` · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What it offered

Indonesian OpenAI- and Anthropic-compatible gateway whose :free ids are billed Rp 0 behind a per-minute and a daily cap — sixteen on 2026-09-16, GLM-4.7-Flash, Nemotron 3 Ultra, Hy3 and Mistral Medium 3.5 among them

## Free models it listed

`nemotron-3-ultra`, `nemotron-3-super`, `step-3.7-flash`, `laguna-s-2.1`

## Limits, in the vendor's words

"Models with the :free suffix, for example step-3-7-flash:free, are billed at Rp 0. In exchange, there is a per-account request limit per minute", and "Besides the per-minute limit, :free models also carry a daily request allowance with three tiers, based on account status". The figures live in the public pricing endpoint the docs point at, kenari.id/api/public/pricing (re-read 2026-09-03, unchanged): a new account gets 50 requests a day at 5 per minute, an account whose top-ups pass Rp 10,000 gets 1,000 a day at 10 per minute, and a subscription lifts the per-minute cap to 15. "Running out of daily quota returns HTTP 429 with a Retry-After header and reason free_quota_daily", and "The free lane is best-effort: capacity is kept lean, with no guarantee of the same speed or availability as paid models". Sign-up asks for no card — top-ups are QRIS, "tanpa kartu kredit internasional", without an international credit card — and the privacy policy says "Kami tidak menyimpan isi prompt maupun isi respons", prompt and response content are not stored; the terms forbid reselling access. Docs are Indonesian with a full English mirror under /en/docs

## Evidence

- Probe: the models catalog at `https://kenari.id/v1/models`, free rows carrying `:free`, each listed family checked for a zero price
- Source: `https://kenari.id/en/docs/billing`
- Source: `https://kenari.id/api/public/pricing`
- Source: `https://kenari.id/v1/models`
- Source: `https://kenari.id/docs/messages`

## History

Each line is a change to what this page publishes, dated the day the list recorded it, in UTC.

- `2026-09-17` — Delisted
- `2026-09-03` — Free models changed: dropped glm-4.7-flash
- `2026-09-03` — Added: Indonesian OpenAI- and Anthropic-compatible gateway whose :free ids are billed Rp 0 behind a per-minute and a daily cap — twelve on 2026-09-02, GLM-4.7-Flash, Nemotron 3 Ultra, Hy3 and Mistral Medium 3.5 among them

---

Generated from `registry.yaml` on 2026-09-24. No probe reads this row any more — it left the list for good unless a reviewer brings it back; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
