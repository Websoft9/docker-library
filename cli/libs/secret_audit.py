from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import yaml
from dotenv import dotenv_values

from libs.repo import repo_path


REFERENCE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")
VARIABLE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
PLATFORM_FIELDS = {"W9_POWER_PASSWORD", "W9_RCODE"}
CANDIDATE = re.compile(r"(?:^|_)(?:KEY|SECRET|TOKEN|SALT|CIPHER|SIGNING|CREDS)(?:_|$)")


def template_issue(value: str) -> str | None:
    body = value[3:] if value.startswith("sk-") else value
    if re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", body):
        return "UUID requires a dedicated generator"
    segments = body.split("-")
    if not value.startswith("sk-") and len(segments) > 1 and re.fullmatch(r"[A-Za-z]+", segments[0]):
        return "ambiguous fixed prefix"
    if any(not re.fullmatch(r"[A-Za-z0-9]+", segment) for segment in segments):
        return "unsupported format; use a random seed and references or a dedicated generator"
    if sum(map(len, segments)) < 12:
        return "random portion must contain at least 12 characters"
    return None


def references(value: str) -> list[str]:
    return [match.group(1) or match.group(2) for match in REFERENCE.finditer(value)]


def check_secret_templates(target: Path) -> dict:
    metadata = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    values = dotenv_values(target / ".env", interpolate=False)
    fields = (metadata.get("env") or {}).get("secrets") or []
    result = {"ok": True, "status": "not_applicable", "fields": [], "errors": []}
    if not isinstance(fields, list) or any(not isinstance(field, str) or not VARIABLE.fullmatch(field) for field in fields):
        return {**result, "ok": False, "status": "invalid", "errors": ["env.secrets: expected variable names"]}

    def resolve(field: str, visiting: set[str]) -> str:
        if field in visiting:
            raise ValueError("circular reference")
        if field in PLATFORM_FIELDS and field in values:
            return "generated-platform-value"
        value = values.get(field)
        if not value:
            raise ValueError("missing or empty reference: " + field)
        resolved = REFERENCE.sub(lambda match: resolve(match.group(1) or match.group(2), visiting | {field}), value)
        if "$" in resolved:
            raise ValueError("unsupported variable reference")
        return resolved

    targets = list(dict.fromkeys(fields + sorted(PLATFORM_FIELDS & values.keys())))
    for field in targets:
        value = values.get(field) or ""
        kind = "platform" if field in PLATFORM_FIELDS else "reference" if references(value) else "random_template"
        result["fields"].append({"name": field, "kind": kind, "references": references(value)})
        if field in PLATFORM_FIELDS:
            continue
        try:
            resolve(field, set())
        except ValueError as error:
            result["errors"].append(field + ": " + str(error))
            continue
        if kind == "random_template" and (issue := template_issue(value)):
            result["errors"].append(field + ": " + issue)
    result["ok"] = not result["errors"]
    result["status"] = "invalid" if result["errors"] else "checked" if targets else "not_applicable"
    return result


def collect_secret_coverage(root: Path | None = None) -> dict:
    root = root or repo_path()
    apps = []
    for path in sorted((root / "apps").glob("*/variables.json")):
        metadata = json.loads(path.read_text(encoding="utf-8"))
        values = dotenv_values(path.parent / ".env", interpolate=False)
        declared = (metadata.get("env") or {}).get("secrets") or []
        implicit = sorted(PLATFORM_FIELDS & values.keys())
        checked = check_secret_templates(path.parent)
        managed = set(declared) | set(implicit)

        def managed_reference(field: str, visiting: set[str]) -> bool:
            if field in visiting:
                return False
            dependencies = references(values.get(field) or "")
            return bool(dependencies) and all(
                dependency in managed or managed_reference(dependency, visiting | {field})
                for dependency in dependencies
            )

        compose = yaml.safe_load((path.parent / "docker-compose.yml").read_text(encoding="utf-8")) or {}
        candidate_names = {key for key in values if CANDIDATE.search(key)}
        configured = {}
        for service_name, service in (compose.get("services") or {}).items():
            environment = service.get("environment") or {}
            supplied = set(environment) if isinstance(environment, dict) else {entry.split("=", 1)[0] for entry in environment}
            candidate_names.update(key for key in supplied if CANDIDATE.search(key))
            env_files = service.get("env_file") or []
            if isinstance(env_files, str):
                env_files = [env_files]
            if ".env" in env_files:
                supplied.update(values)
            configured[service_name] = supplied
        candidates = []
        for field in sorted(candidate_names - managed):
            candidates.append({
                "name": field,
                "classification": "managed_reference" if managed_reference(field, set()) else "needs_review",
                "default_present": bool(values.get(field)),
                "references": references(values.get(field) or ""),
                "configured_services": sorted(name for name, supplied in configured.items() if field in supplied),
            })
        review = any(candidate["classification"] == "needs_review" for candidate in candidates)
        status = "blocked" if not checked["ok"] else "review_required" if review else "declared" if declared else "implicit_only" if implicit else "no_candidates_in_source"
        apps.append({"app": path.parent.name, "status": status, "declared": declared, "implicit": implicit,
                     "template_check": checked, "candidates": candidates})
    return {"schema_version": 1, "scope": "current apps only; candidate scan is not a generation decision or runtime proof",
            "app_count": len(apps), "status_counts": dict(sorted(Counter(app["status"] for app in apps).items())), "apps": apps}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the secret coverage inventory without secret values")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = collect_secret_coverage()
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(json.dumps({"output": str(args.output), "app_count": report["app_count"], "status_counts": report["status_counts"]}))
    else:
        print(text)


if __name__ == "__main__":
    main()