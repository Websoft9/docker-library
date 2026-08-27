from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from libs import main, remote


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

    variables = json.loads((skill_repo_fixture / "apps" / "smoke-app" / "variables.json").read_text(encoding="utf-8"))
    assert "releases" not in variables["upstream"]
    assert "compose" not in variables["upstream"]


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
            "upstream": {"image": "https://hub.docker.com/_/wordpress/tags"},
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


def test_new_app_prefills_upstream_sources(skill_repo_fixture):
    result = runner.invoke(
        main.app,
        [
            "new-app",
            "--name",
            "upstream-app",
            "--trademark",
            "Upstream App",
            "--version",
            "1.0",
            "--repo",
            "ghcr.io/example/upstream-app",
            "--docs-github",
            "https://github.com/example/upstream-app",
            "--docs-install",
            "https://docs.example.com/upstream-app/install",
            "--upstream-releases",
            "https://github.com/example/upstream-app/tags",
            "--upstream-compose",
            "https://raw.githubusercontent.com/example/upstream-app/main/docker-compose.yml",
            "--upstream-env",
            "https://raw.githubusercontent.com/example/upstream-app/main/.env.example",
            "--json",
        ],
    )

    assert result.exit_code == 0
    variables = json.loads((Path(skill_repo_fixture) / "apps" / "upstream-app" / "variables.json").read_text(encoding="utf-8"))
    assert variables["upstream"]["releases"] == "https://github.com/example/upstream-app/tags"
    assert variables["upstream"]["compose"]["compose"] == "https://raw.githubusercontent.com/example/upstream-app/main/docker-compose.yml"
    assert variables["upstream"]["compose"]["env"] == "https://raw.githubusercontent.com/example/upstream-app/main/.env.example"


def test_remote_scrubs_known_hosts_warning():
    result = remote.scrub_completed_process(
        subprocess.CompletedProcess(
            args=["ssh", "example"],
            returncode=0,
            stdout="ok\n",
            stderr="Warning: Permanently added '47.86.46.191' (ED25519) to the list of known hosts.\nreal warning\n",
        )
    )

    assert result.stdout == "ok\n"
    assert result.stderr == "real warning"
