from __future__ import annotations

import concurrent.futures
import os
import subprocess
import sys
import textwrap

import yaml

from libs import app as app_module


def test_collect_apps_includes_archived_and_filters_scope(repo_fixture, app_factory):
    app_factory("public-app")
    internal_app = app_factory("internal-app", variables={
        "name": "internal-app",
        "scope": "internal",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/example/tags"},
        "edition": [{"dist": "community", "version": ["1.0"]}],
    })
    app_factory("archived-app", archived=True)
    (internal_app / "Dockerfile").write_text("FROM busybox\n", encoding="utf-8")

    archive_path = repo_fixture / "metadata" / "archive.yaml"
    archive = yaml.safe_load(archive_path.read_text(encoding="utf-8"))
    archive["apps"] = ["archived-app"]
    archive_path.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")

    all_names = [item["name"] for item in app_module.collect_apps(include_archived=True)]
    internal_names = [item["name"] for item in app_module.collect_apps(scope="internal")]
    apps = {item["name"]: item for item in app_module.collect_apps(include_archived=True)}

    assert all_names == ["archived-app", "internal-app", "public-app"]
    assert internal_names == ["internal-app"]
    assert apps["internal-app"]["dockerfile"] is True
    assert apps["public-app"]["dockerfile"] is False


def test_collect_app_info_returns_relative_path(app_factory):
    app_factory("wordpress", variables={
        "name": "wordpress",
        "trademark": "WordPress",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/wordpress/tags"},
        "requirements": {"cpu": "1"},
        "externalDB": {"1.0": {"mysql": ["8.0+"]}},
        "edition": [{"dist": "community", "version": ["1.0"]}],
    })

    result = app_module.collect_app_info("wordpress")

    assert result["path"] == "apps/wordpress"
    assert result["trademark"] == "WordPress"
    assert result["requirements"] == {"cpu": "1"}


def test_archive_app_real_move_updates_metadata(repo_fixture, app_factory):
    app_factory("ghost")
    maintenance_path = repo_fixture / "metadata" / "maintenance.yaml"
    maintenance = yaml.safe_load(maintenance_path.read_text(encoding="utf-8"))
    maintenance["cadence"] = {"weekly": ["ghost"]}
    maintenance["update_policy"] = {"lts-only": ["ghost"]}
    maintenance["lifecycle"] = {"frozen": ["ghost"]}
    maintenance_path.write_text(yaml.safe_dump(maintenance, sort_keys=False), encoding="utf-8")

    result = app_module.archive_app("ghost", reason="security", dry_run=False)

    assert result["source"] == "apps/ghost"
    assert result["target"] == "archive/apps/ghost"
    assert (repo_fixture / "archive" / "apps" / "ghost").exists()
    assert not (repo_fixture / "apps" / "ghost").exists()

    updated_maintenance = yaml.safe_load(maintenance_path.read_text(encoding="utf-8"))
    updated_archive = yaml.safe_load((repo_fixture / "metadata" / "archive.yaml").read_text(encoding="utf-8"))
    assert updated_maintenance["cadence"]["weekly"] == []
    assert updated_maintenance["update_policy"]["lts-only"] == []
    assert updated_maintenance["lifecycle"]["frozen"] == []
    assert "ghost" in updated_archive["apps"]
    assert updated_archive["overrides"]["ghost"] == {"archive_reason": "security"}


def test_restore_app_real_move_updates_metadata(repo_fixture, app_factory):
    app_factory("ghost", archived=True)
    archive_path = repo_fixture / "metadata" / "archive.yaml"
    archive = yaml.safe_load(archive_path.read_text(encoding="utf-8"))
    archive["apps"] = ["ghost"]
    archive_path.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")

    result = app_module.restore_app("ghost", cadence="weekly", update_policy="lts-only", dry_run=False)

    assert result["source"] == "archive/apps/ghost"
    assert result["target"] == "apps/ghost"
    assert (repo_fixture / "apps" / "ghost").exists()
    assert not (repo_fixture / "archive" / "apps" / "ghost").exists()

    updated_maintenance = yaml.safe_load((repo_fixture / "metadata" / "maintenance.yaml").read_text(encoding="utf-8"))
    updated_archive = yaml.safe_load(archive_path.read_text(encoding="utf-8"))
    assert updated_maintenance["cadence"]["weekly"] == ["ghost"]
    assert updated_maintenance["update_policy"]["lts-only"] == ["ghost"]
    assert updated_archive["apps"] == []


