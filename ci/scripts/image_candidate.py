#!/usr/bin/env python3
"""Reuse a published build-input candidate, never treating registry failures as misses."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def reuse_candidate(plan: dict) -> bool:
    repository = plan["w9_repo"]
    candidate = f"{repository}:{plan['context_tag']}"
    result = subprocess.run(
        ["docker", "buildx", "imagetools", "inspect", candidate, "--format", "{{.Manifest.Digest}}"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        lowered = detail.lower()
        denied = any(word in lowered for word in ("denied", "unauthorized", "forbidden"))
        missing = any(word in lowered for word in ("manifest unknown", "no such manifest", "not found"))
        if missing and not denied:
            print(f"No matching candidate: {candidate}; building.")
            return False
        raise RuntimeError(f"Cannot inspect candidate {candidate}: {detail}")
    digest = result.stdout.strip()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError(f"Invalid candidate digest: {digest}")
    print(f"Reusing {candidate} at {digest}")
    # Do not rewrite the identity tag; all commit/rolling aliases refer to the
    # exact manifest that was inspected, including its platform set.
    for tag in plan["tags"]:
        if tag != candidate:
            subprocess.run(
                ["docker", "buildx", "imagetools", "create", "--prefer-index=false", "--tag", tag,
                 f"{repository}@{digest}"], check=True, timeout=120,
            )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    reused = reuse_candidate(json.loads(Path(args.plan).read_text(encoding="utf-8")))
    with Path(args.output).open("a", encoding="utf-8") as output:
        output.write(f"reused={'true' if reused else 'false'}\n")


if __name__ == "__main__":
    main()
