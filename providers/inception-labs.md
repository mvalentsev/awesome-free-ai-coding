---
layout: default
title: 'Inception Labs (Mercury) free tier: limits, free models, verified 2026-10-08'
description: A signup grant on Mercury diffusion models — Mercury 2.5 and Mercury 2 for chat, Mercury Edit 2 for fill-in-the-middle completions and code edits. No payment details are required. The signup token balance is shared across all models, does not refill and is spent alongside the Free tier's…
permalink: /providers/inception-labs/
last_modified_at: 2026-10-08
crumb: Inception Labs (Mercury)
---

{% raw %}

# Inception Labs (Mercury) free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-08 · [platform.inceptionlabs.ai](https://platform.inceptionlabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A signup grant on Mercury diffusion models — Mercury 2.5 and Mercury 2 for chat, Mercury Edit 2 for fill-in-the-middle completions and code edits

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

100,000,000 tokens once; 1,000 requests/minute; 1,000,000 input tokens/minute; 100,000 output tokens/minute per account

No payment details are required. The signup token balance is shared across all models, does not refill and is spent alongside the Free tier's per-minute traffic limits. After it, usage is pay-as-you-go at the model's current token prices; a launch discount is not a separate free model.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.inceptionlabs.ai/docs/terms-of-use), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “we may use User Submissions to … train our models. If you do not want us to use your User Submissions to train our models, you can opt-out by setting the ‘Improve the model for everyone’ option under User Settings in the API Platform to OFF.” ([source](https://www.inceptionlabs.ai/docs/terms-of-use)).

## Connect

- Base URL: `https://api.inceptionlabs.ai/v1`
- Key: `INCEPTION_LABS_API_KEY` — get one at <https://platform.inceptionlabs.ai>
- Callable ids: `mercury-2.5`, `mercury-2`, `mercury-edit-2`
- Note: mercury-2.5 and mercury-2 answer /v1/chat/completions and are the two ids /v1/models lists; mercury-edit-2 answers /v1/fim/completions and /v1/edit/completions instead and is absent from that catalog by design, so an OpenAI-shaped chat client cannot call it — point an autocomplete plugin at it, not a chat agent

Try it from your terminal with your key in `INCEPTION_LABS_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.inceptionlabs.ai/v1/chat/completions \
  -H "Authorization: Bearer $INCEPTION_LABS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"mercury-2.5","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.inceptionlabs.ai/get-started>, anchored on `100 million free tokens`, `no payment details required`
- Source: <https://docs.inceptionlabs.ai/get-started>
- Source: <https://docs.inceptionlabs.ai/resources/faq>
- Source: <https://docs.inceptionlabs.ai/get-started/models>
- Source: <https://docs.inceptionlabs.ai/get-started/rate-limits>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: dropped mercury-2, mercury-2.5, mercury-edit-2
- `2026-09-10` — Free models changed: added mercury-2.5
- `2026-08-14` — Added: A signup grant on the Mercury diffusion models, one for chat and one built for fill-in-the-middle and code edits — the second is the reason this row is here, since an FIM endpoint is what an IDE completion plugin actually calls

---

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
