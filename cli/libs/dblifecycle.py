from __future__ import annotations

import json
from datetime import date

from libs.http import get
from libs.repo import relative_repo_path, repo_path


API_TEMPLATE = "https://endoflife.date/api/{engine}.json"
STALE_DAYS = 45

ENGINE_TRACKS = {
    "mysql": lambda lts: "lts" if lts else "innovation",
    "mariadb": lambda lts: "lts" if lts else "short-term",
    "postgresql": lambda lts: "stable",
    "clickhouse": lambda lts: "lts" if lts else "stable",
    "redis": lambda lts: "stable",
}


def fetch_engine(engine: str) -> list[dict]:
    response = get(API_TEMPLATE.format(engine=engine))
    response.raise_for_status()
    return response.json()


def lifecycle_path():
    return repo_path("metadata", "db-lifecycle.json")


def keep_cycle(cycle: dict, today: date) -> bool:
    eol = cycle.get("eol")
    if not eol:
        return True
    eol_date = date.fromisoformat(str(eol)[:10])
    if eol_date >= today:
        return True
    if cycle.get("lts") and eol_date.year >= today.year - 1:
        return True
    return False


def build_tracks(cycles: list[dict], engine: str, today: date) -> list[dict]:
    track_fn = ENGINE_TRACKS[engine]
    tracks = []
    for cycle in cycles:
        if not keep_cycle(cycle, today):
            continue
        eol = cycle.get("eol")
        tracks.append({
            "version": str(cycle.get("cycle")),
            "track": track_fn(bool(cycle.get("lts"))),
            "eol": str(eol)[:10] if eol else None,
        })
    return tracks


def load_lifecycle() -> dict:
    path = lifecycle_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def refresh_lifecycle(engine: str | None = None) -> dict:
    if engine and engine not in ENGINE_TRACKS:
        raise ValueError(f"unknown engine: {engine}")

    engines = [engine] if engine else sorted(ENGINE_TRACKS)
    payload = load_lifecycle()
    payload.setdefault("version", 1)
    payload["updated_at"] = date.today().isoformat()
    payload.setdefault("engines", {})

    refreshed = {}
    for name in engines:
        tracks = build_tracks(fetch_engine(name), name, date.today())
        payload["engines"][name] = {
            "source": API_TEMPLATE.format(engine=name),
            "tracks": tracks,
        }
        refreshed[name] = len(tracks)

    path = lifecycle_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "path": relative_repo_path(path),
        "updated_at": payload["updated_at"],
        "refreshed": refreshed,
    }


def is_stale(max_days: int = STALE_DAYS) -> bool:
    payload = load_lifecycle()
    updated_at = payload.get("updated_at")
    if not updated_at:
        return True
    try:
        updated = date.fromisoformat(updated_at)
    except ValueError:
        return True
    return (date.today() - updated).days > max_days