def test_archive_app_dry_run_does_not_move_files(repo_fixture, app_factory):
    app_factory("nextcloud")

    result = app_module.archive_app("nextcloud", dry_run=True)

    assert result["metadata_updated"] is True
    assert (repo_fixture / "apps" / "nextcloud").exists()
    assert not (repo_fixture / "archive" / "apps" / "nextcloud").exists()


def test_archive_app_concurrent_processes_preserve_all_metadata(repo_fixture, app_factory):
    for name in ("owncloud", "posthog", "python", "signoz"):
        app_factory(name)

    script = textwrap.dedent(
        """
        import os
        from libs import app
        app.archive_app(os.environ["APP_NAME"], reason="batch-archive", dry_run=False)
        """
    )
    commands = [[sys.executable, "-c", script] for _ in ("owncloud", "posthog", "python", "signoz")]
    names = ["owncloud", "posthog", "python", "signoz"]

    def run(payload):
        command, name = payload
        env = {**os.environ, "APP_NAME": name}
        return subprocess.run(command, cwd=repo_fixture, check=True, capture_output=True, text=True, env=env)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(run, zip(commands, names, strict=True)))

    updated_archive = yaml.safe_load((repo_fixture / "metadata" / "archive.yaml").read_text(encoding="utf-8"))
    archived_apps = set(updated_archive["apps"])

    assert all(result.returncode == 0 for result in results)
    assert {"owncloud", "posthog", "python", "signoz"}.issubset(archived_apps)
    for name in ("owncloud", "posthog", "python", "signoz"):
        assert updated_archive["overrides"][name] == {"archive_reason": "batch-archive"}


def test_collect_app_info_includes_operational_facts(repo_fixture, app_factory):
    import json

    (repo_fixture / "metadata" / "db-lifecycle.json").write_text(
        json.dumps({
            "version": 1,
            "engines": {"mysql": {"tracks": [{"version": "8.4", "track": "lts", "eol": "2032-04-30"}]}},
        }),
        encoding="utf-8",
    )
    app = app_factory(
        "demo",
        env="W9_ID=demo\nW9_VERSION=1.0\nW9_HTTP_PORT_SET=9001\nW9_DB_VERSION=8.4\n",
        compose=(
            "services:\n"
            "  demo:\n"
            "    image: demo:1\n"
            "    ports:\n"
            "      - \"${W9_HTTP_PORT_SET}:80\" # Web Console\n"
            "  mysql:\n"
            "    image: mysql:${W9_DB_VERSION}\n"
        ),
        variables={
            "name": "demo",
            "trademark": "Demo",
            "release": True,
            "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
            "edition": [{"dist": "community", "version": ["1.0"]}],
            "credentials": {"none": True},
        },
    )
    tests_dir = app / "tests"
    tests_dir.mkdir()
    (tests_dir / "cases.yml").write_text("custom:\n  - id: smoke\n    type: script\n    script: smoke.sh\n", encoding="utf-8")

    result = app_module.collect_app_info("demo")

    assert result["version"] == {"w9_version": "1.0", "declared": ["1.0"]}
    assert result["ports"][0]["published"] == "${W9_HTTP_PORT_SET}:80"
    assert result["published_ports"] == [{"service": "demo", "env": "W9_HTTP_PORT_SET", "published": 9001, "target": 80}]
    assert result["services"] == ["demo", "mysql"]
    assert result["credentials"] == {"none": True}
    assert result["database"]["status"] == "ok"
    assert result["tests"]["cases"] == [{"group": "custom", "id": "smoke", "type": "script"}]
