"""Hermetic HTTP and small shared repository fixtures."""
from pathlib import Path

import curl_cffi
import pytest

from freetier_radar import page_reader

@pytest.fixture(autouse=True)
def no_unmocked_profile_http(monkeypatch):
    def deny(*args, **kwargs):
        raise OSError('profile HTTP must be explicitly mocked in unit tests')
    monkeypatch.setattr(curl_cffi, 'get', deny)
    monkeypatch.setattr(page_reader, '_addresses', lambda host: ['1.1.1.1'])


@pytest.fixture(scope='session')
def _registry_rows():
    """Parse the committed registry once; expose it only through copying fixtures."""
    from freetier_radar.models import load_registry

    return tuple(load_registry(Path(__file__).resolve().parents[1] / 'registry.yaml'))


@pytest.fixture(scope='session')
def registry_entry(_registry_rows):
    """Each caller gets an isolated vendor row."""
    rows = {entry.id: entry for entry in _registry_rows}
    return lambda ident: rows[ident].model_copy(deep=True)


@pytest.fixture
def committed_registry(_registry_rows):
    """Each whole-registry check gets independent rows from the same parsed input."""
    return [entry.model_copy(deep=True) for entry in _registry_rows]


@pytest.fixture
def render_source(tmp_path):
    """A small registry covering variable output paths, independent of vendor churn."""
    from freetier_radar.models import save_registry
    from test_render import make

    source = tmp_path / 'source'
    source.mkdir()
    save_registry(source / 'registry.yaml', [
        make(id=name, name=name.upper(), models=[{'family': 'alpha'}],
             api={'base_url': f'https://{name}.example/v1', 'model_ids': ['alpha']})
        for name in ('a', 'b')])
    return source
