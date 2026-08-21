from __future__ import annotations

from libs import sources


def test_detect_source_type_covers_supported_sources():
    assert sources.detect_source_type("https://hub.docker.com/_/wordpress/tags") == "dockerhub-tags"
    assert sources.detect_source_type("ghcr.io/open-webui/open-webui") == "ghcr-tags"
    assert sources.detect_source_type("https://github.com/foo/bar/releases") == "github-releases"
    assert sources.detect_source_type("https://github.com/foo/bar") == "github-tags"
    assert sources.detect_source_type("https://example.com/file.txt") is None


def test_major_prefix_extracts_numeric_major_only():
    assert sources._major_prefix("6.9") == "6."
    assert sources._major_prefix("v12.1.0") == "12."
    assert sources._major_prefix("latest") is None


def test_dockerhub_api_url_supports_library_and_namespaced_images():
    assert (
        sources._dockerhub_api_url("https://hub.docker.com/_/wordpress/tags")
        == "https://hub.docker.com/v2/repositories/library/wordpress/tags"
    )
    assert (
        sources._dockerhub_api_url("https://hub.docker.com/r/redis/redisinsight/tags")
        == "https://hub.docker.com/v2/repositories/redis/redisinsight/tags"
    )


def test_github_api_url_and_ghcr_repository_parsing():
    assert sources._github_api_url("https://github.com/owner/repo/releases") == "https://api.github.com/repos/owner/repo"
    assert sources._github_api_url("https://example.com/owner/repo") is None
    assert sources._ghcr_repository("ghcr.io/open-webui/open-webui:main") == ("open-webui", "open-webui")
    assert sources._ghcr_repository("ghcr.io/open-webui") is None


def test_stable_candidates_filters_prereleases_and_limits_results():
    tags = [
        {"name": "2.0.0rc1", "last_updated": ""},
        {"name": "2.0.0", "last_updated": ""},
        {"name": "1.9.5", "last_updated": ""},
        {"name": "1.8.0", "last_updated": ""},
        {"name": "1.7.0", "last_updated": ""},
    ]

    assert sources._stable_candidates(tags, "1.6.0", limit=3) == ["2.0.0", "1.9.5", "1.8.0"]


def test_fetch_candidates_rejects_unsupported_source_type():
    latest, error = sources.fetch_candidates("unknown", "https://example.com", "1.0")

    assert latest is None
    assert error == "unsupported source type: unknown"
