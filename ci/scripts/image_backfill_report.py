#!/usr/bin/env python3
"""Report a failed manual promote without granting issue access to image builders."""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cli"))

from libs.docker_inputs import context_tag  # noqa: E402


def api(endpoint: str, payload: dict | None = None):
    command = ["gh", "api", endpoint]
    if payload is not None:
        command += ["--method", "POST", "--input", "-"]
    return json.loads(subprocess.check_output(
        command, input=json.dumps(payload) if payload is not None else None, text=True,
    ))


def pages(endpoint: str) -> list:
    return json.loads(subprocess.check_output(
        ["gh", "api", "--paginate", "--slurp", endpoint], text=True,
    ))


def report(repo: str, run_id: str, attempt: str, sha: str) -> None:
    # Re-running only failed jobs does not re-run the successful setup/upload job.
    artifacts = [artifact for page in pages(f"repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100")
                 for artifact in page["artifacts"]
                 if re.fullmatch(r"image-backfill-[0-9]+", artifact["name"])
                 and int(artifact["name"].rsplit("-", 1)[1]) <= int(attempt) and not artifact["expired"]]
    if not artifacts:
        print("No manual promote request artifact; nothing to report.")
        return
    artifact = max(artifacts, key=lambda item: int(item["name"].rsplit("-", 1)[1]))
    archive = subprocess.check_output([
        "gh", "api", f"repos/{repo}/actions/artifacts/{artifact['id']}/zip",
    ])
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        request = json.loads(bundle.read("backfill.json"))
    app, ref = request["app"], request["ref"]
    if (not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", app)
            or not isinstance(ref, str) or not ref or len(ref) > 255
            or any(ord(char) < 32 for char in ref)
            or not re.fullmatch(r"[0-9a-f]{40}", request["sha"])
            or request["workflow_sha"] != sha):
        raise ValueError("Invalid backfill request identity")
    sha = request["sha"]
    try:
        identity = context_tag(app, sha)
    except (ValueError, RuntimeError):
        identity = "unavailable (see failed run)"
    jobs = [job for page in pages(
        f"repos/{repo}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100"
    ) for job in page["jobs"] if job["conclusion"] == "failure"]
    failures = "\n".join(
        f"- {job['name']}: " + ", ".join(
            step["name"] for step in job.get("steps", []) if step["conclusion"] == "failure"
        ) for job in jobs
    )
    key = hashlib.sha256(f"{app}\n{ref}".encode()).hexdigest()
    marker = f"<!-- image-backfill:{key} -->"
    url = f"https://github.com/{repo}/actions/runs/{run_id}/attempts/{attempt}"
    body = (
        f"{marker}\n## Failed manual image backfill\n\n"
        f"- App: `{app}`\n- Target ref: `{ref}`\n- SHA: `{sha}`\n"
        f"- Context tag: `{identity}`\n- Source SHA: `{request.get('source_sha') or 'exact-context candidate'}`\n"
        f"- Run and error logs: {url}\n\n### Failed stages\n{failures}\n\n"
        "### Recovery\n"
        f"Run `docker.yml` from `main` with `channel=dev`, `app={app}`, `target_ref={ref}`; "
        "then run `channel=promote` with the same app/target_ref. Confirm stable tags before closing this issue.\n"
    )
    existing = next((issue for page in pages(f"repos/{repo}/issues?state=open&per_page=100")
                     for issue in page if "pull_request" not in issue and marker in (issue.get("body") or "")), None)
    if existing:
        labels = {label["name"] for label in existing.get("labels", [])}
        if "bug" not in labels:
            api(f"repos/{repo}/issues/{existing['number']}/labels", {"labels": ["bug"]})
        api(f"repos/{repo}/issues/{existing['number']}/comments", {"body": body})
    else:
        labels = {label["name"] for page in pages(f"repos/{repo}/labels?per_page=100") for label in page}
        if "bug" not in labels:
            api(f"repos/{repo}/labels", {"name": "bug", "color": "d73a4a", "description": "Something isn't working"})
        api(f"repos/{repo}/issues", {
            "title": f"[image-backfill] {app} @ {ref}", "body": body, "labels": ["bug"],
        })


if __name__ == "__main__":
    report(os.environ["REPOSITORY"], os.environ["RUN_ID"], os.environ["RUN_ATTEMPT"], os.environ["RUN_SHA"])
