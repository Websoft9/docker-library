import os
import json
import requests
import time
import argparse
from packaging import version

def get_dockerhub_tags(api_url, max_pages=1, page_size=100, delay=1):
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

def get_current_versions(edition):
    valid_versions = []
    all_versions = []
    for ed in edition:
        if ed['dist'] == 'community':
            versions = ed['version']
            for v in versions:
                all_versions.append(v)
                if v.lower() == 'latest':
                    valid_versions.append('latest')
                else:
                    try:
                        valid_versions.append(version.parse(v))
                    except version.InvalidVersion:
                        continue
    return valid_versions, all_versions

def find_latest_version(tags, current_version):
    current_ver = version.parse(current_version)
    latest_version = None
    all_versions = []

    for tag in tags:
        tag_name = tag['name']
        try:
            tag_ver = version.parse(tag_name)
            all_versions.append(tag_name)
            if tag_ver > current_ver:
                if latest_version is None or tag_ver > version.parse(latest_version['version']):
                    latest_version = {
                        'version': tag_name,
                        'last_updated': tag['last_updated']
                    }
        except version.InvalidVersion:
            continue

    return latest_version, all_versions

def main():
    parser = argparse.ArgumentParser(description='Fetch Docker Hub tags and find the latest version.')
    parser.add_argument('--max-pages', type=int, default=1, help='Maximum number of pages to fetch from Docker Hub API')
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
                    current_versions, all_versions = get_current_versions(variables['edition'])

                    if release:
                        current_version_strs = [str(v) for v in current_versions]
                        if 'latest' in current_version_strs and len(current_version_strs) == 1:
                            print(f"Skipping {name} as current version is set to latest and no other versions are available.")
                            output.append({
                                'name': name,
                                'current_version': all_versions,
                                'note': 'Current version is set to latest, skipping version comparison'
                            })
                            continue

                        # Filter out 'latest' and find the highest version
                        highest_version = max(v for v in current_versions if v != 'latest')
                        highest_version_str = str(highest_version)

                        api_url = convert_to_dockerhub_api_url(version_from)
                        if api_url:
                            print(f"Fetching tags for {name} from {api_url}")
                            tags, error = get_dockerhub_tags(api_url, max_pages=args.max_pages, page_size=args.page_size)
                            if error:
                                output.append({
                                    'name': name,
                                    'error': f"Failed to fetch tags: {error}"
                                })
                                continue

                            latest_version, all_versions = find_latest_version(tags, highest_version_str)
                            output.append({
                                'name': name,
                                'current_version': all_versions,
                                'latest_version': latest_version,
                                'version_from': version_from
                            })
                        else:
                            output.append({
                                'name': name,
                                'current_version': all_versions,
                                'latest_version': None,
                                'version_from': version_from,
                                'error': 'Invalid version_from URL or not a Docker Hub URL'
                            })
                    else:
                        output.append({
                            'name': name,
                            'current_version': all_versions,
                            'latest_version': None,
                            'version_from': version_from,
                            'note': 'Release is set to False'
                        })

    # Sort the output by 'name' in ascending order
    output.sort(key=lambda x: x['name'])

    output_path = 'output.json'
    if output:
        with open(output_path, 'w') as outfile:
            json.dump(output, outfile, indent=4)

if __name__ == '__main__':
    main()
