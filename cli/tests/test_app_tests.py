from __future__ import annotations

import json
import types

import requests
import typer
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
        env="W9_HTTP_PORT_SET=8080\nW9_LOGIN_USER=admin\nW9_LOGIN_PASSWORD=${W9_POWER_PASSWORD}\nW9_POWER_PASSWORD=secret\n",
    )
    cases_dir = repo_fixture / "apps" / "demo" / "tests"
    cases_dir.mkdir()
    (cases_dir / "cases.yml").write_text(
        "optional:\n  - id: console-login\n    type: http-basic\n    path: /admin/\n",
        encoding="utf-8",
    )

    assert app_tests.load_cases("demo")["optional"][0]["type"] == "http-basic"
    assert app_tests.load_env("demo")["W9_LOGIN_PASSWORD"] == "secret"


def test_load_env_strips_matching_outer_quotes(repo_fixture, app_factory):
    app_factory(
        "demo",
        env="W9_HTTP_PORT_SET='8080'\nW9_URL=\"http://example.com\"\nW9_ID='demo'\n",
    )

    payload = app_tests.load_env("demo")

    assert payload["W9_HTTP_PORT_SET"] == "8080"
    assert payload["W9_URL"] == "http://example.com"
    assert payload["W9_ID"] == "demo"


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


def test_default_cases_add_container_healthy_when_healthcheck_exists(repo_fixture, app_factory):
    app_factory(
        "demo",
        env="W9_HTTP_PORT_SET=8080\nW9_ID=demo\n",
        compose="services:\n  demo:\n    container_name: ${W9_ID}\n    healthcheck:\n      test: ['CMD', 'true']\n",
    )

    cases = app_tests._default_cases(app_tests.load_env("demo"), app_tests.load_compose("demo"), "http://localhost:8080", "demo")

    assert [item["id"] for item in cases] == ["compose-config", "container-up", "container-healthy", "web-access"]


