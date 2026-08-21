from __future__ import annotations

from pathlib import Path

from libs import drift


class DummyResponse:
    def __init__(self, text: str, status_ok: bool = True):
        self.text = text
        self._status_ok = status_ok

    def raise_for_status(self):
        if not self._status_ok:
            raise RuntimeError("boom")


def test_dependency_images_deduplicates_and_sorts():
    compose = {
        "services": {
            "a": {"image": "redis:7"},
            "b": {"image": "redis:7"},
            "c": {"image": "postgres:16"},
        }
    }

    assert drift.dependency_images(compose) == ["postgres:16", "redis:7"]


def test_diff_services_detects_added_removed_and_changed_services():
    local = {"services": {"web": {"image": "nginx:1.0", "ports": ["80:80"]}, "db": {"image": "mysql:8"}}}
    upstream = {"services": {"web": {"image": "nginx:1.1", "ports": ["80:80"]}, "cache": {"image": "redis:7"}}}

    result = drift.diff_services(local, upstream)

    assert result["services_added"] == ["cache"]
    assert result["services_removed"] == ["db"]
    assert result["services_changed"]["web"]["image"] == {"local": "nginx:1.0", "upstream": "nginx:1.1"}


def test_parse_env_text_and_diff_config_identify_login_and_url_changes(tmp_path: Path):
    env_text = "# comment\nW9_URL=http://old\nW9_LOGIN_USER=admin\nPLAIN=value\n"
    parsed = drift.parse_env_text(env_text)
    file_path = tmp_path / ".env"
    file_path.write_text(env_text, encoding="utf-8")

    assert parsed == {"W9_URL": "http://old", "W9_LOGIN_USER": "admin", "PLAIN": "value"}
    assert drift.parse_env_file(file_path) == parsed

    diff = drift.diff_config(parsed, {"W9_URL": "http://new", "W9_LOGIN_USER": "root", "OTHER": "x"})
    assert diff["keys_added"] == ["OTHER"]
    assert diff["keys_removed"] == ["PLAIN"]
    assert sorted(diff["url_login_keys_changed"]) == ["W9_LOGIN_USER", "W9_URL"]


def test_fetch_upstream_helpers_return_error_on_request_failure(monkeypatch):
    monkeypatch.setattr(drift, "get", lambda url: DummyResponse("", status_ok=False))

    compose, compose_error = drift.fetch_upstream_compose("https://example.com/docker-compose.yml")
    text, text_error = drift.fetch_upstream_text("https://example.com/.env")

    assert compose is None and "boom" in compose_error
    assert text is None and "boom" in text_error
