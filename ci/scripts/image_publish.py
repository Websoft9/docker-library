#!/usr/bin/env python3
"""Resolve immutable image candidates for the exact app build context."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cli"))

from libs.docker_inputs import context_tag  # noqa: E402  (std-lib-only module)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def source_candidates(app: str, repo: str, runs: list, ref: str = "HEAD") -> list[str]:
    input_tag = context_tag(app, ref)
    candidates = [f"{repo}:{input_tag}"]
    # gh --paginate --slurp returns one response object per page.
    for page in runs:
        for run in page.get("workflow_runs", []):
            sha = run.get("head_sha", "")
            if (run.get("conclusion") != "success" or run.get("event") != "push"
                    or run.get("head_branch") != "main" or not re.fullmatch(r"[0-9a-f]{40}", sha)):
                continue
            ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", sha, ref], capture_output=True)
            if ancestor.returncode != 0:
                continue
            try:
                matches = context_tag(app, sha) == input_tag
            except (subprocess.CalledProcessError, RuntimeError, ValueError):
                continue
            if matches:
                image = f"{repo}:dev-{sha[:7]}"
                if image not in candidates:
                    candidates.append(image)
    return candidates


def resolve_source(candidates: list[str]) -> tuple[str, str]:
    for image in candidates:
        for attempt in range(2):
            result = subprocess.run(
                ["docker", "buildx", "imagetools", "inspect", image, "--format", "{{.Manifest.Digest}}"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                digest = result.stdout.strip()
                if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
                    raise ValueError(f"Invalid manifest digest for {image}: {digest}")
                return image.rsplit(":", 1)[0] + "@" + digest, image
            detail = (result.stderr or result.stdout).strip()
            lowered = detail.lower()
            denied = any(word in lowered for word in ("unauthorized", "forbidden", "denied"))
            missing = any(word in lowered for word in ("manifest unknown", "not found", "no such manifest"))
            print(f"Inspect {image}: {detail}", file=sys.stderr)
            if missing and not denied:
                break
            if attempt == 1:
                raise ValueError(f"Cannot inspect candidate {image}: {detail}")
            time.sleep(2)
    raise ValueError(
        "No candidate matches this app context. Run Build image to DockerHub manually with "
        "channel=dev, this app, and the release tag as the selected ref, then re-run the release. "
        "Refusing to promote dev-latest or an image from a different context."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", required=True)
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--context-tag", action="store_true")
    parser.add_argument("--plan")
    parser.add_argument("--runs-file")
    parser.add_argument("--explicit", action="store_true")
    args = parser.parse_args()
    if args.context_tag:
        print(context_tag(args.app, args.ref))
        return
    with open(args.plan, encoding="utf-8") as handle:
        plan = json.load(handle)
    if args.explicit:
        candidates = [plan["source_image"]]
    else:
        with open(args.runs_file, encoding="utf-8") as handle:
            runs = json.load(handle)
        candidates = source_candidates(args.app, plan["w9_repo"], runs, args.ref)
    image, source_tag = resolve_source(candidates)
    print(json.dumps({"source_image": image, "source_tag": source_tag}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
