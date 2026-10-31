from __future__ import annotations

import re

from packaging import version


VARIANT_SUFFIX_RE = re.compile(
    r"^v?(\d+(?:\.\d+)*)(?:[-_]?(rc|alpha|beta|dev|pre|preview|canary|nightly|snapshot|insider)[.-]?(\d+)?)?(?:[-_].*)?$",
    re.IGNORECASE,
)
PREFIXED_VERSION_RE = re.compile(r"^([a-z][a-z_-]*?)(?:v)?(\d+(?:\.\d+)*)(.*)$", re.IGNORECASE)

NON_STABLE_CHANNELS = {"canary", "nightly", "snapshot", "preview", "insider"}
UNSTABLE_TOKENS = ("rc", "alpha", "beta", "dev", "pre", "preview", "canary", "nightly", "snapshot", "insider")


def normalize_tag(name: str, reference: str | None = None) -> str:
    """Return the comparable version part of an image or release tag.

    Handles common official-image variants such as ``11.4-apache``,
    ``7.1-fpm``, ``11-alpine``, ``9.0-cli-ls84`` and
    ``11.4.11-php8.3-apache``. For prefixed numeric tags, ``reference``
    establishes the prefix (for example ``pg18-trixie`` or ``stable-11248``)
    so unrelated numbers in image labels are not mistaken for versions.
    """
    normalized = re.sub(r"-ls\d+$", "", name)
    # Metabase publishes release trains with an ``.x`` patch placeholder,
    # such as ``v0.64.1.x``. Treat it as the numeric release for comparison.
    normalized = re.sub(r"\.x$", "", normalized, flags=re.IGNORECASE)
    if normalized.endswith("-cli"):
        normalized = normalized[:-4]
    try:
        version.parse(normalized)
        return normalized
    except version.InvalidVersion:
        match = VARIANT_SUFFIX_RE.match(normalized)
        if not match and reference:
            reference_match = PREFIXED_VERSION_RE.match(reference)
            if reference_match:
                prefix = reference_match.group(1)
                if normalized.lower().startswith(prefix.lower()):
                    match = VARIANT_SUFFIX_RE.match(normalized[len(prefix):])
        if not match:
            return normalized
        base = match.group(1)
        prerelease = match.group(2)
        number = match.group(3)
        if prerelease:
            if prerelease.lower() in NON_STABLE_CHANNELS:
                return f"{base}.dev{number or '0'}"
            return f"{base}-{prerelease}{number or ''}"
        lowered = normalized.lower()
        if any(
            re.search(rf"(?:^|[._-]){re.escape(token)}(?:[._-]|$)", lowered)
            for token in UNSTABLE_TOKENS
        ):
            return f"{base}.dev0"
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
                valid_versions.append(version.parse(normalize_tag(str(current), str(current))))
            except version.InvalidVersion:
                continue

    return valid_versions, all_versions


def _variant_tokens(name: str) -> set[str]:
    if name.lower() == "latest":
        return set()
    tail = re.sub(r"(?<!\d)v?\d+(?:\.\d+)*(?:\.x)?", "", name.lower())
    tail = re.sub(r"(?<=[-_])ls\d+(?=$|[-_])", "", tail)
    return {token for token in re.split(r"[-_.]", tail) if token and not token.isdigit()}


def _tag_version(name: str, reference: str | None = None) -> version.Version:
    if name.lower() == "latest":
        return version.Version("0")
    return version.parse(normalize_tag(name, reference))


def variant_score(name: str, current_version: str) -> tuple:
    """Rank variant continuity before version freshness (lower is better)."""
    preferred = _variant_tokens(current_version)
    tokens = _variant_tokens(name)
    # Exact suffix tokens, then partial overlap, then unrelated variants.
    if tokens == preferred:
        return (0, 0, 0)
    shared = len(tokens & preferred)
    return (1 if shared else 2, -shared, len(tokens - preferred))


def prefer_tag_variants(candidates: list, current_version: str, name=lambda item: item[1]) -> list:
    if not candidates:
        return []
    best = min(variant_score(name(item), current_version) for item in candidates)
    return [item for item in candidates if variant_score(name(item), current_version) == best]


def _prefer_variant(tags: list[dict], candidates: list[tuple], current_version: str) -> tuple:
    preferred = _variant_tokens(current_version)
    if not preferred:
        return min(candidates, key=lambda item: (
            item[1].startswith("v") != current_version.startswith("v"),
            len(item[1].split("-")), len(item[1]), item[1],
        ))

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
    current_ver = _tag_version(current_version, current_version)
    minor_candidates = []
    full_candidates = []

    for tag in tags:
        tag_name = tag["name"]
        try:
            tag_ver = _tag_version(tag_name, current_version)
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

    variants = prefer_tag_variants(minor_candidates + full_candidates, current_version)
    pool = [item for item in variants if len(item[0].release) == 2] or variants
    if not pool:
        return None

    best_version = max(item[0] for item in pool)
    same_version = [item for item in pool if item[0] == best_version]
    best = _prefer_variant(tags, same_version, current_version)
    return {
        "version": best[1],
        "last_updated": best[2],
    }


def select_candidates(tags: list[dict], current_version: str, limit: int = 1) -> dict | None:
    """Keep the old single-candidate API, optionally attaching ranked alternatives."""
    remaining = list(tags)
    selected = []
    for _ in range(max(1, min(limit, 3))):
        candidate = find_latest_version(remaining, current_version)
        if candidate is None:
            break
        selected.append(candidate)
        remaining = [tag for tag in remaining if tag["name"] != candidate["version"]]
    if not selected:
        return None
    result = dict(selected[0])
    if limit > 1:
        result["candidates"] = selected
    return result


def update_status(current_version: str, candidate: dict | None) -> str:
    """Classify a candidate while respecting floating minor image tags.

    A current ``x.x`` tag already receives upstream ``x.x.y`` patch updates,
    so a patch candidate in the same minor is informational rather than a
    package update.
    """
    if not candidate:
        return "up-to-date"

    if current_version.lower() == "latest":
        return "update-available"

    current = _tag_version(current_version, current_version)
    latest = _tag_version(str(candidate.get("version", "")), current_version)
    if latest <= current:
        return "up-to-date"
    if len(current.release) == 2 and latest.release[:2] == current.release[:2]:
        return "covered-by-current-minor-tag"
    return "update-available"
