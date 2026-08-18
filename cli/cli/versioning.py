from __future__ import annotations

import time

import requests
from packaging import version


def get_dockerhub_tags(api_url: str, max_pages: int = 1, page_size: int = 100, delay: int = 1):
    tags = []
    next_url = f"{api_url}?page_size={page_size}"
    pages_fetched = 0

    while next_url and pages_fetched < max_pages:
        response = requests.get(next_url, timeout=120)
        if response.status_code == 429:
            time.sleep(delay)
            continue
        response.raise_for_status()
        data = response.json()
        tags.extend(data["results"])
        next_url = data.get("next")
        pages_fetched += 1
        time.sleep(delay)

    return tags


def convert_to_dockerhub_api_url(version_from_url: str) -> str | None:
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
    latest_version = None

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

        if latest_version is None or tag_ver > version.parse(latest_version["version"]):
            latest_version = {
                "version": tag_name,
                "last_updated": tag["last_updated"],
            }

    return latest_version
