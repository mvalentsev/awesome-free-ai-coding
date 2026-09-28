from datetime import date

import httpx
import respx

from freetier_radar.models import DataUse, Entry
from freetier_radar.quotes import check_entries, flatten, page_texts, quote_found, quotes_in, row_quotes


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


def test_the_data_use_quote_is_checked_on_the_page_it_names():
    """A row's word on training is the vendor's sentence on its data page, which
    is usually none of the row's sources — so its url is read too."""
    from freetier_radar.quotes import row_urls
    entry = quoted_entry("no quotes here")
    entry.data_use = DataUse(trains="no", quote="We never train on what you send",
                             url="https://vendor.example/privacy")
    assert row_quotes(entry) == [("data_use.quote", "We never train on what you send")]
    assert "https://vendor.example/privacy" in row_urls(entry)


def test_typography_does_not_hide_a_quote_that_is_there():
    """The vendor's page has markdown emphasis, an em dash, a curly apostrophe
    and a non-breaking space; the row has plain ASCII. Same words."""
    page = flatten("**Free registration** — no credit card required. It&#39;s the account’s first step")
    assert quote_found("Free registration - no credit card required", [page])
    assert quote_found("It's the account's first step", [page])



def test_a_quote_inside_page_data_is_read_with_its_json_escapes_decoded():
    """Page data is read with its JSON escapes decoded: a JSON-LD FAQ (Freebuff's)
    can carry "Smart & Fast" only as `Smart \\u0026 Fast`."""
    body = ('<script type="application/ld+json">{"text": "- DeepSeek V4.1 Flash: Smart \\u0026 Fast. '
            'May use data for AI training.\\n- GPT-6 Luna"}</script>')
    assert quote_found("DeepSeek V4.1 Flash: Smart & Fast. May use data for AI training.", page_texts(body))

def test_a_chinese_quote_is_read_like_any_other():
    """Chinese puts no space between words, so two characters count as a word for
    the three-word rule, and the spaces markup leaves beside them (a link inside
    the sentence, a markdown source) count for nothing."""
    assert quotes_in('标着 "免费" 的模型，"实名认证后使用全部的免费模型"') == ["实名认证后使用全部的免费模型"]
    page = page_texts('<p><a href="/auth">实名认证</a> 后使用全部的免费模型。</p>')
    assert quote_found("实名认证后使用全部的免费模型", page)
    assert not quote_found("实名认证后使用部分免费模型", page)
    markdown = page_texts("- 免费推理API由阿里云提供算力支持， 要求您的ModelScope账号必须首先"
                          "[绑定阿里云账号](../../account.md) 。")
    assert quote_found("免费推理API由阿里云提供算力支持，要求您的ModelScope账号必须首先绑定阿里云账号", markdown)
    data_use = "不会将您的业务数据用于任何大模型的预训练、微调或其他商业用途"
    assert not quote_found(data_use, page_texts("<p>我们可能将您的数据用于模型训练。</p>"))


def test_a_quote_joined_across_an_ellipsis_is_checked_fragment_by_fragment():
    page = flatten("Pick a chat model marked free in the catalog. This step checks the gateway works on a zero balance.")
    assert quote_found("Pick a chat model marked free … checks the gateway works on a zero balance", [page])
    assert not quote_found("Pick a chat model marked free … and your prompts are never stored", [page])


@respx.mock
async def test_a_quote_on_none_of_the_rows_sources_is_reported_with_its_field():
    """A quote none of the row's sources carries is reported with the field it sits
    in, though a near variant of it is on the page."""
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
        missing, unread = await check_entries([entry], client, today=date(2026, 1, 2))
    assert missing == [] and unread == {}
    assert not call.called


@respx.mock
async def test_a_row_whose_shutdown_is_still_to_come_is_read():
    """A vendor's announced shutdown archives the row on that day, not before:
    until then the row is live, and its quotes are read like any other's."""
    respx.get(url__regex=r".*").mock(return_value=httpx.Response(200, text="another sentence"))
    entry = quoted_entry('"a quote the vendor has since reworded"')
    entry.retired_on = date(2026, 1, 2)
    async with httpx.AsyncClient() as client:
        missing, unread = await check_entries([entry], client, today=date(2026, 1, 1))
    assert [m.quote for m in missing] == ["a quote the vendor has since reworded"]


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


