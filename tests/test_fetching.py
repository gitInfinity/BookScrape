import pytest
import requests

from fetch import FetchStats, fetch_page

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


@pytest.mark.parametrize("status_code", [403, 404])
def test_fetch_page_does_not_retry_client_errors(
    monkeypatch, temp_cache_dir, status_code
):
    calls = 0

    class FakeResponse:
        def __init__(self):
            self.status_code = status_code

    def fake_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        return FakeResponse()

    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr("fetch.time.sleep", lambda _: pytest.fail("unexpected retry"))

    assert fetch_page("https://example.com/missing", "missing.html") is None
    assert calls == 1


def test_fetch_page_retries_timeout_once(monkeypatch, temp_cache_dir):
    calls = 0

    def fake_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise requests.Timeout("temporary timeout")
        return type("Response", (), {"status_code": 200, "text": "retried"})()

    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr("fetch.time.sleep", lambda _: None)
    stats = FetchStats()

    assert fetch_page("https://example.com/retry", "retry.html", stats) == "retried"
    assert calls == 2
    assert stats.pages_fetched == 1
    assert stats.failed_pages == 0


def test_fetch_page_retries_server_error_once(monkeypatch, temp_cache_dir):
    calls = 0

    class FakeResponse:
        def __init__(self, status_code, text=""):
            self.status_code = status_code
            self.text = text

    def fake_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        return FakeResponse(503 if calls == 1 else 200, "recovered")

    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr("fetch.time.sleep", lambda _: None)

    assert fetch_page("https://example.com/server-error", "server-error.html") == "recovered"
    assert calls == 2
