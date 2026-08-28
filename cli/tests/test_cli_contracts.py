from __future__ import annotations

import json

from typer.testing import CliRunner

from libs import main
from libs import readme as readme_module


runner = CliRunner()


def _json_output(result) -> dict | list:
    return json.loads(result.stdout)


def test_list_info_scan_plan_only_and_drift_contracts(repo_fixture, app_factory):
    app_factory(
        "wordpress",
        env="W9_URL=''\n",
        compose="services:\n  wordpress:\n    image: wordpress:6.9\n",
        variables={
            "name": "wordpress",
            "trademark": "WordPress",
            "release": True,
            "upstream": {"image": "https://hub.docker.com/_/wordpress/tags"},
            "edition": [{"dist": "community", "version": ["6.9", "latest"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1", "url": "https://example.com"},
        },
    )

    list_result = runner.invoke(main.app, ["list", "--json"])
    info_result = runner.invoke(main.app, ["info", "--app", "wordpress", "--json"])
    scan_result = runner.invoke(main.app, ["scan", "--app", "wordpress", "--plan-only", "--json"])
    drift_result = runner.invoke(main.app, ["drift", "--app", "wordpress", "--json"])

    assert list_result.exit_code == 0
    assert info_result.exit_code == 0
    assert scan_result.exit_code == 0
    assert drift_result.exit_code == 0

    assert _json_output(list_result)[0]["name"] == "wordpress"
    assert _json_output(info_result)["path"] == "apps/wordpress"
    assert _json_output(scan_result)[0]["source_type"] == "dockerhub-tags"
    assert _json_output(drift_result)["dependency_images"] == ["wordpress:6.9"]


def test_new_app_contracts_dry_run_and_duplicate_rejection(repo_fixture, app_factory):
    dry_run = runner.invoke(
        main.app,
        [
            "new-app",
            "--name",
            "demo-app",
            "--trademark",
            "Demo App",
            "--version",
            "1.0",
            "--repo",
            "bitnami/demo-app",
            "--dry-run",
            "--json",
        ],
    )

    assert dry_run.exit_code == 0
    payload = _json_output(dry_run)
    assert payload["app"] == "demo-app"
    assert payload["dry_run"] is True
    assert payload["files"] == [".env", "docker-compose.yml", "variables.json", "README.md", "CHANGELOG.md", "src/.gitkeep"]
    assert not (repo_fixture / "apps" / "demo-app").exists()

    app_factory("demo-app")
    duplicate = runner.invoke(
        main.app,
        ["new-app", "--name", "demo-app", "--trademark", "Demo App", "--json"],
    )

    assert duplicate.exit_code == 4
    assert "already exists" in (duplicate.stdout + getattr(duplicate, "stderr", ""))


def test_archive_and_restore_contracts(repo_fixture, app_factory):
    app_factory("ghost")

    archive_result = runner.invoke(main.app, ["archive", "--app", "ghost", "--json"])
    restore_result = runner.invoke(
        main.app,
        ["restore", "--app", "ghost", "--cadence", "weekly", "--update-policy", "lts-only", "--json"],
    )

    assert archive_result.exit_code == 0
    assert restore_result.exit_code == 0
    assert _json_output(archive_result)["target"] == "archive/apps/ghost"
    assert _json_output(restore_result)["target"] == "apps/ghost"


def test_gen_readme_contract(repo_fixture, app_factory, monkeypatch):
    template_root = repo_fixture / "metadata" / "templates"
    template_root.mkdir(parents=True, exist_ok=True)
    (template_root / "readme.jinja2").write_text("# {{ trademark }}\n", encoding="utf-8")
    monkeypatch.setattr(readme_module, "TEMPLATE_ROOT", template_root)
    app_factory(
        "demo",
        variables={
            "name": "demo",
            "trademark": "Demo",
            "release": True,
            "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
            "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1", "url": "https://example.com"},
        },
    )

    result = runner.invoke(main.app, ["gen-readme", "--app", "demo", "--json"])

    assert result.exit_code == 0
    payload = _json_output(result)
    assert payload["path"] == "apps/demo/README.md"
    assert (repo_fixture / "apps" / "demo" / "README.md").read_text(encoding="utf-8") == "# Demo\n"


def test_db_refresh_contract_with_mocked_engine(repo_fixture, monkeypatch):
    monkeypatch.setattr(main.dblifecycle, "refresh_lifecycle", lambda engine=None: {"path": "metadata/db-lifecycle.json", "updated_at": "2026-08-20", "refreshed": {"mysql": 1}})

    result = runner.invoke(main.app, ["db-refresh", "--engine", "mysql", "--json"])

    assert result.exit_code == 0
    assert _json_output(result) == {
        "path": "metadata/db-lifecycle.json",
        "updated_at": "2026-08-20",
        "refreshed": {"mysql": 1},
    }


def test_repo_discovery_contract_from_subdirectory(repo_fixture, app_factory, monkeypatch):
    app_factory("wordpress")
    nested = repo_fixture / "apps" / "wordpress"
    monkeypatch.chdir(nested)

    result = runner.invoke(main.app, ["info", "--app", "wordpress", "--json"])

    assert result.exit_code == 0
    assert _json_output(result)["path"] == "apps/wordpress"


def test_check_maintenance_contract(repo_fixture):
    result = runner.invoke(main.app, ["check-maintenance"])

    assert result.exit_code == 0
    assert "maintenance metadata valid" in result.stdout
