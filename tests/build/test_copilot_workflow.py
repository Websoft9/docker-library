from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import yaml

from _helpers import REPO_ROOT


def workflow_step(path: str, job: str, name: str) -> str:
    workflow = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    return next(step["run"] for step in workflow["jobs"][job]["steps"] if step.get("name") == name)


def executable(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/bash\nset -eu\n" + text + "\n", encoding="utf-8")
    path.chmod(0o755)


def test_ready_marks_only_latest_successful_copilot_session(tmp_path):
    mock_bin = tmp_path / "bin"
    executable(
        mock_bin / "gh",
        'printf "%s\\n" "$*" >> "$CALLS"\n'
        'case "$*" in\n'
        '  *"actions/runs?"*) printf "%s\\n" "$LATEST_RUN" ;;\n'
        '  *"pulls?"*) printf "%s\\n" "$PR" ;;\n'
        '  "pr ready "*) ;;\n'
        '  *) exit 1 ;;\n'
        'esac',
    )
    env = os.environ | {
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "GH_TOKEN": "test",
        "REPOSITORY": "Websoft9/docker-library",
        "HEAD_BRANCH": "copilot/update-example",
        "EVENT_NAME": "workflow_run",
        "RUN_ID": "42",
        "CALLS": str(tmp_path / "calls"),
        "LATEST_RUN": json.dumps({"id": 42, "status": "completed", "conclusion": "success"}),
        "PR": json.dumps({"number": 12, "draft": True, "head": {"ref": "copilot/update-example", "repo": {"full_name": "Websoft9/docker-library"}}}),
    }
    script = workflow_step(".github/workflows/copilot-pr-ready.yml", "prepare", "Mark completed Copilot PRs ready")

    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "pr ready 12 --repo Websoft9/docker-library" in (tmp_path / "calls").read_text()

    (tmp_path / "calls").unlink()
    env["LATEST_RUN"] = json.dumps({"id": 43, "status": "in_progress", "conclusion": None})
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "pr ready" not in (tmp_path / "calls").read_text()


def test_e2e_readiness_and_sync_retry_after_startup_failure(tmp_path):
    mock_bin = tmp_path / "bin"
    executable(mock_bin / "date", 'printf "1000\\n"')
    executable(mock_bin / "sleep", 'exit 0')
    executable(mock_bin / "timeout", 'while [[ "$1" == --* ]]; do shift; done\nshift\nexec "$@"')
    executable(
        mock_bin / "ssh",
        'count=$(cat "$SSH_COUNT" 2>/dev/null || true)\n'
        'count=${count:-0}; count=$((count + 1)); printf "%s" "$count" > "$SSH_COUNT"\n'
        '[ "$count" -ge 2 ]',
    )
    executable(
        tmp_path / ".venv/bin/libs",
        'count=$(cat "$SYNC_COUNT" 2>/dev/null || true)\n'
        'count=${count:-0}; count=$((count + 1)); printf "%s" "$count" > "$SYNC_COUNT"\n'
        '[ "$count" -ge 2 ]',
    )
    env = os.environ | {
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "HOST": "192.0.2.1",
        "APPS": "odoo",
        "DEADLINE": "1300",
        "SSH_COUNT": str(tmp_path / "ssh_count"),
        "SYNC_COUNT": str(tmp_path / "sync_count"),
    }
    script = workflow_step(".github/workflows/pr-checks.yml", "provision-e2e", "Wait for appstore readiness and sync applications")
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True, timeout=5)

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "ssh_count").read_text() == "2"
    assert (tmp_path / "sync_count").read_text() == "2"

    env["DEADLINE"] = "1000"
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True, timeout=5)
    assert result.returncode != 0
    assert "5-minute post-SSH budget" in result.stderr


def test_e2e_skips_superseded_commit_before_reading_applications(tmp_path):
    mock_bin = tmp_path / "bin"
    executable(
        mock_bin / "gh",
        'printf "%s\\n" "$*" >> "$CALLS"\n'
        'printf "true\\ttrue\\tnewer-commit\\n"',
    )
    output = tmp_path / "output"
    env = os.environ | {
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "REPOSITORY": "Websoft9/docker-library",
        "PR_NUMBER": "12",
        "HEAD_SHA": "checked-commit",
        "GITHUB_OUTPUT": str(output),
        "CALLS": str(tmp_path / "calls"),
    }
    script = workflow_step(".github/workflows/pr-checks.yml", "provision-e2e", "Detect changed applications")
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert output.read_text() == "list=\n"
    assert "/files" not in (tmp_path / "calls").read_text()


def test_e2e_superseded_environment_is_not_announced(tmp_path):
    mock_bin = tmp_path / "bin"
    executable(mock_bin / "gh", 'printf "newer-commit\\n"')
    env = os.environ | {
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "REPOSITORY": "Websoft9/docker-library",
        "PR_NUMBER": "12",
        "HEAD_SHA": "checked-commit",
        "GITHUB_OUTPUT": str(tmp_path / "output"),
    }
    script = workflow_step(".github/workflows/pr-checks.yml", "provision-e2e", "Report test environment")
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "output").exists()
    assert not (tmp_path / "e2e-comment.md").exists()
