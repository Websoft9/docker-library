from __future__ import annotations

from datetime import date, timedelta

import pytest

from libs import scan_state, versions


def test_parse_target_date():
    assert versions._parse_target_date("2026-08-20") == date(2026, 8, 20)
    assert versions._parse_target_date(None) == date.today()


def test_resolve_source_type_uses_upstream_image():
    assert versions.resolve_source_type({"upstream": {"image": "ghcr.io/org/app"}}) == "ghcr-tags"
    assert versions.resolve_source_type({"upstream": {"image": "https://hub.docker.com/_/x/tags"}}) == "dockerhub-tags"
    assert versions.resolve_source_type({"upstream": {"image": "https://gallery.ecr.aws/gravitational/teleport-distroless"}}) == "ecr-public"
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
    assert result[0]["version_status"] == "update-available"


def test_scan_apps_reports_same_minor_patch_as_covered(repo_fixture, app_factory, monkeypatch):
    app_factory("grafana", variables={
        "name": "grafana",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/r/grafana/grafana"},
        "edition": [{"dist": "community", "version": ["13.2", "latest"]}],
    })
    monkeypatch.setattr(
        versions,
        "fetch_candidates",
        lambda *args, **kwargs: ({"version": "13.2.4", "last_updated": "2026-10-13"}, None),
    )

    result = versions.scan_apps(app_filter="grafana")

    assert result[0]["version_status"] == "covered-by-current-minor-tag"


def _variables(name: str, version: str = "1.0") -> dict:
    return {
        "name": name,
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": [version]}],
    }


def test_scan_apps_due_requires_state(repo_fixture, app_factory):
    app_factory("demo", variables=_variables("demo"))

    with pytest.raises(ValueError):
        versions.scan_apps(selection="due", target_date="2026-10-25")


def test_scan_apps_due_selection_uses_state_and_limit(repo_fixture, app_factory, monkeypatch):
    app_factory("alpha", variables=_variables("alpha"))
    app_factory("beta", variables=_variables("beta"))
    calls = []
    monkeypatch.setattr(
        versions,
        "fetch_candidates",
        lambda *args, **kwargs: calls.append(args) or (None, "boom"),
    )
    state = {
        "apps": {
            "alpha": {"ok_at": "2026-01-01T00:00:00Z", "attempt_at": "2026-01-01T00:00:00Z"},
            "beta": {"ok_at": "2026-01-01T00:00:00Z", "attempt_at": "2026-01-02T00:00:00Z"},
        }
    }

    result = versions.scan_apps(
        selection="due",
        state=state,
        target_date="2026-10-25",
        limit=1,
    )

    assert [item["name"] for item in result] == ["alpha"]
    assert len(calls) == 1


def test_scan_apps_due_skips_never_checked_app_outside_slot_window(repo_fixture, app_factory):
    app_factory("demo", variables=_variables("demo"))
    interval = scan_state.INTERVAL_DAYS["monthly"]
    slot = scan_state.stable_slot("demo", interval)
    day = date.fromordinal((date(2026, 1, 1).toordinal() // interval) * interval + slot + 2)

    result = versions.scan_apps(
        selection="due",
        state={"apps": {}},
        target_date=day.isoformat(),
    )

    assert result == []


def test_scan_apps_rejects_corrupt_state_entry(repo_fixture, app_factory):
    app_factory("demo", variables=_variables("demo"))

    with pytest.raises(scan_state.ScanStateError):
        versions.scan_apps(
            selection="due",
            state={"apps": {"demo": "bad"}},
            target_date="2026-10-25",
        )


def test_due_selection_skips_release_false_apps(repo_fixture, app_factory):
    variables = _variables("draft-app")
    variables["release"] = False
    app_factory("draft-app", variables=variables)
    state = {"apps": {"draft-app": {"ok_at": "2026-01-01T00:00:00Z"}}}

    result = versions.scan_apps(selection="due", state=state, target_date="2026-10-25")

    assert result == []


def test_scan_apps_rejects_non_object_state_apps(repo_fixture, app_factory):
    app_factory("demo", variables=_variables("demo"))

    with pytest.raises(scan_state.ScanStateError):
        versions.scan_apps(selection="due", state={"apps": []}, target_date="2026-10-25")