@respx.mock
async def test_a_quote_missing_while_a_source_did_not_answer_is_unverified_not_missing(tmp_path, capsys):
    """A quote the answering pages do not carry is unverified, not missing, while
    another of the row's sources did not answer: a page that refuses one read
    must not read as the vendor changing its words."""
    from freetier_radar.models import save_registry
    from freetier_radar.quotes import _amain
    respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(403))
    respx.get("https://vendor.example/docs").mock(
        return_value=httpx.Response(200, text="one million free tokens a day"))
    entry = quoted_entry('"one million free tokens a day" and "a sentence only the pricing page has"')
    async with httpx.AsyncClient() as client:
        missing, unread = await check_entries([entry], client)
    assert [(m.quote, m.unverified) for m in missing] == [
        ("a sentence only the pricing page has", True)]

    registry = tmp_path / "registry.yaml"
    save_registry(registry, [entry])
    assert await _amain(registry, []) == 0
    out = capsys.readouterr().out
    assert ('  vendor limits: unverified — not on the sources that answered, and '
            'https://vendor.example/pricing: HTTP 403 — "a sentence only the pricing page has"') in out
    assert out.rstrip().endswith("checked 2 quotes in 1 row — 0 not found on the rows' own sources, "
                                 "1 unverified because a source did not answer")


@respx.mock
async def test_a_probe_that_follows_an_index_has_its_quotes_read_on_the_page_the_index_names():
    """A row whose probe follows an index has its quotes read on the page the index
    names (ModelScope's docs), not on the JSON index or an older release's page."""
    data = quoted_entry('"sign in for two hundred credits a day"').model_dump()
    data["source_urls"] = []
    data["probe"] = {"type": "page-keywords", "endpoint": "https://vendor.example/api/doc-index",
                     "keywords": ["200 credits a day"],
                     "follow": {"field": "Data.TargetPrefix", "suffix": "/limits.md"}}
    entry = Entry.model_validate(data)
    respx.get("https://vendor.example/api/doc-index").mock(return_value=httpx.Response(
        200, json={"Data": {"TargetPrefix": "https://docs.vendor.example/2026-9-10"}}))
    respx.get("https://docs.vendor.example/2026-9-10/limits.md").mock(return_value=httpx.Response(
        200, text="Sign in for two hundred credits a day."))
    async with httpx.AsyncClient() as client:
        missing, unread = await check_entries([entry], client)
    assert missing == [] and unread == {}


@respx.mock
async def test_the_run_reports_a_quote_gone_from_its_page_in_its_summary_and_never_fails(tmp_path, capsys):
    """The scheduled run prints the quotes gone from their pages in its summary and
    exits 0: a vanished quote is a row to read again, not a failed run."""
    from freetier_radar.models import save_registry
    from freetier_radar.quotes import _amain
    respx.get("https://vendor.example/pricing").mock(
        return_value=httpx.Response(200, text="<p>End time: October 31, 2026</p>"))
    respx.get("https://vendor.example/docs").mock(
        return_value=httpx.Response(200, text="one million free tokens a day"))
    entry = quoted_entry('"one million free tokens a day" while the promotion runs, with '
                         '"End time: To be announced"')
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [entry])
    assert await _amain(registry, [], report=True) == 0
    out = capsys.readouterr().out
    assert out.startswith("## Quotes no longer on their pages\n")
    assert '- vendor limits: "End time: To be announced"' in out
    assert out.rstrip().endswith("checked 2 quotes in 1 row — 1 not found on the rows' own sources")


@respx.mock
async def test_a_clean_pass_says_every_quote_was_found(tmp_path, capsys):
    from freetier_radar.models import save_registry
    from freetier_radar.quotes import _amain
    respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(200, text=""))
    respx.get("https://vendor.example/docs").mock(
        return_value=httpx.Response(200, text="one million free tokens a day"))
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [quoted_entry('"one million free tokens a day"')])
    assert await _amain(registry, [], report=True) == 0
    out = capsys.readouterr().out
    assert "Every quoted phrase is on its row's own pages." in out
    assert "not on its sources" not in out


@respx.mock
async def test_the_count_is_of_the_rows_whose_quotes_were_read(tmp_path, capsys):
    """The summary counts only the rows whose quotes were read, not the archived
    rows it leaves alone."""
    from freetier_radar.models import save_registry
    from freetier_radar.quotes import _amain
    respx.get("https://vendor.example/pricing").mock(return_value=httpx.Response(200, text=""))
    respx.get("https://vendor.example/docs").mock(
        return_value=httpx.Response(200, text="one million free tokens a day"))
    live = quoted_entry('"one million free tokens a day"')
    gone = quoted_entry('"a quote from a page that ended"').model_copy(
        update={"id": "gone", "retired_on": date(2026, 1, 2)})
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [live, gone])
    assert await _amain(registry, []) == 0
    assert capsys.readouterr().out.rstrip().endswith(
        "checked 1 quote in 1 row — 0 not found on the rows' own sources")
