from __future__ import annotations

import base64
import json

import pytest

from _helpers import REPO_ROOT, load_build_module


review = load_build_module(
    "maintenance_scan_review",
    REPO_ROOT / "ci" / "scripts" / "maintenance_scan_review.py",
)


def test_build_scan_review_issue_contains_full_snapshot_and_owner_command():
    result = review.build_scan_review_issue(
        [
            {
                "name": "wordpress",
                "cadence": "weekly",
                "current_version": ["6.9", "latest"],
                "latest_version": {"version": "7.0", "last_updated": "2026-10-20"},
                "version_status": "update-available",
                "update_policy": "patch-minor",
            },
            {
                "name": "mysql",
                "cadence": "monthly",
                "current_version": ["9.5"],
                "error": "registry timeout",
            },
        ],
        "12345",
        "https://github.com/Websoft9/docker-library/actions/runs/12345",
        "2026-10-26",
    )

    assert result["title"] == "Maintenance scan review: 2026-10-26 (run 12345)"
    assert "<!-- libs:workflow=scan-review -->" in result["body"]
    assert "| wordpress | 6.9 | **7.0 (recommended)** | update-available | — |" in result["body"]
    assert "| mysql | 9.5 | — | undetermined | registry timeout |" in result["body"]
    assert "<!-- libs:approval-start -->" in result["body"]
    assert "<!-- libs:approval-end -->" in result["body"]
    assert "- [ ] wordpress | target: 7.0" in result["body"]
    assert "- [ ] mysql | target: unknown" in result["body"]
    assert "## How to start" in result["body"]
    assert "/approve-updates" in result["body"]

    marker = review.DATA_MARKER_RE.search(result["body"])
    assert marker
    encoded = marker.group(1) + "=" * (-len(marker.group(1)) % 4)
    payload = json.loads(base64.urlsafe_b64decode(encoded))
    assert payload["run_id"] == "12345"
    assert [item["app"] for item in payload["items"]] == ["wordpress", "mysql"]
    assert payload["items"][0]["current"] == ["6.9"]
    assert payload["items"][1]["status"] == "undetermined"


def test_report_links_registry_and_preserves_exact_current_tags():
    issue = review.build_scan_review_issue([
        {"name": "inngest", "upstream_image": "https://hub.docker.com/r/inngest/inngest",
         "current_version": ["v1.46.0", "latest"]},
        {"name": "metabase", "current_version": ["0.64.1.x"]},
    ], "1", "https://example.com", "2026-10-30")
    assert "| [inngest](https://hub.docker.com/r/inngest/inngest) | v1.46.0 |" in issue["body"]
    assert "| metabase | 0.64.1.x |" in issue["body"]


def test_report_lists_three_candidates_but_approval_uses_first():
    issue = review.build_scan_review_issue([{
        "name": "metabase", "current_version": ["v0.64-lts"],
        "latest_version": {"version": "v0.65-lts"},
        "latest_candidates": [{"version": tag} for tag in ["v0.65-lts", "v0.66", "v0.65-core", "v0.67"]],
    }], "1", "https://example.com", "2026-10-30")
    assert "**v0.65-lts (recommended)**<br>v0.66<br>v0.65-core" in issue["body"]
    assert "v0.67" not in issue["body"]
    assert "- [ ] metabase | target: v0.65-lts" in issue["body"]