def test_select_container_line_prefers_exact_match_over_prefixed_worker_name():
    stdout = "activepieces-worker Up 1 minute\nactivepieces Up 1 minute\n"

    assert app_tests._select_container_line(stdout, "activepieces") == "activepieces Up 1 minute"


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
        lambda app_name=None, base_url=None, ssh_host=None, ssh_user=None, ssh_secret_path=None, deploy_root=None, wait_timeout=60, wait_interval=5, progress=None, verbose=False: {
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


def test_app_tests_cli_forwards_wait_options(monkeypatch):
    calls = {}

    def fake_run_app_tests(app_name=None, **kwargs):
        calls["app_name"] = app_name
        calls.update(kwargs)
        return {"app": app_name, "ok": True, "results": []}

    monkeypatch.setattr(app_tests, "run_app_tests", fake_run_app_tests)

    result = runner.invoke(main.app, ["app-tests", "--app", "demo", "--wait-timeout", "90", "--wait-interval", "3", "--json"])

    assert result.exit_code == 0
    assert calls["app_name"] == "demo"
    assert calls["wait_timeout"] == 90
    assert calls["wait_interval"] == 3


def test_run_app_tests_stops_after_required_failure(repo_fixture, app_factory, monkeypatch):
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

    monkeypatch.setattr(app_tests, "_run_subprocess", lambda command: types.SimpleNamespace(returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(
        app_tests.requests,
        "get",
        lambda *args, **kwargs: (_ for _ in ()).throw(requests.ConnectionError("connection refused")),
    )

    payload = app_tests.run_app_tests("demo")

    assert payload["ok"] is False
    assert [item["id"] for item in payload["results"]] == ["compose-config", "container-up"]


def test_run_app_tests_http_failure_is_structured(repo_fixture, app_factory, monkeypatch):
    app_factory(
        "demo",
        env="W9_HTTP_PORT_SET=8080\nW9_LOGIN_USER=admin\nW9_LOGIN_PASSWORD=secret\nW9_ID=demo\n",
    )

    def fake_run(command):
        if command[:2] == ["docker", "ps"]:
            return types.SimpleNamespace(returncode=0, stdout="demo Up\n", stderr="")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(app_tests, "_run_subprocess", fake_run)
    monkeypatch.setattr(
        app_tests.requests,
        "get",
        lambda *args, **kwargs: (_ for _ in ()).throw(requests.ConnectionError("connection refused")),
    )

    payload = app_tests.run_app_tests("demo")

    assert payload["ok"] is False
    assert [item["id"] for item in payload["results"]] == ["compose-config", "container-up", "web-access"]
    assert payload["results"][-1]["error"] == "connection refused"


def test_run_app_tests_retries_until_web_check_succeeds(repo_fixture, app_factory, monkeypatch):
    app_factory(
        "demo",
        env="W9_HTTP_PORT_SET=8080\nW9_ID=demo\n",
    )
    attempts = {"count": 0}

    def fake_run(command):
        if command[:2] == ["docker", "ps"]:
            return types.SimpleNamespace(returncode=0, stdout="demo Up\n", stderr="")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    def fake_get(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise requests.ConnectionError("not ready")
        return DummyResponse(200, url=args[0])

    monkeypatch.setattr(app_tests, "_run_subprocess", fake_run)
    monkeypatch.setattr(app_tests.requests, "get", fake_get)
    monkeypatch.setattr(app_tests.time, "sleep", lambda seconds: None)

    payload = app_tests.run_app_tests("demo", wait_timeout=10, wait_interval=1)

    assert payload["ok"] is True
    assert attempts["count"] == 3
    assert payload["results"][2]["id"] == "web-access"


def test_run_app_tests_container_healthy_reads_inspect_state(repo_fixture, app_factory, monkeypatch):
    app_factory(
        "demo",
        env="W9_HTTP_PORT_SET=8080\nW9_ID=demo\n",
        compose="services:\n  demo:\n    container_name: ${W9_ID}\n    healthcheck:\n      test: ['CMD', 'true']\n",
    )

    def fake_run(command):
        if command[:2] == ["docker", "ps"]:
            return types.SimpleNamespace(returncode=0, stdout="demo Up\n", stderr="")
        if command[:2] == ["docker", "inspect"]:
            return types.SimpleNamespace(returncode=0, stdout=json.dumps({"Status": "running", "Health": {"Status": "healthy"}}), stderr="")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(app_tests, "_run_subprocess", fake_run)
    monkeypatch.setattr(app_tests.requests, "get", lambda *args, **kwargs: DummyResponse(200, url=args[0]))

    payload = app_tests.run_app_tests("demo")

    assert payload["ok"] is True
    assert [item["id"] for item in payload["results"]] == ["compose-config", "container-up", "container-healthy", "web-access"]
    assert payload["results"][2]["health"] == "healthy"


def test_run_app_tests_remote_preflight_failure_stops_immediately(repo_fixture, app_factory, monkeypatch):
    app_factory(
        "demo",
        env="W9_HTTP_PORT_SET=8080\nW9_ID=demo\n",
    )
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    monkeypatch.setattr(app_tests.remote, "default_target", lambda: "remote")
    monkeypatch.setattr(app_tests.remote, "ssh_host", lambda value=None: value or "1.2.3.4")
    monkeypatch.setattr(app_tests.remote, "ssh_user", lambda value=None: value or "root")
    monkeypatch.setattr(app_tests.remote, "resolve_secret_path", lambda value=None: secret_path)
    monkeypatch.setattr(app_tests.remote, "deploy_root", lambda value=None: value or "/websoft9/library/apps")
    monkeypatch.setattr(
        app_tests.remote,
        "preflight_ssh",
        lambda host, user, secret_path: types.SimpleNamespace(returncode=255, stdout="", stderr="ssh: connect to host 1.2.3.4 port 22: Connection refused"),
    )

    payload = app_tests.run_app_tests("demo")

    assert payload["ok"] is False
    assert payload["target"] == "remote"
    assert [item["id"] for item in payload["results"]] == ["remote-connect"]
    assert "Connection refused" in payload["results"][0]["error"]


def test_scrub_ssh_warning_removes_known_hosts_noise():
    cleaned = app_tests.remote.scrub_ssh_stderr(
        "Warning: Permanently added '1.2.3.4' (ED25519) to the list of known hosts.\npermission denied\n"
    )

    assert cleaned == "permission denied"


def test_app_tests_cli_contract_progress_to_stderr(monkeypatch):
    output = []

    def fake_run_app_tests(app_name=None, **kwargs):
        assert callable(kwargs["progress"])
        assert kwargs["verbose"] is False
        kwargs["progress"]("[1/3] running compose-config")
        return {"app": app_name, "target": "local", "ok": True, "results": []}

    monkeypatch.setattr(app_tests, "run_app_tests", fake_run_app_tests)
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    main.app_tests_command(
        app_name="demo",
        base_url=None,
        ssh_host=None,
        ssh_user=None,
        ssh_secret_path=None,
        deploy_root=None,
        progress=True,
        verbose=False,
        as_json=True,
    )

    assert output == [
        ("[1/3] running compose-config", True),
        (json.dumps({"app": "demo", "target": "local", "ok": True, "results": []}, indent=2, ensure_ascii=False), False),
    ]


def test_run_app_tests_remote_progress_starts_with_connectivity_check(repo_fixture, app_factory, monkeypatch):
    app_factory("demo", env="W9_HTTP_PORT_SET=8080\nW9_ID=demo\n")
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")
    progress = []

    monkeypatch.setattr(app_tests.remote, "default_target", lambda: "remote")
    monkeypatch.setattr(app_tests.remote, "ssh_host", lambda value=None: value or "1.2.3.4")
    monkeypatch.setattr(app_tests.remote, "ssh_user", lambda value=None: value or "root")
    monkeypatch.setattr(app_tests.remote, "resolve_secret_path", lambda value=None: secret_path)
    monkeypatch.setattr(app_tests.remote, "deploy_root", lambda value=None: value or "/websoft9/library/apps")
    monkeypatch.setattr(
        app_tests.remote,
        "preflight_ssh",
        lambda host, user, secret_path: types.SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    monkeypatch.setattr(
        app_tests,
        "run_case",
        lambda *args, **kwargs: {"id": args[1].get("id") or args[1]["type"], "ok": False, "stdout": "", "stderr": ""},
    )

    payload = app_tests.run_app_tests("demo", progress=progress.append, verbose=False)

    assert payload["ok"] is False
    assert progress == [
        "[1/4] checking remote connectivity",
        "[2/4] running compose-config",
    ]


def test_emit_case_detail_prefers_health_summary_over_raw_stdout():
    output = []

    app_tests._emit_case_detail(
        output.append,
        {"stdout": '{"Status":"running"}', "status": "running", "health": "healthy", "stderr": ""},
    )

    assert output == ["status=running health=healthy"]
