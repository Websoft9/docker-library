import os
import json
import requests
import subprocess
import sys
import time
import argparse

def get_dockerhub_tags(api_url, max_pages=5, page_size=100, delay=1):
    tags = []
    next_url = f"{api_url}?page_size={page_size}"
    pages_fetched = 0

    while next_url and pages_fetched < max_pages:
        try:
            response = requests.get(next_url)
            if response.status_code == 429:
                time.sleep(delay)
                continue
            response.raise_for_status()
            data = response.json()
            tags.extend(data['results'])
            next_url = data.get('next')
            pages_fetched += 1
            time.sleep(delay)  # Delay between requests
        except Exception as e:
            return tags, str(e)
    return tags, None

def convert_to_dockerhub_api_url(version_from_url):
    try:
        path_parts = version_from_url.split('/')
        if '_/' in version_from_url:
            # Official image
            image_name = path_parts[-2]
            return f"https://hub.docker.com/v2/repositories/library/{image_name}/tags"
        else:
            # Non-official image
            namespace = path_parts[-3]
            image_name = path_parts[-2]
            return f"https://hub.docker.com/v2/repositories/{namespace}/{image_name}/tags"
    except Exception as e:
        return None

def get_current_version(edition):
    valid_versions = []
    for ed in edition:
        if ed['dist'] == 'community':
            versions = ed['version']
            for v in versions:
                try:
                    valid_versions.append(version.parse(v))
                except version.InvalidVersion:
                    continue
    return str(max(valid_versions)) if valid_versions else None

def find_latest_version(tags, current_version):
    current_ver = version.parse(current_version)
    latest_version = None
    for tag in tags:
        tag_name = tag['name']
        try:
            tag_ver = version.parse(tag_name)
            if tag_ver > current_ver and not tag_name.endswith('-SNAPSHOT'):
                if latest_version is None or tag_ver > version.parse(latest_version['version']):
                    latest_version = {
                        'version': tag_name,
                        'last_updated': tag['last_updated']
                    }
        except version.InvalidVersion:
            continue
    return latest_version

def main():
    parser = argparse.ArgumentParser(description='Fetch Docker Hub tags and find the latest version.')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum number of pages to fetch from Docker Hub API')
    parser.add_argument('--page-size', type=int, default=100, help='Number of tags to fetch per page from Docker Hub API')
    args = parser.parse_args()

    apps_dir = 'apps'
    output = []

    for app in os.listdir(apps_dir):
        app_dir = os.path.join(apps_dir, app)
        if os.path.isdir(app_dir):
            variables_path = os.path.join(app_dir, 'variables.json')
            if os.path.exists(variables_path):
                with open(variables_path, 'r') as file:
                    variables = json.load(file)
                    name = variables['name']
                    release = variables.get('release', False)
                    version_from = variables.get('version_from', '')
                    if release:
                        api_url = convert_to_dockerhub_api_url(version_from)
                        if api_url:
                            tags, error = get_dockerhub_tags(api_url, max_pages=args.max_pages, page_size=args.page_size)
                            if error:
                                output.append({
                                    'name': name,
                                    'error': f"Failed to fetch tags: {error}"
                                })
                                continue

                            current_version = get_current_version(variables['edition'])
                            if current_version:
                                latest_version = find_latest_version(tags, current_version)
                                output.append({
                                    'name': name,
                                    'current_version': current_version,
                                    'latest_version': latest_version,
                                    'version_from': version_from
                                })
                            else:
                                output.append({
                                    'name': name,
                                    'current_version': 'N/A',
                                    'latest_version': None,
                                    'version_from': version_from,
                                    'error': 'No current version found'
                                })
                        else:
                            output.append({
                                'name': name,
                                'current_version': 'N/A',
                                'latest_version': None,
                                'version_from': version_from,
                                'error': 'Invalid version_from URL or not a Docker Hub URL'
                            })

    output_path = 'output.json'
    if output:
        with open(output_path, 'w') as outfile:
            json.dump(output, outfile, indent=4)

if __name__ == '__main__':
    main()
