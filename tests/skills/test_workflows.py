from __future__ import annotations

import json

from typer.testing import CliRunner

from libs import main
from libs import readme as readme_module


runner = CliRunner()


def _json_output(result):
    return json.loads(result.stdout)


def test_new_app_skill_workflow_smoke(skill_repo_fixture):
    result = runner.invoke(
        main.app,
        [
            "new-app",
            "--name",
            "smoke-app",
            "--trademark",
            "Smoke App",
            "--version",
            "1.0",
            "--repo",
            "bitnami/smoke-app",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = _json_output(result)
    assert payload["app"] == "smoke-app"
    assert payload["check"]["ok"] is True
    assert (skill_repo_fixture / "apps" / "smoke-app" / "README.md").exists()

    readme_result = runner.invoke(main.app, ["gen-readme", "--app", "smoke-app", "--json"])
    assert readme_result.exit_code == 0
    assert _json_output(readme_result)["path"] == "apps/smoke-app/README.md"


def test_archive_restore_skill_workflow_smoke(skill_repo_fixture, skill_app_factory):
    skill_app_factory("ghost")

    archive_result = runner.invoke(main.app, ["archive", "--app", "ghost", "--json"])
    restore_result = runner.invoke(
        main.app,
        ["restore", "--app", "ghost", "--cadence", "weekly", "--update-policy", "lts-only", "--json"],
    )

    assert archive_result.exit_code == 0
    assert restore_result.exit_code == 0
    assert (skill_repo_fixture / "archive" / "apps" / "ghost").exists() is False
    assert (skill_repo_fixture / "apps" / "ghost").exists() is True


def test_update_assessment_style_workflow_smoke(skill_repo_fixture, skill_app_factory, monkeypatch):
    from libs import versions as versions_module

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
            "version_from": "https://hub.docker.com/_/wordpress/tags",
            "edition": [{"dist": "community", "version": ["6.9", "latest"]}],
        },
    )
    monkeypatch.setattr(versions_module, "fetch_candidates", lambda *args, **kwargs: ({"version": "7.0", "last_updated": "2026-08-13"}, None))
    monkeypatch.setattr(main.dblifecycle, "refresh_lifecycle", lambda engine=None: {"path": "metadata/db-lifecycle.json", "updated_at": "2026-08-20", "refreshed": {"mysql": 1}})

    scan_result = runner.invoke(main.app, ["scan", "--app", "wordpress", "--json"])
    drift_result = runner.invoke(main.app, ["drift", "--app", "wordpress", "--json"])
    db_refresh_result = runner.invoke(main.app, ["db-refresh", "--engine", "mysql", "--json"])

    assert scan_result.exit_code == 0
    assert drift_result.exit_code == 0
    assert db_refresh_result.exit_code == 0
    assert _json_output(scan_result)[0]["latest_version"]["version"] == "7.0"
    assert "mysql:$W9_DB_VERSION" in _json_output(drift_result)["dependency_images"]
    assert _json_output(db_refresh_result)["refreshed"] == {"mysql": 1}
