from __future__ import annotations

from packaging import version


def get_current_versions(edition: list[dict]):
    valid_versions = []
    all_versions = []

    for ed in edition:
        if ed.get("dist") != "community":
            continue
        for current in ed.get("version", []):
            all_versions.append(current)
            if str(current).lower() == "latest":
                valid_versions.append("latest")
                continue
            try:
                valid_versions.append(version.parse(str(current)))
            except version.InvalidVersion:
                continue

    return valid_versions, all_versions


def find_latest_version(tags: list[dict], current_version: str) -> dict | None:
    current_ver = version.parse(current_version)
    minor_candidates = []
    full_candidates = []

    for tag in tags:
        tag_name = tag["name"]
        try:
            tag_ver = version.parse(tag_name)
        except version.InvalidVersion:
            continue

        if tag_ver.is_prerelease or tag_ver.is_devrelease:
            continue

        if tag_ver <= current_ver:
            continue

        if len(tag_ver.release) == 2:
            minor_candidates.append((tag_ver, tag_name, tag["last_updated"]))
        else:
            full_candidates.append((tag_ver, tag_name, tag["last_updated"]))

    pool = minor_candidates or full_candidates
    if not pool:
        return None

    best = max(pool, key=lambda item: item[0])
    return {
        "version": best[1],
        "last_updated": best[2],
    }
