---
layout: default
title: 'Kenari free tier: limits, free models, verified 2026-09-03'
description: Indonesian OpenAI- and Anthropic-compatible gateway whose :free ids are billed Rp 0 behind a per-minute and a daily cap — thirteen on 2026-09-03, GLM-4.7-Flash, Nemotron 3 Ultra, Hy3 and Mistral Medium 3.5 among them. "Models with the :free suffix, for example step-3-7-flash:free, are billed at…
permalink: /providers/kenari/
---

{% raw %}

# Kenari

🧭 Aggregators (one key, many providers) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-03 · [kenari.id](https://kenari.id) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Indonesian OpenAI- and Anthropic-compatible gateway whose :free ids are billed Rp 0 behind a per-minute and a daily cap — thirteen on 2026-09-03, GLM-4.7-Flash, Nemotron 3 Ultra, Hy3 and Mistral Medium 3.5 among them

## Free models

`nemotron-3-ultra`, `nemotron-3-super`, `step-3.7-flash`, `laguna-s-2.1`

## Limits, in the vendor's words

"Models with the :free suffix, for example step-3-7-flash:free, are billed at Rp 0. In exchange, there is a per-account request limit per minute", and "Besides the per-minute limit, :free models also carry a daily request allowance with three tiers, based on account status". The figures live in the public pricing endpoint the docs point at, kenari.id/api/public/pricing (re-read 2026-09-03, unchanged): a new account gets 50 requests a day at 5 per minute, an account whose top-ups pass Rp 10,000 gets 1,000 a day at 10 per minute, and a subscription lifts the per-minute cap to 15. "Running out of daily quota returns HTTP 429 with a Retry-After header and reason free_quota_daily", and "The free lane is best-effort: capacity is kept lean, with no guarantee of the same speed or availability as paid models". Sign-up asks for no card — top-ups are QRIS, "tanpa kartu kredit internasional", without an international credit card — and the privacy policy says "Kami tidak menyimpan isi prompt maupun isi respons", prompt and response content are not stored; the terms forbid reselling access. Docs are Indonesian with a full English mirror under /en/docs

## Connect

- Base URL: `https://kenari.id/v1`
- Key: `KENARI_API_KEY` — get one at <https://kenari.id/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://kenari.id`
- Callable ids: `glm-4-7-flash:free`, `nemotron-3-ultra-550b-a55b:free`, `nemotron-3-super-120b-a12b:free`, `step-3-7-flash:free`, `laguna-s-2-1:free`, `laguna-xs-2-1:free`, `hy3:free`, `mistral-medium-3-5:free`, `mimo-v2-5:free`, `agnes-2-0-flash:free`, `agnes-2-5-flash:free`, `muse-spark-1-2-contributor:free`, `muse-spark-1-3-contributor:free`
- Note: every :free id the catalog carries is listed — thirteen on 2026-09-03, twelve the day before. The catalog marks each one `free: true` inside its pricing object and prints the metered Rupiah rate beside it, which is what the same model costs without the suffix, so the probe reads the flag and not the price. Ids write a version's dot as a hyphen (glm-4-7-flash:free for GLM-4.7-Flash). The lane rotates inside a single day, which is why the Models column names four families and not five: at 09:55 UTC on 2026-09-03 the catalog carried no free glm-4-7-flash id at all and the row failed its probe on it, and it was back twelve hours later. On an api-models probe every family in that column is a tripwire, so the ones that come and go stay in this list and out of it. It also rotates on point releases: in the thirty hours after it was first read qwen3-8-27b:free was withdrawn outright, leaving no metered twin behind, while agnes-2-5-flash:free and muse-spark-1-3-contributor:free joined. The vendor's two endpoints disagree about the pair those two supersede — /v1/models still serves agnes-2-0-flash:free and muse-spark-1-2-contributor:free, which /api/public/pricing has already dropped — and both stay listed here because the probe reads the catalog, which still answers for them. The same key serves /v1/chat/completions and an Anthropic-format /v1/messages The Messages doc says "Arahkan SDK Anthropic ke https://kenari.id/v1" and documents POST /v1/messages with the same kn- key as Bearer; the route that answers is https://kenari.id/v1/messages (401 keyless), so ANTHROPIC_BASE_URL is https://kenari.id — with the docs' /v1 appended it lands on /v1/v1/messages, which answers 405 (2026-09-05)

## Evidence

- Probe: the models catalog at <https://kenari.id/v1/models>, free rows carrying `:free`, every listed family required at a zero price
- Source: <https://kenari.id/en/docs/billing>
- Source: <https://kenari.id/api/public/pricing>
- Source: <https://kenari.id/v1/models>
- Source: <https://kenari.id/docs/messages>

## History

- `2026-09-03` — Free models changed: dropped glm-4.7-flash
- `2026-09-03` — Added to the list: Indonesian OpenAI- and Anthropic-compatible gateway whose :free ids are billed Rp 0 behind a per-minute and a daily cap — twelve on 2026-09-02, GLM-4.7-Flash, Nemotron 3 Ultra, Hy3 and Mistral Medium 3.5 among them

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
