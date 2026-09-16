from datetime import date

import httpx
import respx

from freetier_radar.models import Entry
from freetier_radar.quotes import check_entries, flatten, quote_found, quotes_in, row_quotes


def quoted_entry(limits: str, note: str | None = None) -> Entry:
    data = {
        "id": "vendor",
        "name": "Vendor",
        "category": "api-free-tier",
        "url": "https://vendor.example",
        "source_urls": ["https://vendor.example/pricing"],
        "offering": "stuff",
        "limits": limits,
        "first_seen": date.today(),
        "last_verified": date.today(),
        "probe": {"type": "page-keywords", "endpoint": "https://vendor.example/docs",
                  "keywords": ["one million free tokens"]},
    }
    if note is not None:
        data["api"] = {"base_url": "https://api.vendor.example/v1", "note": note}
    return Entry.model_validate(data)


def test_only_quotes_of_three_words_or_more_are_claims_worth_checking():
    text = 'The plan is "Free" at "$0", and "no credit card required" says the card.'
    assert quotes_in(text) == ["no credit card required"]


def test_quotes_come_from_the_offering_the_limits_and_the_api_note():
    entry = quoted_entry('Tier 1 is "Free registration and no card".', note='the docs say "use the v1 route"')
    assert row_quotes(entry) == [("limits", "Free registration and no card"),
                                 ("api.note", "use the v1 route")]


def test_typography_does_not_hide_a_quote_that_is_there():
    """The vendor's page has markdown emphasis, an em dash, a curly apostrophe
    and a non-breaking space; the row has plain ASCII. Same words."""
    page = flatten("**Free registration** — no credit card required. It&#39;s the account’s first step")
    assert quote_found("Free registration - no credit card required", [page])
    assert quote_found("It's the account's first step", [page])


def test_a_quote_joined_across_an_ellipsis_is_checked_fragment_by_fragment():
    page = flatten("Pick a chat model marked free in the catalog. This step checks the gateway works on a zero balance.")
    assert quote_found("Pick a chat model marked free … checks the gateway works on a zero balance", [page])
    assert not quote_found("Pick a chat model marked free … and your prompts are never stored", [page])


@respx.mock
async def test_a_quote_on_none_of_the_rows_sources_is_reported_with_its_field():
    """MegaNova's row quoted "Free, no credit card required" while its page said
    "Free registration — no credit card required" (2026-09-16)."""
    respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(
        200, text="<p><strong>Free registration</strong> — no credit card required</p>"))
    respx.get("https://vendor.example/docs").mock(return_value=httpx.Response(
        200, text='<script type="application/ld+json">{"text": "one million free tokens a day"}</script>'))
    entry = quoted_entry('"Free registration — no credit card required", "one million free tokens a day" '
                         'and "Free, no credit card required"')
    async with httpx.AsyncClient() as client:
        missing, unread = await check_entries([entry], client)
    assert [(m.entry_id, m.field, m.quote) for m in missing] == [
        ("vendor", "limits", "Free, no credit card required")]
    assert unread == {}


@respx.mock
async def test_an_archived_row_is_history_and_is_not_read():
    call = respx.get(url__regex=r".*").mock(return_value=httpx.Response(200, text=""))
    entry = quoted_entry('"a quote from a page that ended"')
    entry.retired_on = date(2026, 1, 2)
    async with httpx.AsyncClient() as client:
        missing, unread = await check_entries([entry], client)
    assert missing == [] and unread == {}
    assert not call.called


@respx.mock
async def test_a_source_that_does_not_answer_is_said_so_beside_the_quotes_it_could_not_vouch_for():
    respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(404))
    respx.get("https://vendor.example/docs").mock(side_effect=httpx.ConnectError("boom"))
    entry = quoted_entry('"one million free tokens a day"')
    async with httpx.AsyncClient() as client:
        missing, unread = await check_entries([entry], client)
    assert [m.quote for m in missing] == ["one million free tokens a day"]
    assert sorted(unread["vendor"]) == ["https://vendor.example/docs: ConnectError",
                                        "https://vendor.example/pricing: HTTP 404"]
