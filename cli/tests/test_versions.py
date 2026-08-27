from __future__ import annotations

from datetime import date

from libs import versions


def test_parse_target_date_and_cadence_matches():
    assert versions._parse_target_date("2026-08-20") == date(2026, 8, 20)
    assert versions._cadence_matches("weekly", date(2026, 8, 17)) is True
    assert versions._cadence_matches("weekly", date(2026, 8, 20)) is False
    assert versions._cadence_matches("monthly", date(2026, 8, 1)) is True
    assert versions._cadence_matches("quarterly", date(2026, 10, 1)) is True


def test_resolve_source_type_uses_upstream_image():
    assert versions.resolve_source_type({"upstream": {"image": "ghcr.io/org/app"}}) == "ghcr-tags"
    assert versions.resolve_source_type({"upstream": {"image": "https://hub.docker.com/_/x/tags"}}) == "dockerhub-tags"
    assert versions.resolve_source_type({}) == "unknown"


def test_scan_apps_plan_only_uses_current_versions_without_network(repo_fixture, app_factory):
    app_factory("wordpress", variables={
        "name": "wordpress",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/wordpress/tags"},
        "edition": [{"dist": "community", "version": ["6.9", "latest"]}],
    })

    result = versions.scan_apps(plan_only=True, app_filter="wordpress")

    assert result == [{
        "name": "wordpress",
        "status": "active",
        "cadence": "monthly",
        "update_policy": "patch-minor",
        "selected_by": "all-active",
        "target_date": date.today().isoformat(),
        "current_version": ["6.9", "latest"],
        "upstream_image": "https://hub.docker.com/_/wordpress/tags",
        "source_type": "dockerhub-tags",
        "release": True,
    }]


def test_batch_scan_skips_release_false_apps(repo_fixture, app_factory, monkeypatch):
    app_factory("draft-app", variables={
        "name": "draft-app",
        "release": False,
        "upstream": {"image": "https://hub.docker.com/_/draft/tags"},
        "edition": [{"dist": "community", "version": ["1.0"]}],
    })
    calls = []
    monkeypatch.setattr(versions, "fetch_candidates", lambda *args, **kwargs: calls.append(args) or (None, "unexpected"))
    monkeypatch.setattr(versions, "fetch_verified_candidates", lambda *args, **kwargs: calls.append(args) or (None, "unexpected"))

    result = versions.scan_apps()

    assert calls == []
    assert result[0]["error"] == "App release=false"
    assert result[0]["latest_version"] is None
    assert result[0]["release"] is False


def test_single_app_scan_probes_even_when_release_false(repo_fixture, app_factory, monkeypatch):
    app_factory("draft-app", variables={
        "name": "draft-app",
        "release": False,
        "upstream": {"image": "https://hub.docker.com/_/draft/tags"},
        "edition": [{"dist": "community", "version": ["1.0"]}],
    })
    monkeypatch.setattr(versions, "fetch_candidates", lambda *args, **kwargs: ({"version": "1.1", "last_updated": "2026-01-01"}, None))

    result = versions.scan_apps(app_filter="draft-app")

    assert result[0]["latest_version"] == {"version": "1.1", "last_updated": "2026-01-01"}
    assert result[0]["release"] is False
    assert "error" not in result[0]


def test_scan_apps_uses_fetch_candidates_when_release_enabled(repo_fixture, app_factory, monkeypatch):
    app_factory("demo", variables={
        "name": "demo",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0"]}],
    })
    monkeypatch.setattr(versions, "fetch_candidates", lambda *args, **kwargs: ({"version": "1.1", "last_updated": "2026-01-01"}, None))

    result = versions.scan_apps(app_filter="demo")

    assert result[0]["latest_version"] == {"version": "1.1", "last_updated": "2026-01-01"}
