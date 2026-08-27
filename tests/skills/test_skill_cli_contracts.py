from __future__ import annotations

import json

from typer.testing import CliRunner

from libs import main
from libs import versions as versions_module


runner = CliRunner()


def _json_output(result):
    return json.loads(result.stdout)


def test_update_assessment_skill_commands_contract(skill_repo_fixture, skill_app_factory, monkeypatch):
    skill_app_factory(
        "wordpress",
        compose=(
            "services:\n"
            "  wordpress:\n"
            "    image: wordpress:6.9\n"
            "  mysql:\n"
            "    image: mysql:$W9_DB_VERSION\n"
        ),
        variables={
            "name": "wordpress",
            "trademark": "WordPress",
            "release": True,
            "upstream": {"image": "https://hub.docker.com/_/wordpress/tags"},
            "edition": [{"dist": "community", "version": ["6.9", "latest"]}],
        },
    )
    monkeypatch.setattr(versions_module, "fetch_candidates", lambda *args, **kwargs: ({"version": "7.0", "last_updated": "2026-08-13"}, None))

    scan_result = runner.invoke(main.app, ["scan", "--app", "wordpress", "--json"])
    drift_result = runner.invoke(main.app, ["drift", "--app", "wordpress", "--json"])

    assert scan_result.exit_code == 0
    assert drift_result.exit_code == 0
    assert _json_output(scan_result)[0]["latest_version"] == {"version": "7.0", "last_updated": "2026-08-13"}
    assert "mysql:$W9_DB_VERSION" in _json_output(drift_result)["dependency_images"]


def test_deploy_validation_and_restore_skill_commands_contract(skill_repo_fixture, skill_app_factory):
    skill_app_factory("demo")
    skill_app_factory("archived-demo", archived=True)

    check_result = runner.invoke(main.app, ["check", "--app", "demo", "--json"])
    list_result = runner.invoke(main.app, ["list", "--include-archived", "--json"])
    restore_preview = runner.invoke(
        main.app,
        ["restore", "--app", "archived-demo", "--cadence", "monthly", "--update-policy", "patch-minor", "--dry-run", "--json"],
    )

    assert check_result.exit_code == 0
    assert list_result.exit_code == 0
    assert restore_preview.exit_code == 0
    assert _json_output(check_result)["ok"] is True
    assert any(item["name"] == "archived-demo" and item["status"] == "archived" for item in _json_output(list_result))
    assert _json_output(restore_preview)["target"] == "apps/archived-demo"


def test_new_app_and_db_refresh_skill_commands_contract(skill_repo_fixture, monkeypatch):
    monkeypatch.setattr(main.dblifecycle, "refresh_lifecycle", lambda engine=None: {"path": "metadata/db-lifecycle.json", "updated_at": "2026-08-20", "refreshed": {"mysql": 1}})

    new_app_result = runner.invoke(
        main.app,
        ["new-app", "--name", "demo-app", "--trademark", "Demo App", "--version", "1.0", "--repo", "bitnami/demo-app", "--dry-run", "--json"],
    )
    db_refresh_result = runner.invoke(main.app, ["db-refresh", "--engine", "mysql", "--json"])

    assert new_app_result.exit_code == 0
    assert db_refresh_result.exit_code == 0
    assert _json_output(new_app_result)["files"] == [".env", "docker-compose.yml", "variables.json", "README.md", "CHANGELOG.md", "src/.gitkeep"]
    assert _json_output(db_refresh_result)["refreshed"] == {"mysql": 1}


def test_skill_commands_work_from_app_subdirectory(skill_repo_fixture, skill_app_factory, monkeypatch):
    skill_app_factory("wordpress")
    nested = skill_repo_fixture / "apps" / "wordpress"
    monkeypatch.chdir(nested)

    result = runner.invoke(main.app, ["info", "--app", "wordpress", "--json"])

    assert result.exit_code == 0
    assert _json_output(result)["path"] == "apps/wordpress"
