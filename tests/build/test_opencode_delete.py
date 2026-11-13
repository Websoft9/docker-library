from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from _helpers import REPO_ROOT, load_build_module

opencode_delete = load_build_module(
    "opencode_delete_test", REPO_ROOT / "ci" / "scripts" / "opencode_delete.py"
)


def test_list_sessions_uses_v2_api_and_follows_cursors(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    pages = [
        {"data": [{"id": "ses-one"}], "cursor": {"next": "next-page"}},
        {"data": [{"id": "ses-two"}], "cursor": {"next": None}},
    ]

    def fake_api_request(*args: str) -> str:
        calls.append(args[1])
        return json.dumps(pages.pop(0))

    monkeypatch.setattr(opencode_delete, "api_request", fake_api_request)
    directory = Path("/workspace/project")

    sessions = opencode_delete.list_sessions(directory)

    assert [session["id"] for session in sessions] == ["ses-one", "ses-two"]
    first_params = parse_qs(urlsplit(calls[0]).query)
    second_params = parse_qs(urlsplit(calls[1]).query)
    assert first_params == {
        "limit": ["100"],
        "order": ["asc"],
        "parentID": ["null"],
        "directory": [str(directory)],
    }
    assert second_params["cursor"] == ["next-page"]


def test_list_sessions_rejects_repeated_cursor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        opencode_delete,
        "api_request",
        lambda *_: json.dumps({"data": [], "cursor": {"next": "same"}}),
    )

    with pytest.raises(RuntimeError, match="repeated session cursor"):
        opencode_delete.list_sessions(None)


def test_dry_run_does_not_delete(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    sessions = [{"id": "ses-root", "title": "Example", "time": {}, "location": {}}]
    monkeypatch.setattr(opencode_delete, "list_sessions", lambda _directory: sessions)
    monkeypatch.setattr(opencode_delete, "api_request", lambda *_: pytest.fail("unexpected delete"))

    assert opencode_delete.main(["--dry-run"]) == 0
    assert "Dry run: nothing deleted." in capsys.readouterr().out


def test_delete_uses_api_for_each_root(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    sessions = [
        {"id": "ses-root/one", "title": "First", "time": {}, "location": {}},
        {"id": "ses-root-two", "title": "Second", "time": {}, "location": {}},
    ]
    calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(opencode_delete, "list_sessions", lambda _directory: sessions)
    monkeypatch.setattr(opencode_delete, "api_request", lambda *args: calls.append(args) or "")

    assert opencode_delete.main(["--yes"]) == 0
    assert calls == [
        ("delete", "/api/session/ses-root%2Fone"),
        ("delete", "/api/session/ses-root-two"),
    ]
    assert "Deleted 2 root session(s) and their child sessions." in capsys.readouterr().out
