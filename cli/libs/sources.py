from __future__ import annotations

import os
import re
from urllib.parse import urljoin

from packaging import version

from libs.http import get, get_json_with_fallback, probe_url
from libs.versioning import normalize_tag, variant_score, select_candidates


VERSION_START_RE = re.compile(r"^v?(\d+)")

DOCKERHUB_URLS = ("hub.docker.com",)
GITHUB_RELEASES_URLS = ("github.com",)
GHCR_URLS = ("ghcr.io",)
ECR_PUBLIC_URLS = ("gallery.ecr.aws", "public.ecr.aws")
MANIFEST_ACCEPT = (
    "application/vnd.oci.image.index.v1+json, "
    "application/vnd.docker.distribution.manifest.list.v2+json, "
    "application/vnd.docker.distribution.manifest.v2+json"
)


def detect_source_type(url: str) -> str | None:
    lowered = url.lower()
    if any(marker in lowered for marker in DOCKERHUB_URLS):
        return "dockerhub-tags"
    if any(marker in lowered for marker in GHCR_URLS):
        return "ghcr-tags"
    if any(marker in lowered for marker in ECR_PUBLIC_URLS):
        return "ecr-public"
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
    candidate_limit: int = 1,
) -> tuple[dict | None, str | None]:
    if source_type == "dockerhub-tags":
        return _fetch_dockerhub(url, current_version, major_ahead, page_size, candidate_limit)
    if source_type == "ghcr-tags":
        return _fetch_ghcr(url, current_version, major_ahead, page_size, candidate_limit)
    if source_type == "ecr-public":
        return _fetch_ecr_public(url, current_version, major_ahead, page_size, candidate_limit)
    if source_type == "github-releases":
        return _fetch_github_releases(url, current_version, page_size, candidate_limit)
    if source_type == "github-tags":
        return _fetch_github_tags(url, current_version, page_size, candidate_limit)
    return None, f"unsupported source type: {source_type}"


def _major_prefix(version_str: str) -> str | None:
    match = VERSION_START_RE.match(version_str)
    if not match:
        return None
    return f"{match.group(1)}."


def _get_json(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
) -> tuple[dict | list | None, str | None]:
    request_headers = dict(headers or {})
    if "api.github.com" in url and "Authorization" not in request_headers:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            request_headers["Authorization"] = f"Bearer {token}"
    data, _headers, error = get_json_with_fallback(url, params, request_headers or None)
    return data, error


def _dockerhub_api_url(url: str) -> str | None:
    try:
        path = url.split("//", 1)[1]
        parts = [part for part in path.split("/") if part]
        if len(parts) < 3:
            return None
        if parts[1] == "_" and len(parts) >= 3:
            image_name = parts[2]
            return f"https://hub.docker.com/v2/repositories/library/{image_name}/tags"
        if parts[1] == "r" and len(parts) >= 4:
            namespace = parts[2]
            image_name = parts[3]
            return f"https://hub.docker.com/v2/repositories/{namespace}/{image_name}/tags"
        return None
    except Exception:
        return None


def _fetch_dockerhub(url: str, current_version: str, major_ahead: int, page_size: int, candidate_limit: int = 1) -> tuple[dict | None, str | None]:
    api_url = _dockerhub_api_url(url)
    if not api_url:
        return None, "invalid Docker Hub URL"

    prefix = _major_prefix(current_version)
    if prefix is None:
        tags, error = _dockerhub_tags(api_url, name=None, page_size=page_size)
        if error:
            return None, error
        return select_candidates(tags, current_version, candidate_limit), None

    major = int(prefix[:-1])
    queries = [prefix] + [f"{m}." for m in range(major + 1, major + 1 + major_ahead)]
    tags = []
    for query in queries:
        page, error = _dockerhub_tags(api_url, name=query, page_size=page_size)
        if error:
            return None, error
        tags.extend(page)

    # A busy repository's first page can contain only unrelated editions.
    suffix = re.match(r"^v?\d+(?:\.\d+)*([-_].+)$", current_version)
    if suffix:
        page, error = _dockerhub_tags(api_url, name=suffix.group(1), page_size=page_size)
        if error:
            return None, error
        tags.extend(page)

    allowed_majors = set(range(major, major + major_ahead + 1))
    filtered = []
    for tag in tags:
        try:
            tag_ver = version.parse(normalize_tag(tag["name"]))
        except version.InvalidVersion:
            continue
        if tag_ver.release and tag_ver.release[0] in allowed_majors:
            filtered.append(tag)

    return select_candidates(filtered, current_version, candidate_limit), None


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
    url = f"https://ghcr.io/v2/{namespace}/{image}/tags/list"
    headers = {"Authorization": f"Bearer {token}"}
    data, response_headers, error = get_json_with_fallback(url, params, headers)
    if error:
        return [], None, error
    return (data or {}).get("tags") or [], (response_headers or {}).get("Link"), None


