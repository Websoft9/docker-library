from __future__ import annotations

import json
import types
from pathlib import Path

import typer

from libs import app_deploy, main


def test_app_deploy_cli_contract_progress_to_stderr(monkeypatch):
    output = []

    def fake_deploy(**kwargs):
        assert callable(kwargs["progress"])
        assert kwargs["verbose"] is False
        kwargs["progress"]("[1/5] syncing deploy package")
        return {"app": kwargs["app_name"], "target": "remote", "action": "up -d"}

    monkeypatch.setattr(app_deploy, "deploy", fake_deploy)
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    main.app_deploy_command(
        app_name="demo",
        target=None,
        ssh_host=None,
        ssh_user=None,
        ssh_secret_path=None,
        deploy_root=None,
        down=False,
        progress=True,
        verbose=False,
        as_json=True,
    )

    assert output == [
        ("[1/5] syncing deploy package", True),
        (json.dumps({"app": "demo", "target": "remote", "action": "up -d"}, indent=2, ensure_ascii=False), False),
    ]


def test_app_deploy_local_step_sequence(monkeypatch, repo_fixture, app_factory):
    app_factory("demo")
    output = []

    def fake_run(command, *, progress=None, verbose=False):
        if progress and verbose:
            progress(f"$ {' '.join(command)}")
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(app_deploy, "_run", fake_run)

    payload = app_deploy.deploy("demo", target="local", progress=output.append, verbose=False)

    assert payload["target"] == "local"
    assert output == [
        "[1/5] ensuring shared network",
        "[2/5] validating compose config",
        "[3/5] pulling images",
        "[4/5] starting application",
        "[5/5] showing container status",
    ]


def test_app_deploy_remote_step_sequence_for_down(monkeypatch, repo_fixture, app_factory):
    app_factory("demo")
    output = []

    monkeypatch.setattr(app_deploy, "_sync_app_dir", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        app_deploy,
        "_run_remote",
        lambda *args, **kwargs: types.SimpleNamespace(returncode=0, stdout="ok", stderr=""),
    )
    monkeypatch.setattr(app_deploy.remote, "ssh_host", lambda value=None: value or "1.2.3.4")
    monkeypatch.setattr(app_deploy.remote, "ssh_user", lambda value=None: value or "root")
    monkeypatch.setattr(app_deploy.remote, "resolve_secret_path", lambda value=None: repo_fixture / ".secrets" / "ssh" / "default.pem")
    monkeypatch.setattr(app_deploy.remote, "deploy_root", lambda value=None: value or "/websoft9/library/apps")
    (repo_fixture / ".secrets" / "ssh").mkdir(parents=True, exist_ok=True)
    (repo_fixture / ".secrets" / "ssh" / "default.pem").write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    payload = app_deploy.deploy("demo", target="remote", progress=output.append, down=True)

    assert payload["target"] == "remote"
    assert output == [
        "[1/4] syncing deploy package",
        "[2/4] validating compose config",
        "[3/4] stopping application",
        "[4/4] showing container status",
    ]


def test_app_deploy_local_version_uses_patched_env(monkeypatch, repo_fixture, app_factory):
    app_factory("demo", env="W9_VERSION='6.9'\nW9_ID=demo\n")
    captured_env = {}

    def fake_run(command, *, progress=None, verbose=False):
        if "--env-file" in command:
            index = command.index("--env-file")
            captured_env["path"] = command[index + 1]
            captured_env["text"] = Path(command[index + 1]).read_text(encoding="utf-8")
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(app_deploy, "_run", fake_run)

    payload = app_deploy.deploy("demo", target="local", version="7.0")

    assert payload["version"] == "7.0"
    assert captured_env["text"] == "W9_VERSION='7.0'\nW9_ID=demo\n"
    assert not Path(captured_env["path"]).exists()


def test_app_down_cli_forwards_down_flag(monkeypatch):
    calls = {}

    def fake_deploy(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "target": "local", "action": "down -v"}

    monkeypatch.setattr(app_deploy, "deploy", fake_deploy)
    monkeypatch.setattr(typer, "echo", lambda message, err=False: None)

    main.app_down_command(
        app_name="demo",
        target=None,
        ssh_host=None,
        ssh_user=None,
        ssh_secret_path=None,
        deploy_root=None,
        progress=False,
        verbose=False,
        as_json=True,
    )

    assert calls["down"] is True
    assert calls["app_name"] == "demo"


def test_app_deploy_remote_version_patches_remote_env(monkeypatch, repo_fixture, app_factory):
    app_factory("demo")
    calls = []
    (repo_fixture / ".secrets" / "ssh").mkdir(parents=True, exist_ok=True)
    (repo_fixture / ".secrets" / "ssh" / "default.pem").write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    monkeypatch.setattr(app_deploy, "_sync_app_dir", lambda *args, **kwargs: None)
    monkeypatch.setattr(app_deploy.remote, "ssh_host", lambda value=None: value or "1.2.3.4")
    monkeypatch.setattr(app_deploy.remote, "ssh_user", lambda value=None: value or "root")
    monkeypatch.setattr(app_deploy.remote, "resolve_secret_path", lambda value=None: repo_fixture / ".secrets" / "ssh" / "default.pem")
    monkeypatch.setattr(app_deploy.remote, "deploy_root", lambda value=None: value or "/websoft9/library/apps")
    monkeypatch.setattr(
        app_deploy,
        "_run_remote",
        lambda *args, **kwargs: (calls.append(args[3]), types.SimpleNamespace(returncode=0, stdout="ok", stderr=""))[1],
    )

    payload = app_deploy.deploy("demo", target="remote", version="7.0")

    assert payload["version"] == "7.0"
    assert any("W9_VERSION='7.0'" in call for call in calls)
