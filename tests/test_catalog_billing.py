"""Unknown mandatory prices cannot establish a zero-cost catalog offer."""
from datetime import date

import httpx
import pytest

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, probe_entry


def entry():
    return Entry.model_validate({
        "id": "vendor", "name": "Vendor", "category": "api-free-tier",
        "url": "https://vendor.example", "offering": "Free model access",
        "first_seen": date(2026, 1, 1), "last_verified": date(2026, 1, 1),
        "models": [{"family": "qwen3-coder"}],
        "probe": {"type": "api-models", "endpoint": "https://vendor.example/models",
                  "require_zero_price": True},
    })


@pytest.mark.parametrize("field", ["request", "per_request", "request_price",
                                    "price_per_request", "transcription_duration_cost_per_second",
                                    "min_request_price"])
@pytest.mark.parametrize("value,free", [(0, True), ("0", True), (0.1, False),
                                      ("unknown", False), (None, False), (False, False)])
async def test_every_published_mandatory_price_must_be_a_readable_zero(field, value, free):
    model = {"id": "qwen3-coder", "pricing": {"prompt": 0, "completion": 0}}
    if field == "min_request_price":
        model[field] = value
    else:
        model["pricing"][field] = value
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"data": [model]}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is (ProbeStatus.PASS if free else ProbeStatus.FAIL), result.detail
    if not free:
        assert field in result.detail


@pytest.mark.parametrize("ratio,free", [(0, True), (1, True), ("unknown", False),
                                      (None, False), (False, False)])
async def test_an_unreadable_published_completion_multiplier_is_not_a_zero_price(ratio, free):
    model = {"id": "qwen3-coder", "model_ratio": 0, "completion_ratio": ratio}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"data": [model]}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is (ProbeStatus.PASS if free else ProbeStatus.FAIL), result.detail


@pytest.mark.parametrize("fields", [
    {"pricing": {"prompt": 0, "completion": 0, "image": "unknown", "web_search": 1}},
    {"isFree": True, "pricing": {"prompt": 1, "completion": 2, "request": "unknown"}},
    {"model_ratio": 0},
])
async def test_explicit_free_modes_optional_addons_and_omitted_multipliers_stay_eligible(fields):
    model = {"id": "qwen3-coder", **fields}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"data": [model]}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is ProbeStatus.PASS, result.detail


@pytest.mark.parametrize("billable", ["prompt_tokens", "completion_tokens",
                                       "input_text_tokens", "output_text_tokens"])
@pytest.mark.parametrize("cost,free", [(0, True), ("0", True), (0.5, False),
                                     (None, False), ("unknown", False), (False, False)])
async def test_authoritative_billing_lines_override_zero_summary_prices(billable, cost, free):
    # https://aihubmix.com/api/v1/models, checked 2026-11-07: Gemini Live
    # and Omni have zero summary rates beside paid billing_config token lines.
    model = {"id": "qwen3-coder", "pricing": {"input": 0, "output": 0},
             "pricing_source": "billing_config", "pricing_lines": [
                 {"billable": billable, "unit": "million_tokens", "cost_usd": cost}]}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"data": [model]}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is (ProbeStatus.PASS if free else ProbeStatus.FAIL), result.detail
    if not free:
        assert "pricing_lines" in result.detail and billable in result.detail


@pytest.mark.parametrize('billable,model_type,input_modes,output_modes', [
    ('audio_input_seconds', 'stt', 'audio,text', 'text'),
    ('audio_input_seconds', 't2a', 'audio', 'audio'),
    ('audio_generation', 't2a', 'text', 'audio'),
])
@pytest.mark.parametrize('cost,free', [(0, True), (0.12, False), (None, False)])
async def test_native_audio_billing_is_mandatory_despite_zero_token_summaries(
        billable, model_type, input_modes, output_modes, cost, free):
    # AIHubMix's catalog on 2026-11-09: native transcription, isolation and
    # generation bill audio in pricing_lines: https://aihubmix.com/api/v1/models.
    model = {'id': 'qwen3-coder', 'types': model_type,
             'input_modalities': input_modes, 'output_modalities': output_modes,
             'pricing': {'input': 0, 'output': 0}, 'pricing_source': 'billing_config',
             'pricing_lines': [{'billable': billable, 'unit': 'minute', 'cost_usd': cost}]}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={'data': [model]}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is (ProbeStatus.PASS if free else ProbeStatus.FAIL), result.detail
    if not free:
        assert billable in result.detail


async def test_optional_audio_input_does_not_price_a_free_text_chat_lane():
    model = {'id': 'qwen3-coder', 'types': 'llm', 'input_modalities': 'text,audio',
             'output_modalities': 'text', 'pricing': {'input': 0, 'output': 0},
             'pricing_source': 'billing_config', 'pricing_lines': [
                 {'billable': 'audio_input_seconds', 'unit': 'minute', 'cost_usd': 0.12}]}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={'data': [model]}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is ProbeStatus.PASS


@pytest.mark.parametrize("fields", [
    {"pricing_lines": [{"billable": "cached_tokens", "cost_usd": 1},
                       {"billable": "input_image_tokens", "cost_usd": 2}]},
    {"isFree": True, "pricing_lines": [{"billable": "prompt_tokens", "cost_usd": 1}]},
    {"promo": {"status": "active", "is_free": True},
     "pricing_lines": [{"billable": "completion_tokens", "cost_usd": 2}]},
])
async def test_optional_billing_addons_and_explicit_free_modes_remain_free(fields):
    model = {"id": "qwen3-coder", "pricing": {"input": 0, "output": 0},
             "pricing_source": "billing_config", **fields}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"data": [model]}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is ProbeStatus.PASS, result.detail


@pytest.mark.parametrize("lines", [None, {}, "unreadable"])
async def test_unreadable_authoritative_billing_lines_cannot_confirm_free_access(lines):
    model = {"id": "qwen3-coder", "pricing": {"input": 0, "output": 0},
             "pricing_source": "billing_config", "pricing_lines": lines}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"data": [model]}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "pricing_lines unreadable" in result.detail


@pytest.mark.parametrize("prices,free", [
    ({"input_token_price_per_m": 0, "output_token_price_per_m": 0}, True),
    ({"input_token_price_per_m": "0", "output_token_price_per_m": "0"}, True),
    ({"input_token_price_per_m": 0.1, "output_token_price_per_m": 0}, False),
    ({"input_token_price_per_m": 0, "output_token_price_per_m": 0.2}, False),
    ({"input_token_price_per_m": 0}, False),
    ({"input_token_price_per_m": 0, "output_token_price_per_m": None}, False),
    ({"input_token_price_per_m": False, "output_token_price_per_m": 0}, False),
])
async def test_the_published_novita_offer_checks_both_current_catalog_prices(registry_entry, prices, free):
    row = registry_entry('novita')
    model = {"id": "apodex/apodex-1.1-mini", "status": 1, **prices}

    def respond(request):
        if str(request.url) == "https://api.novita.ai/openai/v1/models":
            return httpx.Response(200, json={"data": [model]})
        # The public page can lag behind current API billing.
        return httpx.Response(200, text="apodex/apodex-1.1-mini Input $0 / M Tokens Output $0 / M Tokens")

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await probe_entry(client, row, attempts=1, backoff=0)
    assert (result.status is ProbeStatus.PASS) is free, result.detail
