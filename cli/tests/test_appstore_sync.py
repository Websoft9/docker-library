from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from libs import appstore_sync, main


runner = CliRunner()


def write_catalog_schema(repo_fixture):
    source = Path(__file__).resolve().parents[2] / "metadata" / "catalog.schema.json"
    target = repo_fixture / "metadata" / "catalog.schema.json"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def write_catalog_support(repo_fixture, app_name: str, payload: dict, taxonomy: dict | None = None):
    write_catalog_schema(repo_fixture)
    metadata_dir = repo_fixture / "metadata"
    (metadata_dir / "catalog").mkdir(exist_ok=True)
    (metadata_dir / "catalog" / f"{app_name}.json").write_text(json.dumps(payload) + "\n", encoding="utf-8")
    if taxonomy is None:
        taxonomy = {
            "version": 1,
            "source": "https://example.com/catalog_en.json",
            "locale": "en",
            "categories": [
                {
                    "key": "collaboration",
                    "title": "Collaboration & Office",
                    "position": 7,
                    "children": [{"key": "document", "title": "Document Collaboration", "position": 1}],
                }
            ],
        }
    (metadata_dir / "catalog-taxonomy.json").write_text(json.dumps(taxonomy) + "\n", encoding="utf-8")


def test_appstore_container_defaults_to_websoft9(repo_fixture):
    from libs import remote

    assert remote.appstore_container(None) == "websoft9"


def test_appstore_container_reads_from_remote_env(repo_fixture):
    from libs import remote

    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "remote.env").write_text("TARGET=remote\nCONTAINER=custom\n", encoding="utf-8")

    assert remote.appstore_container(None) == "custom"
    assert remote.appstore_container("explicit") == "explicit"


def test_resolve_key_path_uses_default_and_relative_paths(repo_fixture):
    default = appstore_sync.resolve_secret_path(None)
    relative = appstore_sync.resolve_secret_path("custom.pem")

    assert default == repo_fixture / ".secrets" / "ssh" / "default.pem"
    assert relative == repo_fixture / ".secrets" / "ssh" / "custom.pem"


