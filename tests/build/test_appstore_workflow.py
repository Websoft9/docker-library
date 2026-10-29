from __future__ import annotations

import os
import subprocess

import pytest
import yaml

from _helpers import REPO_ROOT


def run_step(tmp_path, name, **values):
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/appstore-publish.yml").read_text())
    script = next(step["run"] for step in workflow["jobs"]["publish"]["steps"] if step.get("name") == name)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    git = bin_dir / "git"
    git.write_text(
        '#!/bin/bash\n'
        'case "$1" in\n'
        '  fetch) exit 0 ;;\n'
        '  merge-base) exit "${ON_MAIN:-0}" ;;\n'
        '  rev-parse) printf "abcdef123456\\n" ;;\n'
        '  tag) printf "%s\\n" "${TAGS:-}" ;;\n'
        '  *) exit 1 ;;\n'
        'esac\n'
    )
    git.chmod(0o755)
    output = tmp_path / "output"
    env = os.environ | {
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "GITHUB_OUTPUT": str(output),
        "EVENT_NAME": "push",
        "REF_TYPE": "branch",
        "REF_NAME": "main",
        "INPUT_CHANNEL": "",
        "RELEASE_TAG": "",
    } | values
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, text=True, capture_output=True)
    return result, dict(line.split("=", 1) for line in output.read_text().splitlines()) if output.exists() else {}


def test_release_channel_uses_main_tag_as_version(tmp_path):
    result, output = run_step(tmp_path, "Resolve publish channel", EVENT_NAME="release", RELEASE_TAG="0.9.0")
    assert result.returncode == 0, result.stderr
    assert output == {"channel": "release", "version": "0.9.0"}


@pytest.mark.parametrize("tag,on_main", [("0.9.0-rc.1", "0"), ("0.9.0", "1")])
def test_release_rejects_nonstable_tag_or_off_main_commit(tmp_path, tag, on_main):
    result, output = run_step(tmp_path, "Resolve publish channel", EVENT_NAME="release", RELEASE_TAG=tag, ON_MAIN=on_main)
    assert result.returncode != 0
    assert output == {}


@pytest.mark.parametrize("event,channel", [("push", "dev"), ("workflow_dispatch", "dev"), ("workflow_dispatch", "rc")])
def test_nonrelease_versions_are_channel_and_commit_based(tmp_path, event, channel):
    result, output = run_step(tmp_path, "Resolve publish channel", EVENT_NAME=event, INPUT_CHANNEL=channel)
    assert result.returncode == 0, result.stderr
    assert output == {"channel": channel, "version": f"{channel}-abcdef123456"}


def test_manual_release_is_rejected(tmp_path):
    result, _ = run_step(tmp_path, "Resolve publish channel", EVENT_NAME="workflow_dispatch", INPUT_CHANNEL="release")
    assert result.returncode != 0


def test_release_base_ignores_nonstable_tags(tmp_path):
    result, output = run_step(
        tmp_path, "Resolve release base", RELEASE_TAG="0.9.0", TAGS="release-21\n0.9.0\n0.9.0-rc.1\n0.8.1"
    )
    assert result.returncode == 0, result.stderr
    assert output == {"from_ref": "0.8.1", "range": "0.8.1..0.9.0"}


def test_first_release_builds_all_app_packages(tmp_path):
    result, output = run_step(tmp_path, "Resolve release base", RELEASE_TAG="0.9.0", TAGS="0.9.0\nrelease-21")
    assert result.returncode == 0, result.stderr
    assert output == {"all_apps": "true", "range": "0.9.0"}


def test_rc_purges_only_rc_artifacts(tmp_path):
    result, output = run_step(tmp_path, "Resolve legacy purge URLs", CHANNEL="rc")
    assert result.returncode == 0, result.stderr
    assert "/rc/websoft9/plugin/library/library-rc.zip" in output["urls"]
    assert "/rc/websoft9/plugin/media/media-latest.zip" in output["urls"]
    assert "/release/" not in output["urls"]


def test_release_is_published_once_and_waits_for_images():
    workflow = yaml.load((REPO_ROOT / ".github/workflows/appstore-publish.yml").read_text(), Loader=yaml.BaseLoader)
    assert workflow["on"]["release"]["types"] == ["published"]
    assert "tags" not in workflow["on"]["push"]
    assert "release.prerelease == false" in workflow["jobs"]["release-images"]["if"]
    assert workflow["jobs"]["release-images"]["uses"] == "./.github/workflows/docker.yml"
    assert workflow["jobs"]["publish"]["needs"] == "release-images"
    assert "needs.release-images.result == 'success'" in workflow["jobs"]["publish"]["if"]
    assert "pages" not in workflow["jobs"]


def test_bare_tag_push_does_not_publish_release(tmp_path):
    result, output = run_step(tmp_path, "Resolve publish channel", REF_TYPE="tag", REF_NAME="0.9.0")
    assert result.returncode != 0
    assert not output
