from __future__ import annotations

import json
import types

import pytest
import typer

from libs import app_build, main


@pytest.fixture(autouse=True)
def _no_real_binfmt(monkeypatch):
    monkeypatch.setattr(app_build, "_ensure_binfmt_local", lambda archs, progress=None: None)
    monkeypatch.setattr(app_build, "_ensure_binfmt_remote", lambda host, user, secret_path, archs, progress=None: None)


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
    assert payload["source_image"] is None


def test_build_plan_promote_uses_dev_latest_source(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\nLABEL org.opencontainers.image.version="${DEMO_VERSION}"\n',
        encoding="utf-8",
    )

    payload = app_build.build_plan("demo", channel="promote")
    assert payload["channel"] == "promote"
    assert payload["source_image"] == "demo-repo:dev-latest"
    assert payload["tags"] == ["demo-repo:latest", "demo-repo:v1", "demo-repo:v1.2", "demo-repo:v1.2.3"]
    assert payload["primary_image"] == "demo-repo:dev-latest"


def test_build_plan_promote_binds_source_sha(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\nLABEL org.opencontainers.image.version="${DEMO_VERSION}"\n',
        encoding="utf-8",
    )

    payload = app_build.build_plan("demo", channel="promote", source_sha="9f3c1a2b4d5e6f708192a3b4c5d6e7f8091a2b3c")

    assert payload["source_image"] == "demo-repo:dev-9f3c1a2"
    assert payload["primary_image"] == "demo-repo:dev-9f3c1a2"


def test_build_plan_promote_accepts_dev_prefixed_source_sha(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\nLABEL org.opencontainers.image.version="${DEMO_VERSION}"\n',
        encoding="utf-8",
    )

    payload = app_build.build_plan("demo", channel="promote", source_sha="dev-9f3c1a2b4d5e6f708192a3b4c5d6e7f8091a2b3c")

    assert payload["source_image"] == "demo-repo:dev-9f3c1a2"


def test_build_plan_promote_rejects_invalid_source_sha(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\nLABEL org.opencontainers.image.version="${DEMO_VERSION}"\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        app_build.build_plan("demo", channel="promote", source_sha="not-a-sha")


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


def test_build_plan_namespaces_bare_repo_with_org(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\n',
        encoding="utf-8",
    )

    payload = app_build.build_plan("demo", channel="stable", org="websoft9dev")

    assert payload["org"] == "websoft9dev"
    assert payload["w9_repo"] == "websoft9dev/demo-repo"
    assert payload["tags"] == [
        "websoft9dev/demo-repo:latest",
        "websoft9dev/demo-repo:v1",
        "websoft9dev/demo-repo:v1.2",
        "websoft9dev/demo-repo:v1.2.3",
    ]


def test_build_plan_keeps_namespaced_repo_with_org(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: websoft9dev/demo:${W9_VERSION}\n",
        env="W9_REPO=websoft9dev/demo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\n',
        encoding="utf-8",
    )

    payload = app_build.build_plan("demo", channel="stable", org="other-org")

    assert payload["w9_repo"] == "websoft9dev/demo"
    assert payload["tags"][0] == "websoft9dev/demo:latest"


def test_build_plan_reads_org_from_dockerhub_env(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\n',
        encoding="utf-8",
    )
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "dockerhub.env").write_text(
        "DOCKERHUB_USERNAME=user\nDOCKERHUB_TOKEN=token\nDOCKERHUB_ORG=websoft9dev\n",
        encoding="utf-8",
    )

    payload = app_build.build_plan("demo", channel="stable")

    assert payload["org"] == "websoft9dev"
    assert payload["w9_repo"] == "websoft9dev/demo-repo"


def test_build_app_without_push_keeps_bare_repo(repo_fixture, app_factory, monkeypatch):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\n',
        encoding="utf-8",
    )
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "dockerhub.env").write_text(
        "DOCKERHUB_USERNAME=user\nDOCKERHUB_TOKEN=token\nDOCKERHUB_ORG=websoft9dev\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        app_build,
        "_run_stream",
        lambda command, progress=None: types.SimpleNamespace(returncode=0, stdout="ok", stderr=""),
    )

    payload = app_build.build_app("demo")

    assert payload["images"] == ["demo-repo:v1.2.3"]
    assert payload["org"] is None


def test_build_app_push_namespaces_bare_repo_with_org(repo_fixture, app_factory, monkeypatch):
    app_path = app_factory(
        "demo",
        compose="services:\n  web:\n    image: demo-repo:${W9_VERSION}\n",
        env="W9_REPO=demo-repo\nW9_VERSION=v1.2.3\n",
    )
    (app_path / "Dockerfile").write_text(
        'ARG DEMO_VERSION=v1.2.3\nFROM alpine\n',
        encoding="utf-8",
    )
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "dockerhub.env").write_text(
        "DOCKERHUB_USERNAME=user\nDOCKERHUB_TOKEN=token\nDOCKERHUB_ORG=websoft9dev\n",
        encoding="utf-8",
    )
    calls = []
    login = {}

    def fake_stream(command, progress=None):
        calls.append(command)
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(app_build, "_run_stream", fake_stream)
    monkeypatch.setattr(app_build, "_docker_login", lambda registry, username, password, progress=None: login.update({"value": (registry, username, password)}))

    payload = app_build.build_app("demo", push=True, confirm_stable=True)

    assert payload["org"] == "websoft9dev"
    assert payload["images"] == ["websoft9dev/demo-repo:v1.2.3"]
    assert payload["pushed"] == ["websoft9dev/demo-repo:v1.2.3"]
    assert login["value"] == (None, "user", "token")
    assert ["docker", "push", "websoft9dev/demo-repo:v1.2.3"] in calls