def _fetch_ghcr(url: str, current_version: str, major_ahead: int, page_size: int, candidate_limit: int = 1) -> tuple[dict | None, str | None]:
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
    return select_candidates(candidates, current_version, candidate_limit), None


def _ecr_public_repository(url: str) -> tuple[str, str] | None:
    try:
        parts = [part for part in url.split("/") if part]
        host_index = next(i for i, part in enumerate(parts) if "ecr.aws" in part)
        rest = parts[host_index + 1:]
        if len(rest) < 2:
            return None
        namespace = rest[0]
        image = rest[1].split(":")[0]
        return namespace, image
    except Exception:
        return None


def _ecr_public_token(namespace: str, image: str) -> tuple[str | None, str | None]:
    data, error = _get_json(
        "https://public.ecr.aws/token/",
        {"service": "ecr-public", "scope": f"repository:{namespace}/{image}:pull"},
    )
    if error:
        return None, error
    token = (data or {}).get("token")
    if not token:
        return None, "ECR Public token endpoint returned no token"
    return token, None


def _ecr_public_next_url(link: str | None) -> str | None:
    if not link:
        return None
    match = re.search(r"<([^>]+)>", link)
    if not match:
        return None
    return urljoin("https://public.ecr.aws", match.group(1))


def _ecr_public_tags_page(
    namespace: str,
    image: str,
    token: str,
    page_size: int,
    next_url: str | None = None,
) -> tuple[list[str], str | None, str | None]:
    url = next_url or f"https://public.ecr.aws/v2/{namespace}/{image}/tags/list"
    params = None if next_url else {"n": min(page_size, 1000)}
    headers = {"Authorization": f"Bearer {token}"}
    data, response_headers, error = get_json_with_fallback(url, params, headers)
    if error:
        return [], None, error
    return (
        (data or {}).get("tags") or [],
        _ecr_public_next_url((response_headers or {}).get("Link")),
        None,
    )


def _fetch_ecr_public(
    url: str,
    current_version: str,
    major_ahead: int,
    page_size: int,
    candidate_limit: int = 1,
) -> tuple[dict | None, str | None]:
    repository = _ecr_public_repository(url)
    if not repository:
        return None, "invalid ECR Public URL"
    namespace, image = repository

    token, error = _ecr_public_token(namespace, image)
    if error:
        return None, error

    tags: list[str] = []
    next_url = None
    for _ in range(20):
        page_tags, next_url, error = _ecr_public_tags_page(namespace, image, token, page_size, next_url)
        if error:
            return None, error
        tags.extend(page_tags)
        if not next_url:
            break

    prefix = _major_prefix(current_version)
    allowed_majors = None
    if prefix is not None:
        major = int(prefix[:-1])
        allowed_majors = set(range(major, major + major_ahead + 1))

    filtered = []
    for tag in tags:
        try:
            tag_ver = version.parse(normalize_tag(tag))
        except version.InvalidVersion:
            continue
        if allowed_majors is not None and not (tag_ver.release and tag_ver.release[0] in allowed_majors):
            continue
        filtered.append({"name": tag, "last_updated": ""})

    return select_candidates(filtered, current_version, candidate_limit), None


