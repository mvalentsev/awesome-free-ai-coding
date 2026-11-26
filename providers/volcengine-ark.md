---
layout: default
title: 'Volcengine Ark (new-user inference trial) free tier: limits, free models, verified 2026-11-26'
description: No-card online inference trial for new accounts. Registration requires a phone number that receives SMS at +86. Enable the safe trial mode before opening paid model service and check each model's remaining allowance in the console. Each model's quota is shared by subaccounts and by its base and…
permalink: /providers/volcengine-ark/
last_modified_at: 2026-11-26
crumb: Volcengine Ark (new-user inference trial)
---

{% raw %}

# Volcengine Ark (new-user inference trial) free tier

🎁 Trials (no card when possible) · no card · offered only in mainland China · provisional — added on 2026-11-19, a regular row from the first probe it passes on or after 2026-12-03 · **live** — last verified by a probe on 2026-11-26 · [docs.volcengine.com](https://docs.volcengine.com/docs/ark/free-inference-quota?lang=zh) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

No-card online inference trial for new accounts

## Free models

The vendor does not identify which models the free offer includes. See Limits for the published conditions.

## Limits, in the vendor's words

One-time tokens allowance: see your account for values per account per model

Registration requires a phone number that receives SMS at +86. Enable the safe trial mode before opening paid model service and check each model's remaining allowance in the console. Each model's quota is shared by subaccounts and by its base and fine-tuned models. Trial mode stops inference near exhaustion. Batch inference, plug-ins and cache storage are billed separately.

## Where it is offered

Offered only in mainland China ([source](https://docs.volcengine.com/docs/account-related/account-registration-process?lang=zh), read 2026-11-19). That leaves out 93.6% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “1 个可正常接收短信的手机号（+86）”.

## Connect

- Base URL: `https://ark.cn-beijing.volces.com/api/v3`
- Key: `VOLCENGINE_ARK_API_KEY` — get one at <https://console.volcengine.com/ark>
- Callable ids: none listed — Ark shows the available trial models and remaining token allowances in the signed-in console.
- Note: Use the trial console to obtain a key and copy the exact model ID.

Check your key from your terminal — with it in `VOLCENGINE_ARK_API_KEY`, the vendor's catalog lists the models it can call:

```sh
curl -s https://ark.cn-beijing.volces.com/api/v3/models \
  -H "Authorization: Bearer $VOLCENGINE_ARK_API_KEY"
```

## Evidence

- Probe: the page at <https://docs.volcengine.com/docs/ark/activation-management?lang=zh>, anchored on `50w token 免费额度`, `接近免费额度后服务将暂停`
- Source: <https://docs.volcengine.com/docs/ark/activation-management?lang=zh>
- Source: <https://docs.volcengine.com/docs/ark/quick-start-beginner?lang=zh>
- Source: <https://docs.volcengine.com/docs/account-related/account-registration-process?lang=zh>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-19` — Added: No-card online inference trial for new accounts

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
