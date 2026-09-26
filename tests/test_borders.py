"""The border a row records — where its free offer reaches, in the vendor's own
words — and everything read off it: the names on a vendor's page, the share of
developers it leaves out, the line the pages print and the run's re-read."""
from datetime import date

import httpx
import pytest
import respx
from pydantic import ValidationError

from freetier_radar.borders import (SHARED, Yardstick, left_out_of, load_yardstick, share,
                                    snapshot_from_csv)
from freetier_radar.countries import COUNTRIES, NOT_COUNTRIES, codes_named, country_name
from freetier_radar.models import Border, DataUse, Entry
from freetier_radar.prober import ProbeStatus, probe_entry

TODAY = date(2026, 9, 26)

BASE = {
    "id": "x",
    "name": "X",
    "category": "api-free-tier",
    "url": "https://x.ai",
    "offering": "stuff",
    "first_seen": date(2026, 1, 1),
    "last_verified": TODAY,
    "probe": {"type": "page-keywords", "endpoint": "https://x.ai", "keywords": ["x-mini-2", "free"]},
}


def border(**kw) -> Border:
    return Border.model_validate({"on": TODAY, "source": "https://x.ai/terms", **kw})


# ---- the names on a page ----------------------------------------------------

@pytest.mark.parametrize("text,codes", [
    ("Albania, Algeria and Congo (DRC)", {"AL", "DZ", "CD"}),
    # The longest name at a place wins: none of these is also the shorter one.
    ("Guinea-Bissau, Papua New Guinea, Equatorial Guinea", {"GW", "PG", "GQ"}),
    ("South Sudan", {"SS"}),
    ("Niger and Nigeria", {"NE", "NG"}),
    ("Dominican Republic", {"DO"}),
    ("Taiwan, Province of China", {"TW"}),
    ("United Kingdom of Great Britain and Northern Ireland", {"GB"}),
    ("China (including Hong Kong and Macau)", {"CN", "HK", "MO"}),
    ("Ukraine (with certain exceptions)", {"UA"}),
    # A typographic apostrophe is the one Google's list prints.
    ("Côte d’Ivoire", {"CI"}),
    # A Chinese page runs its names together with no space between them.
    ("中国大陆、中国香港、中国澳门、中国台湾居民", {"CN", "HK", "MO", "TW"}),
])
def test_a_page_is_read_for_the_countries_it_names(text, codes):
    assert codes_named(text) == codes


def test_a_place_that_carries_a_countrys_name_names_no_country():
    assert codes_named("offices in New Jersey and New Mexico, and Northern Ireland") == set()


def test_a_country_name_is_read_with_its_capital():
    """"chad", "turkey" and "china" are words before they are countries."""
    assert codes_named("fine china and turkey for chad") == set()


def test_no_spelling_names_two_countries():
    owners: dict[str, str] = {}
    for code, names in COUNTRIES.items():
        for name in names:
            assert owners.setdefault(name, code) == code, name
    assert not set(owners) & set(NOT_COUNTRIES)


def test_every_economy_the_yardstick_counts_has_a_name():
    assert set(load_yardstick().developers) <= set(COUNTRIES)


def test_mainland_china_is_named_as_mainland_china():
    """CN is the mainland alone in ISO's codes and GitHub's counts — Hong Kong,
    Macao and Taiwan are codes of their own — so a page saying "China" beside a
    row that serves Hong Kong would say more than the row does."""
    assert country_name("CN") == "mainland China"


# ---- the record ---------------------------------------------------------------

def test_a_border_is_either_the_list_it_serves_or_the_list_it_leaves_out():
    with pytest.raises(ValidationError, match="exactly one"):
        border()
    with pytest.raises(ValidationError, match="exactly one"):
        border(served=["CN"], left_out=["RU"])
    assert border(left_out=[]).left_out == []


def test_a_border_names_countries_by_their_codes():
    with pytest.raises(ValidationError, match="ZZ"):
        border(left_out=["ZZ"])
    with pytest.raises(ValidationError, match="twice"):
        border(left_out=["RU", "RU"])


def test_an_allow_list_names_at_least_one_country():
    with pytest.raises(ValidationError, match="served"):
        border(served=[])


