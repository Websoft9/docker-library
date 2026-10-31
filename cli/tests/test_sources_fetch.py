from __future__ import annotations

import pytest

from libs import sources


def test_fetch_dockerhub_queries_current_and_future_major(monkeypatch):
    calls: list[str | None] = []

    def fake_tags(api_url, name, page_size):
        calls.append(name)
        if name == "6.":
            return ([{"name": "6.10", "last_updated": "2026-01-01"}], None)
        if name == "7.":
            return ([{"name": "7.0", "last_updated": "2026-02-01"}], None)
        return ([], None)

    monkeypatch.setattr(sources, "_dockerhub_tags", fake_tags)

    latest, error = sources._fetch_dockerhub("https://hub.docker.com/_/wordpress/tags", "6.9", major_ahead=1, page_size=100)

    assert error is None
    assert calls == ["6.", "7."]
    assert latest == {"version": "7.0", "last_updated": "2026-02-01"}


def test_fetch_dockerhub_filters_tags_outside_probed_majors(monkeypatch):
    def fake_tags(api_url, name, page_size):
        return ([
            {"name": "9.0-cli-ls78", "last_updated": "2026-02-01"},
            {"name": "2021.12.14", "last_updated": "2021-12-14"},
            {"name": "latest", "last_updated": "2026-03-01"},
        ], None)

    monkeypatch.setattr(sources, "_dockerhub_tags", fake_tags)

    latest, error = sources._fetch_dockerhub("https://hub.docker.com/r/linuxserver/ffmpeg/tags", "9.0-cli-ls78", major_ahead=3, page_size=100)

    assert error is None
    assert latest is None


def test_github_tags_raw_uses_tags_endpoint(monkeypatch):
    called = []

    def fake_get_json(url, params=None):
        called.append(url)
        return ([{"name": "v1.2.0"}, {"name": "v1.1.0"}], None)

    monkeypatch.setattr(sources, "_get_json", fake_get_json)

    tags, error = sources._github_tags_raw("https://github.com/owner/repo", 100)

    assert error is None
    assert called == ["https://api.github.com/repos/owner/repo/tags"]
    assert tags == [{"name": "v1.2.0", "last_updated": ""}, {"name": "v1.1.0", "last_updated": ""}]


def test_fetch_verified_candidates_falls_back_when_index_fetch_fails(monkeypatch):
    monkeypatch.setattr(sources, "_github_tags_raw", lambda url, page_size: ([], "boom"))
    monkeypatch.setattr(sources, "fetch_candidates", lambda *args, **kwargs: ({"version": "1.2", "last_updated": "2026-01-01"}, None))

    latest, error = sources.fetch_verified_candidates(
        verify_type="dockerhub-tags",
        verify_url="https://hub.docker.com/_/demo/tags",
        index_type="github-tags",
        index_url="https://github.com/example/demo",
        current_version="1.0",
    )

    assert error is None
    assert latest == {"version": "1.2", "last_updated": "2026-01-01"}


def test_fetch_verified_candidates_reads_github_source_without_registry_verification(monkeypatch):
    calls = []

    def fake_candidates(source_type, url, current_version, **kwargs):
        calls.append((source_type, url, current_version))
        return {"version": "1.2.0", "last_updated": ""}, None

    monkeypatch.setattr(sources, "fetch_candidates", fake_candidates)

    latest, error = sources.fetch_verified_candidates(
        verify_type="github-tags",
        verify_url="https://github.com/example/project",
        index_type="github-releases",
        index_url="https://github.com/example/project/releases",
        current_version="1.0.0",
    )

    assert error is None
    assert latest["version"] == "1.2.0"
    assert calls == [("github-releases", "https://github.com/example/project/releases", "1.0.0")]


def test_fetch_verified_candidates_prefers_verified_dockerhub_candidate(monkeypatch):
    monkeypatch.setattr(sources, "_github_tags_raw", lambda url, page_size: ([{"name": "1.2.0", "last_updated": ""}, {"name": "1.1.0", "last_updated": ""}], None))
    monkeypatch.setattr(sources, "_dockerhub_api_url", lambda url: "https://hub.docker.com/v2/repositories/library/demo/tags")
    monkeypatch.setattr(sources, "_dockerhub_verify", lambda api_url, candidate, page_size: {"version": candidate, "last_updated": "2026-02-01"} if candidate == "1.2" else None)

    latest, error = sources.fetch_verified_candidates(
        verify_type="dockerhub-tags",
        verify_url="https://hub.docker.com/_/demo/tags",
        index_type="github-tags",
        index_url="https://github.com/example/demo",
        current_version="1.0",
    )

    assert error is None
    assert latest == {"version": "1.2", "last_updated": "2026-02-01"}