def test_parse_approval_accepts_only_apps_in_parent_scan(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = tmp_path / "apps" / "wordpress"
    app.mkdir(parents=True)
    (app / "variables.json").write_text("{}", encoding="utf-8")
    issue = review.build_scan_review_issue(
        [{"name": "wordpress", "current_version": ["6.9"], "version_status": "update-available"}],
        "12345",
        "https://github.com/Websoft9/docker-library/actions/runs/12345",
        "2026-10-26",
    )

    result = review.parse_approval(issue["body"], "/approve-updates wordpress")

    assert result["run_id"] == "12345"
    assert result["apps"] == ["wordpress"]
    assert result["items"][0]["app"] == "wordpress"


def test_parse_approval_uses_checked_checklist_and_target(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = tmp_path / "apps" / "wordpress"
    app.mkdir(parents=True)
    (app / "variables.json").write_text("{}", encoding="utf-8")
    issue = review.build_scan_review_issue(
        [
            {
                "name": "wordpress",
                "current_version": ["6.9"],
                "latest_version": {"version": "7.0"},
                "version_status": "update-available",
            },
            {
                "name": "mysql",
                "current_version": ["9.5"],
                "latest_version": {"version": "9.6"},
                "version_status": "update-available",
            },
        ],
        "12345",
        "https://github.com/Websoft9/docker-library/actions/runs/12345",
        "2026-10-26",
    )
    body = issue["body"].replace(
        "- [ ] wordpress | target: 7.0",
        "- [x] wordpress | target: 7.1",
    )

    result = review.parse_approval(body, "/approve-updates")

    assert result["apps"] == ["wordpress"]
    assert result["items"][0]["target"] == "7.1"


def test_approved_target_drives_child_title_and_initial_assignment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = tmp_path / "apps/metabase"
    app.mkdir(parents=True)
    (app / "variables.json").write_text("{}")
    issue = review.build_scan_review_issue(
        [{"name": "metabase", "latest_version": {"version": "v0.65.x"}}],
        "1", "https://example.com/run", "2026-10-30",
    )
    body = issue["body"].replace("- [ ] metabase | target: v0.65.x", "- [x] metabase | target: v0.64-lts")
    approved = review.parse_approval(body, "/approve-updates")
    child = review.build_update_child(approved["items"][0], "2209")
    assert child["title"] == "Update: metabase, target version: v0.64-lts"
    assert "Initial PR title: Update metabase to v0.64-lts" in child["body"]
    assert child["body"].index("Target version: v0.64-lts") < child["body"].index("Candidate version: v0.65.x")
    assert "v0.64-lts" in child["instructions"]
    assert "v0.65.x" not in child["instructions"]

    cleared = body.replace("target: v0.64-lts", "target: unknown")
    approved = review.parse_approval(cleared, "/approve-updates")
    assert approved["items"][0]["target"] is None
    with pytest.raises(ValueError, match="explicit approval target"):
        review.build_update_child(approved["items"][0], "2209")


def test_parse_approval_requires_a_checked_item_for_empty_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = tmp_path / "apps" / "wordpress"
    app.mkdir(parents=True)
    (app / "variables.json").write_text("{}", encoding="utf-8")
    issue = review.build_scan_review_issue(
        [{"name": "wordpress", "current_version": ["6.9"], "version_status": "update-available"}],
        "12345",
        "https://github.com/Websoft9/docker-library/actions/runs/12345",
        "2026-10-26",
    )

    with pytest.raises(ValueError, match="Check at least one app"):
        review.parse_approval(issue["body"], "/approve-updates")


@pytest.mark.parametrize(
    ("body", "comment", "message"),
    [
        ("not a scan review", "/approve-updates wordpress", "not a maintenance scan review"),
        ("<!-- libs:workflow=scan-review -->", "/approve-updates wordpress", "no valid scan-review data"),
    ],
)
def test_parse_approval_requires_scan_snapshot(body, comment, message):
    with pytest.raises(ValueError, match=message):
        review.parse_approval(body, comment)


def test_parse_approval_rejects_apps_not_in_scan(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = tmp_path / "apps" / "mysql"
    app.mkdir(parents=True)
    (app / "variables.json").write_text("{}", encoding="utf-8")
    issue = review.build_scan_review_issue(
        [{"name": "wordpress", "current_version": ["6.9"], "version_status": "update-available"}],
        "12345",
        "https://github.com/Websoft9/docker-library/actions/runs/12345",
        "2026-10-26",
    )

    with pytest.raises(ValueError, match="App is not part of this scan"):
        review.parse_approval(issue["body"], "/approve-updates mysql")


def test_parse_approval_rejects_duplicate_and_non_command_text():
    issue = review.build_scan_review_issue(
        [{"name": "wordpress", "current_version": ["6.9"], "version_status": "update-available"}],
        "12345",
        "https://github.com/Websoft9/docker-library/actions/runs/12345",
        "2026-10-26",
    )

    with pytest.raises(ValueError, match="exactly"):
        review.parse_approval(issue["body"], "Please /approve-updates wordpress")
    with pytest.raises(ValueError, match="only appear once"):
        review.parse_approval(issue["body"], "/approve-updates wordpress, wordpress")


def test_parse_approval_rejects_malformed_scan_items():
    encoded = base64.urlsafe_b64encode(
        json.dumps({"run_id": "1", "items": {"wordpress": {}}}).encode()
    ).decode().rstrip("=")
    body = f"<!-- libs:workflow=scan-review -->\n<!-- libs:scan-review-data:{encoded} -->"

    with pytest.raises(ValueError, match="data marker is invalid"):
        review.parse_approval(body, "/approve-updates wordpress")