def test_a_quote_is_printed_inside_quotation_marks_of_its_own():
    with pytest.raises(ValidationError, match="quotation marks"):
        border(left_out=[], quote='the "Service" is not offered')


def test_a_name_the_page_carries_outside_its_list_is_not_in_the_list():
    with pytest.raises(ValidationError, match="also_named"):
        border(served=["US", "CA"], also_named=["US"])


def test_a_list_read_as_codes_has_codes_to_compare():
    with pytest.raises(ValidationError, match="codes"):
        border(left_out=[], read="codes")


def test_a_border_measured_by_dns_names_countries_it_can_ask_from():
    with pytest.raises(ValidationError, match="subnet"):
        border(left_out=["TV"], read="dns", source="https://dns.google/resolve?name=x.ai&type=A")


def test_an_entry_carries_its_border():
    e = Entry.model_validate({**BASE, "border": {"left_out": ["RU"], "on": TODAY,
                                                 "source": "https://x.ai/terms"}})
    assert e.border.left_out == ["RU"]


# ---- the yardstick and the share --------------------------------------------

CSV = """developers,iso2_code,year,quarter
100,US,2025,4
600,US,2026,1
300,CN,2026,1
50,RU,2026,1
40,IR,2026,1
10,HK,2026,1
900,EU,2026,1
"""


def test_the_yardstick_is_the_latest_quarter_without_the_eus_line():
    """The EU's line repeats its member states, so it stays out of the total."""
    snap = snapshot_from_csv(CSV, TODAY)
    assert (snap["year"], snap["quarter"]) == (2026, 1)
    assert snap["developers"] == {"US": 600, "CN": 300, "RU": 50, "IR": 40, "HK": 10}
    assert snap["read_on"] == "2026-09-26"


def yard() -> Yardstick:
    return Yardstick.from_snapshot(snapshot_from_csv(CSV, TODAY))


def test_an_allow_list_leaves_out_every_economy_it_does_not_name():
    assert left_out_of(border(served=["US", "HK"]), yard()) == {"CN", "RU", "IR"}


def test_a_share_counts_the_developers_left_out_beyond_the_shared_exclusions():
    """Iran is on nearly every vendor's list, so leaving it out sets no row apart."""
    assert "IR" in SHARED
    assert share(border(left_out=["CN", "IR"]), yard()) == pytest.approx(300 / 1000)
    assert share(border(served=["US", "HK"]), yard()) == pytest.approx(350 / 1000)
    assert share(border(left_out=[]), yard()) == 0


def test_the_committed_yardstick_is_a_whole_quarter():
    y = load_yardstick()
    assert y.year >= 2026 and 1 <= y.quarter <= 4
    assert "EU" not in y.developers
    assert len(y.developers) > 200


# ---- the run's re-read ---------------------------------------------------------

PAGE = "https://x.ai/pricing"
REGIONS = "https://x.ai/regions"


def probed(**border_kw) -> Entry:
    return Entry.model_validate({
        **BASE, "probe": {"type": "page-keywords", "endpoint": PAGE,
                          "keywords": ["x-mini-2", "no credit card"]},
        "border": {"on": TODAY, "source": REGIONS, **border_kw}})


async def verdict(entry: Entry, attempts: int = 3):
    async with httpx.AsyncClient() as client:
        return await probe_entry(client, entry, backoff=0, attempts=attempts)


@respx.mock
async def test_an_allow_list_still_on_its_page_passes():
    respx.get(PAGE).mock(return_value=httpx.Response(200, text="x-mini-2, no credit card"))
    respx.get(REGIONS).mock(return_value=httpx.Response(
        200, text="<ul><li>United States</li><li>Canada</li></ul><footer>Offices in Germany</footer>"))
    result = await verdict(probed(served=["US", "CA"], also_named=["DE"]))
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_country_the_list_dropped_or_added_is_a_note_beside_a_verified_row():
    """The vendor moved its list: the offer is still there, so the row stays
    verified, and the note names what changed for the reviewer who rereads it."""
    respx.get(PAGE).mock(return_value=httpx.Response(200, text="x-mini-2, no credit card"))
    respx.get(REGIONS).mock(return_value=httpx.Response(
        200, text="<ul><li>United States</li><li>Kosovo</li></ul>"))
    result = await verdict(probed(served=["US", "CA"]))
    assert result.status is ProbeStatus.STALE_IDS
    assert result.detail == (f"border: {REGIONS} — no longer names Canada; now also names Kosovo "
                             "— read the vendor's territory words again")


