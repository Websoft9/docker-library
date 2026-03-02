#!/usr/bin/env python3
"""
Gate 1b: Docker image existence check and app metadata validation.

Usage:
  python3 build/check_images.py "wordpress"
  python3 build/check_images.py "wordpress,nginx,gitlab"
  python3 build/check_images.py "ALL"

Exit codes:
  0 - All checks passed
  1 - One or more checks failed
  2 - Script error
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

APPS_DIR = Path(__file__).parent.parent / "apps"
DOCKER_HUB_API = "https://hub.docker.com/v2"
TIMEOUT = 10


# ─────────────────────────────────────────────
# Docker Hub helpers
# ─────────────────────────────────────────────

def _parse_image(image_ref: str) -> tuple[str, str]:
    """Split 'repo:tag' or 'org/repo:tag' into (repo, tag)."""
    if ":" in image_ref:
        repo, tag = image_ref.rsplit(":", 1)
    else:
        repo, tag = image_ref, "latest"
    return repo, tag


def _check_docker_hub_tag(repo: str, tag: str) -> tuple[bool, str]:
    """
    Return (exists, message).
    Handles:
      - official images  (nginx → library/nginx)
      - custom org images (gitea/gitea, gitlab/gitlab-ce)
    """
    # Normalise to namespace/repo
    if "/" not in repo:
        ns_repo = f"library/{repo}"
    else:
        ns_repo = repo

    url = f"{DOCKER_HUB_API}/repositories/{ns_repo}/tags/{tag}"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            return True, "OK"
        elif r.status_code == 404:
            return False, f"tag '{tag}' not found on Docker Hub ({ns_repo})"
        else:
            return False, f"Docker Hub returned HTTP {r.status_code}"
    except requests.RequestException as exc:
        return False, f"network error: {exc}"


# ─────────────────────────────────────────────
# Per-app checks
# ─────────────────────────────────────────────

class CheckResult:
    def __init__(self, app: str):
        self.app = app
        self.results: list[dict] = []   # {check, status, message}

    def add(self, check: str, ok: bool, message: str = ""):
        self.results.append({
            "check": check,
            "status": "PASS" if ok else "FAIL",
            "message": message,
        })

    @property
    def passed(self) -> bool:
        return all(r["status"] == "PASS" for r in self.results)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if r["status"] == "FAIL")


def check_app(app_name: str) -> CheckResult:
    result = CheckResult(app_name)
    app_dir = APPS_DIR / app_name

    # 1. App directory exists
    if not app_dir.is_dir():
        result.add("app_dir_exists", False, f"apps/{app_name}/ not found")
        return result
    result.add("app_dir_exists", True)

    # 2. variables.json exists
    variables_path = app_dir / "variables.json"
    if not variables_path.exists():
        result.add("variables_json", False, "variables.json is missing")
    else:
        try:
            data = json.loads(variables_path.read_text())
            # Must have at least appName
            has_name = bool(data.get("appName") or data.get("app_name") or data.get("name"))
            result.add("variables_json", has_name,
                       "" if has_name else "variables.json missing 'appName' field")
        except json.JSONDecodeError as exc:
            result.add("variables_json", False, f"invalid JSON: {exc}")

    # 3. Parse .env for W9_REPO / W9_VERSION
    env_path = app_dir / ".env"
    if not env_path.exists():
        result.add("env_exists", False, ".env file missing")
        return result
    result.add("env_exists", True)

    env_vars: dict[str, str] = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip("'\"")   # strip surrounding single/double quotes
        env_vars[k.strip()] = v

    repo = env_vars.get("W9_REPO", "")
    version = env_vars.get("W9_VERSION", "")

    # 4. W9_REPO must exist and be non-empty
    if not repo:
        result.add("w9_repo_set", False, "W9_REPO is not set in .env")
    else:
        result.add("w9_repo_set", True)

    # 5. W9_VERSION must be specific (not empty, not 'latest')
    if not version:
        result.add("w9_version_set", False, "W9_VERSION is not set in .env")
    elif version.lower() == "latest":
        result.add("w9_version_set", False, "W9_VERSION must not be 'latest'")
    else:
        result.add("w9_version_set", True)

    # 6. Docker Hub tag existence (only if repo+version are set and valid)
    if repo and version and version.lower() != "latest":
        exists, msg = _check_docker_hub_tag(repo, version)
        result.add("docker_tag_exists", exists,
                   msg if not exists else f"{repo}:{version} confirmed on Docker Hub")
    else:
        result.add("docker_tag_exists", False, "skipped due to invalid repo/version")

    return result


# ─────────────────────────────────────────────
# Output formatters
# ─────────────────────────────────────────────

def _status_icon(status: str) -> str:
    return "✅" if status == "PASS" else "❌"


def format_console(results: list[CheckResult]) -> str:
    lines = []
    for r in results:
        lines.append(f"\n{'='*50}")
        lines.append(f"App: {r.app}  |  {'PASS' if r.passed else 'FAIL'}")
        lines.append('='*50)
        for item in r.results:
            icon = _status_icon(item["status"])
            msg = f"  {item['message']}" if item["message"] else ""
            lines.append(f"  {icon} {item['check']}{msg}")
    return "\n".join(lines)


def format_pr_comment(results: list[CheckResult]) -> str:
    all_pass = all(r.passed for r in results)
    header = "## Gate 1b — Image & Metadata Check\n"
    header += "🟢 All checks passed\n" if all_pass else "🔴 Some checks failed\n"
    header += f"\n**Apps checked:** {', '.join(r.app for r in results)}\n\n"

    table = "| App | Check | Status | Detail |\n"
    table += "|-----|-------|--------|--------|\n"
    for r in results:
        for item in r.results:
            icon = _status_icon(item["status"])
            detail = item["message"] or ""
            table += f"| `{r.app}` | {item['check']} | {icon} {item['status']} | {detail} |\n"

    return header + table


def format_github_output(results: list[CheckResult]) -> str:
    """Single-line safe for $GITHUB_OUTPUT (newlines encoded)."""
    comment = format_pr_comment(results)
    # Encode for multiline GitHub output
    comment_encoded = comment.replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D")
    return f"comment_body={comment_encoded}"


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Gate 1b: image and metadata checks")
    parser.add_argument("apps", help="Comma-separated app names or 'ALL'")
    parser.add_argument("--output-github", action="store_true",
                        help="Emit $GITHUB_OUTPUT compatible lines")
    parser.add_argument("--output-json", action="store_true",
                        help="Emit JSON summary to stdout")
    args = parser.parse_args()

    if args.apps.upper() == "ALL":
        app_names = sorted(d.name for d in APPS_DIR.iterdir() if d.is_dir())
    else:
        app_names = [a.strip() for a in args.apps.split(",") if a.strip()]

    if not app_names:
        print("No apps specified.", file=sys.stderr)
        return 2

    results = [check_app(name) for name in app_names]

    if args.output_json:
        summary = [
            {
                "app": r.app,
                "passed": r.passed,
                "results": r.results,
            }
            for r in results
        ]
        print(json.dumps(summary, indent=2))
    elif args.output_github:
        print(format_github_output(results))
    else:
        print(format_console(results))

    all_pass = all(r.passed for r in results)
    if not all_pass:
        print(f"\n{'='*50}", file=sys.stderr)
        print(f"FAILED: {sum(r.fail_count for r in results)} check(s) did not pass.",
              file=sys.stderr)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
