from __future__ import annotations

from pathlib import Path

import pytest

from libs import repo


def test_repo_root_resolves_from_repository_root(repo_fixture):
    assert repo.repo_root() == repo_fixture.resolve()
    assert repo.repo_path("apps") == repo_fixture / "apps"


def test_repo_root_resolves_from_nested_subdirectory(repo_fixture, monkeypatch: pytest.MonkeyPatch):
    nested = repo_fixture / "apps" / "wordpress"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    assert repo.repo_root() == repo_fixture.resolve()


def test_relative_repo_path_returns_relative_path_inside_repo(repo_fixture):
    target = repo_fixture / "apps" / "wordpress"
    target.mkdir()

    assert repo.relative_repo_path(target) == "apps/wordpress"


def test_relative_repo_path_returns_absolute_path_outside_repo(repo_fixture):
    outside = repo_fixture.parent / "elsewhere.txt"

    assert repo.relative_repo_path(outside) == str(outside)


def test_repo_root_raises_outside_repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match="docker-library repository root not found"):
        repo.repo_root()
