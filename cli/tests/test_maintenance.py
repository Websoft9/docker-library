from __future__ import annotations

import yaml

import pytest

from libs.maintenance import load_maintenance_metadata, validate_maintenance_metadata


def write_metadata(repo_root, maintenance: dict, archive: dict | None = None):
    (repo_root / "metadata" / "maintenance.yaml").write_text(
        yaml.safe_dump(maintenance, sort_keys=False), encoding="utf-8"
    )
    if archive is not None:
        (repo_root / "metadata" / "archive.yaml").write_text(
            yaml.safe_dump(archive, sort_keys=False), encoding="utf-8"
        )
    else:
        (repo_root / "metadata" / "archive.yaml").unlink(missing_ok=True)


def base_maintenance(**overrides):
    data = {
        "defaults": {"status": "active", "cadence": "monthly", "update_policy": "patch-minor"},
        "cadence": {},
        "update_policy": {},
        "lifecycle": {"frozen": []},
    }
    data.update(overrides)
    return data


def base_archive(**overrides):
    data = {
        "defaults": {"archive_reason": "owner-retired"},
        "apps": [],
        "overrides": {},
    }
    data.update(overrides)
    return data


def test_validate_rejects_unknown_cadence_app(repo_fixture):
    write_metadata(repo_fixture, base_maintenance(cadence={"weekly": ["ghost"]}))

    with pytest.raises(ValueError, match="Unknown app in cadence"):
        validate_maintenance_metadata(base_maintenance(cadence={"weekly": ["ghost"]}))


def test_validate_rejects_duplicate_cadence_buckets(repo_fixture, app_factory):
    app_factory("demo")
    data = base_maintenance(cadence={"weekly": ["demo"], "monthly": ["demo"]})

    with pytest.raises(ValueError, match="multiple cadence buckets"):
        validate_maintenance_metadata(data)


def test_validate_rejects_frozen_and_archived_overlap(repo_fixture, app_factory):
    app_factory("archived-demo", archived=True)
    write_metadata(repo_fixture, base_maintenance(lifecycle={"frozen": ["archived-demo"]}), base_archive(apps=["archived-demo"]))

    with pytest.raises(ValueError, match="both frozen and archived"):
        load_maintenance_metadata()


def test_validate_rejects_archived_app_with_cadence_entry(repo_fixture, app_factory):
    app_factory("archived-demo", archived=True)
    write_metadata(
        repo_fixture,
        base_maintenance(cadence={"weekly": ["archived-demo"]}),
        base_archive(apps=["archived-demo"]),
    )

    with pytest.raises(ValueError, match="cannot have cadence"):
        load_maintenance_metadata()


def test_validate_accepts_clean_metadata(repo_fixture):
    write_metadata(repo_fixture, base_maintenance(), base_archive())
    loaded = load_maintenance_metadata()

    validate_maintenance_metadata(loaded)
