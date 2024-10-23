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
        # Example official URL: https://hub.docker.com/_/logstash/tags
        # Example non-official URL: https://hub.docker.com/r/knowagelabs/knowage-server-docker/tags
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
    for ed in edition:
        if ed['dist'] == 'community':
            versions = ed['version']
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
                                    'last_updated': last_updated,
                                    'version_from': version_from
                                })
                            else:
                                output.append({
                                    'name': name,
                                    'current_version': current_version,
                                    'latest_version': 'N/A',
                                    'last_updated': 'N/A',
                                    'version_from': version_from,
                                    'error': f"Failed to fetch latest version: {last_updated}"
                                })
                        else:
                            output.append({
                                'name': name,
                                'current_version': 'N/A',
                                'latest_version': 'N/A',
                                'last_updated': 'N/A',
                                'version_from': version_from,
                                'error': 'Invalid version_from URL or not a Docker Hub URL'
                            })

    output_path = 'output.json'
    if output:
        with open(output_path, 'w') as outfile:
            json.dump(output, outfile, indent=4)

if __name__ == '__main__':
    main()
