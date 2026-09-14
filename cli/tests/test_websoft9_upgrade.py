from __future__ import annotations

import json
import types
from pathlib import Path

import typer

from libs import main, websoft9_upgrade


def _ok(stdout: str = "ok"):
    return types.SimpleNamespace(returncode=0, stdout=stdout, stderr="")


def test_websoft9_upgrade_cli_contract_progress_to_stderr(monkeypatch):
    output = []

    def fake_upgrade(**kwargs):
        assert callable(kwargs["progress"])
        assert kwargs["verbose"] is False
        assert kwargs["tag"] == "dev"
        kwargs["progress"]("[1/5] resolving compose project")
        return {"container": "websoft9", "target": "remote", "tag": "dev", "action": "upgrade"}

    monkeypatch.setattr(websoft9_upgrade, "upgrade", fake_upgrade)
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    main.websoft9_upgrade_command(
        container=None,
        tag="dev",
        tag_var="IMAGE_TAG",
        compose_dir=None,
        target=None,
        ssh_host=None,
        ssh_user=None,
        ssh_secret_path=None,
        progress=True,
        verbose=False,
        as_json=True,
    )

    assert output == [
        ("[1/5] resolving compose project", True),
        (
            json.dumps(
                {"container": "websoft9", "target": "remote", "tag": "dev", "action": "upgrade"},
                indent=2,
                ensure_ascii=False,
            ),
            False,
        ),
    ]


def test_upgrade_local_updates_env_and_runs_compose(monkeypatch, tmp_path: Path):
    project = tmp_path / "websoft9"
    project.mkdir()
    (project / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
    (project / ".env").write_text("IMAGE_REPO=websoft9dev/websoft9\nIMAGE_TAG=2.4-dev\n", encoding="utf-8")

    calls = []

    def fake_run(command, *, progress=None, verbose=False):
        calls.append(command)
        return _ok()

    monkeypatch.setattr(websoft9_upgrade, "_run", fake_run)

    payload = websoft9_upgrade.upgrade(compose_dir=str(project), target="local")

    assert payload["target"] == "local"
    assert payload["container"] == "websoft9"
    assert payload["tag"] == "dev"
    assert payload["previous_tag"] == "2.4-dev"
    assert payload["compose_file"] == str(project / "docker-compose.yml")
    assert (project / ".env").read_text(encoding="utf-8") == "IMAGE_REPO=websoft9dev/websoft9\nIMAGE_TAG=dev\n"

    pull = ["docker", "compose", "-f", str(project / "docker-compose.yml"), "--env-file", str(project / ".env"), "pull"]
    up = pull[:-1] + ["up", "-d"]
    ps = pull[:-1] + ["ps"]
    assert pull in calls
    assert up in calls
    assert ps in calls


def test_upgrade_local_appends_tag_var_when_missing(monkeypatch, tmp_path: Path):
    project = tmp_path / "websoft9"
    project.mkdir()
    (project / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
    (project / ".env").write_text("IMAGE_REPO=websoft9dev/websoft9\n", encoding="utf-8")

    monkeypatch.setattr(websoft9_upgrade, "_run", lambda *args, **kwargs: _ok())

    payload = websoft9_upgrade.upgrade(compose_dir=str(project), target="local")

    assert payload["previous_tag"] is None
    assert (project / ".env").read_text(encoding="utf-8") == "IMAGE_REPO=websoft9dev/websoft9\nIMAGE_TAG=dev\n"


def test_upgrade_remote_discovers_project_and_updates_tag(monkeypatch, tmp_path: Path):
    secret = tmp_path / ".secrets" / "ssh" / "default.pem"
    secret.parent.mkdir(parents=True)
    secret.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    monkeypatch.setattr(websoft9_upgrade.remote, "ssh_host", lambda value=None: value or "1.2.3.4")
    monkeypatch.setattr(websoft9_upgrade.remote, "ssh_user", lambda value=None: value or "root")
    monkeypatch.setattr(websoft9_upgrade.remote, "resolve_secret_path", lambda value=None: secret)
    monkeypatch.setattr(websoft9_upgrade.remote, "appstore_container", lambda value=None: value or "websoft9")
    monkeypatch.setattr(websoft9_upgrade.remote, "ssh_base", lambda host, user, path: ["ssh", f"{user}@{host}"])

    calls = []

    def fake_run(command, *, progress=None, verbose=False):
        calls.append(command)
        joined = " ".join(command)
        if "project.working_dir" in joined:
            return _ok("/opt/websoft9")
        if "project.config_files" in joined:
            return _ok("/opt/websoft9/docker-compose.yml")
        if command[:2] == ["ssh", "root@1.2.3.4"] and "cat /opt/websoft9/.env" in joined:
            return _ok("IMAGE_TAG=2.4-dev\n")
        return _ok()

    monkeypatch.setattr(websoft9_upgrade, "_run", fake_run)

    payload = websoft9_upgrade.upgrade(target="remote")

    assert payload["target"] == "remote"
    assert payload["host"] == "1.2.3.4"
    assert payload["project_dir"] == "/opt/websoft9"
    assert payload["compose_file"] == "/opt/websoft9/docker-compose.yml"
    assert payload["env_file"] == "/opt/websoft9/.env"
    assert payload["previous_tag"] == "2.4-dev"

    assert any("project.working_dir" in " ".join(call) for call in calls)
    assert any("project.config_files" in " ".join(call) for call in calls)
    assert any("base64 -d > /opt/websoft9/.env" in " ".join(call) for call in calls)
    assert any(
        "docker compose -f /opt/websoft9/docker-compose.yml --env-file /opt/websoft9/.env pull" in " ".join(call)
        for call in calls
    )


def test_upgrade_missing_container_raises_file_not_found(monkeypatch):
    monkeypatch.setattr(websoft9_upgrade.remote, "default_target", lambda: "local")
    monkeypatch.setattr(websoft9_upgrade.remote, "appstore_container", lambda value=None: value or "websoft9")
    monkeypatch.setattr(
        websoft9_upgrade,
        "_run",
        lambda *args, **kwargs: types.SimpleNamespace(returncode=1, stdout="", stderr="No such container: websoft9"),
    )

    try:
        websoft9_upgrade.upgrade(target="local")
    except FileNotFoundError as error:
        assert "No such container" in str(error)
    else:
        raise AssertionError("expected FileNotFoundError for missing container")


def test_upgrade_rejects_invalid_tag_and_var():
    for kwargs in ({"tag": "bad tag"}, {"tag_var": "1BAD"}):
        try:
            websoft9_upgrade.upgrade(target="local", **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {kwargs}")


def test_upgrade_rejects_invalid_target():
    try:
        websoft9_upgrade.upgrade(target="cloud")
    except ValueError as error:
        assert "invalid target" in str(error)
    else:
        raise AssertionError("expected ValueError for invalid target")
