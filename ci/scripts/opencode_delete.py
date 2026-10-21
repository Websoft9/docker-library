#!/usr/bin/env python3
"""List and delete opencode sessions from the local opencode database.

Sessions are selected by directory (or all directories), expanded to include
child sessions, and removed in one transaction together with their messages,
parts, events, and related rows.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_FILENAME = "opencode.db"


def default_db_path() -> Path:
    data_dir = os.environ.get("OPENCODE_DATA_DIR")
    if data_dir:
        return Path(data_dir) / DB_FILENAME

    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        return base / "opencode" / DB_FILENAME
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / "opencode" / DB_FILENAME
    return home / ".local" / "share" / "opencode" / DB_FILENAME


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.is_file():
        raise FileNotFoundError(f"opencode database not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA busy_timeout = 5000")
    return con


def table_columns(con: sqlite3.Connection, table: str) -> set[str]:
    quoted = table.replace('"', '""')
    return {row["name"] for row in con.execute(f'PRAGMA table_info("{quoted}")')}


def existing_tables(con: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }


def select_sessions(con: sqlite3.Connection, directory: Path | None) -> list[sqlite3.Row]:
    con.execute("DROP TABLE IF EXISTS temp.selected_session")
    con.execute("CREATE TEMP TABLE selected_session (id TEXT PRIMARY KEY)")

    query = "SELECT id FROM session"
    params: tuple[str, ...] = ()
    if directory is not None:
        query += " WHERE directory = ?"
        params = (str(directory),)
    query += " ORDER BY time_created"

    root_ids = [row["id"] for row in con.execute(query, params)]
    con.executemany(
        "INSERT OR IGNORE INTO selected_session (id) VALUES (?)",
        ((session_id,) for session_id in root_ids),
    )
    con.execute(
        """
        WITH RECURSIVE tree (id) AS (
            SELECT id FROM selected_session
            UNION
            SELECT child.id
            FROM session AS child
            JOIN tree ON child.parent_id = tree.id
        )
        INSERT OR IGNORE INTO selected_session (id)
        SELECT id FROM tree
        """
    )
    return con.execute(
        """
        SELECT id, title, directory, parent_id, time_created
        FROM session
        WHERE id IN (SELECT id FROM selected_session)
        ORDER BY time_created
        """
    ).fetchall()


def shorten(value: str | None, width: int) -> str:
    text = value or ""
    if len(text) <= width:
        return text
    if width <= 3:
        return text[:width]
    return text[: width - 3] + "..."


def print_sessions(sessions: list[sqlite3.Row], directory: Path | None) -> None:
    if not sessions:
        if directory is None:
            print("No sessions found.")
        else:
            print(f"No sessions found for directory: {directory}")
        return

    id_width = min(max(len("ID"), *(len(row["id"]) for row in sessions)), 28)
    title_width = min(max(len("Session"), *(len(row["title"] or "") for row in sessions)), 48)
    show_directory = directory is None

    columns = [("Created", 16), ("ID", id_width), ("Session", title_width)]
    if show_directory:
        columns.append(("Directory", 36))

    print(f"{len(sessions)} session(s)")
    if directory is not None:
        print(f"Directory: {directory}")
    print("  ".join(name.ljust(width) for name, width in columns))
    print("  ".join("-" * width for _, width in columns))

    for row in sessions:
        created = datetime.fromtimestamp(
            row["time_created"] / 1000, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M")
        values = [
            created.ljust(16),
            shorten(row["id"], id_width).ljust(id_width),
            shorten(row["title"], title_width).ljust(title_width),
        ]
        if show_directory:
            values.append(shorten(row["directory"], 36).ljust(36))
        print("  ".join(values))


def confirm(count: int) -> bool:
    if not sys.stdin.isatty():
        print("Refusing to delete without --yes in a non-interactive shell.", file=sys.stderr)
        return False
    try:
        answer = input(f"Delete these {count} session(s) and their data? [y/N] ")
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer.strip().lower() in {"y", "yes"}


def delete_sessions(con: sqlite3.Connection) -> int:
    tables = existing_tables(con)
    child_tables = [
        table
        for table in sorted(tables)
        if table != "session" and "session_id" in table_columns(con, table)
    ]

    with con:
        if "event" in tables:
            con.execute(
                "DELETE FROM event WHERE aggregate_id IN (SELECT id FROM selected_session)"
            )
        if "event_sequence" in tables:
            con.execute(
                "DELETE FROM event_sequence WHERE aggregate_id IN (SELECT id FROM selected_session)"
            )
        for table in child_tables:
            quoted = table.replace('"', '""')
            con.execute(
                f'DELETE FROM "{quoted}" WHERE session_id IN (SELECT id FROM selected_session)'
            )
        cursor = con.execute(
            "DELETE FROM session WHERE id IN (SELECT id FROM selected_session)"
        )
    return cursor.rowcount


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List and delete opencode sessions")
    parser.add_argument("--db", type=Path, help="path to opencode.db (default: auto-detect)")
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
    db_path = (args.db or default_db_path()).expanduser()
    directory = None
    if not args.all:
        directory = (args.directory or Path.cwd()).expanduser().resolve()

    try:
        con = connect(db_path)
    except (FileNotFoundError, sqlite3.Error) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    try:
        sessions = select_sessions(con, directory)
        print_sessions(sessions, directory)
        if not sessions:
            return 0
        if args.dry_run:
            print("Dry run: nothing deleted.")
            return 0
        if not args.yes and not confirm(len(sessions)):
            print("Aborted, nothing deleted.")
            return 0

        deleted = delete_sessions(con)
        print(f"Deleted {deleted} session(s) from {db_path}")
        return 0
    except sqlite3.Error as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
