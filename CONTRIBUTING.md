# Contributing

To suggest an offer, [open an issue](#suggest-a-service). To change registry data,
start with [eligibility](#what-qualifies) and the [probe reference](#probes-must-anchor-on-the-offer).
For implementation work, use [Development](#development); the [file map](#what-depends-on-what)
identifies each source and writer. [Review and publication](#review-and-publication)
describes the evidence required before and after a push.

## Suggest a service

Open a [Suggest a service](../../issues/new?template=suggest-a-service.yml) issue — that's it.
Every suggestion goes through the same machinery as everything else: a live probe must
confirm the free offer on an official page before the entry lands.
The maintainer does not need a personal API key to admit a documented free offer.
Authenticated generation, billing and coding-client checks are separate evidence;
record unavailable checks without treating them as proof that an offer is ineligible.

## What qualifies

An entry must be **legal** and **directly usable by a developer**:

- an HTTP API endpoint (OpenAI-compatible or similar) you can plug into coding
  agents — opencode, Claude Code, Codex CLI — with a real free tier, free models,
  or no-card trial credits, **or**
- a coding agent / IDE / CLI with **bundled** free model usage or recurring free credits.

**An initial payment is a condition, not an automatic rejection.** A documented
free model quota or recurring free credit may require a one-time deposit or card
verification charge. Include it with the amount and any top-up fee visible;
usage within that quota must be free, with no recurring paid subscription required.
An expiring free-model promotion qualifies too, with its published deadline and
timezone. Date-only `until` values are inclusive UTC dates: the writer expires
them at 00:00 UTC on the following day. The published date stays a date; this
does not assert that the vendor supplied an exact hour. A spend allowance still
names no individually free model.

Record whole-offer payment conditions in `access`, and conditions on specific
callable IDs in `api.model_access` (or `client_lane.model_access`). Each uses the
same structure: `source` (an official HTTPS page), `initial_payment_usd`, optional
`payment_kind`, `topup_fee_percent`, and
`until` (a timestamp with timezone or a UTC date, for model promotions). Omit conditions that
do not apply. These fields generate the disclosures; do not duplicate them in
templates or add exceptions for a particular vendor.

`payment_kind` accepts `top-up`, `card verification`, or `charge`; `top-up` is
the default. Use `charge` when the vendor requires a settled payment without
describing it as a credit top-up or card verification. For example:

```yaml
model_access:
  vendor/preview:
    source: https://vendor.example/models/preview
    initial_payment_usd: 5
    topup_fee_percent: 8
    until: '2026-10-06T23:59:00+03:00'
```

Model deadlines inherit a whole-offer payment. Record that payment once in
`access`; do not put a second payment in `model_access` on the same offer, where
it could hide an account requirement or imply two different amounts.

The expiry writer removes an ended ID from callable configurations and retains
its deadline in `model_access` beside `ignored_ids`. A page-based or unpriced
catalog probe may retain these dated IDs as evidence; undated exclusions still
require a catalog probe that reads zero prices.

What does **not** qualify:

- reverse proxies, key sharing, scraped or "unofficial" gateways;
- BYOK-only tools with zero bundled model usage (free software ≠ free LLM);
- browser-only SDKs that can't serve as an agent endpoint;
- one-off marketing credits that require a credit card;
- hosted app builders whose free tokens are only spendable inside their own
  workspace — an entry has to hand you model access you can aim at code you
  already have, through a client you install or an endpoint you can call.

Domains rejected for cause live in [`blocklist.yaml`](blocklist.yaml) — the scout
will not re-propose them, nor a vendor this list already reaches at another of its
hosts. Model-generation bumps a reviewer has already declined
live in [`dismissed.yaml`](dismissed.yaml), so the same suggestion stops coming
back in every pull request; the ones the scout can rule out on its own — a model
of the same family, a family the row already lists, one the row's own page or
catalog does not name, or a bump that would hide a family the row still serves —
are listed apart in the pull request instead of proposed.

**If your suggestion is declined, it probably lands in
[`watchlist.yaml`](watchlist.yaml), not the blocklist.** A watchlist entry is a
dated, reversible decision for an offer that is legitimate but currently
unverified, unavailable or not free. Record the reason and a `reopen_if`
condition naming the evidence that would change it. Keep the dated decision,
and it expires after 90 days, at which point the scout can raise it again.
If you can supply the requested evidence, open the issue again; if the verdict is wrong, explain the correction and remove
the record in your pull request.

**Suggesting a list to read from, rather than a service?** The lists the scout
already reads on every run are `CURATED_FEEDS` in
[`discovery.py`](src/freetier_radar/discovery.py); the ones read once and put
down are in [`sources.yaml`](sources.yaml), with the same date, reason and
`reopen_if` a watchlist verdict carries. Check both before opening the issue.
Those verdicts expire after 180 days, and the scout reports expired ones
so a directory can be reconsidered when it changes.

## How rows are ordered

`agent-cli` contains coding tools with ongoing Free usage, including completion
allowances alongside introductory credits. `trial` contains offers funded only
by a finite introductory grant or trial. A limited monthly allowance is still a
recurring Free plan. Check every advertised free mode before choosing a category;
the optional paid-plan trial does not define the permanent Free plan.

`rank` sorts a row within its section — lower renders higher — and it answers one
question: **how much work can a developer actually get done on this offer without
paying?** In order of what moves a row up:

1. the vendor publishes the quota, so you can plan against it;
2. the models it serves are ones people build with;
3. no card, no verification wall, no border, no "contact us".

A real but unquantified free tier sits below one that prints its numbers, and a
row that publishes no free model list at all sits below both — the page cannot
tell a reader what they would be calling. A row that needs a card never leads the
no-card rows it ties with; the same applies to an obligatory initial payment.
On a model's page, access without an initial payment leads payment-required
access. Client defaults prefer IDs available without payment, and automatic
`free/*` fallback pools omit IDs that require an initial payment. A named
deployment remains available with its conditions disclosed.

**A border counts like a wall.** An offer its vendor keeps from whole countries —
a sign-up that refuses them, or a site and an endpoint that do not resolve there —
does less work for this list's readers than the same offer open to all of them.
Among comparable offers, rank it lower as the share of excluded developers grows.
Use GitHub's latest [Innovation Graph](https://innovationgraph.github.com/)
quarter, omitting its EU aggregate because the member states are already counted.
The countries under comprehensive US embargo — Cuba, Iran and North Korea —
set no row apart and move no rank: a sanctions clause covers them whether it names
them or not.

**Every live row records its border**, in `border`, the way its vendor states
it: `served`, the countries of an allow-list, or `left_out`, every country a
deny-list names, the embargoed ones included. A vendor that names no country,
or covers them with a sanctions clause that names none, is `left_out: []`. The
codes are ISO 3166-1's, and each border carries the day it was read, its source
and, where the page has one, the vendor's sentence. A disclaimer that a service
is "intended for" one country, with nothing that refuses the rest, is not a
border. A restriction on the end users of an application is also separate from
where its developer may use the API. The run reads each recorded border back
and reports changes while the row stays verified. `freetier-borders` prints every row's share and
`--refresh` updates the committed Innovation Graph snapshot. Browse uses the
same data for its "Where you are" filter.

The first four no-card agents are also the top of the README, with the models
they hand you, the strongest first, so this ordering is the page's answer to
"what do I use, then?"
Nothing about it is typed by hand: change `rank` and both the section and that
block follow. Matching Intelligence Index scores come first, highest first;
unavailable scores use the retained tier, then natural model-name order.
Only the reviewed benchmark variant supplies a score. The same rule applies
before short lists are truncated and to provider pages and the model index.
Pages model orders are `score`, `name` or `providers`: Intelligence Index,
natural name or number of free providers. The choice is shared across the model index, provider pages and Browse, kept in the URL and restored during navigation.
Provider ordering remains `rank` within each section.
The "pick by what you need" table under it is the same ordering
read three names deep per section, card-required rows left out; its frontier
line is the one answer that crosses sections, and it is ordered by how many
families a row marks `tier: frontier`, then by `rank` — so a tier is a claim
that reaches the top of the page, and `freetier-check` refuses a family carrying
two of them.

**A tier is a measurement, not a reputation.** A family's `tier` is read from
the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/leaderboards/models):
`frontier` when the model its free lane serves scores within 10 points of the top
of the index, counting current models only, `strong` within 25, `notable` below
that but at or above the median of the current models the index scores — its
upper half, which earns the model a page of its own and no strong mark — and no
tier below the median or where nothing was measured. An explicit `null` score in
a readable current leaderboard clears the old tier; a missing model or unreadable
source preserves it for review. The measurement writer accepts only the reviewed
index version `5.0.1`; a missing, ambiguous or different revision stops it before
registry or snapshot writes. The snapshot records its version and keeps missing
measurements, unscored records and deprecated variants distinct. Scores from
different index revisions must not be combined in one current comparison.
`aa_model` names the Artificial Analysis slug for the exact variant the free
lane serves. A broad family that identifies no single model carries no tier.
`freetier-check` refuses a tier without an `aa_model` and inconsistent bindings
for one family. `uv run freetier-tiers` reads scores back and `--write` applies
them across rows; the scheduled run does this twice a week. It can bind a bare
family to an exact model name, but never replaces a hand-reviewed `aa_model`.

Unavailable pinned measurements report current
dated checkpoint candidates for review; automatic substitutions are not made.
Confirm the checkpoint and reasoning effort each provider serves before changing
its binding. Retain separate families when providers serve different checkpoints.
Set `aa_auto: false` to hold automatic binding for
a family while its available benchmark variant is under review; explicit
reviewed bindings remain measured. Record the source, checked date and next review trigger in private evidence.
Give a family the most specific name the lane serves, one family per model; a broader
name can hide a distinct model from the index and tier marks. Keep a family broad
only when the evidence names no narrower variant. Preserve the full name and
active-parameter count for mixture-of-experts models when the source provides it.

## How a row leaves the list

Through the Archive, and no other way: a row is never deleted from
`registry.yaml`. It is archived on its own when its vendor's shutdown date
arrives (`retired_on`, which also takes a date already past), after three failed
probes in a row, or after 60 days without a passing probe, and a row its probe
archived comes back the day it passes again. Anything else is a reviewer's call,
recorded on the row:

```yaml
delisted:
  on: 2026-09-16
  reason: rejected for cause — the operator's own JavaScript bundle showed …
```

That covers an offer that ended without notice, a row that no longer meets
[what qualifies](#what-qualifies) and a service rejected for cause. `on` is the
day the row came off; `reason` is the sentence the Archive prints beside it —
lower case, no full stop — while the long account goes to `watchlist.yaml`, or
for cause to `blocklist.yaml`. A delisted row keeps what it was published with,
probe included, and its verification probe is skipped. It drops its connection details only
when its service is rejected for cause, and its page then names the service
without linking it. Its id stays taken, since the id is its page's URL: a vendor
that comes back is restored by removing `delisted`, and the scout reports a
proposal under an archived row's id instead of dropping it.

Returning a legacy row whose history ends in `removed` appends `restored`.
Its original `first_seen` and the published history are preserved.

The scheduled update collects current primary sources for archived offers when
their manual review is at least 7 days old, through `freetier-archive-review`.
The canonical `archive_review` pairs
`checked_on` with `sources` for a completed manual review of every advertised
free mode, including current conditions beyond the last offer's sources. The collector
does not advance that date or restore a row. Missing dates are due immediately;
duplicates and blocklisted services are excluded, including blocked source
links and redirect targets. Its summary and `archive-review` artifact retain
unavailable reads and last-offer probe findings for the reviewer. A matching
old probe does not establish current eligibility. Source collection has a
120-second budget; unfinished reads remain explicit in the report.

### Two rows, one service

A service the registry holds twice is folded, never deleted. The second row
keeps its id, since the id is its page's URL, and names the row that holds the
service:

```yaml
duplicate_of: mimo-code
delisted:
  on: 2026-07-19
  reason: the same project as MiMo Code, the name Xiaomi's own README prints — …
```

That is a reviewer's reading of two rows rather than a probe result, so the row
carries the `delisted` that says why. A folded row is then listed nowhere a
reader counts services — not the Archive, the provider index, `llms.txt` or the
filterable table — while `index.json` keeps it, with the field, so an old id
still resolves. Its page stays at its own URL and points at the row that holds
the service; that row names it back, so nothing the list published disappears
without a word.

`freetier-check` refuses a fold that names a row the registry does not hold or
another fold, and reports two rows whose names read as one. Deleting a row is
refused three times over: `freetier-check` fails on a registry missing an id
`history.jsonl` has recorded, the render stops before it can record the deletion,
and it will not build a page without the row. Restore a published row as a
delisted row with its reason if an earlier change deleted it.

## Probes must anchor on the offer

### Usage quotas

`quotas` stores `amount`, `unit`, `period` and `scope`. Each allowance cites
its source and exact quote; optional conditions and reset words need evidence on
that same source. The scheduled probe flags changed or unreadable quotas beside a
still-live offer. Catalog checks bind the quote to each named model ID; constant
checks compare the numeric JavaScript value. Read modes are `page`, `catalog`, `constant`, `table`, `catalog-field`, and `script-field`. Table bindings identify
the plan, model row and value column; catalog fields identify the model and tier.
Script fields select exactly one JSON script and one plan record, including its
price, before comparing a nested numeric allowance. Their unit and renewal
semantics require a dated review every 7 days, even while the value still
matches. An unpublished `amount` or `period` stays null. Unresolved allowances
require a dated manual review after 7 days. Re-read the complete vendor terms at
that review: an old matching phrase cannot prove that no new number has been
published elsewhere. Compact allowances appear first under the existing Limits
section; shared caps do not become model labels. Concurrent ceilings, one-time
grants and recurring windows remain distinct. A page-only model's quota can name a pending family in `newcomers` without promoting it into `models`. Explicit
unmetered usage is separate from an unpublished amount. Model-bound caps include
their exact API IDs. Indexed documentation uses `follow` to resolve the current
release before checking its allowance. Ended model promotions retain their quota
evidence without advertising a current allowance.

### Page and catalog evidence

Public HTML reads try ordinary HTTP first. A confirmed browser challenge can
start one anonymous `curl_cffi` browser-profile recovery, with a 20-second budget,
up to 5 redirects and an 8 MiB body limit. API catalogs and completion requests,
authenticated clients, private destinations, query strings, rate limits and gone
pages cannot use it. Recovery supplies the vendor's original HTML and status to
the same content checks. It never earns a verification by itself. The probe's
`failures/page-reads/` receipts preserve both responses; the update workflow
uploads them as `public-page-reads`. The review collector retains those attempts
for source reads and uses ordinary HTTP for publication byte checks.

Every `page-keywords` probe needs at least one keyword that disappears when the
free tier does. Three shapes qualify:

| Anchor | Example |
|---|---|
| a figure — quota, price, grant | `$0.10, subject to change` · `anonymous users get one request every 15 seconds` |
| an id — the free model's, as the page prints it | `mistral-medium` · `qwen/qwen3.8-27b` |
| a sentence of 4+ words quoted from the page | `free models through kilo gateway` |

**Keywords are matched against what the page renders**, with `<script>`,
`<style>` and inert `<template>` content removed — JSON-LD excepted when it is
the vendor's structured answer. Strings that exist only in a state blob, an
OpenAPI enum, a response sample or an i18n bundle do not prove that the offer
still exists. When page data is the evidence, put those strings in
`probe.machinery_keywords`, which is searched against the whole response, and
say in `limits` where the evidence lives. Rendered whitespace is normalized and
comments are ignored, so a sentence split by a template still matches as a
reader sees it.

**A page that moves with every release is read through the index that names
it.** Set `probe.endpoint` to the index, `probe.follow.field` to the dotted path
containing the current page prefix and `probe.follow.suffix` to the path after
it. An index that
names no page is `inconclusive`; the page it names is read like any endpoint,
and a 404 fails the row. `freetier-quotes` and the scout read the resolved page,
while the provider page tells readers where the probe starts.

A probe whose keywords are all words that outlive the offer is rejected by
validation, so CI fails on it: `free`, `hobby`, `free quota`, `monthly credits`,
`no signup`, and `no credit card required`. On an `api-models` probe against a
gateway that publishes prices, set `require_zero_price: true` — a model id can
remain in a catalog after it stops being free. Free means free by the catalog's
own account: its `isFree`/`free` flag where the row carries one, otherwise every
published price is zero. A zero per token beside a charge per request or per
second of audio is a price. Where a catalog publishes `available`, the probe
reads it too; a vendor-marked unavailable model is not a free lane. An unpriced catalog may use `tier: free`. Published prices take precedence over that label;
an unreadable price does not become free. Native speech transcription and audio generation use mandatory billing lines even beside zero token summaries;
optional audio input does not price a free text lane.

**A vendor can list its free lane under a key of its own.** Set `probe.lane` to
`free` on the `api-models` probe when that array names the vendor's free lane.
The probe reads only that array: every family in `models[]` and every
`api.model_ids` entry must be in it, and an empty lane fails like an empty
catalog. Distinguish a renamed or missing lane from a lane that currently lists
no ids; the two findings require different repairs.

**A lane served only inside the vendor's own client lists its ids in
`client_lane`.** Use this when free models are selected inside an installed
client and are not available through the vendor API. `client_lane.model_ids` is
checked against the client lane in both directions; `client_lane.no_family_ids`
keeps a rotating codename out of the Models column with a review reason. A
client lane cannot coexist with an `api` block. Its catalog probe needs a named
lane or checked zero prices. A prose-based client lane needs
a per-model identity binding and allowance on the same source for every ID:
`model_bindings` names the model and `quotas[].model_ids` binds its free
allowance. A shared credit wallet is insufficient. The same
`client_lane.model_access.until` expires a dated client promotion.

**A catalog that prices nothing takes its free marks from the vendor's own
list.** Set `probe.free_list` to the keyless document that carries the vendor's
free marks and keep `require_zero_price: true`. The probe joins those marks to
the API catalog and treats dated retirement as unavailable. This adapter reads the
NGC catalog shape used by `nvidia-nim`; other response shapes are reported,
never guessed. An unreadable list is `inconclusive`; a readable list that marks
nothing free fails the row.

### Model identity and free eligibility

**Every family in `models[]` must be named on the page the probe reads.** The
same run that verifies the offer verifies each family: an `api-models` probe
checks catalog membership and free status, while a `page-keywords` probe checks
family text on the page it fetched. A missing family is reported as
`stale-models`; the entry stays live while the column is repaired. A catalog
that serves none of the row's families fails. If an id belongs to the free lane
but has no textual anchor, keep it in `api.model_ids` without making a family
claim. Model names in scripts and inert templates need explicit `machinery_keywords`; comments cannot keep a family listed. A prose-based client
lane uses its separately checked per-model identity and allowance sources.

**An automatic free router declares its upstream catalog in `api.free_routers`.**
Each callable router ID carries a `source` and its owning catalog's forwarding
`quote`. A family reached through that route names the router ID and exact
upstream model ID in `models[].router`. Both catalogs must confirm free,
available access. The shared model labels and Connect section disclose that
the router chooses the model; automatic routes stay outside measured model pools.

**A short gateway ID can have a sourced model identity.** Record it in
`api.model_bindings[ID]` or `client_lane.model_bindings[ID]`, with `family`,
`source`, `quote` and an optional `target` model-card link on that source.
Set `read: catalog` to bind identity text to that exact ID in a JSON catalog.
The exact ID must already be listed. Its source text and link are checked again
by the probe and review collector. The binding applies only to that row;
another gateway can serve a different variant under the same short ID.
Family matching, model pages, tiers, age reports and promotion expiry use the
same binding. A binding cannot make a paid or unavailable ID free.

**A page catalog keeps the complete picker separate from free families.**
`page_catalog` derives `models` and `newcomers`; the registry writer saves only
the catalog for these rows. Record each picker or specialist model once, with
shared conditions and sourced notes in the catalog rather than a second model
list in `limits`. A free session can start a named family's bar; a spending
wallet without such a lane remains visible without entering the free-family
index. `first_free` records the start of the independently free offer, and
`listed` publishes an eligible family for the tier workflow. Wallet records keep
family identity without an unchecked score tier.

The provider, main table, JSON, browse and LLM views use the same catalog. The
page probe checks budgets, the complete picker, limited-mode membership and exact
conditions. Record a session-based limited allowance in `limited_allowance` as a
short quote from the configured FAQ. If model-hour prices are no longer
published, use `table_heading: null`, a `wallet` condition and a dated
`reviewed_on`; the probe requests a fresh review after 7 days. A condition may
name its own `source`, which is checked separately. Shared wallet conditions stay
under Limits rather than model labels. Budgets may bind an exact `quote` for each
scope. An unpublished `amount` stays null, needs the same dated review and is
never rendered as zero or unlimited. An unreadable contract or changed value is a review finding; an
unavailable page remains inconclusive. Known offer deadlines belong in
`page_catalog.model_access[display name].until`: expiry removes the free-family
claim and marks the ended offer while retaining wallet and source evidence. The
catalog source must be the row's directly probed page. This records the
advertised selection; it does not establish an authenticated completion.
An offer still available through a saved selection can set `in_picker: false`.
Its model-specific condition needs its source and a checked quote or dated
review naming that model. The picker comparison omits it; its access evidence,
free-family qualification and review remain required.
An offer that uses no hours can use an `unmetered` condition with a model-specific quote
on its source. The probe rechecks the quote alongside picker and limited-mode
membership; the family's own first-free date still sets its waiting period.

A page catalog's `free-session` condition needs `eligibility`: a named `plan`,
an exact model/plan `table` binding, the free cell's `value`, and a `plan_price`
binding proving that plan's recurring price is zero. The probe checks both
cells on the condition's source. A missing, paid, duplicate or unreadable
cell flags the free-model claim; a matching promotion sentence cannot replace it.

**A sum to spend names no model.** The Models column lists models the vendor
serves free in their own right: a free lane, a free tier or trial that names its
models, or a free quota per model. When the free part is an amount the account
spends across the catalog, the column stays empty; the prose says what the
amount buys and `api.model_ids` carries exact ids to paste. If the vendor names
no id a request carries, use `api.no_ids`; a connectable row must have either
that field or an id list.

A cap counted the same on every model is a free-tier limit, not a spending sum.
Every live row records its kind in `free_part`, and `freetier-check` refuses a
missing value: `models` names the models served free in their own right, `sum`
means an amount spent across listed models, and `unnamed` means the vendor does
not say which models the free part reaches. Only a row of `models` may name a
family. An offer can have a spending wallet beside independently free models;
classify and list those free models separately. `freetier-bars` checks every id
in a row of `models`; an omitted free model needs an explicit decision and reason.

### Promotions and waiting periods

**A dated free promotion is listed immediately.** Once official sources confirm
the free usage and its conditions, give the model its family and record the
deadline in `model_access.until`, even if it ends within two weeks. Readers can
use a brief promotion to try a model they otherwise could not afford. The
deadline appears beside the model; a dated promotion also gets its own model
page. This is one rule for every vendor, not an exception granted to a request.

`freetier-render` withdraws expired IDs and their families at the recorded
instant, preserving a family if another matching ID remains live. It retains
expired API conditions under `ignored_ids`, records the change through the
history writer and keeps published pages. `--check` never mutates the registry.
If the last free ID ends, the offer moves to Archive at the vendor deadline;
the row and all its evidence remain available.
`remaining_free` records a separately continuing mode with its `source`, `quote`,
`free_part` (`sum` or `unnamed`) and optional payment `access`. Its eligibility
quote is re-read by the probe. When the last promotion ends, this evidence keeps
the provider live with that free part and payment condition, without retaining
an expired model ID or assigning an unconfirmed replacement.
For a prose-based tool without callable IDs, `model_access` on the entry uses
the exact family, an eligibility `quote` and a `deadline_quote` beside `until`.
The same source checks, model labels and expiry writer apply. Ended families
remain in `expired_models`; their family-bound quotas stay as evidence and are
excluded from current Limits.
The hourly `expire promotions` workflow invokes `freetier-render --expire-only`,
which writes nothing before a deadline and earns no verification fields.
It explicitly requests a Pages build before notifying IndexNow. A manual run
also rebuilds Pages if no promotion ended, so the publication path can be
checked without changing a deadline. Verification and expiry share a queued
writer group, preserving pending verification runs.
If an earlier publication failed, the next hourly check repairs its Pages build
even when no further model expired.
Publication follows the next successful run; GitHub scheduling can delay it.
The exact deadline remains visible in the interim.

**An undated model on a rotating lane waits two weeks.** A new id is callable
from the read that finds it and joins `models[]` two weeks later, counted from
that read or from the vendor's own free date. A router, stealth codename,
non-coding model, model never named on the probed page and a lane that rotates
one model at a time stay in `api.no_family_ids` (or `client_lane.no_family_ids`)
with a review reason. Dated promotions follow the immediate-listing rule, and
an expired promotion never joins.

`uv run freetier-bars` dates every id in `api.model_ids` and
`client_lane.model_ids` from registry history or an earlier vendor date. It
prints ids that are owed a family and names unreadable free lists;
`freetier-check` refuses an id in `no_family_ids` that the row does not list or a
family already names. An older record that proves an id was free belongs in
`api.free_since` (or `client_lane.free_since`) with the id, date and record; the
record goes when the family joins.

A row with no lane or structured page catalog records a page-only model in
`newcomers`: its family, first free date and source. The report counts two weeks
from that date, validation refuses `newcomers` beside a lane or sum, and
`freetier-check` refuses a newcomer whose family is already in the column.

Discovery checks every available catalog row marked or priced free, even when
its ID does not match `probe.free_marker`. The marker still scopes family
qualification; it cannot hide arrivals from review. Noncoding models, duplicate
aliases and unresolved offers require explicit `ignored_ids` decisions with
dated private evidence and a recheck trigger. A new zero price does not promote
a family or establish an authenticated completion.

### Callable ids and client limits

**The configs call ids, never family names.** `configs/litellm.yaml` and
`configs/opencode.json` are written from `api.model_ids` alone: a family names a
model, while an id is the exact string a request carries. `freetier-check`
refuses a connectable row whose Models column names families without ids.

An explicit catalog operation list must include `Chat Completions` for an ID
used by an OpenAI-compatible chat configuration. The probe reports an
incompatible list for review; absent operation metadata establishes no
restriction. A shared free token balance does not turn a model for decisions,
embeddings or code editing into a chat model.

**Client token limits are rechecked at their source.** When a client's default exceeds
the vendor's cap, record `api.model_limits[ID]` with positive `context_tokens`,
`output_tokens` and `source`. By default, `read: catalog` compares the limits
with this row's checked catalog on every verification, reporting changed or
unavailable context and output values.
For an official OpenCode configuration example, set `read: opencode-config` and
`source_provider` to its exact provider key. The source is re-read for the exact
`provider` / provider key / `models` / model ID / `limit` object in JSON code
examples or a JSON configuration file. Context and output must both be positive
integers; missing, conflicting or changed limits require review. Unrelated model
or provider examples and prose containing the same numbers cannot satisfy it.
The writers supply OpenCode's context/output limits and LiteLLM's default
`max_tokens` for named and pooled deployments. An explicit client token request
can override that LiteLLM default; verify affected clients with live requests.

An OpenCode request budget can instead be chosen in `api.opencode_output_tokens[ID]`.
This positive token count is a client setting, separate from the vendor's model
limits. It writes `max_completion_tokens` into that model's request options
and gives `max_tokens` the same budget for older clients;
it does not supply a context window or assert an unpublished output limit.
The probe rechecks support for this parameter in the row's catalog. If the
vendor documents the output parameter on a page instead, record its exact
`source` and `quote` in `api.opencode_output_sources[ID]`; the quote must name
the parameter and chosen token count, and the probe rechecks that page. Verify a
budget with `freetier-review client`: it records the forwarded request budgets
and checks the real tool read, final answer and completed session. Recheck on
client or upstream changes and retain a dated vendor/client review.

For a page listing paid and free models together, `probe.model_prices` binds
the name column and at least two price columns in one exact table. A model is
eligible only when both its input and output cells equal the declared free
value; a free cached-input or storage cell does not qualify a paid model.
An absent or ambiguous table asks for a model review rather than accepting
names elsewhere on the page.

Bound model tables are checked in both directions: every eligible row must be
accounted for by a listed family, a waiting newcomer, or a sourced exclusion.
Newcomers that lose Free eligibility are flagged before their promotion date.
`newcomers[].table_name` binds a waiting offer to its exact table label where
that label differs from the eventual family; it does not prove model identity.
`models[].table_name` binds a qualified family to an exact vendor label too,
including its variant or footnote, without making broader names cover new rows.
For a tool without a public API, waiting choices also appear in its existing
Connect model list without entering the qualified-family index. A waiting
family on a prose page is checked against that current page too; its exact
Free-plan eligibility still requires the source review.
`probe.model_exclusions` records `name`, `source`, `quote` and `reviewed_on` for
an exact excluded row. Its quote is checked on its own source, and an exclusion
needs another manual review after 7 days. Missing excluded rows also require
review. Inventory findings go to a human; they never promote models or restart
their age automatically.

For a model-by-plan table, `probe.model_plan` binds the model-name column and
one exact plan column. Only an explicit inclusion mark in that cell qualifies
the model; availability on another plan or elsewhere on the page does not.
Missing or duplicate tables and duplicate model rows require review. This uses
the same table reader as price eligibility, whose two-price requirement remains.

### Client compatibility

**A key the reader has not set never becomes another of theirs.** The proxy
command clears `OPENAI_API_KEY` so a missing provider key cannot fall back to
the reader's own key. `render.litellm_command` supplies the complete loopback
startup command. Vendor-published `api.public_key` values are included only for
their own lanes. A keyed `claude-code.sh` function stops until its variable is
set, protecting the reader's other credentials. The measured behavior and
release details belong in the generated configs and `conformance.py`.

**Codex CLI reaches the lanes through LiteLLM.** Every deployment carries
`use_chat_completions_api` so the proxy adapts Responses requests to the lane's
chat completions; the header asks for LiteLLM 1.98 or later. The profile at
[`configs/codex/litellm.config.toml`](configs/codex/litellm.config.toml) goes in
the client's config directory: `--profile NAME` has read
`$CODEX_HOME/NAME.config.toml` since Codex CLI 0.134. Its settings disable
reasoning summaries, sub-agents and web search. Client behavior is checked by
conformance; current vendor compatibility needs real requests.

**What the configs say LiteLLM and Codex do is run, not remembered.** Each
sentence `configs/litellm.yaml` and the Codex profiles print about the two
programs — which release reads a field, where the proxy sends a key, what Codex
sends a lane — is a check in `src/freetier_radar/conformance.py`, and the
`conformance` workflow runs them every Wednesday and on a push that changes what
the files say: the oldest release the files ask for and the newest, the proxy
started by the command the file prints, every lane pointed at one the check
serves and records, Codex on the profile copied where the profile says. A
sentence the programs stop bearing out is a red run that names it and the
release; so is a sentence reworded with its check left behind, and a program
that could not be run as printed.

The verification and expiry writers explicitly dispatch this workflow when
their pushed commit changes watched paths. An automatic dispatch names the
commit, which the run checks before downloading clients.

**`api.model_ids` is checked against the catalog in both directions.** On an
`api-models` probe every id must still be present, callable and — where
`require_zero_price` is set — priced 0. A dead id is reported as `stale-ids`,
with any catalog id that looks like its successor. A vendor-marked unavailable
model or an id past its retirement date is dead whatever its price says. The run
also reports every zero-priced catalog id missing from `model_ids`; these are
review findings, never automatic repairs. Record intentionally omitted ids in
`api.ignored_ids` with a review reason, and keep `api.note` for connection advice.
A keyless catalog at another URL belongs in `probe.catalog`. A catalog that
stops answering is reported as `stale-ids`. A failing `api-models` row carries
its catalog response after a `|`; a failing `page-keywords` row is the offer
itself and is repaired or archived whole. A `stale-models` flag ends nothing:
ids and client lanes are still checked and their findings follow the flag after
a `|`.

**The scout repairs a family verdict, never the half after the `|`.** That half
stays on the pull request's "needs a human" line even when the Models column was
answered. A reply that drops a family the row's own probe still names keeps the
family and records the discrepancy under rejected candidates; shortening a
column cannot prove that a family ended.

**`api.anthropic_base_url` is the Claude Code answer.** Set it only where the
vendor documents an Anthropic Messages route; an auth response alone proves
nothing. `ANTHROPIC_BASE_URL` stops before `/v1/messages`, which the client adds.
Each run calls the route keyless with the first `api.model_ids` value. In this
route check, a 401, 400 or 429 is a route, a 404, 405 or 410
is reported as `stale-ids`; an unreachable route is reported too. The offer
remains verified by its page. The field feeds Claude Code connection data and
`configs/claude-code.sh`.

**`api.codex` is the Codex CLI answer, for a lane Codex calls directly.** Its
`base_url` stops before `/responses`. Set it only when the vendor documents
Codex for this exact free lane and model, or a keyless profile request completes.
A general Responses reference, a paid plan's guide or a 401 is insufficient.
A keyed lane carries `source` and a rechecked `quote` naming Codex. The field
generates `configs/codex/<id>.config.toml` with the first model id, its env key
and the same settings as the LiteLLM profile; connection views link to it.

Every run checks keyless lanes after a chat completion, including bearer
behavior and completed streaming responses. A broken stream is retried; a
persistent refusal or a JSON response to a streaming request is `stale-ids`.
A keyed route is checked the Anthropic check's way: a 404, 405 or 410 is
a route that is gone. Where the catalog publishes per-model endpoints, the
profile's first id must support Responses. The field needs an OpenAI-shaped lane
with an id, cannot coexist with `session_header`, and the one id it
cannot take is `litellm`, the LiteLLM profile's name. Conformance checks that an
unset or empty key stops the profile before any request, even with other
credentials present.

**`api.session_header` is for a lane that wants an id per conversation.** Set it
to the header name when every request needs a stable conversation id. No row sets
the field today. A `litellm.yaml` entry is written once and cannot mint an id per
conversation, so a row that sets it is left out of `litellm.yaml`, `opencode.json`
and `claude-code.sh`; the connection tables, pages, env example and `llms.txt`
name the header. The keyless check and README quickstart send a fresh id. What a
lane asks every request to carry is decided in `ApiInfo.asks`; each table keeps
one line for every ask.

**`api.client_user_agent` is for a lane that asks every client to name itself.**
Record the vendor's requirement in this field. The README quickstart sends `User-Agent: awesome-free-ai-coding-quickstart/1.0`; connection tables, provider
pages and `llms.txt` tell readers to send their own client identity. The keyless
check always calls under this project's own `freetier-radar/0.2`.

### Keyless access and data use

**`api.auth: none` is checked by calling the lane without a key.** The README's
zero-signup curl uses this field and the first `api.model_ids` value. Each run
sends a one-token request to `<base_url>/chat/completions`, without Authorization,
adding a fresh `api.session_header` value when required. A 2xx must carry a
message completion without a body or choice error. A completion naming another
model is `stale-ids`; equivalent vendor spellings are accepted, and automatic
routers name no single model to compare.

Anything else sends the check on to the next id, up to
three, while respecting retry and rate-limit headers. A later id answering is reported as `stale-ids`
naming both results. A 429 can be retried within the allowed budget; a longer
`Retry-After` stops further inference until it has elapsed. Rate-limited ids are
reported explicitly, never used alone to reorder defaults. Without an answering
id, a first-id 401/403 fails the probe unless `api.notice` holds it; a bot wall
is `inconclusive`. Other 4xx responses and unreachable lanes are `stale-ids`
beside a still-verified row. Review eligibility and agent/tool compatibility
before changing a default or removing an existing notice.

**`data_use` is the vendor's word on training on what a reader sends.**
`trains: yes` means the free offer may train or improve models, `opt-out` means
that is the default with a setting to turn it off, and `no` means the vendor
says it does not. `quote` is the exact sentence covering the free offer and
`url` its readable source; a paid or enterprise promise does not cover a free
lane. A gateway's `no` must cover the upstream providers too. If any selectable
free model permits training, use `yes`, or `opt-out` if a setting avoids it.
When the vendor says nothing, omit the field. The README marks `yes` and
`opt-out`, the provider page quotes the sentence, Browse filters `no`, and each
run reads the quote back.

**`api.refuses_bearer` is a keyless lane that answers only a bare call.** After
the first id answers, the run asks it again with `Authorization: Bearer none`.
A refusal without this field or an answer with it is `stale-ids`; a rate limit
says nothing either way. LiteLLM and Claude Code send a bearer token, so their
generated configs exclude these lanes. OpenCode keeps a compatible bare lane.

**`api.public_key` is a key the vendor prints for anyone.** Use it only when a
vendor page publishes the key and its limits. The row stays `auth: api-key`,
and `key_url` names the source. The env example and connection views print it
with that source; it counts as no-account access, while the README's first curl
stays keyless. Each run tests the key and reads its source. A refusal fails the
public-key offer; a key that still works but is no longer published is
`stale-ids`. A leaked, pooled or otherwise shared key never qualifies.

**`api.notice` discloses a lane that does not work as published.** Use it when
the maintainer temporarily keeps an unexplained broken lane. Record `since`,
`text` (what a reader encounters, vendor output in backticks, 500 characters
at most) and a follow-up `url`. The warning appears with the quickstart when
applicable, in the connection table, above the provider offer and in `llms.txt`;
`index.json` carries it too. On a keyless row it holds a refusal off the failure count for 30 days from `since`.
The run reports `stale-ids` during that hold, then counts the refusal normally.
A successful first-id response asks for review of the notice. When the vendor
explains the restriction, update the row to match; do not keep a notice as a
permanent workaround.

## How the pipeline works

`registry.yaml` is the single source of truth. `README.md` is **generated** — never
edit it by hand. Twice a week GitHub Actions probes every entry (live model APIs and
pricing pages), commits verification results, and a web-evidence scout (Tavily, Hacker
News, GitHub search, curated feeds, and a digest of every models.dev provider that
publishes a zero-cost model → LLM extraction → live probe gate) proposes new entries
via pull request. Maintainers review the verification findings and scout PR;
a green workflow does not establish that every vendor fact is current.

The README is the landing page, and the site is the reference. The README
carries the hero, recent additions, picks, comparison, quickstart and one
unfolded list item per live row: its name, `offering`, the first eight
model families and the date. Quotas live on provider pages and `index.html`,
with every family past the eighth, one click from their count. The comparison shows at most 20 families;
measured scores lead, followed by retained-tier and natural model-name order.
Unavailable scores do not become zeros. The comparison axis starts at 0 and scales to the free models,
with labelled, equally spaced ticks, a round upper bound and the same scale at
both widths. The global index leader is a separate reference; the graph names
its index revision and read date. The model index keeps every family and free
provider. `README_BUDGET` in `render.py` is the tested size ceiling.

`providers/` is generated with it: one page per registry row, the provider index
and the page of services checked. A live row's verified date and an archived
row's name link to its page. `_config.yml` supplies canonical URLs and the
sitemap; [`_layouts/default.html`](_layouts/default.html) supplies the shared
heading, navigation and breadcrumb. `404.html` offers rows matching the missing
address. **Never edit generated provider pages by hand**; the render owns their
body and protects vendor text inside `{% raw %}`.

`models/` is generated with them: a page for every model two rows or more serve
free, or that measures notable, strong or frontier, plus an index of every model
served by live rows. A model page lists current providers, access conditions,
verification dates, limits and callable ids, followed by historical providers.
Dated promotions get a page immediately; other one-provider, unmeasured models
stay on the index. **A page, once published, stays** even when a model falls
below the bar or no row serves it. The render reads existing pages beside the
registry, and `freetier-gate` refuses deleting a page under `providers/` or
`models/`. Every page under both carries `last_modified_at`; substantive content
changes advance it, while a routine generation stamp does not. Jekyll writes it
to the sitemap and structured data. **Never edit these pages by hand.**

[`index.html`](index.html) is the site's front page, rendered from the registry
by [`templates/index.html.j2`](templates/index.html.j2) — **never edit it by hand.**
It is a site-specific HTML view of the same data because GitHub Pages and GitHub
Markdown support different block, alert and table markup. `freetier-render --check`
holds the two outputs to the same registry, and `_config.yml` leaves the README
off the site.

[`configs/README.md`](configs/README.md) is generated with them, from
[`templates/configs-README.md.j2`](templates/configs-README.md.j2): the connection
table — base URL, key variable, the important note and any documented
Anthropic-format route — beside the five configs it describes. It is written for
GitHub's renderer and stays off the Pages site. **Never edit it by hand.**

`llms.txt` is generated with them as the machine-readable list. `browse.html`
is the hand-written filterable page; it reads `index.json` in the browser and
shares its field names with the generated data. After publication,
`freetier-indexnow` submits only changed published URLs after Pages has built the
commit. `.github/workflows/indexnow.yml` applies the same map-derived path filter
for other pushes to `main`. The ownership key is the root file named after it;
it grants no access beyond asking an engine to crawl this site.

Google's sitemap reference belongs in the host's root `robots.txt`, not the
project-site path. It is maintained in the user-site repository
[`mvalentsev/mvalentsev.github.io`](https://github.com/mvalentsev/mvalentsev.github.io).
Keep that host file when maintaining indexing; setting a custom domain there
also moves this project site.

Every change to what the list publishes — a row arriving, entering the Archive,
returning, or changing its free models — is appended to [`history.jsonl`](history.jsonl)
by `freetier-render` in the commit that makes the change and published as an
[Atom feed](https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml).
**Never edit it by hand.** The render compares the registry with the existing log,
records the difference before it writes pages and preserves the append-only
history. A repeated render before committing replaces only its own uncommitted
events. A row's `first_seen` agrees with the original Added event.
Calendar-driven changes are recorded by the first render after their condition
takes effect.

## What depends on what

Every file this repository tracks is one line of the map below, and
`freetier-check` refuses a file that is on no line, a line that names no file,
and a page the site serves or leaves out against the map. A **generated** file
is never edited by hand: change what it is made from and run `TZ=UTC uv run
freetier-render`, which also prints this table from
[`layout.py`](src/freetier_radar/layout.py). A **log** is written by its
command alone. **Data** is edited by hand and read back by `freetier-check`.
Whatever every page prints — a count, the verified floor, a rule such as the
frontier bar or how often a row is probed — is worked out in one place in the
render and stated from the constant that applies it, so the README and the site
cannot print two versions of it.

<!-- The map: printed by freetier-render from layout.MAP. Edit layout.py, not this table. -->

| File | What it is | Made from | Written by |
|---|---|---|---|
| `registry.yaml` | **data** — every row the list has published, live or archived — the single source of truth | — | `hand`, `freetier-probe`, `freetier-tiers`, `freetier-scout`, `freetier-render` |
| `watchlist.yaml` | **data** — services checked and not listed: the date, the reason, what would reopen them | — | `hand` |
| `blocklist.yaml` | **data** — domains rejected for cause | — | `hand` |
| `sources.yaml` | **data** — lists read once and put down | — | `hand` |
| `dismissed.yaml` | **data** — model-generation bumps a reviewer declined | — | `hand` |
| `history.jsonl` | **log** — every change to what the list publishes, one event a line, append-only | `registry.yaml` | `freetier-render` |
| `announced.jsonl` | **log** — the posts the announcer has sent, append-only | `history.jsonl` | `freetier-announce` |
| `README.md` | **generated** — the landing page GitHub shows under the file list · not on the site | `templates/README.md.j2`, `registry.yaml`, `watchlist.yaml`, `history.jsonl`, `src/freetier_radar/intelligence-index.json` | `freetier-render` |
| `index.html` | **generated** — the Pages site's front page | `templates/index.html.j2`, `assets/model-name.js`, `assets/search.js`, `registry.yaml`, `watchlist.yaml`, `history.jsonl` | `freetier-render` |
| `configs/README.md` | **generated** — the connection table, beside the configs · not on the site | `templates/configs-README.md.j2`, `registry.yaml`, `watchlist.yaml`, `history.jsonl` | `freetier-render` |
| `configs/opencode.json` | **generated** — the opencode config | `registry.yaml` | `freetier-render` |
| `configs/litellm.yaml` | **generated** — the LiteLLM proxy config and its groups | `registry.yaml` | `freetier-render` |
| `configs/free-llm.env.example` | **generated** — one export per key | `registry.yaml` | `freetier-render` |
| `configs/claude-code.sh` | **generated** — one Claude Code shell function per Anthropic-format lane | `registry.yaml` | `freetier-render` |
| `configs/codex/*.config.toml` | **generated** — Codex CLI profiles: one over the LiteLLM config, one per lane Codex calls directly | `registry.yaml` | `freetier-render` |
| `index.json` | **generated** — every row and the watchlist, for machines | `registry.yaml`, `watchlist.yaml` | `freetier-render` |
| `feed.xml` | **generated** — the Atom feed of the history | `history.jsonl`, `registry.yaml` | `freetier-render` |
| `llms.txt` | **generated** — the whole list as one text file | `registry.yaml` | `freetier-render` |
| `assets/readme/*.svg` | **generated** — the README's pictures: the radar at the top, a dot per live row, and measured free models on a zero-based score axis with the index leader named separately, in each width and theme the README serves — and the radar alone, the site's mark beside its name | `registry.yaml`, `src/freetier_radar/intelligence-index.json` | `freetier-render` |
| `providers/*.md` | **generated** — a page per row, the provider index and the page of services checked · never deleted once published | `registry.yaml`, `history.jsonl`, `watchlist.yaml`, `blocklist.yaml` | `freetier-render` |
| `models/*.md` | **generated** — a page per widely served or strong free model, and the index of every free model · never deleted once published | `registry.yaml`, `history.jsonl` | `freetier-render` |
| `browse.html` | **page** — the filterable table, reading index.json in the browser | `index.json`, `assets/model-name.js`, `assets/search.js` | `hand` |
| `404.html` | **page** — what Pages serves for an address the site does not have, offering the rows that name what the address asked for | — | `hand` |
| `assets/*.svg` | **page** — the favicon and the social preview's source | — | `hand` |
| `assets/*.png` | **page** — the social preview | — | `hand` |
| `assets/*.js` | **page** — shared browser search, model matching and sorting | — | `hand` |
| `assets/*.css` | **page** — shared model sorting controls | — | `hand` |
| `eb68c254f1e03877b906ccc800002691.txt` | **page** — the IndexNow key, named after itself (indexnow.INDEXNOW_KEY) | — | `hand` |
| `AGENTS.md` | **doc** — standing review and evidence rules for repository work · not on the site | — | `hand` |
| `CONTRIBUTING.md` | **doc** — how the list works and how to change it; its map section is this table | `src/freetier_radar/layout.py`, `src/freetier_radar/claims.py`, `.github/workflows/ci.yml`, `.github/workflows/conformance.yml` | `hand`, `freetier-render` |
| `LICENSE` | **doc** — MIT | — | `hand` |
| `assets/README.md` | **doc** — what each asset is for · not on the site | — | `hand` |
| `src/freetier_radar/*.py` | **code** — the probe, the scout, the render and the checks · not on the site | — | `hand` |
| `src/freetier_radar/intelligence-index.json` | **data** — the Artificial Analysis Intelligence Index as freetier-tiers last read it: the day, the top, the median and the score of every family the list measures · not on the site | — | `hand`, `freetier-tiers` |
| `src/freetier_radar/developers.json` | **data** — the developers GitHub's Innovation Graph counts per country in its latest quarter — the yardstick a border's share is counted on · not on the site | — | `hand`, `freetier-borders` |
| `templates/*.j2` | **code** — the page templates freetier-render fills · not on the site | — | `hand` |
| `tests/*.py` | **code** — the test suite · not on the site | — | `hand` |
| `pyproject.toml` | **config** — the package and its commands · not on the site | — | `hand` |
| `uv.lock` | **config** — the pinned dependencies · not on the site | — | `hand` |
| `_config.yml` | **config** — the Pages site: its name, its plugins, what it leaves out · not on the site | — | `hand` |
| `_layouts/*.html` | **config** — the page every generated Markdown page is served in: one heading, the way back to the indexes, the breadcrumb · not on the site | — | `hand` |
| `.gitignore` | **config** — what git leaves alone · not on the site | — | `hand` |
| `.imgbotconfig` | **config** — the images ImgBot leaves alone — all of them: the README's pictures are generated, the favicon and the preview's source keep their comments, and the preview's PNG is the one uploaded to GitHub · not on the site | — | `hand` |
| `.githooks/*` | **config** — the git hooks that run freetier-gate — `git config core.hooksPath .githooks` · not on the site | — | `hand` |
| `.github/workflows/indexnow.yml` | **config** — IndexNow after publication; its push filter is generated from the published map · not on the site | `src/freetier_radar/layout.py` | `hand`, `freetier-render` |
| `.github/workflows/ci.yml` | **config** — registry, generated output and package compatibility checks · not on the site | — | `hand` |
| `.github/workflows/conformance.yml` | **config** — client compatibility on the generated configs · not on the site | — | `hand` |
| `.github/workflows/expire.yml` | **config** — publish only model promotions whose deadlines have passed · not on the site | — | `hand` |
| `.github/workflows/read-page.yml` | **config** — read primary pages with the project HTTP client · not on the site | — | `hand` |
| `.github/workflows/update.yml` | **config** — scheduled verification, model measurements and scouting · not on the site | — | `hand` |
| `.github/dependabot.yml` | **config** — the watcher of the pinned actions and of uv.lock · not on the site | — | `hand` |
| `.github/ISSUE_TEMPLATE/*.yml` | **config** — the suggest-a-service form · not on the site | — | `hand` |

<!-- End of the map. -->

## How the list announces itself

`freetier-announce` runs in the same workflow, after the verification commit:
every event `history.jsonl` has gained — a row arriving, dropping to
the Archive, coming back, changing its free models — becomes one post from
the project's own accounts, labelled as a bot, linking the row's page. It posts
only events from the last 14 days, at most five per channel per run, oldest
first, and only what a channel has not posted before: `announced.jsonl` is the
append-only ledger, keyed by event and channel, so a retried run cannot post a
line twice and a channel that failed is simply retried next time. `--dry-run`
prints every post due on the channels configured and sends nothing.

Channels come from the repository's settings, and until they exist the step
prints "no channel configured" and exits 0:

| Channel | Variable (Settings → Variables) | Secret (Settings → Secrets) |
|---|---|---|
| Bluesky | `BLUESKY_HANDLE` — the account, e.g. `freetier-radar.bsky.social` | `BLUESKY_APP_PASSWORD` — an app password, not the account password |
| Mastodon | `MASTODON_BASE_URL` — the instance, e.g. `https://fosstodon.org` | `MASTODON_ACCESS_TOKEN` — an application token with `write:statuses` |
| Dev.to | — | `DEVTO_API_KEY` — from Settings → Extensions; publishes **one article a month**, the whole list plus what changed last month, on the first run of each month |

Mark the accounts as automated (Mastodon's "This is an automated account", Bluesky's
profile text) and link the repository from them. Nothing here posts to Hacker
News, Reddit or anyone else's list: those forbid or punish automated
submissions, and a post there is a person's decision every time.

## Development

Keep additions within the existing public presentation: provider pages share
their sections, the Free models column holds eligible families or its empty
state, and selection details and conditions belong under Limits. Before
changing a shared component, compare the previous output and representative
peer rows. Preserve these structural contracts in tests separately from checks
that the new data appears. Review the rendered desktop and mobile result;
updating expected strings alone is not a presentation review.
Shared usage limits appear once under Limits, rather than in per-model access
labels. Keep conditions specific to a model attached to that model.

```bash
uv sync
git config core.hooksPath .githooks   # once per clone
TZ=UTC uv run freetier-render         # after changing a source used by generated files
uv run freetier-check
uv run pytest
```

Hooks choose a writable uv cache when `UV_CACHE_DIR` is unset. Other commands
remain available as needed:

| Command | Purpose |
|---|---|
| `uv run freetier-map` | Identify each file's sources and writer. |
| `uv run freetier-probe --dry-run` | Probe all offers live without writing verification fields. |
| `uv run freetier-quotes [ids…]` | Re-read vendor quotes; `--report` prints the scheduled summary. |
| `uv run freetier-bars` | Report free ids owed a family after the waiting period. |
| `uv run freetier-announce --dry-run` | Print due announcements without sending them. |

`freetier-render` also generates the registered numerical rule values in this
guide from their code constants. Other assertions remain checked by `claims.py`;
missing or reworded registered sentences still fail validation. Vendor quotes
and historical observations retain their original values and dates.

### Review and publication

`freetier-review --out <private-directory>` collects evidence for a review.
Use a git-ignored directory or one outside the repository. Run its phases in
order: `prepare --base <commit> --head <commit>`, `sources`, `judgment`, `publication`,
`browser`, then `report`. `publication` waits for the required workflows at that
exact commit, saves their full logs and open PRs, and compares published bytes.
Pages byte checks use the repository map: only files marked `published` are
served there. Changed README files are also checked at the exact GitHub commit,
including documentation excluded from Pages.
For a bot verification or expiry commit, add `prepare --verification-run <producer-run-id>`:
the full successful writer log must prove which commit it produced, since that
push runs its checks and IndexNow inside the writer instead of starting CI.
It prints workflow updates only when their state changes. Run the emitted
`browser.js` with Playwright's `browser_run_code_unsafe` filename argument,
save the returned JSON privately, and import it with `browser --result <file>`.
Run `publication` again to check the README images the browser actually loaded.
`prepare --push-base <commit>` records the commit immediately before the final
human push when it differs from the review base. Workflow requirements use that
push's paths; sources, served files and browser coverage keep the full review
range. The push base must be between the review base and head, and cannot be
changed in an existing evidence directory or combined with `--verification-run`.
`client --client <opencode|codex> --binary <path> --provider <id> --model <id>`
checks a real keyless lane in an isolated home using the committed configuration,
a fresh file, a completed tool read and its final answer. Every attempt is kept.
The browser plan checks each changed page's content once. Shared layout,
themes and desktop/mobile widths use representative providers and models,
including archived, folded and empty states where affected. README images still
exercise their wide/narrow and light/dark variants. The plan records each case's
purpose and its representatives; the importer still requires the complete plan.
Internal changes with no browser-facing output add no browser cases. Shared
layout changes still cover representative provider and model states.

The report covers collected evidence; source reads and quote matches still need
vendor judgment, affected API lanes still need controls, and the full diff still
needs independent review. The hooks below remain mandatory.

The sources phase keeps a delisted row's last-offer checks in `historical_checks`,
including source-read failures under `sources`. These remain visible without
asserting current free eligibility. A URL used by a current row or explicitly
requested still requires a successful read. Source reads and a dated withdrawal
judgment are still required when an offer is withdrawn.
The sources phase rechecks quota review deadlines and recorded territory lists
with the verification checks. Reading a matching quote does not renew a manual review.
An HTML response with an empty app mount and a client bootstrap is unreadable;
its title and metadata cannot establish the page's offer or terms.

The sources phase records unmatched hyperlinks and same-site provider comparison
links in `lead_inventory`; it does not infer a vendor domain from a comparison
slug or fetch the linked page. It also reads named links to comparisons and source directories from
HTML, inline Markdown and reference Markdown. These still need manual source and
offer judgments. Exact URL decisions preserve links to other products and other repositories;
operator blocks retain their domain scope. Query parameters remain part of the link identity.
Each captured lead needs a `lead_dispositions`
record in the judgment, with its ID, concrete finding and private evidence.
Its verdict is `canonical`, `task`, or `irrelevant`: name an existing committed
registry/watchlist/blocklist/source decision, retain an unresolved task with its
register file and ID, or explain why the link is neither a provider nor a source.
Task dispositions require a next action and keep a frozen register receipt.
Signoff and pre-push reject missing dispositions. This link inventory does not
replace reviewing prose-only leads or earlier custom source collections; retain
those in the same persistent task register until individually reconciled.

Before pushing, record that independent review with `judgment --result <file>`.
The JSON names `base`, `sha`, every changed file in sorted `paths`,
`decision: "approve"`, and these `criteria`: `existing_behavior`, `reuse`,
`copy`, `user_path`, `regression`, `diff`, `eligibility`. Each criterion needs a `verdict`
(`pass` or `not-applicable`), a concrete `finding` and an `evidence` list of
private file paths. The command imports and hashes those files; pre-push refuses
a missing review, a different push, incomplete coverage or changed evidence.

For every affected row, including unnamed free offers, `model_eligibility` covers
the previous and resulting families (an empty list still needs a record).
Each record names the current `plan`, `payment`,
`regions`, `limits`, `deadline`, and `conflicts`, with `checked_at`, current
`sources`, and private `evidence`. Source reads must succeed; records older than
one day cannot authorize a new push. Record `conflict_status` as `none`, `resolved`,
or `unresolved`; a resolved conflict needs a concrete `resolution` identifying the
superseding evidence. An archival or family withdrawal cannot pass with unresolved
free-access conflicts. Its `access_modes` must review every advertised free mode
separately, with a name, finding and current reviewed sources. Each mode must be
`ended` or `ineligible`; an available or unresolved mode blocks the withdrawal.
Ending a general credit wallet does not establish that a recurring free-model
allowance ended. A matching quote, a source-code default, a model's existence,
or a historical promotion does not establish current free eligibility.

Review the existing output and peer rows before proposing UI changes; search
for an existing implementation before adding one; remove repeated or unhelpful
copy; exercise the path from choosing an offer to connecting a client; prove
regression checks reject the old defect and allow valid controls; read the whole
diff, including unaffected peers. A test demanding the proposed new control
does not demonstrate its usefulness. Explain non-applicability with evidence.
Signoffs stay in `.remember/review-signoffs/`, never in published files.
CI and scheduled jobs run structural checks; private signoffs are enforced by
the local pre-push hook. The report also requires the recorded judgment.

### Git gates

**The checks run before a commit exists.** With the hooks on, `git commit`
runs `freetier-gate pre-commit`: `freetier-check`, `freetier-render --check` and
the test suite on a snapshot of what is staged, with the dates in UTC. It also
refuses what only a command may write: a line in `history.jsonl` that is not
one the render records for the commit's own registry, or a change the registry
makes that the commit does not record; a commit on `main` that changes
`announced.jsonl`, which only the scheduled run writes; a published log rewritten on any
branch; and a hand edit of `last_verified`,
`probe_failures`, `provisional` or `first_seen`, which only the run's probe
writes — a new row enters provisional, with `first_seen` and `last_verified`
both the day it is added; and a page the site published, under `providers/` or
`models/`, deleted. `commit-msg` wants a subject that starts with its
kind (`fix: …`) and a blank line before the body; `pre-push` runs the same
checks on what is pushed, commit by commit. A proposal branch may re-render its
own unmerged history against the point it left `origin/main`; the push protects
the inherited prefix, checks the full proposed block against its registry and
still checks each new commit for earned fields. A push to `main` protects its
remote tip. CI checks the logs again on every
push and the earned fields on every pull request. CI never runs on the scheduled run's own commit,
so the run checks its logs, the curated files, the render and the tests before it commits,
and checks the scout's branch, earned fields and tests included, before it opens the pull
request. Historical repairs ratified by the owner are named, with their reasons,
in `gate.RATIFIED`; subsequent gates use them as baselines. Ordinary changes
must pass the hooks and preserve the log and earned fields.

### Public prose and claims

**A row's prose is for the reader deciding whether to use the offer.** `offering`
says what it is, `limits` the quota, conditions and data handling, and `api.note`
what a client needs to connect. What changed and when belongs to
`history.jsonl` and the commit log, not the row. `freetier-check` holds `offering` to 300 characters, `limits` to 1,200 and `api.note` to 600. It rejects
maintenance-diary phrases in live public prose, including Models-column waiting
rules and registry field names. Full payment, fee and deadline details are shown
with callable ids; list labels use the same access metadata in shorter form.
Shared limits appear under Provider-wide limits on model pages. The README
prints `offering`, models and the date; quotas stay on the row page and site.

**A row of free models leaves them to its Models line.** For `free_part: models`,
`freetier-check` rejects an `offering` that names a live model family or one of
the row's own ids. This prevents both repetition and advertising a family still
waiting for qualification. A maker's name is allowed. A spending sum has no
Models line, so its prose can name what the amount buys.

**A phrase in quotation marks is a claim that the vendor published those words.**
`freetier-quotes` reads quotes in `offering`, `limits`, `api.note` and
`client_lane.note`, as well as explicit data-use and API Codex quotes. It fetches
a row's `source_urls`, probe endpoint and catalog, and reports every quote of three words or more that none of them carries. Replace a missing quote with the
vendor's exact words or a source URL that contains them. When one source is
unreadable, report the quote as unverified rather than claiming the vendor
reworded it. Endpoint and client responses are not published sentences; write
those in backticks. **A promotion is quoted with the words that say when it
ends**, so a changed deadline phrase triggers a new review.

**A comment that says how someone else's program or service behaves says where
that was read, and when.** A LiteLLM default, Codex flag, sanctions rule or image
width is not checked by the quote reader. Such a comment names the page, release
or command and the date it was read. Behavior documented for LiteLLM or Codex is
checked in `conformance.py`; a floor in `pyproject.toml` is exercised by the
`floors` job in CI.

**Every mutable claim needs a source and a recheck mechanism.** Prefer a
canonical registry field and generated prose. Register handwritten assertions
about repository behavior in `claims.py`; changes in documented client behavior
need a check in `conformance.py`. Neither mechanism discovers arbitrary new
claims automatically. External facts that cannot be checked or expired by code
need a source, a checked date and a dated review with a clear trigger in private
evidence. Model promotions use `model_access.until`; other dated bonuses need
their own review, since a historical vendor quote can remain after a bonus ends.

`freetier-check` validates all curated files — `registry.yaml`, `blocklist.yaml`,
`dismissed.yaml`, `watchlist.yaml` and `sources.yaml` — together with the history
log and their cross-file constraints.

### Manual verification and CI

The `update` workflow also takes manual inputs: `provider_ids` selects
space-separated provider IDs for targeted verification. Only those rows earn
verification fields; unknown or permanently archived IDs stop the run. Resolve
the delisting or retirement first. Targeted runs skip tier changes, scouting and
announcements, and stop if a selected offer fails or cannot be checked. An empty
input retains the complete scheduled run. `dry_run` runs every selected phase and
writes nothing (the scout's report lands in the run summary instead of a PR),
and `scout_backend` forces one LLM backend instead of walking the chain — the
only way to exercise a fallback that never gets its turn.

Python 3.12 to 3.15, httpx + pydantic v2 + Jinja2. Keep the test suite green — CI
runs it on every push to `main` and every pull request, together with
`freetier-check` and `freetier-render --check`: on each of those Pythons with the
versions `uv.lock` pins, and on the oldest once more with the lowest versions
`pyproject.toml` allows, so every floor written there is one the code has run on.
`freetier-render --check` re-renders everything and compares it
with what is committed, so an edit that never reached a file the map marks
generated is a red run and not a page that quietly disagrees with the registry
until the next scheduled run heals it. It pins the comparison to the date the committed
`index.json` carries, so an untouched repository does not go red on the
calendar alone.
