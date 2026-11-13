#!/usr/bin/env python3
"""List and delete OpenCode sessions through the V2 API."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode


def api_request(*arguments: str) -> str:
    try:
        result = subprocess.run(
            ["opencode", "api", *arguments],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError("opencode was not found in PATH") from error

    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(detail or f"opencode api exited with {result.returncode}")
    return result.stdout


def list_sessions(directory: Path | None) -> list[dict]:
    sessions: list[dict] = []
    cursor: str | None = None
    seen_cursors: set[str] = set()

    while True:
        params = {"limit": "100", "order": "asc", "parentID": "null"}
        if directory is not None:
            params["directory"] = str(directory)
        if cursor:
            if cursor in seen_cursors:
                raise RuntimeError("OpenCode returned a repeated session cursor")
            seen_cursors.add(cursor)
            params["cursor"] = cursor

        response = json.loads(api_request("get", f"/api/session?{urlencode(params)}"))
        if not isinstance(response, dict) or not isinstance(response.get("data"), list):
            raise RuntimeError("unexpected response from OpenCode session API")
        sessions.extend(response["data"])

        next_cursor = (response.get("cursor") or {}).get("next")
        if not next_cursor:
            return sessions
        cursor = str(next_cursor)


def shorten(value: str | None, width: int) -> str:
    text = value or ""
    if len(text) <= width:
        return text
    if width <= 3:
        return text[:width]
    return text[: width - 3] + "..."


def print_sessions(sessions: list[dict], directory: Path | None) -> None:
    if not sessions:
        if directory is None:
            print("No sessions found.")
        else:
            print(f"No sessions found for directory: {directory}")
        return

    id_width = min(max(len("ID"), *(len(str(item.get("id", ""))) for item in sessions)), 28)
    title_width = min(
        max(len("Session"), *(len(str(item.get("title") or "")) for item in sessions)), 48
    )
    show_directory = directory is None
    columns = [("Created", 16), ("ID", id_width), ("Session", title_width)]
    if show_directory:
        columns.append(("Directory", 36))

    print(f"{len(sessions)} root session(s) (deleting a root also deletes its child sessions)")
    if directory is not None:
        print(f"Directory: {directory}")
    print("  ".join(name.ljust(width) for name, width in columns))
    print("  ".join("-" * width for _, width in columns))

    for item in sessions:
        created = item.get("time", {}).get("created")
        if isinstance(created, (int, float)):
            created_text = datetime.fromtimestamp(created / 1000, tz=timezone.utc).strftime(
                "%Y-%m-%d %H:%M"
            )
        else:
            created_text = ""
        values = [
            created_text.ljust(16),
            shorten(str(item.get("id", "")), id_width).ljust(id_width),
            shorten(item.get("title"), title_width).ljust(title_width),
        ]
        if show_directory:
            location = item.get("location") or {}
            values.append(shorten(location.get("directory"), 36).ljust(36))
        print("  ".join(values))


def confirm(count: int) -> bool:
    if not sys.stdin.isatty():
        print("Refusing to delete without --yes in a non-interactive shell.", file=sys.stderr)
        return False
    try:
        answer = input(f"Delete these {count} root session(s) and their child sessions? [y/N] ")
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer.strip().lower() in {"y", "yes"}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List and delete OpenCode sessions")
    parser.add_argument(
        "--all",
        action="store_true",
        help="list and delete sessions from all directories",
    )
    parser.add_argument(
        "--directory",
        type=Path,
        help="only list and delete sessions for this directory (default: current directory)",
    )
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="only list sessions, do not delete anything",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    directory = None if args.all else (args.directory or Path.cwd()).expanduser().resolve()

    try:
        sessions = list_sessions(directory)
        print_sessions(sessions, directory)
        if not sessions:
            return 0
        if args.dry_run:
            print("Dry run: nothing deleted.")
            return 0
        if not args.yes and not confirm(len(sessions)):
            print("Aborted, nothing deleted.")
            return 0

        deleted = 0
        for session in sessions:
            session_id = quote(str(session["id"]), safe="")
            try:
                api_request("delete", f"/api/session/{session_id}")
            except RuntimeError as error:
                raise RuntimeError(f"{error} (already deleted {deleted} root session(s))") from error
            deleted += 1
        print(f"Deleted {deleted} root session(s) and their child sessions.")
        return 0
    except (RuntimeError, json.JSONDecodeError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
