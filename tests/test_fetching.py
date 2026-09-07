from pathlib import Path

import pytest

from fetch import fetch_page

@pytest.fixture
def temp_cache_dir(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    monkeypatch.setattr("fetch.CACHE_DIR", cache_dir)
    return cache_dir


def test_fetch_page_uses_cache_when_file_exists(temp_cache_dir):
    cache_path = temp_cache_dir / "cached.html"
    cache_path.write_text("cached content", encoding="utf-8")

    html = fetch_page("https://example.com/test", "cached.html")

    assert html == "cached content"


def test_fetch_page_returns_none_for_non_200(monkeypatch, temp_cache_dir):
    class FakeResponse:
        status_code = 404

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("requests.get", fake_get)

    html = fetch_page("https://example.com/not-found", "missing.html")

    assert html is None
