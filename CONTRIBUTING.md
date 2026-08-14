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

**If your suggestion is declined, it probably lands in
[`watchlist.yaml`](watchlist.yaml), not the blocklist.** Most services checked
here are legitimate and simply have nothing free today, or publish their offer
only on a page no probe can read. That verdict is recorded with its date, its
reason and a `reopen_if` naming the evidence that would change it — and it
expires after 90 days, at which point the scout is free to raise the service
again. If you can supply what `reopen_if` asks for, open the issue again; if the
verdict itself is wrong, say so and delete the record in your pull request.

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
stops being free. Where a catalog publishes an `available` flag the probe reads
it too, with no setting to turn on: a row the vendor marks uncallable is not a
free lane whatever its price says, and it fails the probe as `marked
unavailable`.

## How the pipeline works

`registry.yaml` is the single source of truth. `README.md` is **generated** — never
edit it by hand. Twice a week GitHub Actions probes every entry (live model APIs and
pricing pages), commits verification results, and a web-evidence scout (Tavily, Hacker
News, GitHub search, curated feeds, and a digest of every models.dev provider that
publishes a zero-cost model → LLM extraction → live probe gate) proposes new entries
via pull request. Humans review the PR; robots do everything else.

Every change to what the list publishes — a row arriving, dropping to the
Archive, being delisted, or changing its free models — is appended to
[`history.jsonl`](history.jsonl) by those same two commands and published as an
[Atom feed](https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml).
**Never edit it by hand.** It is append-only, and it is compared against the
registry rather than against the previous run, so a row you add by hand is
reported by the next scheduled run rather than going unrecorded.

## Development

```bash
uv sync
uv run pytest
uv run freetier-probe --dry-run   # live-probe all entries, record nothing
uv run freetier-render            # regenerate README.md + index.json + feed.xml + configs/
uv run freetier-check             # validate the curated files against each other
```

`freetier-check` is the one to run after editing any of `registry.yaml`,
`blocklist.yaml`, `dismissed.yaml` or `watchlist.yaml`. Three of those are read
only by the scout, which runs behind a catch-all — so before this existed, a
malformed one could reach `main` and turn into a green workflow that had quietly
done nothing. It checks `history.jsonl` too, for the different reason that the
log is the only file here that cannot be regenerated from another one.

The `update` workflow also takes manual inputs: `dry_run` runs every phase and
writes nothing (the scout's report lands in the run summary instead of a PR),
and `scout_backend` forces one LLM backend instead of walking the chain — the
only way to exercise a fallback that never gets its turn.

Python 3.12+, httpx + pydantic v2 + Jinja2. Keep the test suite green — CI runs
it on every push and pull request, plus a registry validation / render smoke check.