def _ecr_public_manifest_exists(namespace: str, image: str, tag: str, token: str) -> tuple[bool, str | None]:
    url = f"https://public.ecr.aws/v2/{namespace}/{image}/manifests/{tag}"
    headers = {"Authorization": f"Bearer {token}", "Accept": MANIFEST_ACCEPT}
    probe = probe_url(url)
    if not probe.ok:
        return False, "ECR Public unreachable"
    try:
        response = get(url, headers=headers)
        if response.status_code == 200:
            return True, None
        if response.status_code == 404:
            return False, None
        return False, f"ECR manifest check returned {response.status_code}"
    except Exception as error:
        return False, str(error)


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


def _fetch_github_releases(url: str, current_version: str, page_size: int, candidate_limit: int = 1) -> tuple[dict | None, str | None]:
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
        return _fetch_github_tags(url, current_version, page_size, candidate_limit)

    return select_candidates(tags, current_version, candidate_limit), None


def _fetch_github_tags(url: str, current_version: str, page_size: int, candidate_limit: int = 1) -> tuple[dict | None, str | None]:
    tags, error = _github_tags_raw(url, page_size)
    if error:
        return None, error
    return select_candidates(tags, current_version, candidate_limit), None


def _github_tags_raw(url: str, page_size: int, max_pages: int = 10) -> tuple[list[dict], str | None]:
    api_url = _github_api_url(url)
    if not api_url:
        return [], "invalid GitHub URL"

    tags: list[dict] = []
    per_page = min(page_size, 100)
    for page in range(1, max_pages + 1):
        data, error = _get_json(f"{api_url}/tags", {"per_page": per_page, "page": page})
        if error:
            return [], error
        items = data or []
        tags.extend(
            {"name": item.get("name") or "", "last_updated": ""}
            for item in items
        )
        if len(items) < per_page:
            break

    return tags, None


def _github_releases_raw(url: str, page_size: int, max_pages: int = 5) -> tuple[list[dict], str | None]:
    api_url = _github_api_url(url)
    if not api_url:
        return [], "invalid GitHub URL"

    releases: list[dict] = []
    per_page = min(page_size, 100)
    for page in range(1, max_pages + 1):
        data, error = _get_json(f"{api_url}/releases", {"per_page": per_page, "page": page})
        if error:
            return [], error
        items = data or []
        releases.extend(
            {"name": item.get("tag_name") or "", "last_updated": item.get("published_at") or ""}
            for item in items
            if not item.get("draft")
        )
        if len(items) < per_page:
            break

    return releases, None


def _looks_like_branch_tag(name: str) -> bool:
    match = re.match(r"^v?\d+(?:\.\d+)*[-_](.+)$", name)
    return bool(match and "." in match.group(1))


def _stable_candidates(tags: list[dict], current_version: str, limit: int = 5) -> list[str]:
    current_ver = version.parse(normalize_tag(current_version))
    candidates = set()

    for tag in tags:
        tag_name = tag["name"]
        if _looks_like_branch_tag(tag_name):
            continue
        try:
            tag_ver = version.parse(normalize_tag(tag_name))
        except version.InvalidVersion:
            continue

        if tag_ver.is_prerelease or tag_ver.is_devrelease:
            continue
        if tag_ver <= current_ver:
            continue

        candidates.add(tag_name)

    def version_key(name):
        return version.parse(normalize_tag(name))

    ordered = sorted(candidates, key=lambda name: (version_key(name), name), reverse=True)
    ordered.sort(key=lambda name: variant_score(name, current_version))
    return ordered[:limit]


def _dockerhub_verify(api_url: str, candidate: str, page_size: int) -> dict | None:
    candidate_ver = version.parse(normalize_tag(candidate))
    queries = [candidate]
    stripped = candidate.lstrip("v")
    if stripped != candidate:
        queries.append(stripped)

    for query in queries:
        params = {"page_size": page_size, "name": query}
        data, error = _get_json(api_url, params)
        if error or not data:
            continue

        matches = []
        for tag in (data or {}).get("results") or []:
            tag_name = tag["name"]
            try:
                if version.parse(normalize_tag(tag_name)) == candidate_ver:
                    matches.append(tag)
            except version.InvalidVersion:
                continue
        if matches:
            best = min(matches, key=lambda tag: (variant_score(tag["name"], candidate), tag["name"] != candidate, len(tag["name"]), tag["name"]))
            return {"version": best["name"], "last_updated": best["last_updated"]}
    return None


