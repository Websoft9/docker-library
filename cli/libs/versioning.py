from __future__ import annotations

import re

from packaging import version


VARIANT_SUFFIX_RE = re.compile(
    r"^v?(\d+(?:\.\d+)*)(?:[-_]?(rc|alpha|beta|dev|pre)[.-]?(\d+)?)?(?:[-_].*)?$",
    re.IGNORECASE,
)


def normalize_tag(name: str) -> str:
    """Return the comparable version part of an image or release tag.

    Handles common official-image variants such as ``11.4-apache``,
    ``7.1-fpm``, ``11-alpine``, ``9.0-cli-ls84`` and
    ``11.4.11-php8.3-apache``. If the original value is already a valid
    PEP 440 version (for example ``12.0-rc`` or ``1.2rc1``), it is preserved
    so prerelease filtering still works.
    """
    normalized = re.sub(r"-ls\d+$", "", name)
    if normalized.endswith("-cli"):
        normalized = normalized[:-4]
    try:
        version.parse(normalized)
        return normalized
    except version.InvalidVersion:
        match = VARIANT_SUFFIX_RE.match(normalized)
        if not match:
            return normalized
        base = match.group(1)
        prerelease = match.group(2)
        number = match.group(3)
        if prerelease:
            return f"{base}-{prerelease}{number or ''}"
        return base


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
                valid_versions.append(version.parse(normalize_tag(str(current))))
            except version.InvalidVersion:
                continue

    return valid_versions, all_versions


def _variant_tokens(name: str) -> set[str]:
    normalized = normalize_tag(name).lower()
    lowered = name.lower()
    index = lowered.find(normalized)
    tail = lowered[index + len(normalized):] if index >= 0 else lowered
    return {token for token in re.split(r"[-_.]", tail) if token and not token.isdigit()}


def _prefer_variant(tags: list[dict], candidates: list[tuple], current_version: str) -> tuple:
    preferred = _variant_tokens(current_version)
    if not preferred:
        return min(candidates, key=lambda item: (len(item[1].split("-")), len(item[1]), item[1]))

    def score(item):
        _version_value, tag_name, _last_updated = item
        tokens = _variant_tokens(tag_name)
        shared = len(tokens & preferred)
        extra = len(tokens - preferred)
        return (-shared, extra)

    best_score = min(score(item) for item in candidates)
    best_group = [item for item in candidates if score(item) == best_score]
    return max(best_group, key=lambda item: (item[2], -len(item[1]), item[1]))


def find_latest_version(tags: list[dict], current_version: str) -> dict | None:
    current_ver = version.parse(normalize_tag(current_version))
    minor_candidates = []
    full_candidates = []

    for tag in tags:
        tag_name = tag["name"]
        try:
            tag_ver = version.parse(normalize_tag(tag_name))
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

    best_version = max(item[0] for item in pool)
    same_version = [item for item in pool if item[0] == best_version]
    best = _prefer_variant(tags, same_version, current_version)
    return {
        "version": best[1],
        "last_updated": best[2],
    }
