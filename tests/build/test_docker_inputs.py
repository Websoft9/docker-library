from __future__ import annotations

import subprocess

import pytest

from _helpers import REPO_ROOT, load_build_module


inputs = load_build_module("docker_inputs_test", REPO_ROOT / "cli/libs/docker_inputs.py")


def commit(repo):
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "test"],
        cwd=repo,
        check=True,
    )
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


def make_app(tmp_path, monkeypatch, dockerfile: str, files: dict[str, str] | None = None):
    app = tmp_path / "apps" / "demo"
    app.mkdir(parents=True)
    (app / ".env").write_text("W9_REPO=demo-repo\nW9_VERSION=1.0\n", encoding="utf-8")
    (app / "Dockerfile").write_text(dockerfile, encoding="utf-8")
    for relative, content in (files or {}).items():
        target = app / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    return app


def test_only_copied_context_files_are_inputs(tmp_path, monkeypatch):
    make_app(
        tmp_path,
        monkeypatch,
        "ARG DEMO_VERSION=1.0\nFROM alpine:3.20\nCOPY src/entrypoint.sh /e\nCOPY src/nested/ /n\n",
        {
            "src/entrypoint.sh": "#!/bin/sh\n",
            "src/nested/a.txt": "a\n",
            "src/not-copied.txt": "ignore me\n",
            "README.md": "readme\n",
        },
    )

    result = inputs.resolve_inputs("demo")

    assert result["files"] == ["Dockerfile", "src/entrypoint.sh", "src/nested/a.txt"]
    assert result["from"] == ["alpine:3.20"]


def test_docs_only_change_reuses_the_image(tmp_path, monkeypatch):
    app = make_app(tmp_path, monkeypatch, "ARG DEMO_VERSION=1.0\nFROM alpine\nCOPY src/app.sh /app.sh\n", {"src/app.sh": "1\n"})
    base = commit(tmp_path)
    (app / "README.md").write_text("docs\n", encoding="utf-8")
    head = commit(tmp_path)
    monkeypatch.setattr(inputs, "repo_root", lambda: tmp_path)

    assert inputs.resolve_inputs("demo", base)["hash"] == inputs.resolve_inputs("demo", head)["hash"]
    assert inputs.changed_apps(base, head) == []


def test_non_copied_source_change_does_not_rebuild(tmp_path, monkeypatch):
    app = make_app(tmp_path, monkeypatch, "ARG DEMO_VERSION=1.0\nFROM alpine\nCOPY src/app.sh /app.sh\n", {"src/app.sh": "1\n"})
    base = commit(tmp_path)
    (app / "src" / "unused.txt").write_text("2\n", encoding="utf-8")
    head = commit(tmp_path)

    assert inputs.changed_apps(base, head) == []


def test_dockerfile_and_build_arg_changes_are_inputs(tmp_path, monkeypatch):
    app = make_app(tmp_path, monkeypatch, "ARG DEMO_VERSION=1.0\nFROM alpine\nCOPY src/app.sh /app.sh\n", {"src/app.sh": "1\n"})
    base = commit(tmp_path)

    (app / "src" / "app.sh").write_text("2\n", encoding="utf-8")
    script_head = commit(tmp_path)
    assert inputs.changed_apps(base, script_head) == ["demo"]

    (app / ".env").write_text("W9_REPO=demo-repo\nW9_VERSION=2.0\n", encoding="utf-8")
    version_head = commit(tmp_path)
    assert inputs.changed_apps(script_head, version_head) == ["demo"]


def test_from_other_stage_is_not_a_context_dependency(tmp_path, monkeypatch):
    make_app(
        tmp_path,
        monkeypatch,
        "ARG DEMO_VERSION=1.0\nFROM alpine AS build\nFROM alpine\nCOPY --from=build /out /out\n",
    )

    result = inputs.resolve_inputs("demo")

    assert result["files"] == ["Dockerfile"]
    assert not result["conservative"]


def test_copy_dot_uses_whole_context_and_honours_dockerignore(tmp_path, monkeypatch):
    make_app(
        tmp_path,
        monkeypatch,
        "ARG DEMO_VERSION=1.0\nFROM alpine\nCOPY . /app\n",
        {"README.md": "docs\n", "src/app.sh": "1\n", ".dockerignore": "README.md\n"},
    )

    result = inputs.resolve_inputs("demo")

    assert "src/app.sh" in result["files"]
    assert "README.md" not in result["files"]


def test_unresolvable_copy_falls_back_to_whole_context(tmp_path, monkeypatch):
    make_app(tmp_path, monkeypatch, "ARG DEMO_VERSION=1.0\nFROM alpine\nCOPY $SRC /app\n", {"README.md": "docs\n"})

    result = inputs.resolve_inputs("demo")

    assert result["conservative"] is True
    assert "README.md" in result["files"]


def test_missing_version_source_is_not_a_build_input(tmp_path, monkeypatch):
    app = make_app(tmp_path, monkeypatch, "ARG DEMO_VERSION=1.0\nFROM alpine\n")
    base = commit(tmp_path)
    (app / "variables.json").write_text("{}\n", encoding="utf-8")
    head = commit(tmp_path)

    assert inputs.changed_apps(base, head) == []


@pytest.mark.parametrize(
    "app,expected",
    [
        ("akeneo", ["Dockerfile", "src/000-default.conf", "src/entrypoint.sh"]),
        ("pocketbase", ["Dockerfile", "src/entrypoint.sh"]),
        ("dsh", ["Dockerfile", "src/entrypoint.sh", "src/nginx.conf"]),
        ("umbraco", ["Dockerfile", "src/appsettings.Production.json", "src/docker-entrypoint.sh"]),
    ],
)
def test_repository_dockerfile_inputs(app, expected, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

    assert inputs.resolve_inputs(app)["files"] == expected


def test_removed_app_is_not_selected_for_build(tmp_path, monkeypatch):
    app = make_app(tmp_path, monkeypatch, "ARG DEMO_VERSION=1.0\nFROM alpine\n")
    base = commit(tmp_path)
    for path in sorted(app.rglob("*"), reverse=True):
        path.unlink() if path.is_file() else path.rmdir()
    app.rmdir()
    head = commit(tmp_path)

    assert inputs.changed_apps(base, head) == []


def test_new_app_is_selected_for_build(tmp_path, monkeypatch):
    (tmp_path / "apps").mkdir()
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    base = commit(tmp_path)
    app = tmp_path / "apps" / "demo"
    app.mkdir()
    (app / ".env").write_text("W9_REPO=demo-repo\nW9_VERSION=1.0\n", encoding="utf-8")
    (app / "Dockerfile").write_text("ARG DEMO_VERSION=1.0\nFROM alpine\n", encoding="utf-8")
    head = commit(tmp_path)

    assert inputs.changed_apps(base, head) == ["demo"]


def test_input_detection_errors_are_not_silently_skipped(tmp_path, monkeypatch):
    make_app(tmp_path, monkeypatch, "ARG DEMO_VERSION=1.0\nFROM alpine\n")
    base = commit(tmp_path)
    monkeypatch.setattr(inputs, "resolve_inputs", lambda *a, **k: (_ for _ in ()).throw(ValueError("bad input")))
    # Force the app to be considered touched while keeping real tree lookup.
    original_git = inputs._git
    monkeypatch.setattr(inputs, "_git", lambda *a, **k: "apps/demo/Dockerfile\n" if a[0] == "diff" else original_git(*a, **k))
    with pytest.raises(ValueError, match="bad input"):
        inputs.changed_apps(base, base)
