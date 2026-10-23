from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from libs import http


@pytest.fixture(autouse=True)
def _reset_remote_only():
    http.reset_network_state()
    yield
    http.reset_network_state()


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


def test_get_json_with_fallback_reuses_remote_failure_without_retrying(monkeypatch):
    calls = {"remote": 0}

    monkeypatch.setattr(http, "probe_url", lambda url, **kwargs: http.Reachability(False, url, 3, 5, error="timeout"))

    def fail_remote(*args, **kwargs):
        calls["remote"] += 1
        return None, None, "ssh timeout"

    monkeypatch.setattr(http, "remote_get_json", fail_remote)

    first = http.get_json_with_fallback("https://hub.docker.com/tags")
    second = http.get_json_with_fallback("https://hub.docker.com/tags")

    assert first[2] == "ssh timeout"
    assert second[2] == "ssh timeout"
    assert calls["remote"] == 1
    assert http.network_snapshot()["path"] == "unavailable"


def test_remote_json_fallback_uses_short_curl_timeouts(monkeypatch):
    from libs import remote

    captured = {}

    def fake_run_ssh(host, user, secret_path, script, connect_timeout=15):
        captured["script"] = script
        return subprocess.CompletedProcess(["ssh"], 0, '{"ok": true}', "")

    monkeypatch.setattr(remote, "ssh_host", lambda: "remote.example")
    monkeypatch.setattr(remote, "ssh_user", lambda: "root")
    monkeypatch.setattr(remote, "resolve_secret_path", lambda: Path("/tmp/key"))
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(remote, "run_ssh", fake_run_ssh)

    data, _, error = http.remote_get_json("https://example.com/api", {"page": 1}, None)

    assert data == {"ok": True}
    assert error is None
    assert "--connect-timeout 2" in captured["script"]
    assert "--max-time 4" in captured["script"]


def test_remote_json_fallback_retries_ssh_once(monkeypatch):
    from libs import remote

    calls = []

    def fake_run_ssh(host, user, secret_path, script, connect_timeout=15):
        calls.append(connect_timeout)
        return subprocess.CompletedProcess(["ssh"], 1, "", "connection timeout")

    monkeypatch.setattr(remote, "ssh_host", lambda: "remote.example")
    monkeypatch.setattr(remote, "ssh_user", lambda: "root")
    monkeypatch.setattr(remote, "resolve_secret_path", lambda: Path("/tmp/key"))
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(remote, "run_ssh", fake_run_ssh)

    data, _, error = http.remote_get_json("https://example.com/api", None, None)

    assert data is None
    assert error == "connection timeout"
    assert calls == [3, 3]
    assert http.network_snapshot()["remote_retries"] == 1
