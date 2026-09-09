from __future__ import annotations

import json
from pathlib import Path

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
    assert len(payload["rollback"]) == 1


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
    assert len(payload["rollback"]) == 2


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
