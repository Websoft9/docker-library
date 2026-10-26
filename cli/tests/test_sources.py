from __future__ import annotations

from libs import sources


def test_detect_source_type_covers_supported_sources():
    assert sources.detect_source_type("https://hub.docker.com/_/wordpress/tags") == "dockerhub-tags"
    assert sources.detect_source_type("ghcr.io/open-webui/open-webui") == "ghcr-tags"
    assert sources.detect_source_type("https://gallery.ecr.aws/gravitational/teleport-distroless") == "ecr-public"
    assert sources.detect_source_type("https://public.ecr.aws/gravitational/teleport-distroless") == "ecr-public"
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


def test_dockerhub_api_url_works_without_tags_suffix():
    assert (
        sources._dockerhub_api_url("https://hub.docker.com/_/wordpress")
        == "https://hub.docker.com/v2/repositories/library/wordpress/tags"
    )
    assert (
        sources._dockerhub_api_url("https://hub.docker.com/r/redis/redisinsight")
        == "https://hub.docker.com/v2/repositories/redis/redisinsight/tags"
    )


def test_github_api_url_and_ghcr_repository_parsing():
    assert sources._github_api_url("https://github.com/owner/repo/releases") == "https://api.github.com/repos/owner/repo"
    assert sources._github_api_url("https://example.com/owner/repo") is None
    assert sources._ghcr_repository("ghcr.io/open-webui/open-webui:main") == ("open-webui", "open-webui")
    assert sources._ghcr_repository("ghcr.io/open-webui") is None
    assert sources._ecr_public_repository("https://gallery.ecr.aws/gravitational/teleport-distroless") == ("gravitational", "teleport-distroless")
    assert sources._ecr_public_repository("https://public.ecr.aws/gravitational/teleport-distroless:18.10") == ("gravitational", "teleport-distroless")
    assert sources._ecr_public_repository("https://gallery.ecr.aws/gravitational") is None


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


def test_get_json_authenticates_github_api_when_token_is_present(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "test-token")
    calls = []

    def fake_get_json(url, params=None, headers=None):
        calls.append((url, headers))
        return [], None, None

    monkeypatch.setattr(sources, "get_json_with_fallback", fake_get_json)

    sources._get_json("https://api.github.com/repos/owner/repo/tags")
    sources._get_json("https://public.ecr.aws/token/")

    assert calls[0][1] == {"Authorization": "Bearer test-token"}
    assert calls[1][1] is None


def test_ghcr_tags_page_uses_the_shared_json_fallback(monkeypatch):
    captured = {}

    def fake_get_json(url, params=None, headers=None):
        captured.update({"url": url, "params": params, "headers": headers})
        return {"tags": ["1.0", "1.1"]}, {"Link": '<https://ghcr.io/next>; rel="next"'}, None

    monkeypatch.setattr(sources, "get_json_with_fallback", fake_get_json)

    tags, link, error = sources._ghcr_tags_page("owner", "image", "token", 50, last="0.9")

    assert tags == ["1.0", "1.1"]
    assert link == '<https://ghcr.io/next>; rel="next"'
    assert error is None
    assert captured["headers"] == {"Authorization": "Bearer token"}
    assert captured["params"] == {"n": 50, "last": "0.9"}


def test_ecr_public_tags_page_uses_the_shared_json_fallback(monkeypatch):
    def fake_get_json(url, params=None, headers=None):
        return {"tags": ["1.0", "1.1"]}, {"Link": "<https://public.ecr.aws/next>; rel=\"next\""}, None

    monkeypatch.setattr(sources, "get_json_with_fallback", fake_get_json)

    tags, link, error = sources._ecr_public_tags_page("owner", "image", "token", 50)

    assert tags == ["1.0", "1.1"]
    assert link == "https://public.ecr.aws/next"
    assert error is None


def test_stable_candidates_ignores_branch_named_tags():
    tags = [
        {"name": "v18.11.0", "last_updated": ""},
        {"name": "v19.0.1-angel.gnu.2", "last_updated": ""},
        {"name": "v19.0.0-hugoslack.13", "last_updated": ""},
        {"name": "v18.10.6", "last_updated": ""},
    ]

    assert sources._stable_candidates(tags, "18.10") == ["v18.11.0", "v18.10.6"]