def test_fetch_verified_candidates_accepts_x_placeholder_release_tags(monkeypatch):
    monkeypatch.setattr(
        sources,
        "_github_tags_raw",
        lambda url, page_size: ([{"name": "v1.52.5.x", "last_updated": "2026-02-01"}], None),
    )
    monkeypatch.setattr(
        sources,
        "_dockerhub_api_url",
        lambda url: "https://hub.docker.com/v2/repositories/example/app/tags",
    )
    monkeypatch.setattr(
        sources,
        "_dockerhub_verify",
        lambda api_url, candidate, page_size: {
            "version": "v1.52.5.x",
            "last_updated": "2026-02-01",
        } if candidate in ("1.52.5", "v1.52.5.x") else None,
    )

    latest, error = sources.fetch_verified_candidates(
        verify_type="dockerhub-tags",
        verify_url="https://hub.docker.com/r/example/app",
        index_type="github-tags",
        index_url="https://github.com/example/app",
        current_version="v1.52.4.x",
    )

    assert error is None
    assert latest == {"version": "v1.52.5.x", "last_updated": "2026-02-01"}


def test_dockerhub_verify_preserves_v_prefixed_tag_query(monkeypatch):
    calls = []

    def fake_get_json(url, params=None, headers=None):
        calls.append(params["name"])
        results = [{"name": "v0.64.1.x", "last_updated": "2026-10-07"}] if params["name"] == "v0.64.1.x" else []
        return {"results": results}, None

    monkeypatch.setattr(sources, "_get_json", fake_get_json)

    result = sources._dockerhub_verify(
        "https://hub.docker.com/v2/repositories/metabase/metabase/tags",
        "v0.64.1.x",
        100,
    )

    assert result == {"version": "v0.64.1.x", "last_updated": "2026-10-07"}
    assert calls == ["v0.64.1.x"]


def test_variant_registry_search_overrides_plain_release_index(monkeypatch):
    calls = []

    def tags(url, name, page_size):
        calls.append(name)
        if name == "-lts":
            return [{"name": "v0.65-lts", "last_updated": "2026-10-30"}], None
        return [{"name": "v0.70", "last_updated": "2026-10-30"}], None

    monkeypatch.setattr(sources, "_dockerhub_tags", tags)
    monkeypatch.setattr(sources, "_github_tags_raw", lambda *args: pytest.fail("image channel must not be discarded"))
    latest, error = sources.fetch_verified_candidates(
        "dockerhub-tags", "https://hub.docker.com/r/org/demo", "github-tags",
        "https://github.com/org/demo", "v0.64-lts",
    )
    assert error is None
    assert latest["version"] == "v0.65-lts"
    assert "-lts" in calls


def test_registry_verification_prefers_plain_tag_over_rootless(monkeypatch):
    monkeypatch.setattr(sources, "_get_json", lambda *args: ({"results": [
        {"name": "28.2-rootless", "last_updated": "2026-10-30"},
        {"name": "28.2", "last_updated": "2026-10-30"},
    ]}, None))
    assert sources._dockerhub_verify("https://example.com", "28.2", 100)["version"] == "28.2"


def test_verified_alternatives_exclude_unavailable_releases(monkeypatch):
    monkeypatch.setattr(sources, "_github_tags_raw", lambda *args: ([
        {"name": tag, "last_updated": ""} for tag in ["1.4.0", "1.3.0", "1.2.0", "1.1.0"]
    ], None))
    monkeypatch.setattr(sources, "_dockerhub_verify", lambda url, candidate, page_size:
        {"version": candidate, "last_updated": ""} if candidate in {"1.3", "1.2", "1.1"} else None)
    result, error = sources.fetch_verified_candidates(
        "dockerhub-tags", "https://hub.docker.com/r/org/demo", "github-tags", "https://github.com/org/demo", "1.0", candidate_limit=3,
    )
    assert error is None
    assert result["version"] == "1.3"
    assert [item["version"] for item in result["candidates"]] == ["1.3", "1.2", "1.1"]


def test_fetch_verified_candidates_skips_minor_tag_equal_to_current(monkeypatch):
    monkeypatch.setattr(
        sources,
        "_github_tags_raw",
        lambda url, page_size: ([{"name": "3.12.1", "last_updated": ""}], None),
    )
    monkeypatch.setattr(
        sources,
        "_dockerhub_api_url",
        lambda url: "https://hub.docker.com/v2/repositories/library/arangodb/tags",
    )
    seen = []

    def verify(api_url, candidate, page_size):
        seen.append(candidate)
        if candidate in ("3.12", "3.12.1"):
            return {"version": candidate, "last_updated": "2026-10-01"}
        return None

    monkeypatch.setattr(sources, "_dockerhub_verify", verify)

    latest, error = sources.fetch_verified_candidates(
        verify_type="dockerhub-tags",
        verify_url="https://hub.docker.com/_/arangodb",
        index_type="github-tags",
        index_url="https://github.com/arangodb/arangodb",
        current_version="3.12",
    )

    assert error is None
    assert latest == {"version": "3.12.1", "last_updated": "2026-10-01"}
    assert "3.12" not in seen


