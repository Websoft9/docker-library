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


def test_build_plan_uses_root_dockerfile_and_env_version(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\nLABEL org.opencontainers.image.version="${DEMO_VERSION}"\n',
        encoding="utf-8",
    )

    payload = app_build.build_plan("demo", channel="stable")

    assert payload["version_arg"] == "DEMO_VERSION"
    assert payload["w9_version"] == "v1.2.3"
    assert payload["primary_image"] == "demo-repo:latest"
    assert payload["tags"] == ["demo-repo:latest", "demo-repo:v1", "demo-repo:v1.2", "demo-repo:v1.2.3"]


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

    payload = app_build.build_app("demo", push=True, confirm_stable=True)

    assert payload["pushed"] == ["demo:1"]
    assert login["value"] == (None, "user", "token")
    assert any(command[:2] == ["docker", "push"] for command in pushes)


def test_build_app_push_requires_confirm_stable_outside_ci(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\nLABEL org.opencontainers.image.version="${DEMO_VERSION}"\n',
        encoding="utf-8",
    )

    try:
        app_build.build_app("demo", push=True)
    except ValueError as error:
        assert "confirm-stable" in str(error)
    else:
        raise AssertionError("expected ValueError")


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
        confirm_stable=False,
        target=None,
        ssh_host=None,
        ssh_user=None,
        ssh_secret_path=None,
        deploy_root=None,
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
    assert calls["confirm_stable"] is False
    assert output == [
        (json.dumps({"app": "demo", "push": True, "images": []}, indent=2, ensure_ascii=False), False),
    ]


def test_app_build_plan_cli_contract(monkeypatch):
    calls = {}
    output = []

    def fake_build_plan(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "channel": kwargs["channel"], "tags": ["demo:dev-1234567"]}

    monkeypatch.setattr(app_build, "build_plan", fake_build_plan)
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    main.app_build_plan_command(app_name="demo", channel="dev", git_sha="1234567890", as_json=True)

    assert calls == {"app_name": "demo", "channel": "dev", "git_sha": "1234567890"}
    assert output == [
        (json.dumps({"app": "demo", "channel": "dev", "tags": ["demo:dev-1234567"]}, indent=2, ensure_ascii=False), False),
    ]