@respx.mock
async def test_a_border_resting_on_a_sentence_is_read_for_the_sentence():
    respx.get(PAGE).mock(return_value=httpx.Response(200, text="x-mini-2, no credit card"))
    respx.get(REGIONS).mock(return_value=httpx.Response(
        200, text="Not for use in Russia or Belarus."))
    entry = probed(left_out=["BY", "RU"], quote="The Service is not offered in Russia or Belarus")
    result = await verdict(entry)
    assert result.detail == (f"border: {REGIONS} — its quote is gone "
                             "— read the vendor's territory words again")


@respx.mock
async def test_a_vendor_that_names_no_country_is_read_for_its_words_alone():
    """An empty deny-list has no names to look for; its quote, where it has one,
    is still what the row rests on."""
    respx.get(PAGE).mock(return_value=httpx.Response(200, text="x-mini-2, no credit card"))
    respx.get(REGIONS).mock(return_value=httpx.Response(
        200, text="Not intended for use in certain jurisdictions. Offices in Singapore."))
    entry = probed(left_out=[], quote="not intended for use in certain jurisdictions")
    assert (await verdict(entry)).status is ProbeStatus.PASS


@respx.mock
async def test_a_list_of_codes_is_compared_code_by_code():
    respx.get(PAGE).mock(return_value=httpx.Response(200, text="x-mini-2, no credit card"))
    codes = respx.get(REGIONS).mock(return_value=httpx.Response(200, json=["BY", "RU"]))
    entry = probed(left_out=["BY", "RU"], read="codes")
    assert (await verdict(entry)).status is ProbeStatus.PASS
    codes.mock(return_value=httpx.Response(200, json=["RU", "TR"]))
    assert (await verdict(entry)).detail == (f"border: {REGIONS} now lists TR and no longer lists "
                                             "BY — read the vendor's territory words again")


@respx.mock
async def test_a_border_measured_by_dns_notices_the_host_answering_again():
    respx.get(PAGE).mock(return_value=httpx.Response(200, text="x-mini-2, no credit card"))
    doh = "https://dns.google/resolve?name=www.x.ai&type=A"
    blocked = {"Status": 0, "Answer": [{"name": "www.x.ai.", "type": 5, "data": "x.edge."},
                                       {"name": "x.edge.", "type": 1, "data": "0.0.0.1"}]}
    us = respx.get(doh + "&edns_client_subnet=73.0.0.0/24").mock(
        return_value=httpx.Response(200, json=blocked))
    respx.get(doh + "&edns_client_subnet=95.24.0.0/24").mock(
        return_value=httpx.Response(200, json=blocked))
    entry = probed(left_out=["RU", "US"], read="dns", source=doh)
    assert (await verdict(entry)).status is ProbeStatus.PASS
    us.mock(return_value=httpx.Response(200, json={"Status": 0, "Answer": [
        {"name": "www.x.ai.", "type": 1, "data": "43.1.2.3"}]}))
    assert (await verdict(entry)).detail == ("border: the host answers from the United States "
                                             "(43.1.2.3) now — read the vendor's territory words again")


@respx.mock
async def test_a_border_only_a_browser_can_read_is_not_fetched():
    respx.get(PAGE).mock(return_value=httpx.Response(200, text="x-mini-2, no credit card"))
    regions = respx.get(REGIONS).mock(return_value=httpx.Response(500))
    assert (await verdict(probed(served=["CN"], read="none"))).status is ProbeStatus.PASS
    assert not regions.called


@respx.mock
async def test_a_border_page_that_cannot_be_read_is_said_so():
    respx.get(PAGE).mock(return_value=httpx.Response(200, text="x-mini-2, no credit card"))
    respx.get(REGIONS).mock(return_value=httpx.Response(404))
    result = await verdict(probed(served=["US"]), attempts=1)
    assert result.status is ProbeStatus.STALE_IDS
    assert result.detail == f"border could not be checked against {REGIONS}: answered HTTP 404"


