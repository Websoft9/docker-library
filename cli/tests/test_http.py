from __future__ import annotations

from pathlib import Path

import pytest

from libs import http


@pytest.fixture(autouse=True)
def _reset_remote_only():
    http._REMOTE_ONLY = False
    yield
    http._REMOTE_ONLY = False


def test_default_timeout_uses_env_and_falls_back_on_invalid(monkeypatch):
    monkeypatch.setenv("LIBS_HTTP_TIMEOUT", "20")
    assert http.default_timeout() == (5.0, 20.0)

    monkeypatch.setenv("LIBS_HTTP_TIMEOUT", "bad")
    assert http.default_timeout() == (5.0, 15.0)


def test_saved_proxy_and_clear_proxy_use_config_file(tmp_path: Path, monkeypatch):
    path = tmp_path / "proxy.conf"
    monkeypatch.setattr(http, "REPO_CONFIG_PATH", path)

    http.save_proxy("socks5h://127.0.0.1:1089")
    assert http.saved_proxy() == "socks5h://127.0.0.1:1089"

    http.clear_proxy()
    assert http.saved_proxy() is None


def test_detect_proxy_prefers_environment_over_saved_file(tmp_path: Path, monkeypatch):
    path = tmp_path / "proxy.conf"
    path.write_text("file-proxy\n", encoding="utf-8")
    monkeypatch.setattr(http, "REPO_CONFIG_PATH", path)
    for key in http.PROXY_KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("HTTPS_PROXY", "env-proxy")

    assert http.detect_proxy() == "env-proxy"


def test_normalize_proxy_env_sets_env_and_clears_wildcard_no_proxy(monkeypatch):
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")

    value = http.normalize_proxy_env("http://proxy:8080")

    assert value == "http://proxy:8080"
    assert http.os.environ["http_proxy"] == "http://proxy:8080"
    assert http.os.environ["https_proxy"] == "http://proxy:8080"
    assert http.os.environ["all_proxy"] == "http://proxy:8080"
    assert http.os.environ["NO_PROXY"] == ""
    assert http.os.environ["no_proxy"] == ""


class _ProbeResponse:
    status_code = 204

    def close(self):
        pass


def test_probe_url_returns_quickly_after_two_retries(monkeypatch):
    import requests

    calls = {"count": 0}

    def fake_get(*args, **kwargs):
        calls["count"] += 1
        raise requests.Timeout("blocked")

    monkeypatch.setattr(http.requests, "get", fake_get)

    result = http.probe_url("https://hub.docker.com/v2/repositories/library/drupal/tags")

    assert result.ok is False
    assert result.attempts == 3
    assert calls["count"] == 3
    assert "blocked" in (result.error or "")


def test_probe_url_accepts_any_http_status(monkeypatch):
    monkeypatch.setattr(http.requests, "get", lambda *args, **kwargs: _ProbeResponse())

    result = http.probe_url("https://example.com")

    assert result.ok is True
    assert result.attempts == 1
    assert result.status == 204


def test_get_json_with_fallback_uses_remote_after_probe_failure(monkeypatch):
    monkeypatch.setattr(http, "probe_url", lambda url, **kwargs: http.Reachability(False, url, 3, 5, error="timeout"))
    monkeypatch.setattr(http, "remote_get_json", lambda url, params, headers: ({"ok": True}, {}, None))

    data, headers, error = http.get_json_with_fallback("https://hub.docker.com/v2/repositories/library/drupal/tags")

    assert data == {"ok": True}
    assert headers == {}
    assert error is None