def test_appstore_sync_cli_contract(monkeypatch):
    monkeypatch.setattr(
        appstore_sync,
        "prepare_preview",
        lambda **kwargs: {
            "app": kwargs["app_name"],
            "host": kwargs["host"],
            "container": kwargs["container"],
            "deploy_dir": "/websoft9/library/apps",
            "catalog_dir": "/websoft9/library/metadata/catalog",
            "app_target": "/websoft9/library/apps/demo",
            "catalog_source": "metadata/catalog/demo.json",
            "catalog_target": "/websoft9/library/metadata/catalog/demo.json",
            "backup_dir": "/tmp/backup-demo",
            "rollback": ["cmd1", "cmd2"],
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
            "--catalog-dir",
            "/websoft9/library/metadata/catalog",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["app"] == "demo"
    assert payload["deploy_dir"] == "/websoft9/library/apps"
    assert payload["catalog_target"] == "/websoft9/library/metadata/catalog/demo.json"


def test_appstore_sync_cli_contract_progress_to_stderr(monkeypatch):
    output = []

    def fake_prepare_preview(**kwargs):
        assert callable(kwargs["progress"])
        assert kwargs["verbose"] is False
        kwargs["progress"]("[1/2] syncing app directory")
        return {"app": kwargs["app_name"], "deploy_dir": "/websoft9/library/apps"}

    monkeypatch.setattr(appstore_sync, "prepare_preview", fake_prepare_preview)
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    main.appstore_sync_command(
        app_name="demo",
        ssh_host="1.2.3.4",
        ssh_user=None,
        ssh_secret_path=None,
        container="websoft9",
        catalog_dir="/websoft9/library/metadata/catalog",
        progress=True,
        verbose=False,
        as_json=True,
    )

    assert output == [
        ("[1/2] syncing app directory", True),
        (json.dumps({"app": "demo", "deploy_dir": "/websoft9/library/apps"}, indent=2, ensure_ascii=False), False),
    ]


def test_sync_app_dir_scp_to_staging_then_docker_cp(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    calls = []
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    def fake_run(command, *, progress=None, verbose=False):
        calls.append(command)
        return ""

    monkeypatch.setattr(appstore_sync, "_run", fake_run)

    appstore_sync._sync_app_dir(
        app_name="demo",
        host="1.2.3.4",
        user="root",
        secret_path=secret_path,
        container="websoft9",
        deploy_dir="/websoft9/library/apps",
        backup_dir="/tmp/backup-demo",
    )

    prepare = " ".join(calls[0])
    assert "rm -rf /tmp/websoft9-appstore-staging-demo && mkdir -p /tmp/websoft9-appstore-staging-demo" in prepare
    assert "mkdir -p /tmp/backup-demo" in prepare
    assert "docker exec websoft9 sh -c 'test -d /websoft9/library/apps/demo'" in prepare
    assert "docker exec websoft9 sh -c 'tar czf - -C /websoft9/library/apps demo' > /tmp/backup-demo/demo.tgz" in prepare

    scp_call = calls[1]
    assert scp_call[0] == "scp"
    assert any(arg.endswith("/apps/demo") for arg in scp_call)
    assert scp_call[-1] == "root@1.2.3.4:/tmp/websoft9-appstore-staging-demo/"

    apply_ssh = " ".join(calls[2])
    assert "docker exec websoft9 sh -c 'rm -rf /websoft9/library/apps/demo'" in apply_ssh
    assert "docker cp /tmp/websoft9-appstore-staging-demo/demo websoft9:/websoft9/library/apps" in apply_ssh
    assert "rm -rf /tmp/websoft9-appstore-staging-demo" in apply_ssh


def test_sync_catalog_file_scp_then_docker_cp(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    write_catalog_support(repo_fixture, "demo", {"trademark": "Demo", "summary": "Summary"})
    calls = []
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    def fake_run(command, *, progress=None, verbose=False):
        calls.append(command)
        return ""

    monkeypatch.setattr(appstore_sync, "_run", fake_run)

    catalog_rel = appstore_sync._sync_catalog_file(
        app_name="demo",
        host="1.2.3.4",
        user="root",
        secret_path=secret_path,
        container="websoft9",
        catalog_dir="/websoft9/library/metadata/catalog",
        backup_dir="/tmp/backup-demo",
    )

    assert catalog_rel == "metadata/catalog/demo.json"

    prepare = " ".join(calls[0])
    assert "mkdir -p /tmp/websoft9-appstore-staging-demo" in prepare
    assert "docker exec websoft9 sh -c 'test -f /websoft9/library/metadata/catalog/demo.json'" in prepare
    assert "docker cp websoft9:/websoft9/library/metadata/catalog/demo.json /tmp/backup-demo/catalog-demo.json.bak" in prepare

    scp_call = calls[1]
    assert scp_call[0] == "scp"
    assert any(arg.endswith("/metadata/catalog/demo.json") for arg in scp_call)
    assert scp_call[-1] == "root@1.2.3.4:/tmp/websoft9-appstore-staging-demo/"

    apply_ssh = " ".join(calls[2])
    assert "docker exec websoft9 sh -c 'mkdir -p /websoft9/library/metadata/catalog'" in apply_ssh
    assert "docker cp /tmp/websoft9-appstore-staging-demo/demo.json websoft9:/websoft9/library/metadata/catalog/demo.json" in apply_ssh
    assert "rm -rf /tmp/websoft9-appstore-staging-demo" in apply_ssh


def test_sync_catalog_file_missing_catalog_data_raises(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    write_catalog_schema(repo_fixture)
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    try:
        appstore_sync._sync_catalog_file(
            app_name="demo",
            host="1.2.3.4",
            user="root",
            secret_path=secret_path,
            container="websoft9",
            catalog_dir="/websoft9/library/metadata/catalog",
            backup_dir="/tmp/backup-demo",
        )
    except FileNotFoundError as error:
        assert "metadata/catalog/demo.json" in str(error)
    else:
        raise AssertionError("expected FileNotFoundError for missing catalog data")


def test_prepare_preview_missing_catalog_still_syncs_app_dir(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    write_catalog_schema(repo_fixture)
    calls = []
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    monkeypatch.setattr(appstore_sync, "_run", lambda *args, **kwargs: "")
    monkeypatch.setattr(appstore_sync, "_sync_app_dir", lambda *args, **kwargs: None)

    payload = appstore_sync.prepare_preview(
        app_name="demo",
        host="1.2.3.4",
        user="root",
        secret_path=".secrets/ssh/default.pem",
        container="websoft9",
    )

    assert payload["catalog_synced"] is False
    assert payload["catalog_source"] is None
    assert payload["app_target"] == "/websoft9/library/apps/demo"
    assert len(payload["rollback"]) == 3
    assert payload["database_types_synced"] is True
    assert payload["catalog_refreshed"] is True


def test_prepare_preview_with_catalog_syncs_both(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    write_catalog_support(repo_fixture, "demo", {"trademark": "Demo", "summary": "Summary"})
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")

    monkeypatch.setattr(appstore_sync, "_run", lambda *args, **kwargs: "")
    monkeypatch.setattr(appstore_sync, "_sync_app_dir", lambda *args, **kwargs: None)

    payload = appstore_sync.prepare_preview(
        app_name="demo",
        host="1.2.3.4",
        user="root",
        secret_path=".secrets/ssh/default.pem",
        container="websoft9",
    )

    assert payload["catalog_synced"] is True
    assert payload["catalog_source"] == "metadata/catalog/demo.json"
    assert payload["catalog_target"] == "/websoft9/library/metadata/catalog/demo.json"
    assert len(payload["rollback"]) == 4
    assert payload["database_types_target"] == "/websoft9/library/metadata/database-types.json"
    assert payload["secret_rules_target"] == "/websoft9/library/metadata/secret-rules.json"


@pytest.mark.parametrize("has_catalog", [False, True])
def test_prepare_preview_refreshes_once_after_all_copies(repo_fixture, app_factory, monkeypatch, has_catalog):
    app_factory("demo")
    if has_catalog:
        write_catalog_support(repo_fixture, "demo", {"trademark": "Demo", "summary": "Summary"})
    key = repo_fixture / "key.pem"
    key.write_text("test fixture", encoding="utf-8")
    calls = []
    progress = []
    monkeypatch.setattr(appstore_sync, "_run", lambda command, **kwargs: calls.append(command) or "")

    payload = appstore_sync.prepare_preview(
        "demo", host="1.2.3.4", secret_path=str(key), container="custom", progress=progress.append,
    )

    refresh_commands = [command for command in calls if "appstore reload --json" in command[-1]]
    assert len(refresh_commands) == 1
    assert refresh_commands[0] == calls[-1]
    assert calls[-1][-1] == "docker exec custom websoft9 appstore reload --json"
    assert any("docker cp" in command[-1] for command in calls[:-1])
    if has_catalog:
        assert "catalog/demo.json" in calls[-2][-1]
    total = 4 if has_catalog else 3
    assert progress[-1] == f"[{total}/{total}] refreshing app store catalogs"
    assert payload["catalog_refreshed"] is True
    secret_rollback = payload["rollback"][2]
    assert "secret-rules.json.bak" in secret_rollback
    assert "secret-rules.json.bak.missing" in secret_rollback
    assert "docker cp" in secret_rollback
    assert "docker exec custom rm -f /websoft9/library/metadata/secret-rules.json" in secret_rollback


def test_prepare_preview_refresh_failure_is_not_reported_as_success(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    key = repo_fixture / "key.pem"
    key.write_text("test fixture", encoding="utf-8")

    def fake_run(command, **kwargs):
        if "appstore reload --json" in command[-1]:
            raise RuntimeError("app store refresh failed")
        return ""

    monkeypatch.setattr(appstore_sync, "_run", fake_run)
    with pytest.raises(RuntimeError, match="app store refresh failed"):
        appstore_sync.prepare_preview("demo", host="1.2.3.4", secret_path=str(key))


def test_sync_dictionary_verifies_staged_bytes_before_replacing(repo_fixture, monkeypatch):
    calls = []
    (repo_fixture / "key.pem").write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")
    monkeypatch.setattr(appstore_sync, "_run", lambda command, **kwargs: calls.append(command) or "")
    digest = appstore_sync._sync_database_types(
        "demo", "1.2.3.4", "root", repo_fixture / "key.pem", "websoft9", "/tmp/backup-demo",
    )
    assert digest == hashlib.sha256((repo_fixture / "metadata" / "database-types.json").read_bytes()).hexdigest()
    assert "database-types.json.bak" in calls[0][-1]
    assert "database-types.json.bak.missing" in calls[0][-1]
    assert calls[1][0] == "scp"
    assert "sha256sum -c - && mv" in calls[2][-1]
    assert f".database-types-{digest}.tmp" in calls[2][-1]


def test_sync_missing_dictionary_does_not_mutate_remote(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    key = repo_fixture / "key.pem"
    key.write_text("test fixture")
    (repo_fixture / "metadata" / "database-types.json").unlink()
    calls = []
    monkeypatch.setattr(appstore_sync, "_run", lambda *args, **kwargs: calls.append(args))
    with pytest.raises(FileNotFoundError, match="database-types.json"):
        appstore_sync.prepare_preview("demo", host="1.2.3.4", secret_path=str(key))
    assert calls == []


def test_sync_invalid_dictionary_does_not_mutate_remote(repo_fixture, monkeypatch):
    (repo_fixture / "metadata" / "database-types.json").write_text('{"mysql": {}}', encoding="utf-8")
    calls = []
    monkeypatch.setattr(appstore_sync, "_run", lambda *args, **kwargs: calls.append(args))
    with pytest.raises(ValueError, match="Invalid shared database dictionary"):
        appstore_sync._sync_database_types("demo", "1.2.3.4", "root", repo_fixture / "key.pem", "websoft9", "/tmp/backup")
    assert calls == []


def test_sync_secret_rules_dictionary_validates_and_replaces(repo_fixture, monkeypatch):
    calls = []
    (repo_fixture / "key.pem").write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")
    monkeypatch.setattr(appstore_sync, "_run", lambda command, **kwargs: calls.append(command) or "")
    digest = appstore_sync._sync_secret_rules(
        "demo", "1.2.3.4", "root", repo_fixture / "key.pem", "websoft9", "/tmp/backup-demo",
    )
    assert digest == hashlib.sha256((repo_fixture / "metadata" / "secret-rules.json").read_bytes()).hexdigest()
    assert "secret-rules.json.bak" in calls[0][-1]
    assert "secret-rules.json.bak.missing" in calls[0][-1]
    assert "sha256sum -c - && mv" in calls[2][-1]
    assert f".secret-rules-{digest}.tmp" in calls[2][-1]

    calls.clear()
    (repo_fixture / "metadata" / "secret-rules.json").write_text('{"base64": {}}', encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid shared secret rules dictionary"):
        appstore_sync._sync_secret_rules("demo", "1.2.3.4", "root", repo_fixture / "key.pem", "websoft9", "/tmp/backup")
    assert calls == []


@pytest.mark.parametrize("missing", [False, True])
def test_prepare_preview_rejects_secret_dictionary_before_remote_writes(repo_fixture, app_factory, monkeypatch, missing):
    app_factory("demo")
    key = repo_fixture / "key.pem"
    key.write_text("test fixture", encoding="utf-8")
    dictionary = repo_fixture / "metadata" / "secret-rules.json"
    if missing:
        dictionary.unlink()
    else:
        dictionary.write_text('{"base64": {}}', encoding="utf-8")
    calls = []
    monkeypatch.setattr(appstore_sync, "_run", lambda *args, **kwargs: calls.append(args))
    with pytest.raises((FileNotFoundError, ValueError)):
        appstore_sync.prepare_preview("demo", host="1.2.3.4", secret_path=str(key))
    assert calls == []


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


def test_sync_app_dir_version_override_applies_only_to_staged_copy(repo_fixture, app_factory, monkeypatch):
    app_path = app_factory("demo")
    (app_path / ".env").write_text("W9_REPO=demo\nW9_VERSION=1.0\n", encoding="utf-8")
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")
    captured = {}

    def fake_run(command, *, progress=None, verbose=False):
        if "-r" in command:
            captured["env"] = (Path(command[-2]) / ".env").read_text(encoding="utf-8")
        return ""

    monkeypatch.setattr(appstore_sync, "_run", fake_run)

    appstore_sync._sync_app_dir(
        app_name="demo",
        host="1.2.3.4",
        user="root",
        secret_path=secret_path,
        container="websoft9",
        deploy_dir="/websoft9/library/apps",
        backup_dir="/tmp/backup-demo",
        version="dev-abc1234",
    )

    assert captured["env"] == "W9_REPO=demo\nW9_VERSION=dev-abc1234\n"
    assert (app_path / ".env").read_text(encoding="utf-8") == "W9_REPO=demo\nW9_VERSION=1.0\n"


def test_sync_app_dir_verifies_bytes_and_rejects_overwritten_package(repo_fixture, app_factory, monkeypatch):
    app_path = app_factory("demo")
    env = app_path / ".env"
    env.write_text("W9_VERSION=2.0\n")
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if "sha256sum -c -" in command[-1]:
            digest = hashlib.sha256(env.read_bytes()).hexdigest()
            assert f"{digest}  ./.env" in command[-1]
            raise RuntimeError(".env: FAILED")
        return ""

    monkeypatch.setattr(appstore_sync, "_run", fake_run)
    monkeypatch.setattr(appstore_sync, "ssh_base", lambda *args: ["ssh"])
    monkeypatch.setattr(appstore_sync, "scp_base", lambda *args: ["scp"])
    with pytest.raises(RuntimeError, match="FAILED"):
        appstore_sync._sync_app_dir("demo", "host", "root", Path("key"), "websoft9", "/apps", "/backup")
    assert len(calls) == 4


def test_prepare_preview_reports_version_override(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    write_catalog_schema(repo_fixture)
    secret_path = repo_fixture / ".secrets" / "ssh" / "default.pem"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n", encoding="utf-8")
    monkeypatch.setattr(appstore_sync, "_run", lambda *args, **kwargs: "")
    monkeypatch.setattr(appstore_sync, "_sync_app_dir", lambda *args, **kwargs: None)

    payload = appstore_sync.prepare_preview(
        app_name="demo",
        host="1.2.3.4",
        user="root",
        secret_path=".secrets/ssh/default.pem",
        container="websoft9",
        version="dev-abc1234",
    )

    assert payload["version_override"] == "dev-abc1234"
