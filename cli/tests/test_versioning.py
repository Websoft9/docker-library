from __future__ import annotations

from packaging import version

from libs.versioning import find_latest_version, get_current_versions, normalize_tag


def test_normalize_tag_strips_ls_build_and_cli_suffixes():
    assert normalize_tag("9.0-cli-ls78") == "9.0"
    assert normalize_tag("8.1.2-cli-ls76") == "8.1.2"
    assert normalize_tag("8.1.2") == "8.1.2"
    assert normalize_tag("version-9.0-cli") == "version-9.0"


def test_get_current_versions_accepts_ls_suffixed_tags():
    valid, all_versions = get_current_versions(
        [{"dist": "community", "version": ["9.0-cli-ls78", "latest"]}]
    )

    assert all_versions == ["9.0-cli-ls78", "latest"]
    assert valid == [version.parse("9.0"), "latest"]


def test_find_latest_version_compares_ls_suffixed_tags():
    tags = [
        {"name": "9.0-cli-ls78", "last_updated": "2026-02-01"},
        {"name": "9.0-cli-ls77", "last_updated": "2026-01-01"},
        {"name": "8.1.2", "last_updated": "2026-01-15"},
    ]

    assert find_latest_version(tags, "8.1.2-cli-ls76") == {
        "version": "9.0-cli-ls78",
        "last_updated": "2026-02-01",
    }
    assert find_latest_version(tags, "9.0-cli-ls78") is None


def test_get_current_versions_filters_non_community_and_invalid_versions():
    valid, all_versions = get_current_versions(
        [
            {"dist": "community", "version": ["1.2", "latest", "bad"]},
            {"dist": "enterprise", "version": ["9.9"]},
        ]
    )

    assert all_versions == ["1.2", "latest", "bad"]
    assert valid == [version.parse("1.2"), "latest"]


def test_find_latest_version_prefers_minor_tags_over_patch_tags_when_available():
    tags = [
        {"name": "1.2.9", "last_updated": "2026-01-01"},
        {"name": "1.3", "last_updated": "2026-01-02"},
        {"name": "1.3.4", "last_updated": "2026-01-03"},
    ]

    assert find_latest_version(tags, "1.2") == {
        "version": "1.3",
        "last_updated": "2026-01-02",
    }


def test_find_latest_version_filters_prereleases_and_older_versions():
    tags = [
        {"name": "1.2rc1", "last_updated": "2026-01-01"},
        {"name": "1.1.9", "last_updated": "2026-01-02"},
        {"name": "1.2", "last_updated": "2026-01-03"},
    ]

    assert find_latest_version(tags, "1.2") is None


def test_find_latest_version_uses_patch_candidates_when_no_minor_candidate_exists():
    tags = [
        {"name": "2.4.1", "last_updated": "2026-01-04"},
        {"name": "2.3.9", "last_updated": "2026-01-03"},
    ]

    assert find_latest_version(tags, "2.3") == {
        "version": "2.4.1",
        "last_updated": "2026-01-04",
    }
