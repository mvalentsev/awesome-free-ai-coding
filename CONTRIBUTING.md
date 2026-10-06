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

**An initial payment is a condition, not an automatic rejection.** A documented
free model quota or recurring free credit may require a one-time deposit or card
verification charge. Include it with the amount and any top-up fee visible;
usage within that quota must be free, with no recurring paid subscription required.
An expiring free-model promotion qualifies too, with its exact deadline and
timezone. A spend allowance still names no individually free model.

Record whole-offer payment conditions in `access`, and conditions on specific
callable IDs in `api.model_access` (or `client_lane.model_access`). Each uses the
same structure: `source` (an official HTTPS page), `initial_payment_usd`, optional
`payment_kind: card verification` (otherwise `top-up`), `topup_fee_percent`, and
`until` (a timestamp with timezone, for model promotions). Omit conditions that
do not apply. These fields generate the disclosures; do not duplicate them in
templates or add exceptions for a particular vendor. For example:

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
[`watchlist.yaml`](watchlist.yaml), not the blocklist.** Most services checked
here are legitimate and simply have nothing free today, or publish their offer
only on a page no probe can read. A BYOK-only tool is one of those: it can grow a
free lane of its own, and Cline did — it sat on the blocklist for two months as
"BYOK-only" while its sign-in provider was handing out free models, because a
blocklist verdict never expires and so is never checked again. That verdict is recorded with its date, its
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
does less work for this list's readers than the same offer open to all of them, so
it ranks below the offers of its size that are, and lower the more readers it
leaves out. Readers are counted as developers: a border's share is its
countries' part of the developers GitHub's
[Innovation Graph](https://innovationgraph.github.com/) counts in its latest
quarter, the EU's line left out of the total because it repeats the member
states. The countries under comprehensive US embargo — Cuba, Iran and North Korea —
set no row apart and move no rank: a sanctions clause covers them whether it names
them or not. Syria left that list on 2025-07-01
([OFAC](https://ofac.treasury.gov/sanctions-programs-and-country-information/paarss)),
so a border that names it counts. Russia is not one of them either: on 2026-09-26 fifteen of the eighty live rows left it out in their own
words, so a border that leaves out Russia counts. On 2026-09-25 CodeBuddy's
international site, sign-in and API endpoint answered 0.0.0.1 in the United
States, India and Russia and resolved in the seventeen other countries and
territories asked; with the two largest developer populations on GitHub left out
([Octoverse 2025](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)),
it went from 65, among the recurring agent plans, to 82, below the trials and
credits that reach them. An offer only one market's residents can sign up for —
ModelScope, SenseNova, TokenHub and SiliconFlow take mainland Chinese papers or
phone numbers — leaves out nine readers in ten and sits at the foot of its
section, below every offer that reaches the rest.

**Every live row records its border**, in `border`, the way its vendor states
it: `served`, the countries of an allow-list (Google's region list, a sign-up
that takes mainland Chinese ID cards), or `left_out`, every country a deny-list
names, the embargoed ones included, so a reader in Russia can tell a vendor that
names Russia from one that does not. A vendor that names no country, or covers
them with a sanctions clause that names none, is `left_out: []`. The codes are
ISO 3166-1's, the ones the Innovation Graph counts under, and each border carries
the day it was read, its source and, where the page has one, the vendor's
sentence. A disclaimer that a service is "intended for" one country, with nothing
that refuses the rest, is not a border (CodeGPT's terms); nor is the Gemini API's
rule that only its paid services may serve users in the EEA, Switzerland or the
UK, which is about the apps a developer builds, not the developer. The run reads
every border back — the names still on its page, the codes a vendor publishes as
data, a host still silent from inside a country — and reports a change beside a
row that stays verified; it never fails one. `freetier-borders` prints every
row's share, the figure a rank is argued from, and `--refresh` reads the
Innovation Graph's newest quarter into the committed snapshot. A reader asks the same
data from browse.html's "Where you are" picker: a row stays when its allow-list
names the country or its deny-list does not, out of the countries `index.json`
lists — every one a border can name.

The first four no-card agents are also the top of the README, with the models
they hand you, the strongest first, so this ordering is the page's answer to
"what do I use, then?"
Nothing about it is typed by hand: change `rank` and both the section and that
block follow. The "pick by what you need" table under it is the same ordering
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
tier below the median or where nothing was measured. `notable` exists because
the top moves: on 2026-09-26 Claude Opus 5.5 set it at 57.6, and Claude Opus 4.6
(26.4), Claude Sonnet 4.6 (24.7) and Gemini 3.5 Flash (32.6, a hair under the
strong bar) were models readers still look for, free on the list and with no
page. The family names what was read in `aa_model`,
the slug of the model's page on artificialanalysis.ai, for the variant the lane
serves: where the lane restricts it, that variant — Meta's contributor tier has no
max effort, so Muse Spark 1.3 Contributor is read as `muse-spark-1-3-xhigh` — and
where the lane does not say, the model's own page. A family that stands for no
single model, such as `gemma-4` where Google's pricing page prices Gemma 4 as
one row, or a bare `nemotron`, carries no tier. `freetier-check` refuses a tier without an
`aa_model`, and two rows naming different models for one family; `uv run
freetier-tiers` reads every score back off the leaderboard, prints the marks the
index no longer backs, and with `--write` re-marks every row that carries the
family — the scheduled run does that twice a week. A family that comes in bare is
measured the same way: where the board scores a model of exactly its name, `--write`
names that slug as its `aa_model` — the model's own page, as above — so a new
model's mark follows the index as models come out, not as reviewers remember; a
lane that serves another variant names that one by hand, and a hand-named
`aa_model` is never replaced. On 2026-09-17 the top was 53.4
(Claude Fable 5.1), frontier started at 43.4 and strong at 28.4. Until that day
every family without a mark was `strong`, Apertus 70B at 5 points beside GLM 5.3
Flash at 42, and nineteen of twenty-two frontier marks set by hand no longer met
the bar, because a tier written once never decays by itself. Give a family the
most specific name the lane serves, one family per model, since a broader name
also matches every id that contains it — `glm-5.3` a `glm-5.3-flash` id, `glm-5`
a `glm-5.2` one — and a model hidden under a broader family is missing from the
model index, from the tier marks and from freetier-bars, which counts an id as
named once any family names it. On 2026-09-25 AIHubMix's `glm-5` stood for
GLM-5.2, 5.1, 5 and 5-Turbo, so its strong GLM-5.2 was in no pick; eight rows
split their families that day. A family stays broader than one model only where
the evidence names nothing narrower. A mixture-of-experts model keeps its full
name, active parameters and all (`qwen3.5-122b-a10b`), and a page or an id that
leaves the count off still names it, where no other count follows: Regolo sells
Qwen3.5-122B-A10B as `qwen3.5-122b` and Alibaba names it in full, and until
2026-09-27 the two spellings could not be one family — one row went without the
model, or the model would have had two pages for good.

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
probe included, and is never probed again. It drops its connection details only
when its service is rejected for cause, and its page then names the service
without linking it. Its id stays taken, since the id is its page's URL: a vendor
that comes back is restored by removing `delisted`, and the scout reports a
proposal under an archived row's id instead of dropping it.

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
another fold, and reports two rows whose names read as one — MiMo Code and
MiMoCode, Xiaomi's agent and a placeholder from the list's first day at a domain
that publishes no site, sat in the Archive two lines apart from 2026-07-19 to
2026-09-20, because nothing ever compared two names.

Deleting a row is refused three times over: `freetier-check` fails on a registry
missing an id `history.jsonl` has recorded, the render stops before it can
record the deletion, and it will not build a page without the row.
Before 2026-09-17 twelve rows left by deletion — Cerebras, Novita and Kenari
among them — and the page said nothing about them but "Delisted —". They are
back as delisted rows, with the reason.

## Probes must anchor on the offer

Every `page-keywords` probe needs at least one keyword that disappears when the
free tier does. Three shapes qualify:

| Anchor | Example |
|---|---|
| a figure — quota, price, grant | `$0.10, subject to change` · `anonymous users get one request every 15 seconds` |
| an id — the free model's, as the page prints it | `mistral-medium` · `qwen/qwen3.8-27b` |
| a sentence of 4+ words quoted from the page | `free models through kilo gateway` |

**Keywords are matched against what the page renders**, with `<script>` and
`<style>` removed — JSON-LD excepted, because structured data is the vendor
answering a question and one row's whole offer is a JSON-LD FAQ block. A string
that lives only in a state blob, an OpenAPI enum, a response sample or an i18n
bundle keeps matching after the offer is gone: Groq's Free Plan Limits table
lost `llama-3.3-70b-versatile` some time before 2026-09-08 while the id went on
matching ten times over from the schema and samples beside it, and the list
published a withdrawn free model until someone read the table by hand. Where the
page's data genuinely is the evidence — a client-rendered docs site, a plan name
that exists only in the payload a framework ships — put those strings in
`probe.machinery_keywords`, which is searched against the whole response, and
say in `limits` where the evidence lives — trae's plan payload, the heading
Upstage's docs render in the browser. What a page renders is also what its whitespace
renders as: a line break in the source is a space, so a sentence a template
wraps across two lines is matched whole, as a reader copies it. Comments render
as nothing, so they are taken out whole, what they hold with them: React writes
an empty one on each side of a value it prints into a sentence, and
Experiential Labs' "with 500 credits a month once you verify a card" reached its
source on 2026-09-29 with the number between two.

**A page that moves with every release is read through the index that names
it.** ModelScope serves its docs under a dated release path —
`…/docdata/2026-9-10_15-4-CN/…` — and replaces it with each release while the
old paths go on answering, so a probe pinned to one would read an outdated page
for as long as the old release is kept. The site names the current prefix in a
JSON index. `probe.follow` starts the probe there: the endpoint is the index,
`follow.field` the dotted path to the value (`Data.TargetPrefix`) and
`follow.suffix` the path after it, and the keywords are read on the page that
builds. An index that names no page is `inconclusive`, and the page it names is
read like any endpoint, a 404 failing the row. `freetier-quotes` and the scout
read the same page, and the provider page says where the probe starts rather
than printing a dated URL that the next release makes stale.

A probe whose keywords are all words that outlive the offer is rejected by
validation, so CI fails on it:
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

**A vendor can list its free lane under a key of its own.** Cline's
recommended-models document carries no price and no free flag: it lists
`recommended`, `free`, `clinePass` and `clineCloud` side by side, and one model
can sit in the free lane and in the paid plan at the same time. Set
`probe.lane: free` on the `api-models` probe and the rows are that array and
nothing else in the document — every family in `models[]` has to be in it,
`api.model_ids` is checked against it, and an empty lane fails the way an empty
catalog does. The two ways a lane comes back empty are reported apart, `the
'free' lane lists no model ids` and `response has no 'free' lane`, because a
promotion that ended and a key the vendor renamed want opposite repairs.

**A lane served only inside the vendor's own client lists its ids in
`client_lane`.** Cline's free models are picked in Cline — "Free model usage is
not supported through the Cline API" — so the row has no `api` block, and until
2026-09-25 nothing recorded which ids its lane carried: eight came or went
between 2026-09-10 and 09-25 by the vendor's own snapshots of the lane, and no
run said so. `client_lane.model_ids` holds them, checked against the lane in
both directions as `api.model_ids` is against a catalog and dated for the Models
column the same way; `client_lane.no_family_ids` keeps a stealth codename out of
the column, with the review reason in the commit message. Nothing a reader pastes is
written from it, and validation refuses it beside an `api` block — one lane,
one list — or on a probe that cannot tell the lane from the rest of what it
reads: a page, or a catalog with neither `probe.lane` nor prices read.

**A catalog that prices nothing takes its free marks from the vendor's own
list.** NVIDIA's `/v1/models` answered 82 ids on 2026-09-23 with nothing beside
each one but its owner, older ids with no page among them, while build.nvidia.com
marks each model's page "Free Endpoint", available or deprecated. Set
`probe.free_list` to the keyless document that carries those marks, with
`require_zero_price: true`, and the probe joins it onto the catalog: an id the
list marks is free, one it dates for retirement is marked unavailable, and every
other id is not free — so the families, `api.model_ids` and the unlisted ids are
read as they are against a price. NVIDIA's list is NGC's catalog search filtered
to its free label (see the `nvidia-nim` row); a document of another shape is
reported, not guessed at. Until then the row's free ids were found by hand: Kimi
K3 was free from 2026-08-27 and reached the row on 2026-09-22, and on 2026-09-23
the list marked six chat models the row did not carry, DeepSeek V4.1 Flash
among them. A list that cannot be read leaves the offer unchecked, which is
`inconclusive`; one that answers and marks nothing free fails the row.

**Every family in `models[]` must be named on the page the probe reads.** The
Free models column is a claim, and it needs to be re-checkable by the same run
that re-checks the offer: an `api-models` probe demands each family back from the
catalog, free where the row reads prices, and a `page-keywords` probe now looks
for each family in the page it already fetched. A family the page does not name,
or one the catalog stopped serving free while it still serves another family the
row lists, is reported as `stale-models` — the entry stays live and verified,
because a marketing page dropping a model name is not a tier ending and neither
is one model leaving a lane, but the column is flagged until someone fixes it. A
catalog that serves none of the row's families fails the row. Where the
vendor keeps its offer on one page and its model list on another, probe the page
that carries both, or list fewer families: an id that belongs to the free lane but
has nothing to anchor it belongs in `api.model_ids`, which feeds the generated
configs without making a claim on the page.

**A page catalog keeps the complete picker separate from free families.**
`page_catalog` derives `models` and `newcomers`; the registry writer saves only
the catalog for these rows. Record regional credit budgets, model-hour examples
and each picker or specialist model once. Shared conditions and sourced notes
also live there, rather than in a second model list in `limits`. An unmetered
offer or a conditional free session can start a named family's bar; wallet,
paid-plan and specialist rows remain visible without entering the free-family
index. `first_free` records the start of the independently free offer, not the
day a model first appeared in a spending wallet. `listed` publishes an eligible
family; the existing tier workflow writes its canonical `model` record.
Wallet records keep family identity without an unchecked score tier.
The provider, main table, JSON, browse and LLM views use the same catalog.
The page probe compares the configured headed hours list and JSON-LD FAQ
answers for budgets, the complete picker, limited-mode membership and exact
conditions. An unreadable contract or changed value is a review finding;
an unavailable page remains inconclusive. Known offer deadlines belong in
`page_catalog.model_access[display name].until`: expiry removes the free-family
claim and marks the ended offer while retaining the wallet and source evidence.
The catalog source must be the row's directly probed page. This records the
advertised selection; it does not establish an authenticated completion.

**A sum to spend names no model.** The Models column lists models the vendor
serves free in their own right: a free lane, a free tier or trial that names its
models, a free quota per model. Where the free part is an amount the account
spends across the catalog — a signup credit, a grant of tokens every model draws
on, a monthly allowance at each model's own price, Cloudflare's 10,000 neurons a
day — no model is free by itself: the column stays empty, the prose says what
the amount buys, and `api.model_ids` carries a few of the vendor's exact ids to
paste. A connectable row whose vendor names no id a request carries — its
catalog answers only a key, and no page it publishes lists them — says so in
`api.no_ids`, and its page checks a reader's key against that catalog instead;
`freetier-check` refuses a connectable row with neither. A cap counted the same on every model is not such an amount but the limit
of a free tier: Cohere's trial keys are "limited to 1,000 API calls a month" and
Regolo's trial to a million tokens a day, whichever model answers. Mistral's $10
a month, Hugging Face's credits and Fireworks' starter credit were read that way
from the start; until 2026-09-25 six rows were not — Cloudflare named llama-4,
Upstage two Solar models and Dahl its three, and a second pass the same day
found Inception's three Mercury models on a grant "shared across all models",
Sail Research's five on $5 a month and Sarvam-105B on ₹100 of credit.

The first pass had read the rows by hand, so every live row now says which kind
of free it is in `free_part`, and `freetier-check` refuses one that does not:
`models` where the vendor names the models its free part serves in their own
right, `sum` where the free part is an amount spent across the models it lists,
and `unnamed` where it does not say which models the free part reaches — Copilot
Free's "auto model selection only", a credit whose models no page names. Only a
row of `models` may name a family, and a probe that reads each model's own free
mark, or a lane the vendor's client serves, reads `models` whatever else the row
offers: Vercel's $5 a month sits beside the models it prices at zero, and
those are its column. `freetier-bars` asks the same question of every id a
row of `models` lists, whatever its probe reads, so a free model kept out of the
column is kept out by a decision with its reason, never by a row the report did
not look at.

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

**An undated model on a rotating lane waits two weeks.** OpenRouter,
Kilo, Requesty, AIHubMix and Cline add and drop free ids within days, so a new id
is callable from the read that finds it and joins `models[]` two weeks later,
counted from that read or from the vendor's own date for the free id, such as the
`dateCreated` of an NVIDIA endpoint. Every chat model that has stayed that long
joins the column, since the list of models and everyone who serves each one free
is built from it. A router is not a model and a stealth codename names none, and a
model whose own developer advises against agentic coding stays out; so does a
model the page the probe reads never names, since a family has to be named where
the run reads it again — SEA-LION announces its free API on a page that names no
model — and a lane that serves one model at a time and rotates it, where a family
would fail the row at the next rotation; each is
listed in `api.no_family_ids`, with the review reason in the commit message
(`client_lane.no_family_ids` on a lane no API serves). Dated promotions follow the rule above;
an already expired promotion never joins. Until 2026-09-24 a family that
left the lane failed the row, so the column was kept to a few names per lane, and
OpenRouter was missing from the list for `north-mini-code`, which it had served
free since June. `uv run freetier-bars` dates every id in `api.model_ids` and
`client_lane.model_ids` from the registry's git history, or from the vendor's
own date where the row's free list carries one and it is earlier — NVIDIA
created `z-ai/glm-5.3`'s free endpoint on 2026-09-15 and the row listed it on
09-22, and until 2026-09-25 the report counted from the row alone, a week late.
It prints which ids are owed a family and when the rest fall due, and names any
free list it could not read; the scheduled run prints the same report in its
summary, and `freetier-check` refuses an id in `no_family_ids` that the row does
not list or a family already names. Where an older record than the registry
shows an id free — a Wayback snapshot of the vendor's free list, the vendor's
own snapshot of its lane, an earlier commit of this list that named it in prose
— the row says so in `api.free_since` (or `client_lane.free_since`): the id,
the day and the record, which the report counts from. Alibaba's pricing page
gave DeepSeek V4.1 Flash its quota by 2026-09-14 by Wayback while the row listed
the id on 09-25, and until that day such bars lived in a maintainer's notes. A
record goes when the family joins, and `freetier-check` says so.
A row with no lane or structured page catalog has no ids to date — opencode's
Zen page names its free models in prose — so a model such a page takes on free
is recorded in `newcomers`: the family it will join as, the first day a record
shows it free, and the record, a Wayback snapshot or the commit of this list that
first named it. The report counts its two weeks from there, validation refuses
the list on a row with a lane or on a sum, and `freetier-check` refuses a record
whose family the column already names. Until 2026-09-27 these bars, too, lived in
a maintainer's notes.

**The configs call ids, never family names.** `configs/litellm.yaml` and
`configs/opencode.json` are written from `api.model_ids` alone: a family names a
model, an id is the string a request carries, and the two coincide only by
luck. Until 2026-09-25 a row with no ids had its family names written in their
place — Cloudflare's config handed out `llama-4`, which Workers AI does not know,
and Upstage's `solar-pro-3` for the id `solar-pro3` — so `freetier-check` now
refuses a connectable row whose column names families with no ids beside them.

**Client token limits come from the catalog.** When a client's default exceeds
the vendor's cap, record `api.model_limits[ID]` with positive `context_tokens`,
`output_tokens` and `source`. The source must be this row's checked catalog;
every verification compares `context_length` and
`top_provider.max_completion_tokens`, reporting changed or unavailable values.
The writers supply OpenCode's context/output limits and LiteLLM's default
`max_tokens` for named and pooled deployments. An explicit client token request
can override that LiteLLM default; verify affected clients with live requests.

**A key the reader has not set never becomes another of theirs.** LiteLLM gives
an entry whose key variable is not set the `OPENAI_API_KEY` it runs with and
sends it to that lane, so every place that prints the proxy's command starts it
as `env -u OPENAI_API_KEY … litellm --config …`. The full local-development
command comes from `render.litellm_command`, including the explicit keyless
startup opt-in required by LiteLLM 1.104 and the loopback bind; conformance runs
that command on the oldest and newest releases. Vendor-published trial keys
from `api.public_key` are included in LiteLLM deployments directly, so a pool
that needs no account also works before sourcing the env example. Conformance
checks those literal credentials against their own lanes. Claude Code with an empty
`ANTHROPIC_AUTH_TOKEN` takes the next credential in its
[authentication order](https://code.claude.com/docs/en/authentication#authentication-precedence),
the reader's own sign-in included, and sends it to the gateway, so a keyed
function in `claude-code.sh` stops until its variable is set. Both were measured
on 2026-09-28 against a local stand-in for the lane: LiteLLM 1.89.0, 1.98.0 and
1.103.0, and Claude Code 2.1.283.

**Codex CLI reaches the lanes through LiteLLM.** Codex speaks only the OpenAI
Responses API — a provider given `wire_api = "chat"` has been a config error
since its discussion #7782 — and on 2026-09-27 seventeen of the list's 61 lanes
answered POST `/responses` with 404, while OVHcloud's refused the request Codex
sends. LiteLLM's `/v1/responses` sends an `openai/` deployment's call on to the
lane's own `/responses` unless the deployment carries `use_chat_completions_api`;
then it builds the call from the lane's chat completions, the format every lane
here is verified in. So every entry of `configs/litellm.yaml` carries the flag,
and the header asks for LiteLLM 1.98 or later: 1.88.3 and earlier write the flag
into the vendor's request body, where a strict vendor refuses a field it does
not know (OVHcloud's and LLM7's lanes answered 400 to it on 2026-09-28), and
1.98.0 is the first release to read the `allowed_fails_policy` each group
deployment carries, without which a lane that answers 500 or has no key set is
tried again instead of benched — one lane a request, since the proxy records one
failure a request (1.98 and 1.103 on 2026-09-28). [`configs/codex/litellm.config.toml`](configs/codex/litellm.config.toml) is
Codex's profile for the proxy — `--profile NAME` has read
`$CODEX_HOME/NAME.config.toml` since Codex CLI 0.134 — and its three settings are
the ones measured that day, with Codex 0.157.1 and LiteLLM 1.102.1, to break a
lane otherwise: reasoning summaries off, since LiteLLM 1.102.1 hands Codex's
summary setting to the lane as a `reasoning_effort` object, which LLM7, LLM Tech
and Pollinations refused; sub-agents off, since Codex sends their tools as a
`namespace`, which OVHcloud refused called directly, and which LiteLLM hands on
as plain functions that LLM7 refused (400 "does not support vision input" when
asked again on 2026-09-28); and web search off, a tool OpenAI's servers run,
which LiteLLM passes on as `web_search_options`. With
those, Codex ran a shell command through the proxy on LLM7 and read its output
back, and `free/strong` with no key set answered from the keyless lanes. A lane
whose chat template takes a single system message — LLM Tech's Qwen answered
"System message must be at the beginning" to the second one Codex sends — or a
model that takes no tools, such as LLM7's Mistral Nemo, answers 400, and a group
moves on to the next lane.

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

**`api.model_ids` is checked against the catalog in both directions.** On an
`api-models` probe every id there must still be in the catalog, callable and —
where `require_zero_price` is set — priced 0; a dead id is reported as
`stale-ids`, with any catalog id that reads like its successor. Callable is the
catalog's own word: a row it marks `available: false`, or one whose own
retirement date has come — Requesty's `retires`, OpenRouter's and Kilo's
`expiration_date` — is dead whatever its price says. Requesty kept
poolside/laguna-xs.2 and laguna-m.1 at 0 for a week after the day both rows
said they retired, 2026-09-21, and this list kept handing them out. The same run
reports every zero-priced id the catalog carries that `model_ids` does not, so a
lane that grows is visible without anyone re-reading the catalog. Both are notes
for a human and never repairs: an id is an exact string, and whether a new one
belongs in the configs is a judgement about what the row is for. Record the ones
you have read and left out — an image generator, a row whose own description says
it was removed, a lane the row does not track — in `api.ignored_ids`, with the
review reason in the commit message, and they stop being reported. Keep `api.note`
for advice a reader needs to connect. A `page-keywords` row whose
vendor keeps its ids in a keyless catalog at another url names it in
`probe.catalog`, and its ids are checked there for the dead direction; a
catalog that stops answering is reported as `stale-ids` too, since a check that
quietly did not run is the silence this whole mechanism exists to end. A failing
`api-models` row is asked the same question and carries the answer after a `|` in
its own failure line: the catalog that failed its families is the response
already in hand, and the run that loses a model is the run most likely to have
lost ids beside it — on 2026-09-07 LLMTR failed on `minimax-m3` while three of
its ids went unreported and stayed in the generated configs. A failing
`page-keywords` row is not: there the failure is the offer itself, and the row is
repaired or archived whole. A `stale-models` flag, on the other hand, ends nothing:
the ids, the keyless lane, the Anthropic route and Codex's are still asked, and what they
say follows the flag after a `|` — on 2026-09-21 Regolo's Llama 3.3 left its price
table and its catalog together, and the flag alone had hidden the dead id.

**The scout repairs a family verdict, never the half after the `|`.** That half
stays on the pull request's "needs a human" line even when the row's Models
column was answered, and a reply that drops a family the row's own probe still
names keeps the family and says so under the rejected candidates — a shorter
column always passes the probe, so the probe cannot catch that reply by itself.
On 2026-09-21 aihubmix failed on `gpt-oss` alone; the reply kept one family of
six, four of the five it dropped were still free in the catalog, and the eight
ids that had left it were on no line of the pull request.

**`api.anthropic_base_url` is the Claude Code answer.** Set it only where the
vendor documents an Anthropic-format Messages route — a 401 alone proves
nothing, since a gateway's auth wall answers 401 on any path. It is the value
`ANTHROPIC_BASE_URL` takes, so it stops before `/v1/messages` (Claude Code
appends that itself; validation refuses a value that already carries it). Every
run then POSTs to the route keyless, naming the row's first id in `api.model_ids`
— Fireworks answers a model it does not serve with 404 before it asks for a key
— and a 401, 400 or 429 is a route, a 404, 405 or 410
is reported as `stale-ids` beside the row while the row stays verified by its
page, and a route that cannot be reached is reported rather than skipped. The
field feeds the Claude Code line of the picks table, the second URL in the
connection table and [`configs/claude-code.sh`](configs/claude-code.sh), and
`index.json` carries it as written.

**`api.codex` is the Codex CLI answer, for a lane Codex calls directly.** Its
`base_url` is the value a Codex provider's `base_url` takes, Codex appending
`/responses` itself: the lane's own base on most rows, while a vendor may keep
Codex apart — Vercel's AI Gateway serves it at `/codex/v1`, whose model list is
in the shape Codex reads when it starts. Set it where a keyless call of the
request Codex sends completes, or where the vendor's own page sets Codex up on
the lane — never on a 401 alone, nor on a Responses API reference that does not
name Codex: OVHcloud's route exists and refused the request Codex sends. The
page has to cover the lane the row lists and the id the profile names. A plan's
own endpoint is another lane (Z.ai's Codex page is its GLM Coding Plan's), and a
vendor that narrows Codex to some models decides for them: on 2026-09-29
Requesty's Codex guide took only its `openai-responses/` models, none of them
free, and LLMTR's catalog served every free id at `/v1/chat/completions` alone,
which its Codex post says the Responses endpoint will not take. A keyed lane's
block carries the page as `source` and words from it that name Codex as `quote`,
which the run reads back with the row's other quotes; a lane without an account
is its own evidence. The request is the one Codex CLI 0.157.1 sent a provider
under this list's profiles, cut to one tool and one message; a lane with the
field gets a profile of its own, `configs/codex/<id>.config.toml`, with the
row's first id, the key from the variable `free-llm.env.example` exports and the
same three settings as the LiteLLM profile, and the provider page, both
connection tables, the picks and `llms.txt` name `codex -p <id>`. A keyed
profile also says what Codex does while its key is missing: unset or empty, it
stops before any request, the reader's own OpenAI key and `auth.json` beside it
or not — measured with Codex 0.134.0 and 0.158.0 on 2026-09-29, and one of the
sentences the conformance run holds to the program. On 2026-09-27 Kilo's gateway
was the one lane that took the request keyless, and Codex ran a shell command on
`kilo-auto/free` and read its output back. Every run asks again. A lane without
an account is asked the whole request once its first id has answered a chat
call, both ways, as with a bearer token: a row without the field that takes it
is reported so, and a row with the field that stops taking it — a refusal, a
stream that fails each time it is asked, a whole JSON answer to a request for a
stream — is reported as `stale-ids` while the row stays verified; a turn that
breaks off once is asked again, as Codex CLI asks it again. A keyed row with the field is asked
the route keyless, the Anthropic check's way: a 404, 405 or 410 is a route that
is gone. Where a catalog lists the paths it serves each model at — Routeway's
`endpoints`, LLMTR's `supported_endpoints` — the profile's id is held to them
too, since a free lane rotates and the next first id may be served at chat
completions alone. The field needs an OpenAI-shaped lane with an id and is
refused beside `session_header`, since Codex sends no header of a vendor's
naming; the one id a row with it
cannot take is `litellm`, the LiteLLM profile's name.

**`api.session_header` is for a lane that wants an id per conversation.** Set it
to the header name when the vendor requires every request to carry a stable id
for its conversation. opencode Zen was the case it was written for: from
2026-09-07 its free ids answered a request without `x-opencode-session` with
HTTP 400 MissingSessionID, and one carrying a stable UUID — what OpenCode's team
asked of other clients for OpenCode Go — with 200, keyless on 2026-09-16, until
Zen closed its free tier to every client but OpenCode on 2026-09-17. No row sets
the field today. A `litellm.yaml` entry is written once and cannot mint an id per
conversation, and OpenCode sends such a header only for its own built-in
provider, so a row that sets the field is left out of `litellm.yaml`,
`opencode.json` and `claude-code.sh`; the connection table, the provider and
model pages, the env example and `llms.txt` name the header, and the keyless
check below and the README's quickstart curl send a fresh id in it. What a lane
asks every request to carry is decided in one place, `ApiInfo.asks` — the
session header and the client's own `User-Agent` today — and every page and
config that words an ask keeps its words in a table keyed by the asks'
names, which the tests hold to the whole list: a new ask is one line there and
one line in each table, and none of them can be forgotten.

**`api.client_user_agent` is for a lane that asks every client to name itself.**
OpenCode's client rules for Go ask for two headers, not one: "Identify itself with its
own user agent, such as my-coding-agent/1.0, rather than a generic SDK or
HTTP-library name", beside the session id above. curl left to itself sends
`curl/8.x`, exactly the name those rules exclude, so on a row that sets the field
the README's quickstart curl sends `User-Agent: awesome-free-ai-coding-quickstart/1.0`,
and the connection table, the provider page and `llms.txt` tell the reader their
client must send one of its own. The keyless check always calls under this
project's own `freetier-radar/0.2`.

**`api.auth: none` is checked by calling the lane without a key.** On a row that
sets it, the missing key is the offer: the README's zero-signup curl and its "No
account at all" answer are both built from that field, with the first id in
`api.model_ids`. So every run sends that id one chat completion — one token, no
`Authorization` header, and a fresh id in the row's `api.session_header` when it
names one — to `<base_url>/chat/completions`. A 2xx carrying a completion — a
choice holding a message, no `error` in the body or the choice — is the only
answer that leaves nothing to say: OpenRouter's docs warn that its 200 goes out
before the first token, so a failure after it arrives as an error in a 200, and
Kilo's gateway answers in the same format. A completion that names another
model than the id — a gateway serving one model under another's name — is
reported as `stale-ids` naming both; a vendor's own spelling of the same model
is not that (`qwen38` for `nvidia/Qwen3.8-27B-NVFP4`, a dated revision for an
undated id), and a router id such as `kilo-auto/free` names no model to compare.
Anything else sends the check on to the next id, up to
three, because a rate limit does not end the offer but does end the command: on
2026-09-16 opencode's `big-pickle` answered 429 to every keyless call while
`ling-3.0-flash-fin-free` beside it answered 200, and the README's first command
was the one that never worked. The first id is asked again after a 429 with the
patience a 5xx gets, unless the vendor's `Retry-After` names a longer wait: a
rate limit of the moment moved between kilo-auto/free and LLM7's first id from
one network to the other within the hour on 2026-09-17, and is no reason to
reorder a row. A later id answering is reported as `stale-ids`
naming it, since the fix is to put it first; every id answering 429 is reported
as a rate-limited lane. With no id answering, a 401 or 403 on the first is the
vendor asking for a key and fails the row, which after three runs takes it and
its command off the page — unless an `api.notice` holds it, below; a bot wall
there is `inconclusive`, not a refusal. Any
other 4xx — vLLM's 404 for a model id that rotated out — and a lane that cannot be
reached are reported as `stale-ids` beside a row that stays verified. Put the id
that answers first: that is the one a reader runs.

**`data_use` is the vendor's word on training on what a reader sends.** A free
tier is often paid for in data, and the vendors that split tiers say so: the
Gemini API's free column reads "Content used to improve our products" where the
paid one says the opposite. `trains: yes` is a vendor that says what is sent on
the free offer may train or improve models, `opt-out` one where that is the
default with a setting to turn it off, `no` one that says it does not. `quote`
is the vendor's sentence, verbatim, about the free offer or plainly covering it
— a paid or enterprise tier's promise is not evidence for the free one — and
`url` the page that carries it. A vendor's promise about its own use covers only
the vendor: where the call goes on to other companies' models — a gateway, or an
agent that runs on them — `no` needs words that also reach those providers, such
as a no-training rule for every model it lists or zero retention at the
supplier. A free model the vendor itself says may be trained on makes the row
`yes` even when the others are not, since the reader is the one choosing among
them — `opt-out` where a setting keeps calls away from it, as OpenRouter's does.
`url` must be a page the run can read; one behind a bot wall would be reported
on every run, and a Chinese or Japanese quote is read like any other. A row whose vendor says nothing either way carries none.
The README marks `yes` and `opt-out` with 👁 beside the name, the row's page
quotes the sentence, browse.html keeps the `no` rows behind "Not trained on",
and every run reads `url` back for the quote.

**`api.refuses_bearer` is a keyless lane that answers only a bare call.** Once
the first id has answered, the run asks it again carrying `Authorization: Bearer
none` — what LiteLLM sends for `api_key: none`, and LiteLLM sends a bearer token
on every call. On 2026-09-21 OVHcloud's anonymous lane and VLM Run's answered
that with 403 and Kilo's with 401, so a row whose lane does sets the field and
`litellm.yaml` leaves it out, saying why in its header; so does
`claude-code.sh`, which hands Claude Code a token of "none" that goes out as a
bearer; opencode's config adds no header without a key and keeps it. The run reports it as `stale-ids` both ways: a
refusal on a row without the field, and an answer on a row with it. A rate limit
on the second call says nothing either way.

**`api.public_key` is a key the vendor prints for anyone.** LLM Tech's
quickstart publishes "a shared free trial key", with its limits beside it, so
that anyone can "try before you talk to anyone": a reader calls the lane
without opening an account, as on a keyless row, only with a key in the header.
The field holds that key, on a row that is otherwise `auth: api-key`, and
`key_url` names the vendor's page that prints it. The env example carries it
filled in; the connection table, the provider page and `llms.txt` print it with
that page; and the row counts towards "no signup" and answers "No account at
all" beside the keyless rows. The README's first command stays a keyless one,
since it is the curl with nothing to paste into it. Every run calls the lane
with the key the way it calls a keyless lane without one, and a lane that
refuses it fails the row the same way: that is the no-account offer ending, or a
key the vendor has replaced, which only a person reading the page can copy. The
run also reads `key_url` back for the key, because it is the vendor's key only
while the vendor's page prints it, and a key that still works after its page
stopped printing it is reported as `stale-ids`. A key anyone else hands out —
leaked, pooled, passed around — is key sharing, and does not qualify at all.
AI Horde's anonymous key `0000000000` is the same kind of key, on a route that
takes no tools, which is why AI Horde is on the watchlist and not here.

**`api.notice` is the list owning up to a lane that does not work as
published.** When a lane breaks in a way its vendor has not explained, and the
maintainer chooses to wait for the vendor's word rather than take the lane off,
the row says so to its readers. opencode Zen began answering every free-model
call that does not come from OpenCode's own app with `403 FreeTierError` on
2026-09-17, with no docs change and no answer on its issues, while its lane led
the README. A notice has `since` (the day it started), `text` (what a reader
runs into, in this list's own words, vendor output in backticks, 500 characters
at most) and `url` (where the problem is followed). It is printed as a warning
right under the quickstart curl when the row is the quickstart, first in the
row's cell of the connection table, above the offer on the provider page and in
`llms.txt`, and `index.json` carries it as written. On a keyless row it also
holds a refusal off the failure count for 30 days from `since`: the run reports
the refusal as `stale-ids` beside a row its own page keeps verified, naming the
notice and the day it stops holding, and past that day the refusal fails the row
as it would have without one — a vendor that has said nothing for a month about
breaking every other client has answered. The day the lane answers again, the
run asks for the notice to come down. A notice is temporary by construction:
when the vendor speaks, delete it and change the row to match what it said.
opencode's came down on 2026-09-18, the day an OpenCode maintainer wrote that the
free tier cannot be used in other harnesses: the row lost its api block and
stayed on the list as the agent it is.

## How the pipeline works

`registry.yaml` is the single source of truth. `README.md` is **generated** — never
edit it by hand. Twice a week GitHub Actions probes every entry (live model APIs and
pricing pages), commits verification results, and a web-evidence scout (Tavily, Hacker
News, GitHub search, curated feeds, and a digest of every models.dev provider that
publishes a zero-cost model → LLM extraction → live probe gate) proposes new entries
via pull request. Humans review the PR; robots do everything else.

The README is the landing page, and the site is the reference. A visitor scrolls
the README on GitHub, under the file list, so it carries the hero — a picture of the
list the render draws, a dot per live row — the rows added this week, the picks, the
strong models, the quickstart and one list item per live row — the name, `offering`, the first eight
model families and the date, with where to get a key beside it for a lane that takes
one — and folds nothing in the list; the quota
in the vendor's words is on the row's own page and on `index.html`, one click
from the date, and so is every family past the eighth, one click from their count. On 2026-09-20 it had
grown to 161 KB, 83 KB of it inside folded cells, thirty-one desktop screens and
fifty-one on a phone. The list was four tables until 2026-09-25, and they measured
thirty-one phone screens: GitHub gives a table the screen's width and no more, so
the offer got a column a word or two wide and the models and the dates sat off the
right edge. The same rows as list items measured eighteen. The strong models are
the families the tier bar reaches, frontier first, then the most widely served first and at most 20;
the README draws them as a chart, each as long as its score on the Artificial
Analysis index from the snapshot `freetier-tiers` keeps, and folds who serves each
under it in the chart's order; every family and everyone who serves it free is the site's model index, which grows
with the families rather than the rows — 70 in 7 KB on 2026-09-20, 149 in 18.7 KB on
09-25 — and left the README that day. `README_BUDGET` in `render.py` is the ceiling, and a test
renders the committed registry against it, so the reference job cannot creep back
a column at a time.

`providers/` is generated with it: one page per row on the GitHub Pages site,
in the row's own words, with the evidence the probe reads and the row's history,
plus an index — the verified date of a live README row links to it, and
so does the name of an archived one. The
pages exist for the reader who arrives from a search about one vendor, so their
titles name the vendor, the tier and the date; `_config.yml` names the site so
Jekyll writes canonical URLs and a sitemap, and gives every page the list's
preview card. Jekyll serves them, and the model pages below, in
[`_layouts/default.html`](_layouts/default.html): one heading a page, the title
as the render wrote it, a line back to the list and its indexes, a breadcrumb
for search results. An address the site does not have gets
[`404.html`](404.html), which offers the rows that name what the address asked
for. **Never edit them by hand** — the
render rewrites every one, an archived row's included, and the body sits inside
`{% raw %}` so a vendor's own sentence can never break the build.

`models/` is generated with them: a page for every model two rows or more serve
free, or that measures notable, strong or frontier, and an index of every model the live
rows serve. A reader — or a model answering one — arrives with a model in mind
as often as with a vendor: where is Kimi K3 free. A model page's title is that
question, and its body is every live row that serves the model, in the list's
order: what the row asks for, the day a probe last confirmed it, the day the
list started carrying the model there, the limits in the vendor's words and the
ids of that model to call, then the rows that listed it before and the days
they did. A model one row serves and nothing measures in the index's upper half
gets no page unless it has a dated free promotion; those promotions get a page
immediately so readers can find them before they end. Other unmeasured models
stay on the index beside the row. **A page, once
published, stays**: a model that falls below the bar keeps its page, and a model
no row serves any more keeps one that says so in its title, since when, and
which rows listed it — the list never takes back an address a search engine
indexed or an answer cited, as it never deletes a row. The render reads the
pages already in `models/` beside the registry to know which it published, and
`freetier-gate` refuses a commit, a push or a run that deletes a page under
`providers/` or `models/`. Every page under both carries `last_modified_at`, the
newest of its rows' verified dates and history lines, which Jekyll writes into
the sitemap as `<lastmod>` and into the page's structured data as
`dateModified`. **Never edit them by hand** either.

[`index.html`](index.html) is the site's own front page, rendered from the
registry by the same command from [`templates/index.html.j2`](templates/index.html.j2)
— **never edit it by hand.** It exists because GitHub Pages renders Markdown
with kramdown, which does not read Markdown inside a block-level `<div>`, does
not know GitHub's alert syntax and escapes a `<summary>` inside a table cell: the
README is written for GitHub's own renderer, so served through Jekyll its hero's
badges arrived as literal `[![badge](…)]` text and every fold in a table cell as
a bare "Details" with its summary escaped. The README keeps its GitHub features, the site gets HTML, and
`freetier-render --check` holds both to the same registry. `_config.yml` leaves
`README.md` out of the site for the same reason.

[`configs/README.md`](configs/README.md) is generated with them, from
[`templates/configs-README.md.j2`](templates/configs-README.md.j2) and the README's
own context: the connection table — base URL, key env var, the note that matters,
the Anthropic-format route where the vendor documents one — for every live
OpenAI-compatible API, beside the five configs it describes. GitHub renders a
folder's README under its file list, which is where a reader who came for
`opencode.json` finds the base URLs. It is written for GitHub's renderer like the
root README, so `_config.yml` leaves it off the site too; the site's own copy of the
table is on `index.html`. **Never edit it by hand.**

`llms.txt` is generated with them — the whole list as one text file, in the
shape the [llms.txt proposal](https://llmstxt.org/) gives agents — and `browse.html` is a hand-written static
page that reads `index.json` in the browser, so it changes only when a field
does; `tests/test_browse.py` holds the two to the same field names. After the
scheduled run pushes, `freetier-indexnow` submits to IndexNow (Bing, Yandex and
the engines that share their index) the pages whose data changed — a row's page
and the pages of its models, a model's page, and the pages that list every row
— read off `index.json` before and after the push, and so does
`.github/workflows/indexnow.yml` after any other push to `main` that changes a
file the site publishes — its path filter is the map's published lines, held
to them by a test, and the run's own push starts no workflow, so a commit is
never announced twice; a hand push counts from the last ping that went out,
since a push that lands while one waits cancels it, and leaves out what the
run's verification commits in between changed, which the run pinged itself. Until 2026-09-27 every
ping sent every URL, 186 of them for commits that each touched a handful of rows. Both
wait until Pages has built the commit they ping for (`freetier-indexnow
--after-pages-build`), so an engine that fetches on the ping reads the new page; the key it proves
ownership with is the file named after it at the repository root: public
here, though the protocol would keep it private, and all it lets anyone do is
ask an engine to crawl this site's pages.

Google takes a sitemap from Search Console or from the `Sitemap:` line of a
`robots.txt`, and a crawler reads `robots.txt` only at the root of a host,
where a project site cannot serve one — the copy Jekyll writes beside this
site's sitemap is never read. The host's own lives in the account's user site,
[`mvalentsev/mvalentsev.github.io`](https://github.com/mvalentsev/mvalentsev.github.io),
beside a placeholder front page kept out of search results; its `Sitemap:` line
names this site's sitemap, so that repository stays, and a custom domain set
on it would move this site with it.

Every change to what the list publishes — a row arriving, dropping to the
Archive, coming back, or changing its free models — is appended to
[`history.jsonl`](history.jsonl) by `freetier-render`, in the commit that makes
the change, and published as an
[Atom feed](https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml).
**Never edit it by hand.** The render compares the registry with the log the
commit starts from and records the difference before it writes a page, so a
row you add by hand gets its line in your commit, dated that day, and its page
already shows it; a render run again before the commit rewrites only its own
uncommitted lines. A change the calendar makes — a row going unverified past
the staleness limit, a vendor's shutdown date arriving — is recorded by the
first render after it, the scheduled run's at the latest. Until 2026-09-24 only
the scheduled run recorded, up to four days after a change reached the list;
that day the log was rebuilt from main's history, every line dated by the
commit that made its change (the commit `gate.RATIFIED` names), and a row's
`first_seen` is the day the log added it — `freetier-check` holds the two to
one day.

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
| `index.html` | **generated** — the Pages site's front page | `templates/index.html.j2`, `assets/model-name.js`, `registry.yaml`, `watchlist.yaml`, `history.jsonl` | `freetier-render` |
| `configs/README.md` | **generated** — the connection table, beside the configs · not on the site | `templates/configs-README.md.j2`, `registry.yaml`, `watchlist.yaml`, `history.jsonl` | `freetier-render` |
| `configs/opencode.json` | **generated** — the opencode config | `registry.yaml` | `freetier-render` |
| `configs/litellm.yaml` | **generated** — the LiteLLM proxy config and its groups | `registry.yaml` | `freetier-render` |
| `configs/free-llm.env.example` | **generated** — one export per key | `registry.yaml` | `freetier-render` |
| `configs/claude-code.sh` | **generated** — one Claude Code shell function per Anthropic-format lane | `registry.yaml` | `freetier-render` |
| `configs/codex/*.config.toml` | **generated** — Codex CLI profiles: one over the LiteLLM config, one per lane Codex calls directly | `registry.yaml` | `freetier-render` |
| `index.json` | **generated** — every row and the watchlist, for machines | `registry.yaml`, `watchlist.yaml` | `freetier-render` |
| `feed.xml` | **generated** — the Atom feed of the history | `history.jsonl`, `registry.yaml` | `freetier-render` |
| `llms.txt` | **generated** — the whole list as one text file | `registry.yaml` | `freetier-render` |
| `assets/readme/*.svg` | **generated** — the README's pictures: the radar at the top, a dot per live row, and the strong models drawn against the top of the index, in each width and theme the README serves — and the radar alone, the site's mark beside its name | `registry.yaml`, `src/freetier_radar/intelligence-index.json` | `freetier-render` |
| `providers/*.md` | **generated** — a page per row, the provider index and the page of services checked · never deleted once published | `registry.yaml`, `history.jsonl`, `watchlist.yaml`, `blocklist.yaml` | `freetier-render` |
| `models/*.md` | **generated** — a page per widely served or strong free model, and the index of every free model · never deleted once published | `registry.yaml`, `history.jsonl` | `freetier-render` |
| `browse.html` | **page** — the filterable table, reading index.json in the browser | `index.json`, `assets/model-name.js` | `hand` |
| `404.html` | **page** — what Pages serves for an address the site does not have, offering the rows that name what the address asked for | — | `hand` |
| `assets/*.svg` | **page** — the favicon and the social preview's source | — | `hand` |
| `assets/*.png` | **page** — the social preview | — | `hand` |
| `assets/*.js` | **page** — shared browser model-name matching | — | `hand` |
| `eb68c254f1e03877b906ccc800002691.txt` | **page** — the IndexNow key, named after itself (indexnow.INDEXNOW_KEY) | — | `hand` |
| `AGENTS.md` | **doc** — standing review and evidence rules for repository work · not on the site | — | `hand` |
| `CONTRIBUTING.md` | **doc** — how the list works and how to change it; its map section is this table | `src/freetier_radar/layout.py` | `hand`, `freetier-render` |
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
| `.github/workflows/*.yml` | **config** — CI, the scheduled run, read-page, the IndexNow ping on a push and the conformance run of LiteLLM and Codex CLI on the configs · not on the site | — | `hand` |
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

```bash
uv sync
git config core.hooksPath .githooks   # once per clone: every check runs before each commit
uv run pytest
uv run freetier-map               # the map: what every file is, what it is made from, what writes it
uv run freetier-probe --dry-run   # live-probe all entries, record nothing
uv run freetier-render            # regenerate every file the map above marks generated, and the map
uv run freetier-check             # validate the curated files against each other
uv run freetier-quotes [ids…]     # read every quoted phrase back against the row's own sources (--report: the run's summary)
uv run freetier-bars              # which ids a free lane has carried two weeks with no family
uv run freetier-announce --dry-run  # print what the announcer would post, send nothing
```

`freetier-review --out <private-directory>` collects evidence for a review.
Use a git-ignored directory or one outside the repository. Run its phases in
order: `prepare --base <commit> --head <commit>`, `sources`, `publication`,
`browser`, then `report`. `publication` waits for the required workflows at that
exact commit, saves their full logs and open PRs, and compares published bytes.
Pages byte checks use the repository map: only files marked `published` are
served there. Changed README files are also checked at the exact GitHub commit,
including documentation excluded from Pages.
For a bot verification commit, add `prepare --verification-run <update-run-id>`:
the full successful update log must prove which commit it produced, since that
push runs its checks and IndexNow inside the update instead of starting CI.
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
The report covers collected evidence; source reads and quote matches still need
vendor judgment, affected API lanes still need controls, and the full diff still
needs independent review. The hooks below remain mandatory.

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
request. A published log rewritten or an earned field typed on purpose is the repository
owner's alone: made once with the hooks off and named, with the reason, in
`gate.RATIFIED` by the commit after it — a push or a CI run that meets it checks
from it on.

**A row's prose is for the reader deciding whether to use the offer.** `offering` says
what it is, `limits` the quota, the conditions and what happens to the data, and
`api.note` what a client needs to connect — in the vendor's words where they
decide something. What changed and when belongs to `history.jsonl` and the commit
log, not to the row: by 2026-09-16 the median `limits` had grown from 87
characters to 813, most of it dated lane counts, and the README to 260 KB.
`freetier-check` holds `offering` to 300 characters, `limits` to 1,200 and
`api.note` to 600. It also rejects maintenance-diary phrases in live public prose,
including Models-column waiting rules and registry field names. Full payment,
fee and deadline details are shown with callable IDs; list labels use a shorter
form from the same access metadata. Multi-model providers' shared limits fold
under Provider-wide limits on model pages. The README prints none of `limits`: since 2026-09-21 a row on it
is `offering`, the models and the date, and the quota is on the row's own page and
the site, one click from the date.

**A row of free models leaves them to its Models line.** Every page prints
`offering` beside that line, which the probe reads back and the two-week bar
holds, so a model named in the prose either repeats the line or names one it holds
back. On 2026-09-26 twenty-eight rows of `models` did one or both — opencode spelled
out all six of its models, Freebuff two still short of their two weeks — and
`freetier-check` now refuses, in such a row's `offering`, a family any live row
carries or one of the row's own ids. A maker's name is not a model's: "Claude and
open-weight models" says what Kiro serves without listing it. A sum has no Models
line, so its prose names what the amount buys.

**A phrase in quotation marks is a claim that the vendor published those words.**
`freetier-quotes` reads quotes in `offering`, `limits`, `api.note` and
`client_lane.note`, as well as the explicit data-use and API Codex quotes. It
fetches a row's `source_urls`, its probe endpoint and its
catalog, and reports every quote of three words or more that none of them
carries; the fix is the vendor's exact words or a source URL that has them. A
quote the pages that answered do not carry, while another of the row's sources
did not answer, is reported as unverified rather than missing — a refused
read is not a vendor rewording — and read again later. On
2026-09-16 it found MegaNova quoting a sign-up line its pages never had and
LLMTR promising a privacy guarantee its policy does not make. What an endpoint
or a client answered — an error body, a refusal, a status line — is not a
published sentence: write it in backticks, which the check does not read.

The scheduled run prints the same pass in its summary (`freetier-quotes
--report`), beside the models owed a family. Until 2026-09-27 nothing read a
quote back unless someone ran the command, and a full pass that day found five
gone: BazaarLink's allowance had turned into weighted units, Token Harbor's "No
per-minute request cap" into 60 requests a minute. A quote gone from its page is
a row to read again, never a failed run. **A promotion is quoted with the words
that say when it ends** — Qoder's daily credits with "End time: To be
announced", CodeBuddy's bonus with "The end date of this promotion will be
announced separately" — so the run notices the day those words change, which is
the day a rank resting on the promotion moves back.

**A comment that says how someone else's program or service behaves says where
that was read, and when.** A LiteLLM default, a Codex flag, a sanctions rule,
the width GitHub shows a picture at: nothing reads a comment back the way
`freetier-quotes` reads a row's quotes, and on 2026-09-28 a pass that read every
such sentence here against its source — 845 of them — found 118 false or out of
date and 38 with no source at all, four package floors and a key sent to a lane
that was not its own among them. So such a comment names the page, the release
or the command it rests on and the date it was read; what a config says LiteLLM
or Codex does is a check in `conformance.py` instead; and a floor in
`pyproject.toml` is one the `floors` job in CI installs and runs.

**Every mutable claim needs a source and a recheck mechanism.** Prefer a
canonical registry field and generated prose. Register handwritten assertions
about repository behavior in `claims.py`; changes in documented client behavior
need a check in `conformance.py`. Neither mechanism discovers arbitrary new
claims automatically. External facts that cannot be checked or expired by code
need a source, a checked date and a dated review with a clear trigger in private
evidence. Model promotions use `model_access.until`; other dated bonuses need
their own review, since a historical vendor quote can remain after a bonus ends.

`freetier-check` is the one to run after editing any of `registry.yaml`,
`blocklist.yaml`, `dismissed.yaml`, `watchlist.yaml` or `sources.yaml`. Two of
those — `dismissed.yaml` and `sources.yaml` — are read only by the scout, which
runs behind a catch-all, so before this existed a malformed one could reach
`main` and turn into a green workflow that had quietly done nothing. It checks
`history.jsonl` too, for the different reason that the log is the only file here
that cannot be regenerated from another one.

The `update` workflow also takes manual inputs: `dry_run` runs every phase and
writes nothing (the scout's report lands in the run summary instead of a PR),
and `scout_backend` forces one LLM backend instead of walking the chain — the
only way to exercise a fallback that never gets its turn.

Python 3.12 to 3.14, httpx + pydantic v2 + Jinja2. Keep the test suite green — CI
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
