# Contributing

## Suggest a service

Open a [Suggest a service](../../issues/new?template=suggest-a-service.yml) issue — that's it.
Every suggestion goes through the same machinery as everything else: a live probe must
confirm the free offer on an official page before the entry lands.

## What qualifies

An entry must be **legal** and **directly usable by a developer**:

- an HTTP API endpoint (OpenAI-compatible or similar) you can plug into coding
  agents — opencode, Claude Code, Codex CLI — with a real free tier, free models,
  or no-card trial credits, **or**
- a coding agent / IDE / CLI with **bundled** free model usage or recurring free credits.

What does **not** qualify:

- reverse proxies, key sharing, scraped or "unofficial" gateways;
- BYOK-only tools with zero bundled model usage (free software ≠ free LLM);
- browser-only SDKs that can't serve as an agent endpoint;
- one-off marketing credits that require a credit card.

Domains rejected for cause live in [`blocklist.yaml`](blocklist.yaml) — the scout
will not re-propose them. Model-generation bumps a reviewer has already declined
live in [`dismissed.yaml`](dismissed.yaml), so the same suggestion stops coming
back in every pull request.

## Probes must anchor on the offer

Every `page-keywords` probe needs at least one keyword that disappears when the
free tier does. Three shapes qualify:

| Anchor | Example |
|---|---|
| a figure — quota, price, grant | `$0.10, subject to change` · `anonymous users get one request every 15 seconds` |
| an id — model id or JSON field | `mistral-medium` · `advanced_model_request_limit` · `"name":"free"` |
| a sentence of 4+ words quoted from the page | `free models through kilo gateway` |

Words that outlive the offer are rejected by validation, so CI fails on them:
`free`, `hobby`, `free quota`, `monthly credits`, `no signup`, `no credit card
required`. On an `api-models` probe against a gateway that publishes prices, set
`require_zero_price: true` — a model id can stay in the catalog long after it
stops being free.

## How the pipeline works

`registry.yaml` is the single source of truth. `README.md` is **generated** — never
edit it by hand. Twice a week GitHub Actions probes every entry (live model APIs and
pricing pages), commits verification results, and a web-evidence scout (Tavily, Hacker
News, GitHub search, curated feeds → LLM extraction → live probe gate) proposes new
entries via pull request. Humans review the PR; robots do everything else.

## Development

```bash
uv sync
uv run pytest
uv run freetier-probe --dry-run   # live-probe all entries, record nothing
uv run freetier-render            # regenerate README.md + index.json + configs/
```

The `update` workflow also takes manual inputs: `dry_run` runs every phase and
writes nothing (the scout's report lands in the run summary instead of a PR),
and `scout_backend` forces one LLM backend instead of walking the chain — the
only way to exercise a fallback that never gets its turn.

Python 3.12+, httpx + pydantic v2 + Jinja2. Keep the test suite green — CI runs
it on every push and pull request, plus a registry validation / render smoke check.
