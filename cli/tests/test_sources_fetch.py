from __future__ import annotations

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
