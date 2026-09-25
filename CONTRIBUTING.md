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

**A tier is a measurement, not a reputation.** A family's `tier` is read from
the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/leaderboards/models):
`frontier` when the model its free lane serves scores within 10 points of the top
of the index, counting current models only, `strong` within 25, and no tier below
that or where nothing was measured. The family names what was read in `aa_model`,
the slug of the model's page on artificialanalysis.ai, for the variant the lane
serves: where the lane restricts it, that variant — Meta's contributor tier has no
max effort, so Muse Spark 1.3 Contributor is read as `muse-spark-1-3-xhigh` — and
where the lane does not say, the model's own page. A family that stands for no
single model, such as `gemma-4` where Google's pricing page prices Gemma 4 as
one row, or a bare `nemotron`, carries no tier. `freetier-check` refuses a tier without an
`aa_model`, and two rows naming different models for one family; `uv run
freetier-tiers` reads every score back off the leaderboard, prints the marks the
index no longer backs, and with `--write` re-marks every row that carries the
family — the scheduled run does that twice a week. On 2026-09-17 the top was 53.4
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
the evidence names nothing narrower.

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
wraps across two lines is matched whole, as a reader copies it.

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
2026-09-25 nothing recorded which ids its lane carried: nine came or went
between 2026-09-10 and 09-25 by the vendor's own snapshots of the lane, and no
run said so. `client_lane.model_ids` holds them, checked against the lane in
both directions as `api.model_ids` is against a catalog and dated for the Models
column the same way; `client_lane.no_family_ids` keeps a stealth codename out of
the column, with the reason in `client_lane.note`. Nothing a reader pastes is
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

**A sum to spend names no model.** The Models column lists models the vendor
serves free in their own right: a free lane, a free tier or trial that names its
models, a free quota per model. Where the free part is an amount spent across a
metered catalog at each model's own price — a signup credit, a monthly
allowance, Cloudflare's 10,000 neurons a day — no model is free by itself: the
column stays empty, the prose says what the amount buys, and `api.model_ids`
carries a few of the vendor's exact ids to paste. Mistral's $10 a month, Hugging
Face's credits and Fireworks' starter credit were read that way from the start;
until 2026-09-25 Cloudflare named llama-4, Upstage two Solar models and Dahl
its three, the only rows that did not.

**A lane that rotates names a model once it has stayed two weeks.** OpenRouter,
Kilo, Requesty, AIHubMix and Cline add and drop free ids within days, so a new id
is callable from the read that finds it and joins `models[]` two weeks later,
counted from that read or from the vendor's own date for the free id, such as the
`dateCreated` of an NVIDIA endpoint. Every chat model that has stayed that long
joins the column, since the list of models and everyone who serves each one free
is built from it. A router is not a model and a stealth codename names none, and a
model whose own developer advises against agentic coding stays out; each is
listed in `api.no_family_ids`, with the reason in `api.note` (`client_lane`'s own
two fields on a lane no API serves). A free id the vendor dates to end within those two weeks
never joins: OpenRouter and Kilo publish the date as `expiration_date`, and on
2026-09-24 it was the next day for both Nex-N2.5 ids. Until that day a family that
left the lane failed the row, so the column was kept to a few names per lane, and
OpenRouter was missing from the list for `north-mini-code`, which it had served
free since July. `uv run freetier-bars` dates every id in `api.model_ids` and
`client_lane.model_ids` from the registry's git history, or from the vendor's
own date where the row's free list carries one and it is earlier — NVIDIA
created `z-ai/glm-5.3`'s free endpoint on 2026-09-15 and the row listed it on
09-22, and until 2026-09-25 the report counted from the row alone, a week late.
It prints which ids are owed a family and when the rest fall due, and names any
free list it could not read; the scheduled run prints the same report in its
summary, and `freetier-check` refuses an id in `no_family_ids` that the row does
not list or a family already names.

