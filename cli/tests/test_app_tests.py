from __future__ import annotations

import json
import types

from typer.testing import CliRunner

from libs import app_tests, main


runner = CliRunner()


class DummyResponse:
    def __init__(self, status_code: int, url: str = "http://localhost:8080/"):
        self.status_code = status_code
        self.url = url


def test_load_cases_and_env_resolution(repo_fixture, app_factory):
    app_factory(
        "demo",
        env="W9_HTTP_PORT_SET=8080\nW9_LOGIN_USER=admin\nW9_LOGIN_PASSWORD=$W9_POWER_PASSWORD\nW9_POWER_PASSWORD=secret\n",
    )
    cases_dir = repo_fixture / "apps" / "demo" / "tests"
    cases_dir.mkdir()
    (cases_dir / "cases.yml").write_text(
        "optional:\n  - id: console-login\n    type: http-basic\n    path: /admin/\n",
        encoding="utf-8",
    )

    assert app_tests.load_cases("demo")["optional"][0]["type"] == "http-basic"
    assert app_tests.load_env("demo")["W9_LOGIN_PASSWORD"] == "secret"


def test_run_app_tests_with_mocked_cases(repo_fixture, app_factory, monkeypatch):
    app_factory(
        "demo",
        env="W9_HTTP_PORT_SET=8080\nW9_LOGIN_USER=admin\nW9_LOGIN_PASSWORD=secret\nW9_ID=demo\n",
    )
    cases_dir = repo_fixture / "apps" / "demo" / "tests"
    cases_dir.mkdir()
    (cases_dir / "cases.yml").write_text(
        "optional:\n  - id: console-login\n    type: http-basic\n    path: /admin/\n    expect_status: 200\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(app_tests, "_run_subprocess", lambda command: types.SimpleNamespace(returncode=0, stdout="demo Up", stderr=""))
    monkeypatch.setattr(app_tests.requests, "get", lambda *args, **kwargs: DummyResponse(200, url=args[0]))

    payload = app_tests.run_app_tests("demo")

    assert payload["ok"] is True
    assert [item["id"] for item in payload["results"]] == ["compose-config", "container-up", "web-access", "console-login"]


def test_skip_suppresses_required_case(repo_fixture, app_factory, monkeypatch):
    app_factory(
        "demo",
        env="W9_HTTP_PORT_SET=8080\nW9_LOGIN_USER=admin\nW9_LOGIN_PASSWORD=secret\nW9_ID=demo\n",
    )
    cases_dir = repo_fixture / "apps" / "demo" / "tests"
    cases_dir.mkdir()
    (cases_dir / "cases.yml").write_text(
        "skip:\n  - id: web-access\n    reason: no web check\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(app_tests, "_run_subprocess", lambda command: types.SimpleNamespace(returncode=0, stdout="demo Up", stderr=""))
    monkeypatch.setattr(app_tests.requests, "get", lambda *args, **kwargs: DummyResponse(200, url=args[0]))

    payload = app_tests.run_app_tests("demo")

    assert [item["id"] for item in payload["results"]] == ["compose-config", "container-up"]


def test_app_tests_cli_contract(monkeypatch):
    monkeypatch.setattr(
        app_tests,
        "run_app_tests",
        lambda app_name, base_url=None, ssh_host=None, ssh_user=None, ssh_secret_path=None, deploy_root=None: {
            "app": app_name,
            "base_url": base_url,
            "ok": True,
            "results": [],
        },
    )

    result = runner.invoke(main.app, ["app-tests", "--app", "demo", "--base-url", "http://localhost:8080", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["app"] == "demo"
    assert payload["base_url"] == "http://localhost:8080"
