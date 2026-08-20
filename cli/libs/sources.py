from __future__ import annotations

import time
import re

from packaging import version

from libs.http import get
from libs.versioning import find_latest_version


VERSION_START_RE = re.compile(r"^v?(\d+)")

DOCKERHUB_URLS = ("hub.docker.com",)
GITHUB_RELEASES_URLS = ("github.com",)
GHCR_URLS = ("ghcr.io",)


def detect_source_type(url: str) -> str | None:
    lowered = url.lower()
    if any(marker in lowered for marker in DOCKERHUB_URLS):
        return "dockerhub-tags"
    if any(marker in lowered for marker in GHCR_URLS):
        return "ghcr-tags"
    if any(marker in lowered for marker in GITHUB_RELEASES_URLS):
        if "releases" in lowered:
            return "github-releases"
        return "github-tags"
    return None


def fetch_candidates(
    source_type: str,
    url: str,
    current_version: str,
    major_ahead: int = 3,
    page_size: int = 100,
) -> tuple[dict | None, str | None]:
    if source_type == "dockerhub-tags":
        return _fetch_dockerhub(url, current_version, major_ahead, page_size)
    if source_type == "ghcr-tags":
        return _fetch_ghcr(url, current_version, major_ahead, page_size)
    if source_type == "github-releases":
        return _fetch_github_releases(url, current_version, page_size)
    if source_type == "github-tags":
        return _fetch_github_tags(url, current_version, page_size)
    return None, f"unsupported source type: {source_type}"


def _major_prefix(version_str: str) -> str | None:
    match = VERSION_START_RE.match(version_str)
    if not match:
        return None
    return f"{match.group(1)}."


def _get_json(url: str, params: dict | None = None) -> tuple[dict | list | None, str | None]:
    try:
        response = get(url, params)
        if response.status_code == 429:
            time.sleep(1)
            response = get(url, params)
        response.raise_for_status()
        return response.json(), None
    except Exception as error:
        return None, str(error)


def _dockerhub_api_url(version_from_url: str) -> str | None:
    try:
        path_parts = version_from_url.split("/")
        if "_/" in version_from_url:
            image_name = path_parts[-2]
            return f"https://hub.docker.com/v2/repositories/library/{image_name}/tags"

        namespace = path_parts[-3]
        image_name = path_parts[-2]
        return f"https://hub.docker.com/v2/repositories/{namespace}/{image_name}/tags"
    except Exception:
        return None


def _fetch_dockerhub(url: str, current_version: str, major_ahead: int, page_size: int) -> tuple[dict | None, str | None]:
    api_url = _dockerhub_api_url(url)
    if not api_url:
        return None, "invalid Docker Hub URL"

    prefix = _major_prefix(current_version)
    if prefix is None:
        tags, error = _dockerhub_tags(api_url, name=None, page_size=page_size)
        if error:
            return None, error
        return find_latest_version(tags, current_version), None

    major = int(prefix[:-1])
    queries = [prefix] + [f"{m}." for m in range(major + 1, major + 1 + major_ahead)]
    tags = []
    for query in queries:
        page, error = _dockerhub_tags(api_url, name=query, page_size=page_size)
        if error:
            return None, error
        tags.extend(page)

    return find_latest_version(tags, current_version), None


def _dockerhub_tags(api_url: str, name: str | None, page_size: int) -> tuple[list[dict], str | None]:
    params = {"page_size": page_size}
    if name:
        params["name"] = name
    data, error = _get_json(api_url, params)
    if error:
        return [], error
    return (data or {}).get("results") or [], None


def _ghcr_repository(url: str) -> tuple[str, str] | None:
    try:
        parts = [part for part in url.split("/") if part]
        host_index = next(i for i, part in enumerate(parts) if "ghcr.io" in part)
        rest = parts[host_index + 1:]
        if len(rest) < 2:
            return None
        namespace = rest[0]
        image = rest[1].split(":")[0]
        return namespace, image
    except Exception:
        return None


def _ghcr_token(namespace: str, image: str) -> tuple[str | None, str | None]:
    data, error = _get_json(
        "https://ghcr.io/token",
        {"scope": f"repository:{namespace}/{image}:pull", "service": "ghcr.io"},
    )
    if error:
        return None, error
    token = (data or {}).get("token")
    if not token:
        return None, "GHCR token endpoint returned no token"
    return token, None


