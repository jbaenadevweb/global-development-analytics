import requests
import pytest

from src.scraping.fetch import FetchError, fetch_html


def test_fetch_stops_when_robots_is_unreachable(monkeypatch):
    calls = []

    def blocked(*args, **kwargs):
        calls.append(args[0])
        response = requests.Response()
        response.status_code = 403
        raise requests.HTTPError("403 Forbidden", response=response)

    monkeypatch.setattr("src.scraping.fetch.requests.get", blocked)
    with pytest.raises(FetchError, match="robots.txt"):
        fetch_html("https://example.org/table")
    assert calls == ["https://example.org/robots.txt"]
