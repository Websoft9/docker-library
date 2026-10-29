from __future__ import annotations

import subprocess
from types import SimpleNamespace

import pytest

from _helpers import REPO_ROOT, load_build_module


candidate = load_build_module("image_candidate_test", REPO_ROOT / "ci/scripts/image_candidate.py")


@pytest.mark.parametrize("tags", [
    ["example/app:dev-abc1234", "example/app:dev-src-123"],
    ["example/app:dev-abc1234", "example/app:dev-latest", "example/app:dev-src-123"],
])
def test_reuse_retags_exact_digest_without_building(monkeypatch, tags):
    calls = []
    digest = "sha256:" + "a" * 64

    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout=digest, stderr="")

    monkeypatch.setattr(candidate.subprocess, "run", run)
    assert candidate.reuse_candidate({"w9_repo": "example/app", "context_tag": "dev-src-123", "tags": tags})
    assert all("build" not in call for call in calls)
    retags = calls[1:]
    assert len(retags) == len(tags) - 1
    assert all(call[-1] == f"example/app@{digest}" for call in retags)
    assert all("--prefer-index=false" in call for call in retags)


@pytest.mark.parametrize("detail,missing", [
    ("manifest unknown", True),
    ("unauthorized: repository not found", False),
    ("connection timed out", False),
])
def test_only_confirmed_missing_manifest_allows_rebuild(monkeypatch, detail, missing):
    monkeypatch.setattr(candidate.subprocess, "run", lambda *a, **k: SimpleNamespace(
        returncode=1, stdout="", stderr=detail,
    ))
    plan = {"w9_repo": "example/app", "context_tag": "dev-src-123", "tags": []}
    if missing:
        assert candidate.reuse_candidate(plan) is False
    else:
        with pytest.raises(RuntimeError, match="Cannot inspect"):
            candidate.reuse_candidate(plan)
