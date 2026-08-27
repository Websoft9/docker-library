from __future__ import annotations

import json
from pathlib import Path

import typer
from typer.testing import CliRunner

from libs import appstore_preview, main


runner = CliRunner()


def test_resolve_key_path_uses_default_and_relative_paths(repo_fixture):
    default = appstore_preview.resolve_secret_path(None)
    relative = appstore_preview.resolve_secret_path("custom.pem")

    assert default == repo_fixture / ".secrets" / "ssh" / "default.pem"
    assert relative == repo_fixture / ".secrets" / "ssh" / "custom.pem"


def test_distribution_for_app_reads_variables(repo_fixture, app_factory):
    app_factory(
        "demo",
        variables={
            "name": "demo",
            "release": True,
            "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
            "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
        },
    )

    assert appstore_preview.distribution_for_app("demo") == [{"key": "community", "value": ["1.0", "latest"]}]


def test_patch_product_entries_updates_only_target_app():
    before = [
        {"key": "demo", "distribution": [{"key": "community", "value": ["1.0"]}]},
        {"key": "other", "distribution": [{"key": "community", "value": ["9.9"]}]},
    ]

    old_distribution, new_distribution, updated, created = appstore_preview.patch_product_entries(
        before,
        "demo",
        [{"key": "community", "value": ["2.0", "latest"]}],
    )

    assert old_distribution == [{"key": "community", "value": ["1.0"]}]
    assert new_distribution == [{"key": "community", "value": ["2.0", "latest"]}]
    assert created is False
    assert updated[0]["distribution"] == [{"key": "community", "value": ["2.0", "latest"]}]
    assert updated[1]["distribution"] == [{"key": "community", "value": ["9.9"]}]


def test_patch_product_entries_creates_missing_node():
    before = [{"key": "other", "distribution": [{"key": "community", "value": ["9.9"]}]}]

    old_distribution, new_distribution, updated, created = appstore_preview.patch_product_entries(
        before,
        "newapp",
        [{"key": "community", "value": ["1.0"]}],
    )

    assert old_distribution is None
    assert new_distribution == [{"key": "community", "value": ["1.0"]}]
    assert created is True
    assert updated[-1] == {"key": "newapp", "distribution": [{"key": "community", "value": ["1.0"]}]}


def test_appstore_preview_cli_contract(monkeypatch):
    monkeypatch.setattr(
        appstore_preview,
        "prepare_preview",
        lambda **kwargs: {
            "app": kwargs["app_name"],
            "host": kwargs["host"],
            "container": kwargs["container"],
            "json_dir": kwargs["json_dir"],
            "deploy_dir": "/websoft9/library/apps",
            "app_target": "/websoft9/library/apps/demo",
            "created_entry": False,
            "backup_dir": "/tmp/backup-demo",
            "distribution_before": [{"key": "community", "value": ["1.0"]}],
            "distribution_after": [{"key": "community", "value": ["2.0", "latest"]}],
            "rollback": ["cmd1", "cmd2", "cmd3"],
        },
    )

    result = runner.invoke(
        main.app,
        [
            "appstore-sync",
            "--app",
            "demo",
            "--ssh-host",
            "1.2.3.4",
            "--container",
            "websoft9",
            "--json-dir",
            "/websoft9/media/json",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["app"] == "demo"
    assert payload["deploy_dir"] == "/websoft9/library/apps"
    assert payload["distribution_after"][0]["value"] == ["2.0", "latest"]


def test_appstore_sync_cli_contract_progress_to_stderr(monkeypatch):
    output = []

    def fake_prepare_preview(**kwargs):
        assert callable(kwargs["progress"])
        assert kwargs["verbose"] is False
        kwargs["progress"]("[1/6] syncing app directory")
        return {"app": kwargs["app_name"], "deploy_dir": "/websoft9/library/apps"}

    monkeypatch.setattr(appstore_preview, "prepare_preview", fake_prepare_preview)
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    main.appstore_sync_command(
        app_name="demo",
        ssh_host="1.2.3.4",
        ssh_user=None,
        ssh_secret_path=None,
        container="websoft9",
        json_dir="/websoft9/media/json",
        progress=True,
        verbose=False,
        as_json=True,
    )

    assert output == [
        ("[1/6] syncing app directory", True),
        (json.dumps({"app": "demo", "deploy_dir": "/websoft9/library/apps"}, indent=2, ensure_ascii=False), False),
    ]


def test_sync_app_dir_sends_app_folder_without_extra_apps_prefix(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    calls = []
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    def fake_run(command, check, cwd=None, text=True, capture_output=False):
        calls.append(command)
        class Result:
            stdout = ""
            stderr = ""
            returncode = 0
        return Result()

    monkeypatch.setattr(appstore_preview.subprocess, "run", fake_run)

    appstore_preview._sync_app_dir(
        app_name="demo",
        host="1.2.3.4",
        user="root",
        secret_path=secret_path,
        container="websoft9",
        deploy_dir="/websoft9/library/apps",
        backup_dir="/tmp/backup-demo",
    )

    assert "tar czf - -C apps demo" in calls[0][2]
    assert "docker exec -i websoft9 tar xzf - -C /websoft9/library/apps" in calls[0][2]


def test_appstore_deploy_stub_not_implemented():
    result = runner.invoke(
        main.app,
        [
            "appstore-deploy",
            "--app",
            "demo",
            "--ssh-host",
            "1.2.3.4",
        ],
    )

    assert result.exit_code == 1
    assert "not implemented" in result.output


def test_appstore_deploy_stub_accepts_shared_options():
    result = runner.invoke(
        main.app,
        [
            "appstore-deploy",
            "--app",
            "demo",
            "--ssh-host",
            "1.2.3.4",
            "--progress",
            "--verbose",
        ],
    )

    assert result.exit_code == 1
    assert "[1/1] appstore-deploy is not implemented yet" in result.output