**The configs call ids, never family names.** `configs/litellm.yaml` and
`configs/opencode.json` are written from `api.model_ids` alone: a family names a
model, an id is the string a request carries, and the two coincide only by
luck. Until 2026-09-25 a row with no ids had its family names written in their
place — Cloudflare's config handed out `llama-4`, which Workers AI does not know,
and Upstage's `solar-pro-3` for the id `solar-pro3` — so `freetier-check` now
refuses a connectable row whose column names families with no ids beside them.

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
quietly did not run is the silence this whole mechanism exists to end. A failing
`api-models` row is asked the same question and carries the answer after a `|` in
its own failure line: the catalog that failed its families is the response
already in hand, and the run that loses a model is the run most likely to have
lost ids beside it — on 2026-09-07 LLMTR failed on `minimax-m3` while three of
its ids went unreported and stayed in the generated configs. A failing
`page-keywords` row is not: there the failure is the offer itself, and the row is
repaired or archived whole. A `stale-models` flag, on the other hand, ends nothing:
the ids, the keyless lane and the Anthropic route are still asked, and what they
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

**`api.session_header` is for a lane that wants an id per conversation.** Set it
to the header name when the vendor requires every request to carry a stable id
for its conversation. opencode Zen was the case it was written for: from
2026-09-07 its free ids answered a request without `x-opencode-session` with
HTTP 400 MissingSessionID, and one carrying a stable UUID — what OpenCode's team
asked of other clients for OpenCode Go — with 200, keyless on 2026-09-16, until
Zen closed its free tier to every client but OpenCode on 2026-09-17. No row sets
the field today. A `litellm.yaml` entry is written once and cannot mint an id per
conversation, and OpenCode sends such a header only for its own built-in
provider, so a row that sets the field is left out of `litellm.yaml` and
`opencode.json`; the connection table, the provider page, the env example and
`llms.txt` name the header, and the keyless check below and the README's
quickstart curl send a fresh id in it.

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
`litellm.yaml` leaves it out, saying why in its header; opencode's config adds
no header without a key and keeps it. The run reports it as `stale-ids` both ways: a
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
the README on GitHub, under the file list, so it carries the hero, the picks, the
quickstart and one line per live row — the name, `offering`, the first eight
model families and the date — and folds nothing in the list's tables; the quota
in the vendor's words is on the row's own page and on `index.html`, one click
from the date, and so is every family past the eighth, one click from their count. On 2026-09-20 it had
grown to 161 KB, 83 KB of it inside folded cells, thirty-one desktop screens and
fifty-one on a phone. `README_BUDGET` in `render.py` is the ceiling, and a test
renders the committed registry against it, so the reference job cannot creep back
a column at a time.

`providers/` is generated with it: one page per row on the GitHub Pages site,
in the row's own words, with the evidence the probe reads and the row's history,
plus an index — the "Last verified" date of a live README row links to it, and
so does the name of an archived one. The
pages exist for the reader who arrives from a search about one vendor, so their
titles name the vendor, the tier and the date; `_config.yml` names the site so
Jekyll writes canonical URLs and a sitemap. **Never edit them by hand** — the
render rewrites every one, an archived row's included, and the body sits inside
`{% raw %}` so a vendor's own sentence can never break the build.

[`index.html`](index.html) is the site's own front page, rendered from the
registry by the same command from [`templates/index.html.j2`](templates/index.html.j2)
— **never edit it by hand.** It exists because GitHub Pages renders Markdown
with kramdown, which does not read Markdown inside a block-level `<div>`, does
not know GitHub's alert syntax and escapes a `<summary>` inside a table cell: the
README is written for GitHub's own renderer, so served through Jekyll its whole
hero arrived as literal `[![badge](…)]` text and every folded cell as a wall of
prose. The README keeps its GitHub features, the site gets HTML, and
`freetier-render --check` holds both to the same registry. `_config.yml` leaves
`README.md` out of the site for the same reason.

