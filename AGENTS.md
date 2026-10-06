# Repository working rules

Read CONTRIBUTING.md before changing registry data, probes, generated files or
publication workflows. Public repository text is English.

## Preserve the shared public interface

Before changing presentation, inspect the previous committed output and at
least two comparable rows. Record the existing sections, labels, empty states
and navigation in private evidence. New registry data uses those shared
components; a new data shape does not justify its own public sections or links.
If the interface must change, apply and validate the shared change across
representative rows rather than adding an exception for one data source.

Check rendered output against the established contract independently of the
feature's own content tests and generated browser plan. Demonstrate that a
regression check rejects the previous bad output before correcting it. Review
unaffected peer rows as well as the changed row in the final diff and browser.
Passing content assertions, byte checks and CI do not establish design quality.

Review model classification separately from presentation. Compare the previous
and resulting families, and record vendor evidence for every removal or new
empty state. Check every advertised free access mode: a priced wallet can sit
beside a free tier with the same usage cap on each model.

## Review every automated update without reminders

When an update arrives, review both the verification commit and the scout PR.
Record their exact commits and preserve the complete workflow log. A green run
does not establish that every vendor fact is current.

- Inspect every probe finding, missing or unreadable quote, provisional
  promotion attempt, model arrival/removal, score change and dated deadline.
- Re-read the relevant primary vendor sources with this project's HTTP client.
  Check price, free eligibility, authentication, payment requirements,
  retirement dates, model identity and the two-week bar. State contradictory
  evidence and distinguish unavailable checks from established changes.
- Read changed rows whole, including API ids, client lanes, prose, quotes and
  generated configs. Re-check current vendor state before removing a model;
  the state can change after the scheduled run.
- Exercise real requests for affected public lanes with fresh payloads and
  appropriate controls. Respect retry and rate-limit headers. Do not claim
  authenticated completion tests without credentials or substitute mocks for
  live evidence.
- Rebuild history and every generated surface through their writers. Run
  freetier-check, freetier-render --check, the earned-field/history gate and
  the full test suite. For probe fixes, first demonstrate a failing regression
  at the HTTP boundary. Verify affected client behavior with conformance when
  applicable.
- Review the complete final diff independently. After publication, verify CI,
  Pages, the affected served pages/configs and relevant desktop/mobile flows.
  Inspect open dependency PRs. Report what passed, what changed and every
  material unresolved limitation, with reproducible evidence.

Do not substitute a list of unchecked items for completing the checks. Obtain
missing access when a check needs it and continue independent work meanwhile.
If the owner explicitly defers creating provider keys, complete all checks
that do not require them and remind the owner once, at the very end.

Earned fields are written only by the verification workflow. Never bypass
hooks, delete a registry row or published page, or hand-edit generated files
and history. Keep raw responses, credentials and internal review notes outside
tracked public files.

Every new or changed mutable claim needs a canonical field or a registered
check, its source, and a recheck mechanism. Register handwritten repository
assertions in claims.py and client behavior in conformance.py. External-behavior
comments name the source or measured release and the date checked. For claims
that cannot be generated, checked or expired automatically, record a dated
review and its trigger in private evidence. Model promotion deadlines belong
in model_access.until; a historical quote alone cannot detect an ended offer.

Use `freetier-review` for reusable private evidence; its commands and limits are
in CONTRIBUTING.md. Prepare from exact commits and keep full artifacts in a
git-ignored directory. Use the generated browser coverage plan. The runner does
not replace hooks, live API controls, vendor judgments or independent review.
Read compact phase results first; open raw evidence for failures and disputed
facts. Do not reuse a served-page check across publications.

## Attribution

Do not add assistant or vendor attribution, co-author trailers, generated-by
signatures, or session links to commits, PRs, tags, changelogs or other public
artifacts.
