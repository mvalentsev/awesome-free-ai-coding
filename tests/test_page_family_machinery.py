from datetime import date

import httpx
import pytest
import respx

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, probe_entry


@pytest.mark.parametrize('model_text, machinery, expected', [
    ('<script>const retiredNavigation = "science-flash";</script>', [], ProbeStatus.STALE_MODELS),
    ('<!-- science-flash -->', [], ProbeStatus.STALE_MODELS),
    ('<p>science-flash</p>', [], ProbeStatus.PASS),
    ('<script>const currentModel = "science-flash";</script>', ['science-flash'], ProbeStatus.PASS),
    ('<!-- science-flash -->', ['science-flash'], ProbeStatus.STALE_MODELS),
])
@respx.mock
async def test_navigation_state_and_comments_do_not_keep_a_family_listed(model_text, machinery, expected):
    row = Entry.model_validate({
        'id': 'vendor', 'name': 'Vendor', 'category': 'api-free-tier',
        'url': 'https://vendor.example', 'offering': 'Free models',
        'free_part': 'models', 'models': [{'family': 'science-flash'}],
        'first_seen': date(2026, 1, 1), 'last_verified': date(2026, 1, 1),
        'probe': {'type': 'page-keywords', 'endpoint': 'https://vendor.example/pricing',
                  'keywords': ['100 free requests per day'], 'machinery_keywords': machinery},
    })
    respx.get(row.probe.endpoint).respond(200, text='<p>100 free requests per day</p>' + model_text)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, row, attempts=1, backoff=0)
    assert result.status is expected