[`configs/README.md`](configs/README.md) is generated with them, from
[`templates/configs-README.md.j2`](templates/configs-README.md.j2) and the README's
own context: the connection table — base URL, key env var, the note that matters,
the Anthropic-format route where the vendor documents one — for every live
OpenAI-compatible API, beside the four config files it describes. GitHub renders a
folder's README under its file list, which is where a reader who came for
`opencode.json` finds the base URLs. It is written for GitHub's renderer like the
root README, so `_config.yml` leaves it off the site too; the site's own copy of the
table is on `index.html`. **Never edit it by hand.**

`llms.txt` is generated with them — the whole list as one text file, in the
shape LLM search and agents read — and `browse.html` is a hand-written static
page that reads `index.json` in the browser, so it changes only when a field
does; `tests/test_browse.py` holds the two to the same field names. After the
scheduled run pushes, `freetier-indexnow` submits the site's URLs to IndexNow
(Bing, Yandex and the engines that share their index); the key it proves
ownership with is the file named after it at the repository root, and it is
not a secret.

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
| `registry.yaml` | **data** — every row the list has published, live or archived — the single source of truth | — | `hand`, `freetier-probe`, `freetier-tiers`, `freetier-scout` |
| `watchlist.yaml` | **data** — services checked and not listed: the date, the reason, what would reopen them | — | `hand` |
| `blocklist.yaml` | **data** — domains rejected for cause | — | `hand` |
| `sources.yaml` | **data** — lists read once and put down | — | `hand` |
| `dismissed.yaml` | **data** — model-generation bumps a reviewer declined | — | `hand` |
| `history.jsonl` | **log** — every change to what the list publishes, one event a line, append-only | `registry.yaml` | `freetier-render` |
| `announced.jsonl` | **log** — the posts the announcer has sent, append-only | `history.jsonl` | `freetier-announce` |
| `README.md` | **generated** — the landing page GitHub shows under the file list · not on the site | `templates/README.md.j2`, `registry.yaml`, `watchlist.yaml`, `history.jsonl` | `freetier-render` |
| `index.html` | **generated** — the Pages site's front page | `templates/index.html.j2`, `registry.yaml`, `watchlist.yaml`, `history.jsonl` | `freetier-render` |
| `configs/README.md` | **generated** — the connection table, beside the configs · not on the site | `templates/configs-README.md.j2`, `registry.yaml`, `watchlist.yaml`, `history.jsonl` | `freetier-render` |
| `configs/opencode.json` | **generated** — the opencode config | `registry.yaml` | `freetier-render` |
| `configs/litellm.yaml` | **generated** — the LiteLLM proxy config and its groups | `registry.yaml` | `freetier-render` |
| `configs/free-llm.env.example` | **generated** — one export per key | `registry.yaml` | `freetier-render` |
| `configs/claude-code.sh` | **generated** — one Claude Code shell function per Anthropic-format lane | `registry.yaml` | `freetier-render` |
| `index.json` | **generated** — every row and the watchlist, for machines | `registry.yaml`, `watchlist.yaml` | `freetier-render` |
| `feed.xml` | **generated** — the Atom feed of the history | `history.jsonl`, `registry.yaml` | `freetier-render` |
| `llms.txt` | **generated** — the whole list as one text file | `registry.yaml` | `freetier-render` |
| `providers/*.md` | **generated** — a page per row, the provider index and the page of services checked | `registry.yaml`, `history.jsonl`, `watchlist.yaml`, `blocklist.yaml` | `freetier-render` |
| `browse.html` | **page** — the filterable table, reading index.json in the browser | `index.json` | `hand` |
| `assets/*.svg` | **page** — the banners and the social preview's source | — | `hand` |
| `assets/*.png` | **page** — the social preview | — | `hand` |
| `eb68c254f1e03877b906ccc800002691.txt` | **page** — the IndexNow key, named after itself (indexnow.INDEXNOW_KEY) | — | `hand` |
| `CONTRIBUTING.md` | **doc** — how the list works and how to change it; its map section is this table | `src/freetier_radar/layout.py` | `hand`, `freetier-render` |
| `LICENSE` | **doc** — MIT | — | `hand` |
| `assets/README.md` | **doc** — what each asset is for · not on the site | — | `hand` |
| `src/freetier_radar/*.py` | **code** — the probe, the scout, the render and the checks · not on the site | — | `hand` |
| `templates/*.j2` | **code** — the page templates freetier-render fills · not on the site | — | `hand` |
| `tests/*.py` | **code** — the test suite · not on the site | — | `hand` |
| `pyproject.toml` | **config** — the package and its commands · not on the site | — | `hand` |
| `uv.lock` | **config** — the pinned dependencies · not on the site | — | `hand` |
| `_config.yml` | **config** — the Pages site: its name, its plugins, what it leaves out · not on the site | — | `hand` |
| `.gitignore` | **config** — what git leaves alone · not on the site | — | `hand` |
| `.githooks/*` | **config** — the git hooks that run freetier-gate — `git config core.hooksPath .githooks` · not on the site | — | `hand` |
| `.github/workflows/*.yml` | **config** — CI, the scheduled run and read-page · not on the site | — | `hand` |
| `.github/dependabot.yml` | **config** — the pinned actions' watcher · not on the site | — | `hand` |
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

