from datetime import date

import httpx
import pytest

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, probe_entry


def entry(lane=None):
    return Entry.model_validate({
        'id': 'fixture', 'name': 'Fixture', 'url': 'https://vendor.example',
        'category': 'aggregator', 'offering': 'A free model gateway', 'free_part': 'models',
        'models': [{'family': 'fixture'}],
        'api': {'base_url': 'https://vendor.example/v1', 'auth': 'api-key', 'model_ids': ['fixture-free']},
        'probe': {'type': 'api-models', 'endpoint': 'https://vendor.example/v1/models',
                  'require_zero_price': True, **({'lane': lane} if lane else {})},
        'first_seen': date(2026, 11, 8), 'last_verified': date(2026, 11, 8),
    })


@pytest.mark.asyncio
async def test_nested_openai_catalog_is_read_at_the_http_boundary():
    body = {'data': {'object': 'list', 'data': [
        {'id': 'fixture-free', 'pricing': {'prompt': '0', 'completion': '0'}}]}}
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body))) as client:
        result = await probe_entry(client, entry(), attempts=1, today=date(2026, 11, 8))
    assert result.status is ProbeStatus.PASS


@pytest.mark.asyncio
async def test_explicit_empty_lane_does_not_fall_back_to_a_nested_catalog():
    body = {'free': [], 'data': {'data': [
        {'id': 'fixture-free', 'pricing': {'prompt': '0', 'completion': '0'}}]}}
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body))) as client:
        result = await probe_entry(client, entry('free'), attempts=1, today=date(2026, 11, 8))
    assert result.status is ProbeStatus.FAIL
