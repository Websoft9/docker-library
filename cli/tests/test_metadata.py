from __future__ import annotations

import yaml

from libs.metadata import resolve_app_metadata, resolve_archive_entries


def test_resolve_archive_entries_merges_defaults_and_overrides():
    resolved = resolve_archive_entries(
        {
            "defaults": {"archive_reason": "owner-retired", "contentful": {"action": "archive"}},
            "apps": ["ghost"],
            "overrides": {
                "ghost": {"archive_reason": "security"},
                "legacy": {"archive_reason": "deprecated"},
            },
        }
    )

    assert resolved == {
        "ghost": {"archive_reason": "security", "contentful": {"action": "archive"}},
        "legacy": {"archive_reason": "deprecated", "contentful": {"action": "archive"}},
    }


def test_resolve_app_metadata_uses_defaults_and_bucket_overrides(repo_fixture):
    (repo_fixture / "metadata" / "maintenance.yaml").write_text(
        yaml.safe_dump(
            {
                "defaults": {"status": "active", "cadence": "monthly", "update_policy": "patch-minor"},
                "cadence": {"weekly": ["wordpress"]},
                "update_policy": {"lts-only": ["wordpress"]},
                "lifecycle": {"frozen": []},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (repo_fixture / "metadata" / "archive.yaml").write_text("defaults: {}\napps: []\noverrides: {}\n", encoding="utf-8")

    result = resolve_app_metadata("wordpress")

    assert result.status == "active"
    assert result.cadence == "weekly"
    assert result.update_policy == "lts-only"
    assert result.archive_reason is None


def test_resolve_app_metadata_marks_frozen_apps(repo_fixture):
    (repo_fixture / "metadata" / "maintenance.yaml").write_text(
        yaml.safe_dump(
            {
                "defaults": {"status": "active", "cadence": "monthly", "update_policy": "patch-minor"},
                "cadence": {},
                "update_policy": {},
                "lifecycle": {"frozen": ["mysql"]},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (repo_fixture / "metadata" / "archive.yaml").write_text("defaults: {}\napps: []\noverrides: {}\n", encoding="utf-8")

    result = resolve_app_metadata("mysql")

    assert result.status == "frozen"
    assert result.cadence == "monthly"
    assert result.update_policy == "patch-minor"


def test_resolve_app_metadata_archived_state_overrides_other_buckets(repo_fixture):
    (repo_fixture / "metadata" / "maintenance.yaml").write_text(
        yaml.safe_dump(
            {
                "defaults": {"status": "active", "cadence": "monthly", "update_policy": "patch-minor"},
                "cadence": {"weekly": ["legacy-app"]},
                "update_policy": {"lts-only": ["legacy-app"]},
                "lifecycle": {"frozen": ["legacy-app"]},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (repo_fixture / "metadata" / "archive.yaml").write_text(
        yaml.safe_dump(
            {
                "defaults": {"archive_reason": "owner-retired", "contentful": {"action": "archive", "production": False}},
                "apps": ["legacy-app"],
                "overrides": {},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    result = resolve_app_metadata("legacy-app")

    assert result.status == "archived"
    assert result.cadence == "none"
    assert result.update_policy == "none"
    assert result.archive_reason == "owner-retired"
    assert result.contentful == {"action": "archive", "production": False}
