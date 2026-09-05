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
- one-off marketing credits that require a credit card;
- hosted app builders whose free tokens are only spendable inside their own
  workspace — an entry has to hand you model access you can aim at code you
  already have, through a client you install or an endpoint you can call.

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

**Suggesting a list to read from, rather than a service?** The lists the scout
already reads on every run are `CURATED_FEEDS` in
[`discovery.py`](src/freetier_radar/discovery.py); the ones read once and put
down are in [`sources.yaml`](sources.yaml), with the same date, reason and
`reopen_if` a watchlist verdict carries. Check both before opening the issue —
a list that carries nothing this registry can use costs a full read to find that
out, and that read has often already happened. Those verdicts expire after 180
days, and the scout reports the expired ones in its pull requests, because a
directory can grow into a feed long after someone first opened it.

## How rows are ordered

`rank` sorts a row within its section — lower renders higher — and it answers one
question: **how much work can a developer actually get done on this offer without
paying?** In order of what moves a row up:

1. the vendor publishes the quota, so you can plan against it;
2. the models it serves are ones people build with;
3. no card, no verification wall, no "contact us".

A real but unquantified free tier sits below one that prints its numbers, and a
row that publishes no free model list at all sits below both — the page cannot
tell a reader what they would be calling. A row that needs a card never leads the
no-card rows it ties with.

The first four no-card agents are also the top of the README, with the models
they hand you, so this ordering is the page's answer to "what do I use, then?"
Nothing about it is typed by hand: change `rank` and both the section and that
block follow. The "pick by what you need" table under it is the same ordering
read three names deep per section, card-required rows left out; its frontier
line is the one answer that crosses sections, and it is ordered by how many
families a row marks `tier: frontier`, then by `rank` — so a tier is a claim
that reaches the top of the page, and `freetier-check` refuses a family carrying
two of them.

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
stops being free. Free there means free by the catalog's own account: the
vendor's `isFree`/`free` flag where the row carries one, otherwise every price
the row publishes at zero — a zero per token beside a charge per request or per
second of audio is a price. Where a catalog publishes an `available` flag the probe reads
it too, with no setting to turn on: a row the vendor marks uncallable is not a
free lane whatever its price says, and it fails the probe as `marked
unavailable`.

**Every family in `models[]` must be named on the page the probe reads.** The
Free models column is a claim, and it needs to be re-checkable by the same run
that re-checks the offer: an `api-models` probe demands each family back from the
catalog, and a `page-keywords` probe now looks for each family in the page it
already fetched. A family the page does not name is reported as `stale-models` —
the entry stays live and verified, because a marketing page dropping a model name
is not a tier ending, but the column is flagged until someone fixes it. Where the
vendor keeps its offer on one page and its model list on another, probe the page
that carries both, or list fewer families: an id that belongs to the free lane but
has nothing to anchor it belongs in `api.model_ids`, which feeds the generated
configs without making a claim on the page.

**`api.model_ids` is checked against the catalog in both directions.** On an
`api-models` probe every id there must still be in the catalog, callable and —
where `require_zero_price` is set — priced 0; a dead id is reported as
`stale-ids`, with any catalog id that reads like its successor. The same run
reports every zero-priced id the catalog carries that `model_ids` does not, so a
lane that grows is visible without anyone re-reading the catalog. Both are notes
for a human and never repairs: an id is an exact string, and whether a new one
belongs in the configs is a judgement about what the row is for. Record the ones
you have read and left out — an image generator, a row whose own description says
it was removed, a lane the row does not track — in `api.ignored_ids` with the
reason in `api.note`, and they stop being reported. A `page-keywords` row whose
vendor keeps its ids in a keyless catalog at another url names it in
`probe.catalog`, and its ids are checked there for the dead direction; a
catalog that stops answering is reported as `stale-ids` too, since a check that
quietly did not run is the silence this whole mechanism exists to end.

**`api.anthropic_base_url` is the Claude Code answer.** Set it only where the
vendor documents an Anthropic-format Messages route — a 401 alone proves
nothing, since a gateway's auth wall answers 401 on any path. It is the value
`ANTHROPIC_BASE_URL` takes, so it stops before `/v1/messages` (Claude Code
appends that itself; validation refuses a value that already carries it). Every
run then POSTs to the route keyless: a 401, 400 or 429 is a route, a 404 or 405
is reported as `stale-ids` beside the row while the row stays verified by its
page, and a route that cannot be reached is reported rather than skipped. The
field feeds the Claude Code line of the picks table, the second URL in the
connection table and [`configs/claude-code.sh`](configs/claude-code.sh), and
`index.json` carries it as written.

## How the pipeline works

`registry.yaml` is the single source of truth. `README.md` is **generated** — never
edit it by hand. Twice a week GitHub Actions probes every entry (live model APIs and
pricing pages), commits verification results, and a web-evidence scout (Tavily, Hacker
News, GitHub search, curated feeds, and a digest of every models.dev provider that
publishes a zero-cost model → LLM extraction → live probe gate) proposes new entries
via pull request. Humans review the PR; robots do everything else.

`providers/` is generated with it: one page per row on the GitHub Pages site,
in the row's own words, with the evidence the probe reads and the row's history,
plus an index — the "Last verified" date in every README row links to it. The
pages exist for the reader who arrives from a search about one vendor, so their
titles name the vendor, the tier and the date; `_config.yml` names the site so
Jekyll writes canonical URLs and a sitemap. **Never edit them by hand** — the
render deletes the page of a row that leaves and rewrites the rest, and the body
sits inside `{% raw %}` so a vendor's own sentence can never break the build.

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
`blocklist.yaml`, `dismissed.yaml`, `watchlist.yaml` or `sources.yaml`. Four of
those are read only by the scout, which runs behind a catch-all — so before this
existed, a malformed one could reach `main` and turn into a green workflow that
had quietly done nothing. It checks `history.jsonl` too, for the different
reason that the log is the only file here that cannot be regenerated from
another one.

The `update` workflow also takes manual inputs: `dry_run` runs every phase and
writes nothing (the scout's report lands in the run summary instead of a PR),
and `scout_backend` forces one LLM backend instead of walking the chain — the
only way to exercise a fallback that never gets its turn.

Python 3.12+, httpx + pydantic v2 + Jinja2. Keep the test suite green — CI runs
it on every push and pull request, plus a registry validation / render smoke check.
