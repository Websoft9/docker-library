from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import yaml
import pytest

from _helpers import REPO_ROOT


def workflow_step(path: str, job: str, name: str) -> str:
    workflow = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    return next(step["run"] for step in workflow["jobs"][job]["steps"] if step.get("name") == name)


def executable(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/bash\nset -eu\n" + text + "\n", encoding="utf-8")
    path.chmod(0o755)


def test_handoff_starts_check_for_completed_agent(tmp_path):
    mock_bin = tmp_path / "bin"
    executable(
        mock_bin / "gh",
        'printf "%s\\n" "$*" >> "$CALLS"\n'
        'case "$*" in\n'
        '  *"actions/runs?"*) printf "%s\\n" "$LATEST_RUN" ;;\n'
        '  *"pulls/12"*) printf "abc123\\n" ;;\n'
        '  *"check-runs"*) printf "99\\n" ;;\n'
        '  *) exit 1 ;;\n'
        'esac',
    )
    env = os.environ | {
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "GH_TOKEN": "test",
        "REPOSITORY": "Websoft9/docker-library",
        "HEAD_BRANCH": "copilot/update-example",
        "AUTHOR": "Copilot",
        "EVENT_NAME": "pull_request_target",
        "HEAD_REPO": "Websoft9/docker-library",
        "HEAD_SHA": "abc123",
        "PR_NUMBER": "12",
        "RUN_URL": "https://example.com/run",
        "GITHUB_OUTPUT": str(tmp_path / "output"),
        "CALLS": str(tmp_path / "calls"),
        "LATEST_RUN": json.dumps({"id": 42, "status": "completed", "conclusion": "success"}),
        "PR": json.dumps({"number": 12, "draft": True, "head": {"ref": "copilot/update-example", "repo": {"full_name": "Websoft9/docker-library"}}}),
    }
    script = workflow_step(".github/workflows/pr-checks.yml", "handoff", "Confirm completed agent and start commit check")

    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output").read_text() == "check_id=99\n"

    (tmp_path / "calls").unlink()
    env["LATEST_RUN"] = json.dumps({"id": 43, "status": "completed", "conclusion": "failure"})
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode != 0
    # A failed handoff must still have a check ID for the finalizer to fail.
    assert "check-runs" in (tmp_path / "calls").read_text()


def test_required_checks_cover_all_pr_changes_and_keep_e2e_at_handoff():
    # BaseLoader keeps the YAML `on` key instead of interpreting it as a boolean.
    workflow = yaml.load(
        (REPO_ROOT / ".github/workflows/pr-checks.yml").read_text(), Loader=yaml.BaseLoader
    )
    assert workflow["on"]["pull_request_target"]["types"] == ["review_requested"]
    assert set(workflow["on"]) == {"pull_request_target", "pull_request"}
    assert workflow["on"]["pull_request"] == {
        "branches": ["main"],
        "types": ["opened", "synchronize", "reopened", "ready_for_review"],
    }
    assert not (REPO_ROOT / ".github/workflows/copilot-pr-ready.yml").exists()
    assignment = yaml.load((REPO_ROOT / ".github/workflows/copilot-issue.yml").read_text(), Loader=yaml.BaseLoader)
    assert assignment["on"]["issues"]["types"] == ["labeled"]
    assert workflow["jobs"]["pr-checks"]["permissions"] == {"contents": "read", "pull-requests": "read"}
    assert all("secrets." not in str(step) for step in workflow["jobs"]["pr-checks"]["steps"])
    assert "pull_request_target" in workflow["jobs"]["provision-e2e"]["if"]
    ready = next(step for step in workflow["jobs"]["report-check"]["steps"] if step["name"] == "Mark successful PR ready")
    assert ready["if"] == "github.event_name == 'pull_request_target' && github.event.pull_request.user.login == 'Copilot'"
    assert "needs" not in workflow["jobs"]["pr-checks"]
    assert "needs" not in workflow["jobs"]["detect-buildable"]


def test_intermediate_copilot_push_does_not_wait_for_agent(tmp_path):
    mock_bin = tmp_path / "bin"
    executable(
        mock_bin / "gh",
        'case "$*" in\n'
        '  *"actions/runs?"*) exit 1 ;;\n'
        '  *"pulls/12"*) printf "abc123\\n" ;;\n'
        '  *"check-runs"*) printf "99\\n" ;;\n'
        '  *) exit 1 ;;\n'
        'esac',
    )
    env = os.environ | {
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "REPOSITORY": "Websoft9/docker-library", "HEAD_REPO": "Websoft9/docker-library",
        "HEAD_SHA": "abc123", "PR_NUMBER": "12", "AUTHOR": "Copilot",
        "EVENT_NAME": "pull_request", "RUN_URL": "https://example.com/run",
        "GITHUB_OUTPUT": str(tmp_path / "output"),
    }
    script = workflow_step(".github/workflows/pr-checks.yml", "handoff", "Confirm completed agent and start commit check")
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output").read_text() == "check_id=99\n"


@pytest.mark.parametrize("result,head,detect,has_images,build,event,draft,handoff,ready", [
    ("success", "abc123", "success", "false", "skipped", "pull_request_target", "true", "success", True),
    ("success", "abc123", "success", "true", "success", "pull_request_target", "true", "success", True),
    ("failure", "abc123", "success", "false", "skipped", "pull_request_target", "true", "success", False),
    ("success", "new-head", "success", "false", "skipped", "pull_request_target", "true", "success", False),
    ("success", "abc123", "failure", "", "skipped", "pull_request_target", "true", "success", False),
    ("success", "abc123", "success", "true", "skipped", "pull_request_target", "true", "success", False),
    ("success", "abc123", "success", "true", "failure", "pull_request_target", "true", "success", False),
    ("success", "abc123", "success", "false", "skipped", "pull_request", "false", "success", True),
    ("success", "abc123", "success", "true", "success", "pull_request", "false", "success", True),
    ("success", "abc123", "success", "true", "failure", "pull_request", "false", "success", False),
    ("success", "abc123", "success", "true", "skipped", "pull_request", "false", "success", False),
    ("success", "abc123", "success", "true", "skipped", "pull_request", "true", "success", True),
    ("success", "abc123", "success", "false", "skipped", "pull_request_target", "true", "failure", False),
])
def test_commit_check_only_unlocks_tested_head(tmp_path, result, head, detect, has_images, build, event, draft, handoff, ready):
    mock_bin = tmp_path / "bin"
    executable(
        mock_bin / "gh",
        'printf "%s\\n" "$*" >> "$CALLS"\n'
        'case "$*" in\n'
        '  *"--jq .head.sha"*) printf "%s\\n" "$CURRENT_HEAD" ;;\n'
        '  *"--jq .draft"*) printf "true\\n" ;;\n'
        'esac',
    )
    env = os.environ | {
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "REPOSITORY": "Websoft9/docker-library",
        "PR_NUMBER": "12",
        "HEAD_SHA": "abc123",
        "CURRENT_HEAD": head,
        "CHECK_ID": "99",
        "RESULT": result,
        "HANDOFF_RESULT": handoff,
        "BUILD_RESULT": build,
        "DETECT_RESULT": detect,
        "HAS_IMAGES": has_images,
        "EVENT_NAME": event,
        "IS_DRAFT": draft,
        "CALLS": str(tmp_path / "calls"),
    }
    script = workflow_step(".github/workflows/pr-checks.yml", "report-check", "Publish commit check")
    response = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    calls = (tmp_path / "calls").read_text()
    assert (response.returncode == 0) == ready
    assert "pr ready" not in calls
    assert f"conclusion={'success' if ready else 'failure'}" in calls


@pytest.mark.parametrize("paths,run_tests", [
    (["docs/runbook.md", "README.md"], False),
    ([".github/workflows/maintenance-scan.yml"], True),
    (["apps/wordpress/.env"], True),
    (["docs/runbook.md", "cli/libs/main.py"], True),
    ([], True),
])
def test_validation_scope_skips_suites_only_for_plain_markdown(tmp_path, paths, run_tests):
    mock_bin = tmp_path / "bin"
    executable(mock_bin / "git", 'printf "%s" "$CHANGED_PATHS" | tr "\\n" "\\0"')
    env = os.environ | {
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "BASE_SHA": "base", "HEAD_SHA": "head",
        "CHANGED_PATHS": "\n".join(paths),
        "GITHUB_OUTPUT": str(tmp_path / "output"),
    }
    script = workflow_step(".github/workflows/pr-checks.yml", "pr-checks", "Select validation scope")
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output").read_text() == f"run_tests={str(run_tests).lower()}\n"


def test_ready_uses_user_token_in_separate_step(tmp_path):
    mock_bin = tmp_path / "bin"
    executable(
        mock_bin / "gh",
        'case "$*" in\n'
        '  *"--jq .draft"*) printf "true\\n" ;;\n'
        '  *"--jq .head.sha"*) printf "abc123\\n" ;;\n'
        '  "pr ready "*) printf "%s" "$GH_TOKEN" > "$TOKEN_USED" ;;\n'
        'esac',
    )
    env = os.environ | {
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "GH_TOKEN": "user-test-token", "REPOSITORY": "Websoft9/docker-library",
        "PR_NUMBER": "12", "HEAD_SHA": "abc123", "TOKEN_USED": str(tmp_path / "token"),
    }
    script = workflow_step(".github/workflows/pr-checks.yml", "report-check", "Mark successful PR ready")
    script = script.replace('${{ github.token }}', 'workflow-test-token')
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "token").read_text() == "user-test-token"


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
