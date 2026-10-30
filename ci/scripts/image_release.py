#!/usr/bin/env python3
"""Select only custom images whose build inputs changed since the previous stable tag."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cli"))

from libs.docker_inputs import changed_apps  # noqa: E402

STABLE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def release_plan(tag: str, published_tags: list[str]) -> dict:
    if not STABLE.fullmatch(tag):
        raise ValueError("Release tags must use stable X.Y.Z format")
    version = tuple(map(int, tag.split(".")))
    tags = git("tag", "--merged", tag).splitlines()
    previous = max(
        (candidate for candidate in tags if candidate in published_tags and STABLE.fullmatch(candidate)
         and tuple(map(int, candidate.split("."))) < version),
        key=lambda candidate: tuple(map(int, candidate.split("."))), default="",
    )
    if previous:
        candidates = changed_apps(previous, tag)
    else:
        files = git("ls-tree", "-r", "--name-only", tag, "--", "apps").splitlines()
        candidates = sorted({path.split("/")[1] for path in files
                             if re.fullmatch(r"apps/[a-z0-9][a-z0-9_-]*/Dockerfile", path)})
    apps = []
    for app in candidates:
        dockerfile = git("show", f"{tag}:apps/{app}/Dockerfile")
        if re.search(rf"^ARG\s+{re.escape(app.upper())}_VERSION=", dockerfile, re.MULTILINE):
            apps.append(app)
    return {"apps": apps, "has_apps": bool(apps), "from_ref": previous,
            "all_apps": not previous, "range": f"{previous}..{tag}" if previous else tag}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--releases-file", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    releases = json.loads(Path(args.releases_file).read_text(encoding="utf-8"))
    published_tags = [release["tag_name"] for page in releases for release in page
                      if not release["draft"] and not release["prerelease"] and release.get("published_at")]
    plan = release_plan(args.release_tag, published_tags)
    with Path(args.output).open("a", encoding="utf-8") as output:
        for key, value in plan.items():
            encoded = json.dumps(value, separators=(",", ":")) if not isinstance(value, str) else value
            output.write(f"{key}={encoded}\n")
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