def _ghcr_tags_page(namespace: str, image: str, token: str, page_size: int, last: str | None = None) -> tuple[list[str], str | None, str | None]:
    params = {"n": min(page_size, 1000)}
    if last:
        params["last"] = last
    try:
        response = get(
            f"https://ghcr.io/v2/{namespace}/{image}/tags/list",
            params,
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 429:
            time.sleep(1)
            response = get(
                f"https://ghcr.io/v2/{namespace}/{image}/tags/list",
                params,
                headers={"Authorization": f"Bearer {token}"},
            )
        response.raise_for_status()
        data = response.json()
        return (data or {}).get("tags") or [], response.headers.get("Link"), None
    except Exception as error:
        return [], None, str(error)


def _fetch_ghcr(url: str, current_version: str, major_ahead: int, page_size: int) -> tuple[dict | None, str | None]:
    repository = _ghcr_repository(url)
    if not repository:
        return None, "invalid GHCR URL"
    namespace, image = repository

    token, error = _ghcr_token(namespace, image)
    if error:
        return None, error

    tags: list[str] = []
    for _ in range(3):
        page_tags, link, error = _ghcr_tags_page(namespace, image, token, page_size, tags[-1] if tags else None)
        if error:
            return None, error
        tags.extend(page_tags)
        if not link or "rel=\"next\"" not in link:
            break

    candidates = [{"name": tag, "last_updated": ""} for tag in tags]
    return find_latest_version(candidates, current_version), None


def _github_api_url(version_from_url: str) -> str | None:
    try:
        parts = [part for part in version_from_url.split("/") if part]
        if len(parts) < 4 or parts[1] != "github.com":
            return None
        owner = parts[2]
        repo = parts[3].replace(".git", "")
        return f"https://api.github.com/repos/{owner}/{repo}"
    except Exception:
        return None


def _fetch_github_releases(url: str, current_version: str, page_size: int) -> tuple[dict | None, str | None]:
    api_url = _github_api_url(url)
    if not api_url:
        return None, "invalid GitHub releases URL"

    data, error = _get_json(f"{api_url}/releases", {"per_page": min(page_size, 100)})
    if error:
        return None, error

    tags = []
    for release in data or []:
        if release.get("prerelease") or release.get("draft"):
            continue
        tags.append({
            "name": release.get("tag_name") or "",
            "last_updated": release.get("published_at") or "",
        })

    if not tags:
        return _fetch_github_tags(url, current_version, page_size)

    return find_latest_version(tags, current_version), None


def _fetch_github_tags(url: str, current_version: str, page_size: int) -> tuple[dict | None, str | None]:
    tags, error = _github_tags_raw(url, page_size)
    if error:
        return None, error
    return find_latest_version(tags, current_version), None


def _github_tags_raw(url: str, page_size: int) -> tuple[list[dict], str | None]:
    api_url = _github_api_url(url)
    if not api_url:
        return [], "invalid GitHub URL"

    data, error = _get_json(f"{api_url}/tags", {"per_page": min(page_size, 100)})
    if error:
        return [], error

    return [
        {"name": item.get("name") or "", "last_updated": ""}
        for item in (data or [])
    ], None


def _stable_candidates(tags: list[dict], current_version: str, limit: int = 5) -> list[str]:
    current_ver = version.parse(current_version)
    candidates = set()

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

        candidates.add(tag_name)

    def version_key(name):
        return version.parse(name)

    return sorted(candidates, key=version_key, reverse=True)[:limit]


def _dockerhub_verify(api_url: str, candidate: str, page_size: int) -> dict | None:
    candidate_ver = version.parse(candidate)
    params = {"page_size": page_size, "name": candidate.lstrip("v")}
    data, error = _get_json(api_url, params)
    if error or not data:
        return None

    best = None
    for tag in (data or {}).get("results") or []:
        tag_name = tag["name"]
        try:
            if version.parse(tag_name) == candidate_ver:
                best = {
                    "version": candidate,
                    "last_updated": tag["last_updated"],
                }
                break
        except version.InvalidVersion:
            continue

    return best


def fetch_verified_candidates(
    verify_type: str,
    verify_url: str,
    index_type: str,
    index_url: str,
    current_version: str,
    major_ahead: int = 3,
    page_size: int = 100,
) -> tuple[dict | None, str | None]:
    def fallback() -> tuple[dict | None, str | None]:
        return fetch_candidates(
            verify_type,
            verify_url,
            current_version,
            major_ahead=major_ahead,
            page_size=page_size,
        )

    if index_type not in ("github-releases", "github-tags"):
        return fallback()

    index_tags, error = _github_tags_raw(index_url, page_size)
    if error:
        return fallback()

    candidates = _stable_candidates(index_tags, current_version)
    minors = sorted(
        {version.parse(name).release[:2] for name in candidates},
        reverse=True,
    )
    wanted = [".".join(str(p) for p in minor) for minor in minors] + candidates

    if verify_type == "dockerhub-tags":
        api_url = _dockerhub_api_url(verify_url)
        if not api_url:
            return None, "invalid Docker Hub URL"
        for candidate in wanted:
            confirmed = _dockerhub_verify(api_url, candidate, page_size)
            if confirmed:
                return confirmed, None
        return fallback()

    if verify_type == "ghcr-tags":
        repository = _ghcr_repository(verify_url)
        if not repository:
            return None, "invalid GHCR URL"
        namespace, image = repository
        token, error = _ghcr_token(namespace, image)
        if error:
            return fallback()

        tags: list[str] = []
        for _ in range(3):
            page_tags, link, error = _ghcr_tags_page(namespace, image, token, page_size, tags[-1] if tags else None)
            if error:
                return fallback()
            tags.extend(page_tags)
            if not link or "rel=\"next\"" not in link:
                break

        tag_set = set(tags)
        for candidate in wanted:
            if candidate in tag_set or candidate.lstrip("v") in tag_set:
                return {"version": candidate, "last_updated": ""}, None
        return fallback()

    return None, f"unsupported verify source type: {verify_type}"
