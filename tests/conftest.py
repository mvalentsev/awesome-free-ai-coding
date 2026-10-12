"""Keep the alternate HTTP transport hermetic, like respx keeps httpx."""
import curl_cffi
import pytest

from freetier_radar import page_reader

@pytest.fixture(autouse=True)
def no_unmocked_profile_http(monkeypatch):
    def deny(*args, **kwargs):
        raise OSError('profile HTTP must be explicitly mocked in unit tests')
    monkeypatch.setattr(curl_cffi, 'get', deny)
    monkeypatch.setattr(page_reader, '_addresses', lambda host: ['1.1.1.1'])
