from __future__ import annotations

import pytest
import yaml

from _helpers import REPO_ROOT, load_build_module

maintenance_metadata = load_build_module("maintenance_metadata_v", REPO_ROOT / "build" / "maintenance_metadata.py")


def write_metadata(tmp_path, maintenance: dict, archive: dict | None = None):
    (tmp_path / "metadata").mkdir(parents=True, exist_ok=True)
    (tmp_path / "metadata" / "maintenance.yaml").write_text(
        yaml.safe_dump(maintenance, sort_keys=False), encoding="utf-8"
    )
    if archive is not None:
        (tmp_path / "metadata" / "archive.yaml").write_text(
            yaml.safe_dump(archive, sort_keys=False), encoding="utf-8"
        )
    else:
        (tmp_path / "metadata" / "archive.yaml").unlink(missing_ok=True)


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


def test_validate_rejects_unknown_cadence_app(build_fixture):
    write_metadata(build_fixture, base_maintenance(cadence={"weekly": ["ghost"]}))

    with pytest.raises(ValueError, match="Unknown app in cadence"):
        maintenance_metadata.validate_maintenance_metadata(base_maintenance(cadence={"weekly": ["ghost"]}))


def test_validate_rejects_duplicate_cadence_buckets(build_fixture):
    data = base_maintenance(cadence={"weekly": ["demo"], "monthly": ["demo"]})

    with pytest.raises(ValueError, match="multiple cadence buckets"):
        maintenance_metadata.validate_maintenance_metadata(data)


def test_validate_rejects_frozen_and_archived_overlap(build_fixture):
    write_metadata(build_fixture, base_maintenance(lifecycle={"frozen": ["archived-demo"]}), base_archive(apps=["archived-demo"]))

    with pytest.raises(ValueError, match="both frozen and archived"):
        maintenance_metadata.load_maintenance_metadata()


def test_validate_rejects_archived_app_with_cadence_entry(build_fixture):
    write_metadata(
        build_fixture,
        base_maintenance(cadence={"weekly": ["archived-demo"]}),
        base_archive(apps=["archived-demo"]),
    )

    with pytest.raises(ValueError, match="cannot have cadence"):
        maintenance_metadata.load_maintenance_metadata()


def test_validate_accepts_clean_metadata(build_fixture):
    write_metadata(build_fixture, base_maintenance(), base_archive())
    loaded = maintenance_metadata.load_maintenance_metadata()

    maintenance_metadata.validate_maintenance_metadata(loaded)


def test_validate_rejects_unknown_cadence_bucket(build_fixture):
    data = base_maintenance(cadence={"daily": ["demo"]})

    with pytest.raises(ValueError, match="Unknown cadence bucket"):
        maintenance_metadata.validate_maintenance_metadata(data)


def test_validate_rejects_unknown_update_policy_bucket(build_fixture):
    data = base_maintenance(update_policy={"patch-only": ["demo"]})

    with pytest.raises(ValueError, match="Unknown update policy bucket"):
        maintenance_metadata.validate_maintenance_metadata(data)
