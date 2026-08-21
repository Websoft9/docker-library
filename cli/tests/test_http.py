from __future__ import annotations

from pathlib import Path

from libs import http


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
