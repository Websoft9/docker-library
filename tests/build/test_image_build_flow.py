from __future__ import annotations

import os
import subprocess

import pytest
import yaml

from _helpers import REPO_ROOT


def load(path: str, base_loader: bool = False):
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    return yaml.load(text, Loader=yaml.BaseLoader) if base_loader else yaml.safe_load(text)


def test_pr_checks_builds_images_before_e2e():
    workflow = load(".github/workflows/pr-checks.yml", base_loader=True)
    jobs = workflow["jobs"]

    assert set(jobs) >= {"handoff", "detect-buildable", "build-images", "pr-checks", "report-check", "provision-e2e"}
    build = jobs["build-images"]
    assert build["uses"] == "./.github/workflows/docker.yml"
    assert build["with"]["pr_sha"] == "${{ github.event.pull_request.head.sha }}"
    assert build["with"]["app"] == "${{ matrix.app }}"
    assert set(build["secrets"]) == {"DOCKER_USERNAME", "DOCKER_PASSWORD"}
    assert "github.event_name == 'pull_request_target'" in build["if"]

    assert "build-images" in jobs["report-check"]["needs"]
    assert "build-images" in jobs["provision-e2e"]["needs"]
    assert "needs.build-images.result" in jobs["provision-e2e"]["if"]


def test_report_check_blocks_merge_on_build_failure():
    workflow = load(".github/workflows/pr-checks.yml", base_loader=True)
    step = workflow["jobs"]["report-check"]["steps"][0]
    script = step["run"]
    assert "BUILD_RESULT" in step["env"]
    assert '[ "$DETECT_RESULT" = success ]' in script
    assert '[ "$HAS_IMAGES" = true ] && [ "$BUILD_RESULT" = success ]' in script
    assert "conclusion=failure" in script


def test_pr_candidates_are_digest_reported_and_do_not_overwrite_description():
    workflow = load(".github/workflows/docker.yml", base_loader=True)

    assert "pull_request" not in workflow["on"]
    assert set(workflow["on"]["workflow_call"]["inputs"]) == {"release_tag", "app", "pr_sha", "tooling_sha"}
    assert set(workflow["on"]["workflow_call"]["secrets"]) == {"DOCKER_USERNAME", "DOCKER_PASSWORD"}

    build = workflow["jobs"]["build"]
    names = [step.get("name") for step in build["steps"]]
    assert "Upload PR candidate digest" in names
    upload = next(step for step in build["steps"] if step.get("name") == "Upload PR candidate digest")
    assert upload["if"] == "env.CHANNEL == 'pr'"

    description = next(step for step in build["steps"] if step.get("name") == "Docker Hub Description")
    assert "env.CHANNEL != 'pr'" in description["if"]


def test_custom_image_apps_do_not_build_locally():
    for app in ("canvas", "pocketbase"):
        compose = load(f"apps/{app}/docker-compose.yml")
        for service in (compose.get("services") or {}).values():
            assert "build" not in service, f"{app} compose must be pull-only"


@pytest.mark.parametrize("apps,expected", [('[]', 'false'), ('["strapi"]', 'true')])
def test_detection_step_handles_empty_image_matrix(tmp_path, apps, expected):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, body in {
        "git": "exit 0",
        "python3": 'printf \'{"apps":%s,"matrix":%s}\\n\' "$APPS" "$APPS"',
    }.items():
        path = bin_dir / name
        path.write_text("#!/bin/bash\n" + body + "\n")
        path.chmod(0o755)
    workflow = load(".github/workflows/pr-checks.yml")
    script = next(step['run'] for step in workflow['jobs']['detect-buildable']['steps'] if step.get('id') == 'detect')
    output = tmp_path / "output"
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=os.environ | {
        "PATH": f"{bin_dir}:{os.environ['PATH']}", "BASE_SHA": "base", "HEAD_SHA": "head",
        "APPS": apps, "GITHUB_OUTPUT": str(output),
    }, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert f"has_apps={expected}\n" in output.read_text()


def test_build_permissions_and_tooling_are_explicit():
    workflow = load(".github/workflows/pr-checks.yml")
    builder = load(".github/workflows/docker.yml")
    caller = workflow['jobs']['build-images']
    assert caller['permissions'] == builder['permissions']
    assert caller['with']['tooling_sha'] == '${{ github.event.pull_request.base.sha }}'
    steps = builder['jobs']['build']['steps']
    trusted = next(s for s in steps if s.get('name') == 'Checkout trusted build tooling')
    assert trusted['with']['path'] == 'tooling'
    assert trusted['with']['persist-credentials'] is False
    plan = next(s for s in steps if s.get('name') == 'Generate build/promote plan')
    assert 'python -I' in plan['run']
    assert "TOOLING_ROOT" in plan['run']
    assert '!cancelled()' in workflow['jobs']['provision-e2e']['if']
