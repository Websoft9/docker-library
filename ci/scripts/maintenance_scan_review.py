from __future__ import annotations

import argparse
import base64
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urlsplit


WORKFLOW_MARKER = "<!-- libs:workflow=scan-review -->"
DATA_MARKER_RE = re.compile(r"<!-- libs:scan-review-data:([A-Za-z0-9_-]+) -->")
APPROVAL_START = "<!-- libs:approval-start -->"
APPROVAL_END = "<!-- libs:approval-end -->"
CHECKLIST_RE = re.compile(r"^-\s*\[([ xX])\]\s*([^|]+?)\s*\|\s*target:\s*(.*?)\s*$")
APP_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$", re.IGNORECASE)


def build_update_child(item: dict, parent: str) -> dict:
    app = item["app"]
    target = _clean_target(item.get("target"))
    if not target:
        raise ValueError(f"Set an explicit approval target for {app} before starting Copilot")
    title = f"Update: {app}, target version: {target}"
    pr_title = f"Update {app} to {target}"
    body = "\n".join([
        "<!-- libs:workflow=update-app -->",
        "<!-- libs:scan-review-child -->",
        f"<!-- libs:scan-review-child-key:{parent}:{app} -->",
        "",
        f"App: `{app}`",
        f"Target version: {target}",
        f"Initial PR title: {pr_title}",
        "",
        "The owner-approved checklist target above is authoritative. Use it from the initial "
        "branch/PR creation through implementation; do not replace it with a scan candidate "
        "or a newly discovered release. If it cannot be used, report the blocker instead.",
        "",
        f"Parent: #{parent}",
        f"Current version: {', '.join(item.get('current') or []) or 'unknown'}",
        "",
        "## Scan evidence (reference only; not the approved target)",
        f"Candidate version: {item.get('latest') or 'unknown'}",
        f"Scan result: {item.get('status') or 'planned'}",
        f"Scan error: {item['error']}" if item.get("error") else "",
    ])
    instructions = (
        f"Update {app} to the owner-approved target version {target}. "
        f"Use '{pr_title}' as the initial PR title, before implementation begins. "
        "The Target version in the child issue comes from the owner's approval checklist "
        "and overrides Candidate version and the parent scan table. "
        "Read AGENTS.md first. Use .github/skills/libs/SKILL.md and follow the update-app "
        "hidden marker in this issue. The canonical workflow documents and skills are under "
        "skills/. Work autonomously, run the repository quality gates, and let Copilot create "
        "the branch and pull request. Open the pull request as ready for review, not as a draft."
    )
    return {"app": app, "title": title, "body": body, "instructions": instructions}


def _display(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, list):
        value = ", ".join(str(part) for part in value)
    escaped = html.escape(str(value), quote=False)
    return escaped.replace("|", r"\|").replace("\r", " ").replace("\n", "<br>")


def _app_link(record: dict) -> str:
    label = _display(record["app"])
    url = str(record.get("upstream_image") or "")
    if urlsplit(url).scheme not in {"http", "https"}:
        return label
    return f"[{label}]({quote(url, safe=':/?=&%#@+~-._')})"


def _display_candidates(record: dict) -> str:
    candidates = record["candidates"]
    if not candidates:
        return "—"
    return "<br>".join(
        f"**{_display(tag)} (recommended)**" if index == 0 else _display(tag)
        for index, tag in enumerate(candidates)
    )


def _item_data(item: dict) -> dict:
    latest = item.get("latest_version")
    if isinstance(latest, dict):
        latest = latest.get("version")
    status = item.get("version_status")
    if item.get("error"):
        status = "undetermined"
    current = [
        value for value in (item.get("current_version") or [])
        if str(value).lower() != "latest"
    ]
    return {
        "app": item.get("name", ""),
        "upstream_image": item.get("upstream_image"),
        "cadence": item.get("cadence"),
        "current": current,
        "latest": latest,
        "candidates": [candidate["version"] for candidate in item.get("latest_candidates", [])][:3]
        or ([latest] if latest else []),
        "status": status or "planned",
        "error": item.get("error"),
        "update_policy": item.get("update_policy"),
    }


