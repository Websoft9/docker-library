from __future__ import annotations

import json
import types

import typer

from libs import app_build, main


def test_build_app_uses_only_build_services(repo_fixture, app_factory, monkeypatch):
    app_factory(
        "demo",
        compose=(
            "services:\n"
            "  web:\n"
            "    build: .\n"
            "    image: demo:1\n"
            "  jobs:\n"
            "    image: demo:1\n"
            "  db:\n"
            "    image: postgres:16\n"
        ),
    )
    calls = []
    monkeypatch.setattr(
        app_build,
        "_run_stream",
        lambda command, progress=None: (calls.append(command), types.SimpleNamespace(returncode=0, stdout="ok", stderr=""))[1],
    )

    payload = app_build.build_app("demo")

    assert payload["build_services"] == ["web"]
    assert payload["images"] == ["demo:1"]
    assert calls[0][-2:] == ["build", "web"]


def test_build_app_push_uses_dockerhub_credentials(repo_fixture, app_factory, monkeypatch):
    app_factory("demo", compose="services:\n  web:\n    build: .\n    image: demo:1\n")
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "dockerhub.env").write_text(
        "DOCKERHUB_USERNAME=user\nDOCKERHUB_TOKEN=token\n",
        encoding="utf-8",
    )
    pushes = []
    login = {}

    def fake_stream(command, progress=None):
        pushes.append(command)
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(app_build, "_run_stream", fake_stream)
    monkeypatch.setattr(app_build, "_docker_login", lambda registry, username, password, progress=None: login.update({"value": (registry, username, password)}))

    payload = app_build.build_app("demo", push=True)

    assert payload["pushed"] == ["demo:1"]
    assert login["value"] == (None, "user", "token")
    assert any(command[:2] == ["docker", "push"] for command in pushes)


def test_app_build_cli_contract(monkeypatch):
    calls = {}
    output = []

    def fake_build_app(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "push": kwargs["push"], "images": []}

    monkeypatch.setattr(app_build, "build_app", fake_build_app)
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    main.app_build_command(
        app_name="demo",
        push=True,
        registry=None,
        username=None,
        password=None,
        token=None,
        env_file=None,
        progress=False,
        as_json=True,
    )

    assert calls["app_name"] == "demo"
    assert calls["push"] is True
    assert output == [
        (json.dumps({"app": "demo", "push": True, "images": []}, indent=2, ensure_ascii=False), False),
    ]
