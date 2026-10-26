from __future__ import annotations

from packaging import version

from libs.versioning import find_latest_version, get_current_versions, normalize_tag, update_status


def test_normalize_tag_strips_ls_build_and_cli_suffixes():
    assert normalize_tag("9.0-cli-ls78") == "9.0"
    assert normalize_tag("8.1.2-cli-ls76") == "8.1.2"
    assert normalize_tag("8.1.2") == "8.1.2"
    assert normalize_tag("version-9.0-cli") == "version-9.0"


def test_normalize_tag_strips_metabase_patch_placeholder():
    assert normalize_tag("v0.64.1.x") == "v0.64.1"
    assert normalize_tag("v0.64.x") == "v0.64"


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


def test_update_status_treats_same_minor_patch_as_covered_by_floating_tag():
    assert update_status("13.2", {"version": "13.2.4"}) == "covered-by-current-minor-tag"
    assert update_status("13.2", {"version": "13.3"}) == "update-available"
    assert update_status("13.2", None) == "up-to-date"


def test_normalize_tag_strips_image_variants_but_preserves_prereleases():
    from packaging import version as packaging_version

    assert normalize_tag("11.4-apache") == "11.4"
    assert normalize_tag("11.4.11-php8.3-apache") == "11.4.11"
    assert normalize_tag("7.1-fpm") == "7.1"
    assert normalize_tag("6-apache") == "6"
    assert normalize_tag("11-alpine") == "11"
    assert normalize_tag("12.0-rc") == "12.0-rc"
    assert normalize_tag("12.0-rc-php8.5-fpm-trixie") == "12.0-rc"
    assert normalize_tag("11.5.0-beta1-apache") == "11.5.0-beta1"
    assert normalize_tag("1.2rc1") == "1.2rc1"
    assert packaging_version.parse(normalize_tag("11.4-apache")) == packaging_version.parse("11.4")


def test_get_current_versions_accepts_image_variant_tags():
    valid, all_versions = get_current_versions(
        [{"dist": "community", "version": ["11.4-apache", "latest"]}]
    )

    assert all_versions == ["11.4-apache", "latest"]
    assert valid == [version.parse("11.4"), "latest"]


def test_normalize_tag_maps_unstable_channels_to_prereleases():
    assert version.parse(normalize_tag("2025.9.6-canary.903")).is_prerelease
    assert version.parse(normalize_tag("7.1.2-nightly")).is_prerelease
    assert version.parse(normalize_tag("1.4.0-snapshot")).is_prerelease
    assert version.parse(normalize_tag("2.0.0-preview.3")).is_prerelease


def test_find_latest_version_ignores_canary_tags():
    tags = [
        {"name": "0.27.4", "last_updated": "2026-09-01"},
        {"name": "2025.9.6-canary.903", "last_updated": "2026-10-20"},
    ]

    assert find_latest_version(tags, "0.27.4") is None


def test_stable_candidates_ignore_canary_tags():
    from libs.sources import _stable_candidates

    tags = [
        {"name": "0.27.4"},
        {"name": "2025.9.6-canary.903"},
        {"name": "0.28.0"},
    ]

    assert _stable_candidates(tags, "0.27.4") == ["0.28.0"]