def fetch_verified_candidates(
    verify_type: str,
    verify_url: str,
    index_type: str,
    index_url: str,
    current_version: str,
    major_ahead: int = 3,
    page_size: int = 100,
    candidate_limit: int = 1,
) -> tuple[dict | None, str | None]:
    def fallback() -> tuple[dict | None, str | None]:
        return fetch_candidates(
            verify_type,
            verify_url,
            current_version,
            major_ahead=major_ahead,
            page_size=page_size,
            candidate_limit=candidate_limit,
        )

    # Release indexes often omit image-only variants such as -lts or -core.
    # Use registry discovery for these tags rather than verifying plain releases.
    if re.match(r"^v?\d+(?:\.\d+)*[-_]", current_version):
        return fallback()

    if index_type == "github-releases":
        index_tags, error = _github_releases_raw(index_url, page_size)
        if error or not index_tags:
            index_tags, error = _github_tags_raw(index_url, page_size)
            if error:
                return fallback()
    elif index_type == "github-tags":
        index_tags, error = _github_tags_raw(index_url, page_size)
        if error:
            return fallback()
    else:
        return fallback()

    candidates = _stable_candidates(index_tags, current_version)
    if not candidates:
        return None, None

    minors = sorted(
        {version.parse(normalize_tag(name)).release[:2] for name in candidates},
        reverse=True,
    )
    wanted = [".".join(str(p) for p in minor) for minor in minors] + candidates

    # A minor tag equal to the current version must never be reported as a
    # candidate: verifying it would echo the current version back.
    current_ver = version.parse(normalize_tag(current_version))
    filtered = []
    for candidate in wanted:
        try:
            if version.parse(normalize_tag(candidate)) > current_ver:
                filtered.append(candidate)
        except version.InvalidVersion:
            continue
    wanted = filtered

    confirmed_tags = []

    def collect(confirmed: dict) -> dict | None:
        confirmed_tags.append({"name": confirmed["version"], "last_updated": confirmed["last_updated"]})
        return select_candidates(confirmed_tags, current_version, candidate_limit)

    if verify_type == "dockerhub-tags":
        api_url = _dockerhub_api_url(verify_url)
        if not api_url:
            return None, "invalid Docker Hub URL"
        for candidate in wanted:
            confirmed = _dockerhub_verify(api_url, candidate, page_size)
            if confirmed:
                result = collect(confirmed)
                if len({tag["name"] for tag in confirmed_tags}) >= max(1, min(candidate_limit, 3)):
                    return result, None
        if confirmed_tags:
            return select_candidates(confirmed_tags, current_version, candidate_limit), None
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
            actual = next((name for name in (candidate, candidate.lstrip("v")) if name in tag_set), None)
            if actual:
                result = collect({"version": actual, "last_updated": ""})
                if len({tag["name"] for tag in confirmed_tags}) >= max(1, min(candidate_limit, 3)):
                    return result, None
        if confirmed_tags:
            return select_candidates(confirmed_tags, current_version, candidate_limit), None
        return fallback()

    if verify_type == "ecr-public":
        repository = _ecr_public_repository(verify_url)
        if not repository:
            return None, "invalid ECR Public URL"
        namespace, image = repository
        token, error = _ecr_public_token(namespace, image)
        if error:
            return fallback()

        for candidate in wanted:
            for tag in (candidate, candidate.lstrip("v")):
                exists, error = _ecr_public_manifest_exists(namespace, image, tag, token)
                if error:
                    return fallback()
                if exists:
                    result = collect({"version": tag, "last_updated": ""})
                    if len({item["name"] for item in confirmed_tags}) >= max(1, min(candidate_limit, 3)):
                        return result, None
                    break
        if confirmed_tags:
            return select_candidates(confirmed_tags, current_version, candidate_limit), None
        return fallback()

    return None, f"unsupported verify source type: {verify_type}"
