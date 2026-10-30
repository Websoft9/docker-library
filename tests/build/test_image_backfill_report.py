from __future__ import annotations

import io
import json
import zipfile

import yaml

from _helpers import REPO_ROOT, load_build_module

reporter = load_build_module("image_backfill_report_test", REPO_ROOT / "ci/scripts/image_backfill_report.py")


def test_manual_failure_creates_bug_and_rerun_comments(monkeypatch):
    sha = "a" * 40
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("backfill.json", json.dumps({
            "app": "demo", "ref": "0.8.3", "sha": "b" * 40, "workflow_sha": sha, "source_sha": "",
        }))
    monkeypatch.setattr(reporter.subprocess, "check_output", lambda *a, **k: archive.getvalue())
    monkeypatch.setattr(reporter, "context_tag", lambda *a: "dev-src-123")
    issues, writes = [], []

    def pages(endpoint):
        if "/artifacts?" in endpoint:
            return [{"artifacts": [{"id": 7, "name": "image-backfill-1", "expired": False}]}]
        if "/jobs?" in endpoint:
            return [{"jobs": [{"name": "promote (demo)", "conclusion": "failure", "steps": [
                {"name": "Promote dev image", "conclusion": "failure"},
            ]}]}]
        if "/labels?" in endpoint:
            return [[{"name": "bug"}]]
        return [issues]

    def api(endpoint, payload):
        writes.append((endpoint, payload))
        if endpoint.endswith("/issues"):
            issues.append(payload | {"number": 42, "labels": [{"name": "bug"}]})

    monkeypatch.setattr(reporter, "pages", pages)
    monkeypatch.setattr(reporter, "api", api)
    reporter.report("org/repo", "123", "1", sha)
    assert writes[0][1]["labels"] == ["bug"]
    assert writes[0][1]["title"] == "[image-backfill] demo @ 0.8.3"
    assert "dev-src-123" in writes[0][1]["body"]
    assert "Promote dev image" in writes[0][1]["body"]
    reporter.report("org/repo", "124", "2", sha)
    assert writes[1][0].endswith("/issues/42/comments")
    assert "/runs/124/attempts/2" in writes[1][1]["body"]


def test_nonpromote_dispatch_has_no_report_artifact(monkeypatch):
    monkeypatch.setattr(reporter, "pages", lambda endpoint: [{"artifacts": []}])
    monkeypatch.setattr(reporter, "api", lambda *a: (_ for _ in ()).throw(AssertionError("unexpected write")))
    reporter.report("org/repo", "123", "1", "a" * 40)


def test_only_failed_manual_workflow_can_write_issues():
    workflow = yaml.load((REPO_ROOT / ".github/workflows/image-backfill-report.yml").read_text(), Loader=yaml.BaseLoader)
    assert workflow["on"]["workflow_run"]["workflows"] == ["Build image to DockerHub"]
    assert "workflow_dispatch" in workflow["jobs"]["report"]["if"]
    assert "conclusion == 'failure'" in workflow["jobs"]["report"]["if"]
    assert workflow["permissions"]["issues"] == "write"
    builder = yaml.safe_load((REPO_ROOT / ".github/workflows/docker.yml").read_text())
    assert "issues" not in builder["permissions"]
    assert "'promote' || 'build'" in builder["jobs"]["build"]["name"]
    upload = next(step for step in builder["jobs"]["setup"]["steps"] if step.get("name") == "Upload manual backfill request")
    assert "inputs.channel == 'promote'" in upload["if"]
    checkout = next(step for step in builder["jobs"]["build"]["steps"] if step.get("name") == "Checkout code")
    assert "inputs.target_ref" in checkout["with"]["ref"]
    tooling = next(step for step in builder["jobs"]["build"]["steps"] if step.get("name") == "Checkout trusted build tooling")
    assert "inputs.target_ref" not in tooling["with"]["ref"]
