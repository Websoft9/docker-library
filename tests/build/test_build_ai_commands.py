from __future__ import annotations

import json
from pathlib import Path

from _helpers import REPO_ROOT, load_build_module


builder = load_build_module("build_ai_commands", REPO_ROOT / "ci" / "scripts" / "build_ai_commands.py")


def test_manifest_commands_are_unique_and_skills_exist():
    specs = builder.load_specs(builder.MANIFEST_PATH)
    command_ids = {spec.command_id for spec in specs}
    assert len(command_ids) == len(specs)

    for spec in specs:
        skill_path = REPO_ROOT / "skills" / spec.skill / "SKILL.md"
        assert skill_path.exists(), f"missing skill for {spec.command_id}: {skill_path}"


def test_generated_outputs_match_repository_files():
    specs = builder.load_specs(builder.MANIFEST_PATH)
    expected = builder.expected_outputs(REPO_ROOT, specs)

    for path, content in expected.items():
        assert path.exists(), f"missing generated file: {path}"
        assert path.read_text(encoding="utf-8") == content, f"outdated generated file: {path}"

    for root in (
        REPO_ROOT / ".opencode" / "command",
        REPO_ROOT / ".github" / "prompts",
        REPO_ROOT / ".codex" / "prompts",
    ):
        expected_paths = {path for path in expected if path.parent == root}
        actual_paths = set(root.glob("*.md")) | set(root.glob("*.prompt.md"))
        assert actual_paths == expected_paths, f"unexpected generated files under {root}"


def test_find_stale_outputs_and_clean(tmp_path):
    specs = builder.load_specs(builder.MANIFEST_PATH)
    expected = builder.expected_outputs(tmp_path, specs[:1])
    builder.write_outputs(expected)

    stale_path = tmp_path / ".github" / "prompts" / "libs-stale.prompt.md"
    stale_path.parent.mkdir(parents=True, exist_ok=True)
    stale_path.write_text("stale", encoding="utf-8")

    stale = builder.find_stale_outputs(tmp_path, expected)
    assert stale == [stale_path]

    removed = builder.remove_stale_outputs(stale)
    assert removed == [stale_path]
    assert not stale_path.exists()


def test_main_check_detects_drift_without_writing(tmp_path, monkeypatch):
    manifest = tmp_path / "skills" / "commands.manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "commands": [
            {
                "id": "libs-demo",
                "description": "Demo command.",
                "skill": "install-app",
                "argument_hint": "<app>",
                "usage": "/libs-demo <app>",
            }
        ]
    }
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(builder, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(builder, "MANIFEST_PATH", manifest)

    rc = builder.main(["--check"])
    assert rc == 1

    opencode_target = tmp_path / ".opencode" / "command" / "libs-demo.md"
    assert not opencode_target.exists()
