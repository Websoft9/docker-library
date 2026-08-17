import argparse
import json
import os
import time
from datetime import date, datetime
from pathlib import Path

import requests
from packaging import version

from maintenance_metadata import load_maintenance_metadata, resolve_app_metadata


def get_dockerhub_tags(api_url, max_pages=1, page_size=100, delay=1):
    tags = []
    next_url = f"{api_url}?page_size={page_size}"
    pages_fetched = 0

    while next_url and pages_fetched < max_pages:
        try:
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
        except Exception as e:
            return tags, str(e)
    return tags, None


def convert_to_dockerhub_api_url(version_from_url):
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


def get_current_versions(edition):
    valid_versions = []
    all_versions = []
    for ed in edition:
        if ed["dist"] != "community":
            continue
        for current in ed["version"]:
            all_versions.append(current)
            if current.lower() == "latest":
                valid_versions.append("latest")
                continue
            try:
                valid_versions.append(version.parse(current))
            except version.InvalidVersion:
                continue
    return valid_versions, all_versions


def find_latest_version(tags, current_version):
    current_ver = version.parse(current_version)
    latest_version = None

    for tag in tags:
        tag_name = tag["name"]
        try:
            tag_ver = version.parse(tag_name)
            if tag_ver <= current_ver:
                continue
            if latest_version is None or tag_ver > version.parse(latest_version["version"]):
                latest_version = {
                    "version": tag_name,
                    "last_updated": tag["last_updated"],
                }
        except version.InvalidVersion:
            continue

    return latest_version


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch Docker Hub tags and find newer app versions.")
    parser.add_argument("--max-pages", type=int, default=1, help="Maximum number of Docker Hub pages")
    parser.add_argument("--page-size", type=int, default=100, help="Number of tags per Docker Hub page")
    parser.add_argument(
        "--selection",
        choices=("all-active", "due", "weekly", "monthly", "quarterly"),
        default="all-active",
        help="Select all active apps or only apps matching cadence rules",
    )
    parser.add_argument(
        "--date",
        dest="target_date",
        default=os.getenv("TARGET_DATE"),
        help="Date used for cadence selection in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Only output selected apps and metadata without remote version checks",
    )
    return parser.parse_args()

def parse_target_date(raw_date):
    if not raw_date:
        return date.today()
    return datetime.strptime(raw_date, "%Y-%m-%d").date()


def cadence_matches(cadence, target_date):
    if cadence == "weekly":
        return target_date.weekday() == 0
    if cadence == "monthly":
        return target_date.day == 1
    if cadence == "quarterly":
        return target_date.day == 1 and target_date.month in (1, 4, 7, 10)
    return False


def should_check_app(app_name, app_metadata, selection, target_date):
    status = app_metadata.get("status", "active")
    if status == "archived":
        return False, "archived"

    if selection == "all-active":
        return True, "all-active"

    cadence = app_metadata.get("cadence", "monthly")
    if selection == "due":
        return cadence_matches(cadence, target_date), cadence

    return cadence == selection, cadence


def build_app_result(name, app_metadata, current_versions, version_from, latest_version=None, error=None):
    return {
        "name": name,
        "status": app_metadata.get("status", "active"),
        "cadence": app_metadata.get("cadence", "monthly"),
        "update_policy": app_metadata.get("update_policy", "patch-minor"),
        "current_version": current_versions,
        "latest_version": latest_version,
        "version_from": version_from,
        **({"error": error} if error else {}),
    }


def main():
    args = parse_args()
    target_date = parse_target_date(args.target_date)
    metadata = load_maintenance_metadata()
    apps_dir = Path("apps")
    output = []

    for app_dir in sorted(path for path in apps_dir.iterdir() if path.is_dir()):
        variables_path = app_dir / "variables.json"
        if not variables_path.exists():
            continue

        app_metadata = resolve_app_metadata(metadata, app_dir.name)
        should_check, selected_by = should_check_app(app_dir.name, app_metadata, args.selection, target_date)
        if not should_check:
            continue

        with open(variables_path, "r", encoding="utf-8") as file:
            variables = json.load(file)

        name = variables["name"]
        release = variables.get("release", False)
        version_from = variables.get("version_from", "")
        current_versions, all_versions = get_current_versions(variables["edition"])

        if args.plan_only:
            output.append({
                **build_app_result(name, app_metadata, all_versions, version_from),
                "selected_by": selected_by,
                "target_date": target_date.isoformat(),
            })
            continue

        if not release:
            output.append({
                **build_app_result(name, app_metadata, all_versions, version_from, error="App release=false"),
                "selected_by": selected_by,
                "target_date": target_date.isoformat(),
            })
            continue

        current_version_strs = [str(current) for current in current_versions]
        if not current_versions or ("latest" in current_version_strs and len(current_version_strs) == 1):
            output.append({
                **build_app_result(name, app_metadata, all_versions, version_from, error="No valid current versions found"),
                "selected_by": selected_by,
                "target_date": target_date.isoformat(),
            })
            continue

        highest_version = max(current for current in current_versions if current != "latest")
        api_url = convert_to_dockerhub_api_url(version_from)
        if not api_url:
            output.append({
                **build_app_result(name, app_metadata, current_version_strs, version_from, error="Invalid version_from URL or not a Docker Hub URL"),
                "selected_by": selected_by,
                "target_date": target_date.isoformat(),
            })
            continue

        print(f"Fetching tags for {name} from {api_url}")
        tags, error = get_dockerhub_tags(api_url, max_pages=args.max_pages, page_size=args.page_size)
        if error:
            output.append({
                **build_app_result(name, app_metadata, current_version_strs, version_from, error=f"Failed to fetch tags: {error}"),
                "selected_by": selected_by,
                "target_date": target_date.isoformat(),
            })
            continue

        output.append({
            **build_app_result(name, app_metadata, current_version_strs, version_from, latest_version=find_latest_version(tags, str(highest_version))),
            "selected_by": selected_by,
            "target_date": target_date.isoformat(),
        })

    output_path = Path("output.json")
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(output, outfile, indent=4)


if __name__ == "__main__":
    main()