def _clean_target(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().strip("`").strip()
    if text.lower() in {"", "unknown", "n/a", "none", "—", "-"}:
        return None
    return text


def _parse_checklist(parent_body: str) -> list[tuple[bool, str, str | None]]:
    if APPROVAL_START not in parent_body or APPROVAL_END not in parent_body:
        return []
    section = parent_body.split(APPROVAL_START, 1)[1].split(APPROVAL_END, 1)[0]
    parsed: list[tuple[bool, str, str | None]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ["):
            continue
        match = CHECKLIST_RE.fullmatch(stripped)
        if not match:
            raise ValueError("Invalid approval checklist item")
        checked = match.group(1).lower() == "x"
        app = match.group(2).strip().strip("`").strip().lower()
        target = _clean_target(match.group(3))
        parsed.append((checked, app, target))
    return parsed


def build_scan_review_issue(items: list[dict], run_id: str, run_url: str, scan_date: str) -> dict:
    records = [_item_data(item) for item in items]
    payload = {"run_id": str(run_id), "scan_date": scan_date, "items": records}
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).decode("ascii").rstrip("=")

    lines = [
        WORKFLOW_MARKER,
        f"<!-- libs:scan-run-id:{run_id} -->",
        f"<!-- libs:scan-review-data:{encoded} -->",
        "",
        f"## Maintenance scan review — {scan_date}",
        "",
        f"- Workflow run: [#{run_id}]({run_url})",
        f"- Apps scanned: {len(records)}",
        "",
    ]
    if records:
        lines.extend([
            "| App | Current | Latest candidates | Result | Details |",
            "| --- | --- | --- | --- | --- |",
        ])
        for record in records:
            lines.append(
                "| " + " | ".join((
                    _app_link(record),
                    _display(record["current"]),
                    _display_candidates(record),
                    _display(record["status"]),
                    _display(record["error"]),
                )) + " |"
            )
    else:
        lines.append("No applications were due in this scan run.")

    lines.extend([
        "",
        "## Approval",
        "",
        APPROVAL_START,
    ])
    for record in records:
        target = record["latest"] if record["latest"] not in (None, "") else "unknown"
        lines.append(f"- [ ] {record['app']} | target: {target}")
    lines.extend([
        APPROVAL_END,
        "",
        "## How to start",
        "",
        "Check the apps to update, optionally edit each `target`, then comment:",
        "",
        "```text",
        "/approve-updates",
        "```",
        "",
        "You can also list apps explicitly with `/approve-updates app1, app2`. Only apps listed in this scan are accepted. Copilot starts only after you submit the comment.",
    ])
    return {
        "title": f"Maintenance scan review: {scan_date} (run {run_id})",
        "body": "\n".join(lines),
    }


def parse_approval(parent_body: str, comment_body: str) -> dict:
    if WORKFLOW_MARKER not in parent_body:
        raise ValueError("This is not a maintenance scan review issue")

    data_match = DATA_MARKER_RE.search(parent_body)
    if not data_match:
        raise ValueError("This issue has no valid scan-review data marker")
    encoded = data_match.group(1)
    encoded += "=" * (-len(encoded) % 4)
    try:
        payload = json.loads(base64.urlsafe_b64decode(encoded).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("The scan-review data marker is invalid") from error

    records = {}
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("The scan-review data marker is invalid")
    for item in items:
        if not isinstance(item, dict) or not item.get("app"):
            raise ValueError("The scan-review data marker is invalid")
        records[str(item["app"]).lower()] = item

    checklist = _parse_checklist(parent_body)
    names = [name for _, name, _ in checklist]
    if len(names) != len(set(names)):
        raise ValueError("Each app may only appear once in the approval checklist")
    target_by_app = {name: target for _, name, target in checklist}

    match = re.fullmatch(
        r"/approve-updates(?:\s+([a-z0-9][a-z0-9_-]*(?:\s*,\s*[a-z0-9][a-z0-9_-]*)*))?",
        comment_body.strip(),
        flags=re.IGNORECASE,
    )
    if not match:
        raise ValueError("Use exactly: /approve-updates or /approve-updates app1, app2")

    explicit = match.group(1)
    if explicit:
        requested = [part.strip().lower() for part in explicit.split(",")]
    else:
        requested = [name for checked, name, _ in checklist if checked]
        if not requested:
            raise ValueError("Check at least one app or list apps explicitly")
    if len(requested) != len(set(requested)):
        raise ValueError("Each app may only appear once in the approval list")

    approved = []
    approved_items = []
    for name in requested:
        if not APP_NAME_RE.fullmatch(name):
            raise ValueError(f"Invalid app name: {name}")
        item = records.get(name)
        if not item:
            raise ValueError(f"App is not part of this scan: {name}")
        if not (Path("apps") / name / "variables.json").is_file():
            raise ValueError(f"App is not an active repository app: {name}")
        approved.append(name)
        # A present checklist row is authoritative, even if its target is unknown.
        # Never silently replace an owner's cleared target with the scan candidate.
        target = target_by_app[name] if name in target_by_app else _clean_target(item.get("latest"))
        approved_items.append({**item, "target": target})

    return {
        "run_id": str(payload.get("run_id", "")),
        "apps": approved,
        "items": approved_items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or validate maintenance scan review issues")
    commands = parser.add_subparsers(dest="command", required=True)

    render = commands.add_parser("render")
    render.add_argument("--scan-file", required=True)
    render.add_argument("--run-id", required=True)
    render.add_argument("--run-url", required=True)
    render.add_argument("--scan-date", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("--parent-body-file", required=True)
    validate.add_argument("--comment-file", required=True)

    args = parser.parse_args()
    try:
        if args.command == "render":
            items = json.loads(Path(args.scan_file).read_text(encoding="utf-8"))
            payload = build_scan_review_issue(items, args.run_id, args.run_url, args.scan_date)
        else:
            parent_body = Path(args.parent_body_file).read_text(encoding="utf-8")
            comment_body = Path(args.comment_file).read_text(encoding="utf-8")
            payload = parse_approval(parent_body, comment_body)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