def test_fetch_ecr_public_uses_paginated_tags(monkeypatch):
    monkeypatch.setattr(sources, "_ecr_public_repository", lambda url: ("gravitational", "teleport-distroless"))
    monkeypatch.setattr(sources, "_ecr_public_token", lambda namespace, image: ("token", None))
    pages = [
        (["18.10.4", "18.10.6", "sha256-abc.sig"], "https://public.ecr.aws/next"),
        (["18.11", "18.11.7"], None),
    ]
    calls = []

    def fake_page(namespace, image, token, page_size, next_url=None):
        calls.append(next_url)
        return pages[len(calls) - 1][0], pages[len(calls) - 1][1], None

    monkeypatch.setattr(sources, "_ecr_public_tags_page", fake_page)

    latest, error = sources.fetch_candidates(
        "ecr-public",
        "https://gallery.ecr.aws/gravitational/teleport-distroless",
        "18.10",
        page_size=1000,
    )

    assert error is None
    assert latest == {"version": "18.11", "last_updated": ""}
    assert calls == [None, "https://public.ecr.aws/next"]


def test_fetch_registry_v2_reads_paginated_tags(monkeypatch):
    pages = [
        ({"tags": ["1.0", "1.1"]}, {"Link": '<https://registry.example/v2/team/app/tags/list?n=2&last=1.1>; rel="next"'}, None, None),
        ({"tags": ["1.2"]}, {}, None, None),
    ]
    calls = []

    def fake_registry_json(url, params=None, headers=None):
        calls.append((url, params))
        return pages[len(calls) - 1]

    monkeypatch.setattr(sources, "_registry_json", fake_registry_json)

    latest, error = sources.fetch_candidates(
        "registry-v2-tags",
        "https://registry.example/team/app",
        "1.0",
        page_size=2,
    )

    assert error is None
    assert latest["version"] == "1.2"
    assert calls == [
        ("https://registry.example/v2/team/app/tags/list", {"n": 2}),
        ("https://registry.example/v2/team/app/tags/list?n=2&last=1.1", None),
    ]


def test_fetch_verified_candidates_verifies_ecr_public_tag(monkeypatch):
    monkeypatch.setattr(
        sources,
        "_github_releases_raw",
        lambda url, page_size: ([{"name": "v18.10.0"}, {"name": "v18.11.0"}], None),
    )
    monkeypatch.setattr(sources, "_ecr_public_repository", lambda url: ("gravitational", "teleport-distroless"))
    monkeypatch.setattr(sources, "_ecr_public_token", lambda namespace, image: ("token", None))
    monkeypatch.setattr(
        sources,
        "_ecr_public_manifest_exists",
        lambda namespace, image, tag, token: (tag == "18.11", None),
    )

    latest, error = sources.fetch_verified_candidates(
        verify_type="ecr-public",
        verify_url="https://gallery.ecr.aws/gravitational/teleport-distroless",
        index_type="github-releases",
        index_url="https://github.com/gravitational/teleport/releases",
        current_version="18.10",
    )

    assert error is None
    assert latest == {"version": "18.11", "last_updated": ""}


def test_github_releases_raw_uses_releases_endpoint_and_skips_drafts(monkeypatch):
    called = []

    def fake_get_json(url, params=None, headers=None):
        called.append((url, params, headers))
        return (
            [
                {"tag_name": "v1.2.0", "published_at": "2026-01-01", "draft": False},
                {"tag_name": "v1.3.0-rc.1", "published_at": "2026-02-01", "draft": True},
            ],
            None,
        )

    monkeypatch.setattr(sources, "_get_json", fake_get_json)

    tags, error = sources._github_releases_raw("https://github.com/owner/repo/releases", 100)

    assert error is None
    assert called[0][0] == "https://api.github.com/repos/owner/repo/releases"
    assert tags == [{"name": "v1.2.0", "last_updated": "2026-01-01"}]


def test_fetch_verified_candidates_returns_no_update_when_release_index_has_nothing_newer(monkeypatch):
    monkeypatch.setattr(
        sources,
        "_github_releases_raw",
        lambda url, page_size: ([{"name": "v18.10.0", "last_updated": ""}], None),
    )
    called = []
    monkeypatch.setattr(sources, "_github_tags_raw", lambda *args, **kwargs: called.append("tags") or ([], None))

    latest, error = sources.fetch_verified_candidates(
        verify_type="ecr-public",
        verify_url="https://gallery.ecr.aws/gravitational/teleport-distroless",
        index_type="github-releases",
        index_url="https://github.com/gravitational/teleport/releases",
        current_version="18.10",
    )

    assert error is None
    assert latest is None
    assert called == []
