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
        kwargs["progress"]("[1/6] syncing deploy package")
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
        ("[1/6] syncing deploy package", True),
        (json.dumps({"app": "demo", "target": "remote", "action": "up -d"}, indent=2, ensure_ascii=False), False),
    ]


def test_app_deploy_local_step_sequence(monkeypatch, repo_fixture, app_factory):
    app_factory("demo", compose="services:\n  demo:\n    build: .\n")
    output = []

    def fake_run(command, *, progress=None, verbose=False):
        if progress and verbose:
            progress(f"$ {' '.join(command)}")
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    def fake_build(app_name, mode, *, compose_env_file=None, progress=None, **kwargs):
        if progress:
            progress("build line")

    monkeypatch.setattr(app_deploy, "_run", fake_run)
    monkeypatch.setattr(app_deploy, "_build_via_app_build", fake_build)

    payload = app_deploy.deploy("demo", target="local", progress=output.append, verbose=False)

    assert payload["target"] == "local"
    assert output == [
        "[1/6] ensuring shared network",
        "[2/6] validating compose config",
        "[3/6] pulling images",
        "[4/6] building local images",
        "build line",
        "[5/6] starting application",
        "[6/6] showing container status",
    ]


def test_app_deploy_remote_step_sequence_for_down(monkeypatch, repo_fixture, app_factory):
    app_factory("demo", compose="services:\n  demo:\n    build: .\n")
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
    app_factory("demo", compose="services:\n  web:\n    build: .\n    image: demo:1\n  jobs:\n    image: demo:1\n  db:\n    image: postgres:16\n")
    calls = []
    build_calls = []
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
    monkeypatch.setattr(
        app_deploy,
        "_build_via_app_build",
        lambda app_name, mode, **kwargs: (build_calls.append((app_name, mode, kwargs)), None)[1],
    )

    payload = app_deploy.deploy("demo", target="remote", version="7.0")

    assert payload["version"] == "7.0"
    assert any("W9_VERSION='7.0'" in call for call in calls)
    assert any("pull --policy always db" in call for call in calls)
    assert not any("pull jobs" in call for call in calls)
    assert build_calls == [("demo", "remote", {"ssh_host": "1.2.3.4", "ssh_user": "root", "ssh_secret_path": str(repo_fixture / ".secrets" / "ssh" / "default.pem"), "deploy_root": "/websoft9/library/apps", "progress": None})]


def test_app_deploy_skips_build_when_compose_has_no_build(monkeypatch, repo_fixture, app_factory):
    app_factory("demo", compose="services:\n  demo:\n    image: nginx:latest\n")
    output = []
    calls = []

    def fake_run(command, *, progress=None, verbose=False):
        calls.append(command)
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
    assert not any(command[:4] == ["docker", "compose", "--progress", "plain"] for command in calls)


def test_app_deploy_never_pull_uses_existing_images(monkeypatch, repo_fixture, app_factory):
    app_factory("demo", compose="services:\n  demo:\n    image: nginx:latest\n")
    calls = []

    def fake_run(command, *, progress=None, verbose=False):
        calls.append(command)
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(app_deploy, "_run", fake_run)

    payload = app_deploy.deploy("demo", target="local", pull_policy="never")

    assert payload["pull_policy"] == "never"
    assert not any("pull" in command[-3:] and "--pull" not in command[-3:] for command in calls)
    assert any(command[-4:] == ["up", "-d", "--pull", "never"] for command in calls)


def test_compose_published_ports_resolves_env_reference(repo_fixture, app_factory):
    app = app_factory(
        "demo",
        env="W9_HTTP_PORT_SET=9011\n",
        compose="services:\n  demo:\n    image: demo:1\n    ports:\n      - \"${W9_HTTP_PORT_SET}:80\"\n",
    )

    rows = app_deploy._compose_published_ports(app, app_deploy._env_map(app / ".env"))

    assert rows == [{"service": "demo", "env": "W9_HTTP_PORT_SET", "published": 9011, "target": 80}]


def test_parse_occupied_ports_excludes_own_containers():
    text = "drupal|0.0.0.0:9001->80/tcp\nwordpress|0.0.0.0:9002->80/tcp\n"

    assert app_deploy._parse_occupied_ports(text, ["drupal"]) == {9002}


def test_pick_free_port_skips_occupied_ports():
    assert app_deploy._pick_free_port({9001, 9002}, 9001) == 9003


def test_app_deploy_local_auto_port_overrides_temp_env(monkeypatch, repo_fixture, app_factory):
    app_factory(
        "demo",
        env="W9_ID=demo\nW9_VERSION='1.0'\nW9_HTTP_PORT_SET=9001\n",
        compose="services:\n  demo:\n    image: demo:1\n    ports:\n      - \"${W9_HTTP_PORT_SET}:80\"\n",
    )
    captured = {}

    def fake_run(command, *, progress=None, verbose=False):
        if "--env-file" in command:
            path = Path(command[command.index("--env-file") + 1])
            captured["text"] = path.read_text(encoding="utf-8")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(app_deploy, "_run", fake_run)
    monkeypatch.setattr(app_deploy, "_occupied_ports_local", lambda prefixes=None: {9001})

    payload = app_deploy.deploy("demo", target="local")

    assert payload["port_overrides"] == {"W9_HTTP_PORT_SET": "9002"}
    assert payload["base_url"] == "http://localhost:9002"
    assert "W9_HTTP_PORT_SET=9002" in captured["text"]
