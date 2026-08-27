#!/usr/bin/env python3
"""List and delete opencode sessions.

Deletes sessions from the opencode database after interactive confirmation.
Related rows (messages, parts, events, todos, ...) are removed together.
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

CHILD_TABLES = (
    "message",
    "part",
    "session_message",
    "session_input",
    "todo",
    "session_context_epoch",
)


def default_db_path():
    data_dir = os.environ.get("OPENCODE_DATA_DIR")
    if data_dir:
        return os.path.join(data_dir, "opencode.db")
    home = Path.home()
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local"))
        return os.path.join(base, "opencode", "opencode.db")
    if sys.platform == "darwin":
        return str(home / "Library" / "Application Support" / "opencode" / "opencode.db")
    return str(home / ".local" / "share" / "opencode" / "opencode.db")


def connect(db_path):
    if not os.path.exists(db_path):
        sys.exit(f"error: opencode database not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def list_sessions(con, directory=None):
    query = "SELECT id, title, slug, directory, time_created FROM session"
    params = []
    if directory:
        query += " WHERE directory = ?"
        params.append(directory)
    query += " ORDER BY time_created"
    return con.execute(query, params).fetchall()


def shorten(value, width):
    if len(value) <= width:
        return value
    if width <= 3:
        return value[:width]
    return value[: width - 3] + "..."


def print_sessions(sessions, directory=None):
    if not sessions:
        if directory:
            print(f"No sessions found for directory: {directory}")
        else:
            print("No sessions found.")
        return

    id_width = min(max(len("ID"), max(len(s["id"]) for s in sessions)), 28)
    title_width = min(max(len("Session"), max(len(s["title"] or "") for s in sessions)), 48)
    show_directory = directory is None
    dir_width = 36

    print(f"{len(sessions)} session(s)")
    if directory:
        print(f"Directory: {directory}")

    columns = [
        ("Created", 16),
        ("ID", id_width),
        ("Session", title_width),
    ]
    if show_directory:
        columns.append(("Directory", dir_width))

    header = "  ".join(name.ljust(width) for name, width in columns)
    divider = "  ".join("-" * width for _, width in columns)
    print(header)
    print(divider)

    for s in sessions:
        ts = datetime.fromtimestamp(s["time_created"] / 1000, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M"
        )
        row = [
            ts.ljust(16),
            shorten(s["id"], id_width).ljust(id_width),
            shorten(s["title"] or "", title_width).ljust(title_width),
        ]
        if show_directory:
            row.append(shorten(s["directory"] or "", dir_width).ljust(dir_width))
        print("  ".join(row))


def confirm(count):
    answer = input(f"Delete these {count} session(s) and their messages? [y/N] ").strip().lower()
    return answer in ("y", "yes")


def delete_sessions(con, ids):
    con.execute("BEGIN")
    placeholders = ",".join("?" * len(ids))
    for table in CHILD_TABLES:
        con.execute(f"DELETE FROM {table} WHERE session_id IN ({placeholders})", ids)
    con.execute("DELETE FROM event WHERE aggregate_id IN ({})".format(placeholders), ids)
    cur = con.execute(f"DELETE FROM session WHERE id IN ({placeholders})", ids)
    con.commit()
    return cur.rowcount


def main():
    parser = argparse.ArgumentParser(description="List and delete opencode sessions")
    parser.add_argument("--db", help="path to opencode.db (default: auto-detect)")
    parser.add_argument(
        "--all",
        action="store_true",
        help="list and delete sessions from all directories",
    )
    parser.add_argument(
        "--directory",
        help="only list and delete sessions for this directory (default: current directory)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="skip the confirmation prompt and delete all sessions",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="only list sessions, do not delete anything",
    )
    args = parser.parse_args()

    db_path = args.db or default_db_path()
    con = connect(db_path)
    directory = None if args.all else os.path.abspath(args.directory or os.getcwd())

    sessions = list_sessions(con, directory=directory)
    print_sessions(sessions, directory=directory)

    if not sessions:
        return

    if args.dry_run:
        print("Dry run: nothing deleted.")
        return

    if not args.yes and not confirm(len(sessions)):
        print("Aborted, nothing deleted.")
        return

    ids = [s["id"] for s in sessions]
    deleted = delete_sessions(con, ids)
    print(f"Deleted {deleted} session(s) from {db_path}")


if __name__ == "__main__":
    main()
