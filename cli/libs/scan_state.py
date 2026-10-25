from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path

STATE_VERSION = 1
INTERVAL_DAYS = {"weekly": 7, "monthly": 30, "quarterly": 90}
MAX_FAILS = 3
GRACE_DAYS = 1


class ScanStateError(ValueError):
    """Raised when persisted scan state cannot be trusted."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def empty_state() -> dict:
    return {"version": STATE_VERSION, "updated_at": None, "apps": {}}


def load_state(path: Path) -> dict:
    if not path.exists():
        raise ScanStateError(f"state file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError as error:
        raise ScanStateError(f"state file is not valid JSON: {path}: {error}") from error
    if not isinstance(data, dict):
        raise ScanStateError(f"state root must be an object: {path}")
    apps = data.get("apps")
    if apps is None:
        apps = {}
    if not isinstance(apps, dict):
        raise ScanStateError(f"state.apps must be an object: {path}")
    data["version"] = STATE_VERSION
    data["apps"] = apps
    return data


def save_state(path: Path, state: dict) -> None:
    payload = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    path.write_text(payload + "\n", encoding="utf-8")


def stable_slot(app_name: str, interval: int) -> int:
    """Return a deterministic day slot inside the cadence cycle."""
    digest = hashlib.sha256(app_name.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % interval


def _parse_day(value) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def app_due(entry: dict, cadence: str, app_name: str, day: date) -> tuple[bool, str]:
    """Decide whether one app is due for an upstream check.

    The returned reason is only for reporting; it never changes the decision.
    """
    interval = INTERVAL_DAYS.get(cadence)
    if not interval:
        return False, f"unknown cadence: {cadence}"

    fails = int(entry.get("fails") or 0)
    if fails >= MAX_FAILS:
        return False, "needs-attention"

    last_ok = _parse_day(entry.get("ok_at"))
    if entry.get("ok_at") and last_ok is None:
        return True, "invalid-ok_at"
    if last_ok is not None:
        elapsed = (day - last_ok).days
        if elapsed >= interval:
            return True, f"due-{elapsed - interval}d-over"
        return False, f"next-in-{interval - elapsed}d"

    slot = stable_slot(app_name, interval)
    cycle_day = day.toordinal() % interval
    delta = (cycle_day - slot) % interval
    if delta <= GRACE_DAYS:
        return True, "never-checked"
    return False, f"slot-in-{(slot - cycle_day) % interval}d"


def apply_results(state: dict, results: list[dict], now_iso: str) -> dict:
    """Merge this run's results into the state and return the updated state."""
    apps = state.setdefault("apps", {})
    if not isinstance(apps, dict):
        raise ScanStateError("state.apps must be an object")
    for result in results:
        app_name = result.get("app")
        if not app_name:
            continue
        entry = apps.get(app_name)
        if entry is None:
            entry = {}
        if not isinstance(entry, dict):
            raise ScanStateError(f"state entry for {app_name} must be an object")
        if result.get("ok"):
            entry["ok_at"] = now_iso
            entry["fails"] = 0
            latest = result.get("latest")
            if latest:
                entry["latest"] = str(latest)
            else:
                entry.pop("latest", None)
        else:
            entry["fails"] = int(entry.get("fails") or 0) + 1
        entry["attempt_at"] = now_iso
        apps[app_name] = entry
    if results:
        state["updated_at"] = now_iso
    return state