@respx.mock
async def test_a_moved_border_and_a_moved_data_use_sentence_are_both_reported():
    respx.get(PAGE).mock(return_value=httpx.Response(200, text="x-mini-2, no credit card"))
    respx.get(REGIONS).mock(return_value=httpx.Response(200, text="Canada"))
    respx.get("https://x.ai/privacy").mock(return_value=httpx.Response(200, text="We may train."))
    entry = probed(served=["US"])
    entry.data_use = DataUse(trains="no", quote="We never train on your prompts",
                             url="https://x.ai/privacy")
    detail = (await verdict(entry)).detail
    assert detail.startswith("data_use quote is no longer on https://x.ai/privacy")
    assert f" | border: {REGIONS} — no longer names the United States; now also names Canada" in detail


# ---- the pages ---------------------------------------------------------------

def bordered(**border_kw) -> Entry:
    return Entry.model_validate({**BASE, "border": {"on": TODAY, "source": REGIONS, **border_kw}})


def test_a_provider_page_says_where_the_offer_reaches_and_what_share_that_leaves_out():
    from freetier_radar.render import build_provider_page
    page = build_provider_page(bordered(left_out=["CN", "HK", "MO", "RU", "IR"],
                                        quote="not available in China or Russia"), [], TODAY)
    top = page.split("## What you get")[0]
    assert "no card · not offered in mainland China, Russia, Hong Kong and 2 more places" in top
    section = page.split("## Where it is offered")[1].split("##")[0]
    assert section.strip().startswith(
        f"Not offered in mainland China, Russia, Hong Kong, Iran and Macao ([source]({REGIONS}), "
        "read 2026-09-26). That leaves out ")
    assert "beyond the embargoed countries most offers leave out" in section
    assert "In the vendor's words: “not available in China or Russia”." in section


def test_a_sign_up_for_one_market_is_said_as_where_the_offer_is():
    from freetier_radar.render import build_provider_page
    page = build_provider_page(bordered(served=["CN"]), [], TODAY)
    assert "no card · offered only in mainland China" in page
    assert "Offered only in mainland China ([source]" in page


def test_an_offer_that_names_no_country_says_so_and_flags_nothing():
    from freetier_radar.render import build_provider_page
    page = build_provider_page(bordered(left_out=[]), [], TODAY)
    assert "The vendor names no country it keeps the offer from ([source]" in page
    assert "not offered in" not in page.split("## What you get")[0]
    embargo = build_provider_page(bordered(left_out=["CU", "IR", "KP", "SY"]), [], TODAY)
    assert ("Not offered in Cuba, Iran, North Korea or Syria, the embargoed countries most offers "
            "leave out, and in no other country the vendor names") in embargo
    assert "That leaves out" not in embargo


def test_an_archived_rows_page_says_nothing_of_a_border():
    from freetier_radar.render import build_provider_page
    gone = Entry.model_validate({**BASE, "last_verified": date(2026, 1, 2), "border": {
        "left_out": ["RU"], "on": TODAY, "source": REGIONS}})
    page = build_provider_page(gone, [], TODAY)
    assert "(archived)" in page
    assert "Where it is offered" not in page and "not offered in" not in page


def test_a_model_page_and_llms_txt_carry_the_border_beside_the_card():
    from freetier_radar.render import _llms_line, _model_row
    e = bordered(served=["CN", "HK", "MO", "TW"], models=[{"family": "x-mini-2"}])
    assert " · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · " in \
        "\n".join(_model_row(e, "x-mini-2", []))
    assert "; no card; offered only in mainland China, Hong Kong, Taiwan and Macao" in _llms_line(e)


def test_index_json_carries_the_border_as_recorded():
    from freetier_radar.render import build_index
    row = build_index([bordered(left_out=[])], TODAY)["entries"][0]
    assert row["border"] == {"left_out": [], "on": "2026-09-26", "source": REGIONS, "quote": "",
                             "read": "page", "also_named": []}
