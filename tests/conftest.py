"""Hermetic HTTP and small shared repository fixtures."""
import curl_cffi
import pytest

from freetier_radar import page_reader

@pytest.fixture(autouse=True)
def no_unmocked_profile_http(monkeypatch):
    def deny(*args, **kwargs):
        raise OSError('profile HTTP must be explicitly mocked in unit tests')
    monkeypatch.setattr(curl_cffi, 'get', deny)
    monkeypatch.setattr(page_reader, '_addresses', lambda host: ['1.1.1.1'])


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
