import os
import json
import requests

def get_dockerhub_latest_version(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        latest_tag = data['results'][0]['name']
        return latest_tag, data['results'][0]['last_updated']
    except Exception as e:
        return None, str(e)

def convert_to_dockerhub_api_url(version_from_url):
    try:
        path_parts = version_from_url.split('/')
        if '_/' in path_parts:
            # Official image
            image_name = path_parts[-2]
            return f"https://hub.docker.com/v2/repositories/library/{image_name}/tags?page_size=1"
        else:
            # Non-official image
            repo = f"{path_parts[-3]}/{path_parts[-2]}"
            return f"https://hub.docker.com/v2/repositories/{repo}/tags?page_size=1"
    except Exception as e:
        return None

def get_current_version(edition):
    for ed in edition:
        if ed['dist'] == 'community':
            versions = ed['version']
            if 'latest' in versions:
                versions.remove('latest')
            return ', '.join(versions)
    return None

def main():
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
                            latest_version, last_updated = get_dockerhub_latest_version(api_url)
                            current_version = get_current_version(variables['edition'])
                            if latest_version:
                                output.append({
                                    'name': name,
                                    'current_version': current_version,
                                    'latest_version': latest_version,
                                    'last_updated': last_updated
                                })
                            else:
                                output.append({
                                    'name': name,
                                    'current_version': current_version,
                                    'latest_version': 'N/A',
                                    'last_updated': 'N/A',
                                    'error': f"Failed to fetch l
