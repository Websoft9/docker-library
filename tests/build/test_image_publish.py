from __future__ import annotations

import json
import os
import subprocess
from types import SimpleNamespace

import pytest
import yaml

from _helpers import REPO_ROOT, load_build_module


images = load_build_module("image_publish_test", REPO_ROOT / "ci/scripts/image_publish.py")


def commit(repo):
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run([
        "git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "test",
    ], cwd=repo, check=True)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


def test_sources_require_successful_main_build_with_exact_context(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    app = tmp_path / "apps/demo"
    app.mkdir(parents=True)
    (app / ".env").write_text("W9_REPO=demo-repo\nW9_VERSION=1.0\n")
    (app / "Dockerfile").write_text("ARG DEMO_VERSION=1.0\nFROM scratch\n")
    (app / "package.json").write_text('{"version":"1"}\n')
    old = commit(tmp_path)
    # Only a Dockerfile build input changes the image identity.
    (app / "Dockerfile").write_text("ARG DEMO_VERSION=1.0\nFROM scratch\nLABEL v=2\n")
    built = commit(tmp_path)
    # README is not copied by the Dockerfile, so it must reuse the same image.
    (app / "README.md").write_text("docs only\n")
    commit(tmp_path)
    monkeypatch.chdir(tmp_path)

    def run(sha, **extra):
        return {"head_sha": sha, "conclusion": "success", "event": "push", "head_branch": "main"} | extra

    candidates = images.source_candidates("demo", "example/demo", [{"workflow_runs": [
        run(old), run(built, conclusion="failure"), run(built, head_branch="dev"), run(built),
    ]}])
    assert candidates == [f"example/demo:{images.context_tag('demo')}", f"example/demo:dev-{built[:7]}"]


def test_source_is_pinned_to_digest(monkeypatch):
    digest = "sha256:" + "a" * 64
    monkeypatch.setattr(images.subprocess, "run", lambda *a, **k: SimpleNamespace(
        returncode=0, stdout=digest, stderr="",
    ))
    assert images.resolve_source(["example/demo:dev-src-123"]) == (
        f"example/demo@{digest}", "example/demo:dev-src-123",
    )


def test_missing_context_candidate_uses_verified_commit_candidate(monkeypatch):
    calls = []
    digest = "sha256:" + "b" * 64

    def inspect(command, **kwargs):
        calls.append(command[4])
        if command[4].endswith("missing"):
            return SimpleNamespace(returncode=1, stdout="", stderr="manifest unknown")
        return SimpleNamespace(returncode=0, stdout=digest, stderr="")

    monkeypatch.setattr(images.subprocess, "run", inspect)
    assert images.resolve_source(["example/demo:missing", "example/demo:dev-abc1234"])[0].endswith(digest)
    assert calls == ["example/demo:missing", "example/demo:dev-abc1234"]


def test_registry_errors_are_not_reported_as_missing(monkeypatch):
    monkeypatch.setattr(images.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(images.subprocess, "run", lambda *a, **k: SimpleNamespace(
        returncode=1, stdout="", stderr="unauthorized: access denied",
    ))
    with pytest.raises(ValueError, match="unauthorized: access denied"):
        images.resolve_source(["example/demo:candidate"])


def test_missing_candidates_require_backfill_without_floating_fallback(monkeypatch):
    monkeypatch.setattr(images.subprocess, "run", lambda *a, **k: SimpleNamespace(
        returncode=1, stdout="", stderr="manifest unknown",
    ))
    with pytest.raises(ValueError, match="channel=dev"):
        images.resolve_source(["example/demo:candidate"])


def test_image_workflow_has_single_official_release_caller_and_no_fail_fast():
    workflow = yaml.load((REPO_ROOT / ".github/workflows/docker.yml").read_text(), Loader=yaml.BaseLoader)
    assert "tags" not in workflow["on"]["push"]
    assert "workflow_call" in workflow["on"]
    assert "release" not in workflow["on"]  # appstore invokes it before publishing artifacts
    assert workflow["jobs"]["build"]["strategy"]["fail-fast"] == "false"


@pytest.mark.parametrize("files,expected", [("apps/demo/package.json", ["demo"]), ("docs/guide.md", [])])
def test_main_build_selection_covers_entire_app_context(tmp_path, files, expected):
    app = tmp_path / "apps/demo"
    app.mkdir(parents=True)
    (app / "Dockerfile").write_text("ARG DEMO_VERSION=1.0\nFROM scratch\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    git = bin_dir / "git"
    git.write_text('#!/bin/bash\ncase "$1" in\nrev-parse) printf "head\\n" ;;\ndiff) printf "%s\\n" "$FILES" ;;\n*) exit 1 ;;\nesac\n')
    git.chmod(0o755)
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/docker.yml").read_text())
    script = next(step["run"] for step in workflow["jobs"]["setup"]["steps"] if step.get("id") == "set-matrix")
    output = tmp_path / "output"
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, text=True, capture_output=True, env=os.environ | {
        "PATH": f"{bin_dir}:{os.environ['PATH']}", "FILES": files,
        "EVENT_NAME": "push", "RELEASE_TAG": "", "PR_SHA": "", "BEFORE_SHA": "before",
        "GITHUB_OUTPUT": str(output),
    })
    assert result.returncode == 0, result.stderr
    lines = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert json.loads(lines["matrix"])["app"] == expected
    assert lines["has_apps"] == ("true" if expected else "false")


def test_release_matrix_only_uses_selected_apps(tmp_path):
    for name in ("demo", "unrelated"):
        app = tmp_path / "apps" / name
        app.mkdir(parents=True)
        (app / "Dockerfile").write_text(f"ARG {name.upper()}_VERSION=1.0\nFROM scratch\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    git = bin_dir / "git"
    git.write_text('#!/bin/bash\ncase "$1" in\nrev-parse) printf "head\\n" ;;\nfetch|merge-base) exit 0 ;;\n*) exit 1 ;;\nesac\n')
    git.chmod(0o755)
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/docker.yml").read_text())
    script = next(step["run"] for step in workflow["jobs"]["setup"]["steps"] if step.get("id") == "set-matrix")
    output = tmp_path / "output"
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, text=True, capture_output=True, env=os.environ | {
        "PATH": f"{bin_dir}:{os.environ['PATH']}", "EVENT_NAME": "release", "INPUT_APP": "",
        "RELEASE_TAG": "0.8.3", "RELEASE_APPS": '["demo"]', "PR_SHA": "", "GITHUB_OUTPUT": str(output),
    })
    assert result.returncode == 0, result.stderr
    lines = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert json.loads(lines["matrix"])["app"] == ["demo"]