Mark the accounts as automated (Mastodon's "This is a bot account", Bluesky's
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
uv run freetier-quotes [ids…]     # read every quoted phrase back against the row's own sources
uv run freetier-bars              # which ids a free lane has carried two weeks with no family
uv run freetier-announce --dry-run  # print what the announcer would post, send nothing
```

**The checks run before a commit exists.** With the hooks on, `git commit`
runs `freetier-gate pre-commit`: `freetier-check`, `freetier-render --check` and
the test suite on a snapshot of what is staged, with the dates in UTC. It also
refuses what only a command may write: a line in `history.jsonl` that is not
one the render records for the commit's own registry, or a change the registry
makes that the commit does not record; a commit on `main` that changes
`announced.jsonl`, which only the scheduled run writes; a log rewritten on any
branch; and a hand edit of `last_verified`,
`probe_failures`, `provisional` or `first_seen`, which only the run's probe
writes — a new row enters provisional, with `first_seen` and `last_verified`
both the day it is added. `commit-msg` wants a subject that starts with its
kind (`fix: …`) and a blank line before the body; `pre-push` runs the same
checks on what is pushed, commit by commit. CI checks the logs again on every
push and the earned fields on every pull request. CI never runs on the scheduled run's own commit,
so the run checks its logs, the curated files and the render before it commits,
and checks the scout's branch, earned fields included, before it opens the pull
request. A log rewritten or an earned field typed on purpose is the repository
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
`api.note` to 600. The README prints none of `limits`: since 2026-09-21 a row on it
is `offering`, the models and the date, and the quota is on the row's own page and
the site, one click from the date.

**A phrase in quotation marks is a claim that the vendor published those words.**
`freetier-quotes` fetches a row's `source_urls`, its probe endpoint and its
catalog, and reports every quote of three words or more that none of them
carries; the fix is the vendor's exact words or a source URL that has them. A
quote the pages that answered do not carry, while another of the row's sources
did not answer, is reported as unverified rather than missing — Qodo's terms
page refuses some reads with 403 and serves the next — and read again later. On
2026-09-16 it found MegaNova quoting a sign-up line its pages never had and
LLMTR promising a privacy guarantee its policy does not make. What an endpoint
or a client answered — an error body, a refusal, a status line — is not a
published sentence: write it in backticks, which the check does not read.

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

Python 3.12+, httpx + pydantic v2 + Jinja2. Keep the test suite green — CI runs
it on every push to `main` and every pull request, together with `freetier-check` and
`freetier-render --check`. The second one re-renders everything and compares it
with what is committed, so an edit that never reached a file the map marks
generated is a red run and not a page that quietly disagrees with the registry
until the next scheduled run heals it. It pins the comparison to the date the committed
`index.json` carries, so an untouched repository does not go red on the
calendar alone.
