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
single model, such as `gpt-oss` on a lane serving both sizes or a bare
`nemotron`, carries no tier. `freetier-check` refuses a tier without an
`aa_model`, and two rows naming different models for one family; `uv run
freetier-tiers` reads every score back off the leaderboard, prints the marks the
index no longer backs, and with `--write` re-marks every row that carries the
family — the scheduled run does that twice a week. On 2026-09-17 the top was 53.4
(Claude Fable 5.1), frontier started at 43.4 and strong at 28.4. Until that day
every family without a mark was `strong`, Apertus 70B at 5 points beside GLM 5.3
Flash at 42, and nineteen of twenty-two frontier marks set by hand no longer met
the bar, because a tier written once never decays by itself. Give a family the
most specific name the lane serves, since `glm-5.3` is also matched by a
`glm-5.3-flash` id.

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

Deleting a row is refused three times over: `freetier-check` fails on a registry
missing an id `history.jsonl` has recorded, the probe run stops before it can
record the deletion, and the render will not build the page without the row.
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
`probe.machinery_keywords`, which is searched against the whole response. Two
rows use it (`trae`, `upstage`), each saying in `limits` where its evidence
lives.

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
quietly did not run is the silence this whole mechanism exists to end. A failing
`api-models` row is asked the same question and carries the answer after a `|` in
its own failure line: the catalog that failed the family is the response already
in hand, and the run that fails a row over one model is the run most likely to
have lost ids beside it — on 2026-09-07 LLMTR failed on `minimax-m3` while three
of its ids went unreported and stayed in the generated configs. A failing
`page-keywords` row is not: there the failure is the offer itself, and the row is
repaired or archived whole.

**`api.anthropic_base_url` is the Claude Code answer.** Set it only where the
vendor documents an Anthropic-format Messages route — a 401 alone proves
nothing, since a gateway's auth wall answers 401 on any path. It is the value
`ANTHROPIC_BASE_URL` takes, so it stops before `/v1/messages` (Claude Code
appends that itself; validation refuses a value that already carries it). Every
run then POSTs to the route keyless, naming the row's first id in `api.model_ids`
— Fireworks answers a model it does not serve with 404 before it asks for a key
— and a 401, 400 or 429 is a route, a 404 or 405
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
names one — to `<base_url>/chat/completions`. A 2xx is the only answer that
leaves nothing to say. Anything else sends the check on to the next id, up to
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
[`history.jsonl`](history.jsonl) by those same two commands and published as an
[Atom feed](https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml).
**Never edit it by hand.** It is append-only, and it is compared against the
registry rather than against the previous run, so a row you add by hand is
reported by the next scheduled run rather than going unrecorded.

## How the list announces itself

`freetier-announce` runs in the same workflow, after the verification commit:
every event the run appended to `history.jsonl` — a row arriving, dropping to
the Archive, coming back, changing its free models — becomes one post from
the project's own accounts, labelled as a bot, linking the row's page. It posts
only events from the last 14 days, at most five per channel per run, oldest
first, and only what a channel has not posted before: `announced.jsonl` is the
append-only ledger, keyed by event and channel, so a retried run cannot post a
line twice and a channel that failed is simply retried next time. `--dry-run`
prints every due post and sends nothing.

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
uv run pytest
uv run freetier-probe --dry-run   # live-probe all entries, record nothing
uv run freetier-render            # regenerate README.md + index.json + feed.xml + llms.txt + configs/ + providers/
uv run freetier-check             # validate the curated files against each other
uv run freetier-quotes [ids…]     # read every quoted phrase back against the row's own sources
uv run freetier-announce --dry-run  # print what the announcer would post, send nothing
```

**A row's prose is for the reader deciding whether to use the offer.** `offering` says
what it is, `limits` the quota, the conditions and what happens to the data, and
`api.note` what a client needs to connect — in the vendor's words where they
decide something. What changed and when belongs to `history.jsonl` and the commit
log, not to the row: by 2026-09-16 the median `limits` had grown from 87
characters to 813, most of it dated lane counts, and the README to 260 KB.
`freetier-check` holds `offering` to 300 characters, `limits` to 1,200 and
`api.note` to 600.

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
it on every push and pull request, together with `freetier-check` and
`freetier-render --check`. The second one re-renders everything and compares it
with what is committed, so an edit to `registry.yaml` that never reached
`README.md`, `index.json`, the configs or the provider pages is a red run and
not a page that quietly disagrees with the registry for three days until the
next scheduled run heals it. It pins the comparison to the date the committed
`index.json` carries, so an untouched repository does not go red on the
calendar alone.
