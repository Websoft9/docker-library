from __future__ import annotations

import yaml

from libs import app as app_module


def test_collect_apps_includes_archived_and_filters_scope(repo_fixture, app_factory):
    app_factory("public-app")
    app_factory("internal-app", variables={
        "name": "internal-app",
        "scope": "internal",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/example/tags"},
        "edition": [{"dist": "community", "version": ["1.0"]}],
    })
    app_factory("archived-app", archived=True)

    archive_path = repo_fixture / "metadata" / "archive.yaml"
    archive = yaml.safe_load(archive_path.read_text(encoding="utf-8"))
    archive["apps"] = ["archived-app"]
    archive_path.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")

    all_names = [item["name"] for item in app_module.collect_apps(include_archived=True)]
    internal_names = [item["name"] for item in app_module.collect_apps(scope="internal")]

    assert all_names == ["archived-app", "internal-app", "public-app"]
    assert internal_names == ["internal-app"]


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