def _dockerfile_app(app_factory, repo="demo-repo", version="v1.2.3"):
    app_path = app_factory(
        "demo",
        compose=f"services:\n  web:\n    image: {repo}:${{W9_VERSION}}\n",
        env=f"W9_REPO={repo}\nW9_VERSION={version}\n",
    )
    (app_path / "Dockerfile").write_text(
        f'ARG DEMO_VERSION={version}\nFROM alpine\n',
        encoding="utf-8",
    )
    return app_path


def _write_dockerhub_env(repo_fixture, org=None):
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    body = "DOCKERHUB_USERNAME=user\nDOCKERHUB_TOKEN=token\n"
    if org:
        body += f"DOCKERHUB_ORG={org}\n"
    (repo_fixture / ".secrets" / "dockerhub.env").write_text(body, encoding="utf-8")


def test_build_app_default_platform_is_host_native(repo_fixture, app_factory, monkeypatch):
    _dockerfile_app(app_factory)
    calls = []
    monkeypatch.setattr(
        app_build,
        "_run_stream",
        lambda command, progress=None: (calls.append(command), types.SimpleNamespace(returncode=0, stdout="ok", stderr=""))[1],
    )

    payload = app_build.build_app("demo")

    assert payload["platform"] == "host"
    assert calls[0][:2] == ["docker", "build"]
    assert "--platform" not in calls[0]


def test_build_app_platform_amd64_adds_flag(repo_fixture, app_factory, monkeypatch):
    _dockerfile_app(app_factory)
    calls = []
    monkeypatch.setattr(
        app_build,
        "_run_stream",
        lambda command, progress=None: (calls.append(command), types.SimpleNamespace(returncode=0, stdout="ok", stderr=""))[1],
    )

    payload = app_build.build_app("demo", platform="amd64")

    assert payload["platform"] == "amd64"
    assert calls[0][:2] == ["docker", "build"]
    assert "linux/amd64" in calls[0]


def test_build_app_platform_arm64_uses_single_platform_build(repo_fixture, app_factory, monkeypatch):
    _dockerfile_app(app_factory)
    calls = []
    monkeypatch.setattr(
        app_build,
        "_run_stream",
        lambda command, progress=None: (calls.append(command), types.SimpleNamespace(returncode=0, stdout="ok", stderr=""))[1],
    )

    payload = app_build.build_app("demo", platform="arm64")

    assert payload["platform"] == "arm64"
    assert calls[0][:2] == ["docker", "build"]
    assert "linux/arm64" in calls[0]


def test_build_app_platform_both_requires_push(repo_fixture, app_factory):
    _dockerfile_app(app_factory)

    try:
        app_build.build_app("demo", platform="both")
    except ValueError as error:
        assert "requires --push" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_build_app_platform_both_uses_buildx_push(repo_fixture, app_factory, monkeypatch):
    _dockerfile_app(app_factory)
    _write_dockerhub_env(repo_fixture)
    calls = []
    login = {}
    installed = {}

    def fake_stream(command, progress=None):
        calls.append(command)
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(app_build, "_run_stream", fake_stream)
    monkeypatch.setattr(app_build, "_docker_login", lambda registry, username, password, progress=None: login.update({"value": (registry, username, password)}))
    monkeypatch.setattr(app_build, "_local_arch", lambda: "amd64")
    monkeypatch.setattr(app_build, "_ensure_binfmt_local", lambda archs, progress=None: installed.update({"archs": archs}))

    payload = app_build.build_app("demo", push=True, confirm_stable=True, platform="both")

    assert payload["platform"] == "both"
    assert payload["pushed"] == ["demo-repo:v1.2.3"]
    assert installed["archs"] == ["arm64"]
    buildx = [command for command in calls if command[:3] == ["docker", "buildx", "build"]]
    assert len(buildx) == 1
    assert "linux/amd64,linux/arm64" in buildx[0]
    assert "--push" in buildx[0]
    assert login["value"] == (None, "user", "token")


def test_build_app_no_binfmt_skips_install(repo_fixture, app_factory, monkeypatch):
    _dockerfile_app(app_factory)
    _write_dockerhub_env(repo_fixture)
    installed = []
    monkeypatch.setattr(
        app_build,
        "_run_stream",
        lambda command, progress=None: types.SimpleNamespace(returncode=0, stdout="ok", stderr=""),
    )
    monkeypatch.setattr(app_build, "_docker_login", lambda *args, **kwargs: None)
    monkeypatch.setattr(app_build, "_local_arch", lambda: "amd64")
    monkeypatch.setattr(app_build, "_ensure_binfmt_local", lambda archs, progress=None: installed.append(archs))

    app_build.build_app("demo", push=True, confirm_stable=True, platform="both", binfmt=False)

    assert installed == []


