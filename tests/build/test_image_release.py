from __future__ import annotations

import subprocess

import pytest

from _helpers import REPO_ROOT, load_build_module

release = load_build_module("image_release_test", REPO_ROOT / "ci/scripts/image_release.py")


def git(repo, *args):
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def commit(repo):
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "test")


@pytest.fixture
def repo(tmp_path, monkeypatch):
    git(tmp_path, "init", "-q")
    for name in ("demo", "unchanged", "legacy"):
        app = tmp_path / "apps" / name
        app.mkdir(parents=True)
        (app / ".env").write_text("W9_VERSION=1.0\n")
        arg = f"ARG {name.upper()}_VERSION=1.0\n" if name != "legacy" else ""
        (app / "Dockerfile").write_text(arg + "FROM scratch\nCOPY src/ /opt/\n")
        (app / "src").mkdir()
        (app / "src/run.sh").write_text("original\n")
    commit(tmp_path)
    git(tmp_path, "tag", "0.8.0")
    git(tmp_path, "tag", "0.8.1-rc.1")
    git(tmp_path, "tag", "release-21")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_first_release_selects_buildable_apps_only(repo):
    plan = release.release_plan("0.8.0", ["0.8.0"])
    assert plan["apps"] == ["demo", "unchanged"]
    assert plan["all_apps"] is True
    assert plan["range"] == "0.8.0"


def test_docs_and_nonbuild_env_changes_skip_images(repo):
    (repo / "apps/demo/README.md").write_text("docs\n")
    (repo / "apps/demo/.env").write_text("W9_VERSION=1.0\nW9_HTTP_PORT_SET=9000\n")
    commit(repo)
    git(repo, "tag", "0.8.1")
    plan = release.release_plan("0.8.1", ["0.8.0", "0.8.1"])
    assert plan["apps"] == []
    assert plan["has_apps"] is False
    assert plan["from_ref"] == "0.8.0"


def test_changed_inputs_new_and_deleted_dockerfiles(repo):
    (repo / "apps/demo/src/run.sh").write_text("changed\n")
    (repo / "apps/unchanged/Dockerfile").unlink()
    (repo / "apps/legacy/Dockerfile").write_text("ARG LEGACY_VERSION=1.0\nFROM scratch\n")
    new = repo / "apps/new"
    new.mkdir()
    (new / "Dockerfile").write_text("ARG NEW_VERSION=1.0\nFROM scratch\n")
    commit(repo)
    git(repo, "tag", "0.8.1")
    assert release.release_plan("0.8.1", ["0.8.0", "0.8.1"])["apps"] == ["demo", "legacy", "new"]


def test_previous_tag_is_lower_and_reachable(repo):
    git(repo, "tag", "9.0.0")  # Higher version at an ancestor must not be the baseline.
    git(repo, "checkout", "-qb", "unrelated")
    (repo / "branch.txt").write_text("branch\n")
    commit(repo)
    git(repo, "tag", "0.8.9")
    git(repo, "checkout", "-q", "0.8.0")
    (repo / "main.txt").write_text("main\n")
    commit(repo)
    git(repo, "tag", "0.9.0")
    assert release.release_plan("0.9.0", ["0.8.0", "0.8.9", "9.0.0"])["from_ref"] == "0.8.0"


def test_invalid_release_tag_is_rejected(repo):
    with pytest.raises(ValueError, match="stable X.Y.Z"):
        release.release_plan("0.9.0-rc.1", [])


def test_unpublished_tag_is_not_a_release_baseline(repo):
    (repo / "apps/demo/src/run.sh").write_text("changed\n")
    commit(repo)
    git(repo, "tag", "0.8.1")  # Bare tag, not a published Release.
    git(repo, "tag", "0.8.2")
    plan = release.release_plan("0.8.2", ["0.8.0", "0.8.2"])
    assert plan["from_ref"] == "0.8.0"
    assert plan["apps"] == ["demo"]
