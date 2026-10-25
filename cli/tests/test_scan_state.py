from __future__ import annotations

from datetime import date, timedelta

import pytest

from libs import scan_state


def test_stable_slot_is_deterministic_and_in_range():
    first = scan_state.stable_slot("wordpress", 7)

    assert first == scan_state.stable_slot("wordpress", 7)
    assert 0 <= first < 7


def test_never_checked_app_is_due_only_in_its_slot_window():
    app = "wordpress"
    interval = scan_state.INTERVAL_DAYS["weekly"]
    slot = scan_state.stable_slot(app, interval)
    day = date.fromordinal((date(2026, 1, 1).toordinal() // interval) * interval + slot)

    assert scan_state.app_due({}, "weekly", app, day) == (True, "never-checked")
    assert scan_state.app_due({}, "weekly", app, day + timedelta(days=1)) == (True, "never-checked")
    assert scan_state.app_due({}, "weekly", app, day + timedelta(days=2))[0] is False


def test_checked_app_is_due_after_its_interval():
    today = date(2026, 10, 25)
    recent = {"ok_at": (today - timedelta(days=6)).isoformat()}
    overdue = {"ok_at": (today - timedelta(days=7)).isoformat()}

    assert scan_state.app_due(recent, "weekly", "wordpress", today)[0] is False
    assert scan_state.app_due(overdue, "weekly", "wordpress", today)[0] is True


def test_failed_app_stops_consuming_scan_budget():
    entry = {"fails": scan_state.MAX_FAILS}

    due, reason = scan_state.app_due(entry, "weekly", "wordpress", date(2026, 10, 25))

    assert due is False
    assert reason == "needs-attention"


def test_unknown_cadence_is_not_due():
    due, reason = scan_state.app_due({}, "none", "wordpress", date(2026, 10, 25))

    assert due is False
    assert reason == "unknown cadence: none"


def test_apply_results_increments_failures_and_resets_on_success():
    state = scan_state.empty_state()
    now = "2026-10-25T03:17:00Z"

    scan_state.apply_results(state, [{"app": "a", "ok": False}], now)
    scan_state.apply_results(state, [{"app": "a", "ok": False}], now)
    assert state["apps"]["a"]["fails"] == 2

    scan_state.apply_results(state, [{"app": "a", "ok": True, "latest": "1.2"}], now)

    assert state["apps"]["a"] == {
        "ok_at": now,
        "fails": 0,
        "attempt_at": now,
        "latest": "1.2",
    }


def test_load_state_fails_closed_when_missing(tmp_path):
    with pytest.raises(scan_state.ScanStateError):
        scan_state.load_state(tmp_path / "missing.json")


def test_load_state_fails_closed_on_invalid_json(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(scan_state.ScanStateError):
        scan_state.load_state(path)


def test_save_state_round_trip(tmp_path):
    path = tmp_path / "state.json"
    state = scan_state.empty_state()
    state["apps"]["wordpress"] = {
        "ok_at": "2026-10-25T03:17:00Z",
        "fails": 0,
        "attempt_at": "2026-10-25T03:17:00Z",
    }

    scan_state.save_state(path, state)

    assert scan_state.load_state(path)["apps"]["wordpress"]["ok_at"] == "2026-10-25T03:17:00Z"


def test_load_state_rejects_non_object_apps(tmp_path):
    path = tmp_path / "state.json"
    path.write_text('{"apps": []}', encoding="utf-8")

    with pytest.raises(scan_state.ScanStateError):
        scan_state.load_state(path)


def test_app_with_invalid_timestamp_is_due_again():
    due, reason = scan_state.app_due(
        {"ok_at": "not-a-date"},
        "weekly",
        "wordpress",
        date(2026, 10, 25),
    )

    assert due is True
    assert reason == "invalid-ok_at"