def test_build_app_platform_arm64_same_host_skips_binfmt(repo_fixture, app_factory, monkeypatch):
    _dockerfile_app(app_factory)
    installed = []
    monkeypatch.setattr(
        app_build,
        "_run_stream",
        lambda command, progress=None: types.SimpleNamespace(returncode=0, stdout="ok", stderr=""),
    )
    monkeypatch.setattr(app_build, "_local_arch", lambda: "arm64")
    monkeypatch.setattr(app_build, "_ensure_binfmt_local", lambda archs, progress=None: installed.append(archs))

    app_build.build_app("demo", platform="arm64")

    assert installed == [[]]


def test_required_binfmt_archs_only_returns_foreign():
    assert app_build._required_binfmt_archs("amd64", "amd64") == []
    assert app_build._required_binfmt_archs("arm64", "amd64") == ["arm64"]
    assert app_build._required_binfmt_archs("both", "amd64") == ["arm64"]
    assert app_build._required_binfmt_archs("both", "arm64") == ["amd64"]
    assert app_build._required_binfmt_archs(None, "amd64") == []


def test_buildx_error_adds_builder_hint():
    assert "docker buildx create" in app_build._buildx_error(
        "multiple platforms feature is currently not supported for docker driver"
    )
    assert app_build._buildx_error("boom") == "boom"


def test_build_app_platform_both_remote_uses_buildx_push(repo_fixture, app_factory, monkeypatch):
    _dockerfile_app(app_factory)
    _write_dockerhub_env(repo_fixture)
    (repo_fixture / ".secrets" / "ssh").mkdir(parents=True, exist_ok=True)
    (repo_fixture / ".secrets" / "ssh" / "default.pem").write_text(
        "-----BEGIN OPENSSH PRIVATE KEY-----\nkey\n", encoding="utf-8"
    )
    scripts = []
    login = {}
    installed = {}
    monkeypatch.setattr(
        app_build.remote,
        "stream_ssh",
        lambda host, user, secret_path, script, on_line=None: (scripts.append(script), types.SimpleNamespace(returncode=0, stdout="ok", stderr=""))[1],
    )
    monkeypatch.setattr(app_build.remote, "run_command", lambda command: types.SimpleNamespace(returncode=0, stdout="ok", stderr=""))
    monkeypatch.setattr(app_build, "_docker_login_remote", lambda host, user, secret_path, registry, username, password, progress=None: login.update({"value": (username, password)}))
    monkeypatch.setattr(app_build, "_remote_arch", lambda host, user, secret_path: "amd64")
    monkeypatch.setattr(app_build, "_ensure_binfmt_remote", lambda host, user, secret_path, archs, progress=None: installed.update({"archs": archs}))

    payload = app_build.build_app(
        "demo",
        push=True,
        confirm_stable=True,
        platform="both",
        target="remote",
        ssh_host="1.2.3.4",
        skip_sync=True,
    )

    assert payload["platform"] == "both"
    assert payload["pushed"] == ["demo-repo:v1.2.3"]
    assert installed["archs"] == ["arm64"]
    assert any("docker buildx build" in script and "linux/amd64,linux/arm64" in script and "--push" in script for script in scripts)
    assert login["value"] == ("user", "token")


def test_build_app_platform_rejects_compose_services(repo_fixture, app_factory):
    app_factory("demo", compose="services:\n  web:\n    build: .\n    image: demo:1\n")

    try:
        app_build.build_app("demo", platform="both")
    except ValueError as error:
        assert "compose build services" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_build_app_platform_rejects_unknown_value(repo_fixture, app_factory):
    app_factory("demo", compose="services:\n  web:\n    build: .\n    image: demo:1\n")

    try:
        app_build.build_app("demo", platform="riscv64")
    except ValueError as error:
        assert "unsupported platform" in str(error)
    else:
        raise AssertionError("expected ValueError")


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
        org=None,
        platform="amd64",
        binfmt=True,
        env_file=None,
        progress=False,
        as_json=True,
    )

    assert calls["app_name"] == "demo"
    assert calls["push"] is True
    assert calls["confirm_stable"] is False
    assert calls["platform"] == "amd64"
    assert calls["binfmt"] is True
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

    main.app_build_plan_command(app_name="demo", channel="dev", git_sha="1234567890", source_sha=None, org=None, env_file=None, as_json=True)

    assert calls == {"app_name": "demo", "channel": "dev", "git_sha": "1234567890", "source_sha": None, "org": None, "env_file": None}
    assert output == [
        (json.dumps({"app": "demo", "channel": "dev", "tags": ["demo:dev-1234567"]}, indent=2, ensure_ascii=False), False),
    ]
