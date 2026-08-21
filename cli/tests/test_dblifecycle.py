from __future__ import annotations

from datetime import date as real_date

import json

from libs import dblifecycle


class FakeDate(real_date):
    @classmethod
    def today(cls):
        return cls(2026, 8, 20)


def test_keep_cycle_accepts_active_and_recent_lts_cycles():
    today = real_date(2026, 8, 20)

    assert dblifecycle.keep_cycle({"eol": "2027-01-01"}, today) is True
    assert dblifecycle.keep_cycle({"eol": "2025-01-01", "lts": True}, today) is True
    assert dblifecycle.keep_cycle({"eol": "2024-01-01", "lts": False}, today) is False


def test_build_tracks_maps_engine_track_names():
    tracks = dblifecycle.build_tracks(
        [
            {"cycle": "8.4", "lts": True, "eol": "2032-04-30"},
            {"cycle": "9.0", "lts": False, "eol": "2025-04-30"},
        ],
        "mysql",
        real_date(2026, 8, 20),
    )

    assert tracks == [{"version": "8.4", "track": "lts", "eol": "2032-04-30"}]


def test_refresh_lifecycle_writes_snapshot(repo_fixture, monkeypatch):
    monkeypatch.setattr(dblifecycle, "date", FakeDate)
    monkeypatch.setattr(
        dblifecycle,
        "fetch_engine",
        lambda engine: [{"cycle": "8.4", "lts": True, "eol": "2032-04-30"}],
    )

    result = dblifecycle.refresh_lifecycle(engine="mysql")
    payload = json.loads((repo_fixture / "metadata" / "db-lifecycle.json").read_text(encoding="utf-8"))

    assert result == {
        "path": "metadata/db-lifecycle.json",
        "updated_at": "2026-08-20",
        "refreshed": {"mysql": 1},
    }
    assert payload["engines"]["mysql"]["tracks"] == [{"version": "8.4", "track": "lts", "eol": "2032-04-30"}]


def test_is_stale_detects_missing_invalid_and_old_snapshots(repo_fixture):
    path = repo_fixture / "metadata" / "db-lifecycle.json"

    assert dblifecycle.is_stale() is True

    path.write_text('{"updated_at":"bad"}\n', encoding="utf-8")
    assert dblifecycle.is_stale() is True

    path.write_text('{"updated_at":"2026-06-01"}\n', encoding="utf-8")
    assert dblifecycle.is_stale(max_days=30) is True

    path.write_text('{"updated_at":"2026-08-10"}\n', encoding="utf-8")
    assert dblifecycle.is_stale(max_days=30) is False
