import os
import json
import requests
from packaging import version

def get_dockerhub_tags(api_url, min_date=None):
    tags = []
    next_url = api_url
    while next_url:
        try:
            response = requests.get(next_url)
            response.raise_for_status()
            data = response.json()
            for tag in data['results']:
                if min_date is None or tag['last_updated'] > min_date:
                    tags.append(tag)
            next_url = data['next']
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
    for ed in edition:
        if ed['dist'] == 'community':
            versions = ed['version']
            return max(versions, key=version.parse)
    return None

def filter_versions(tags, current_version):
    current_ver = version.parse(current_version)
    higher_versions = []
    for tag in tags:
        tag_name = tag['name']
        try:
            tag_ver = version.parse(tag_name)
            if tag_ver > current_ver and not tag_name.endswith('-SNAPSHOT'):
                higher_versions.append({
                    'version': tag_name,
                    'last_updated': tag['last_updated']
                })
        except:
            continue
    return higher_versions

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
                            tags, error = get_dockerhub_tags(api_url)
                            if error:
                                output.append({
                                    'name': name,
                                    'error': f"Failed to fetch tags: {error}"
                                })
                                continue

                            current_version = get_current_version(variables['edition'])
                            if current_version:
                                # 查找当前版本的发布时间
                                current_version_info = next((tag for tag in tags if tag['name'] == current_version), None)
                                if current_version_info:
                                    min_date = current_version_info['last_updated']
                                    # 获取在当前版本发布之后的所有版本
                                    tags, error = get_dockerhub_tags(api_url, min_date)
                                    if error:
                                        output.append({
                                            'name': name,
                                            'error': f"Failed to fetch tags after {min_date}: {error}"
                                        })
                                        continue

                                    higher_versions = filter_versions(tags, current_version)
                                    output.append({
                                        'name': name,
                                        'current_version': current_version,
                                        'higher_versions': higher_versions,
                                        'version_from': version_from
                                    })
                                else:
                                    output.append({
                                        'name': name,
                                        'current_version': current_version,
                                        'higher_versions': [],
                                        'version_from': version_from,
                                        'error': 'Current version not found in tags'
                                    })
                            else:
                                output.append({
                                    'name': name,
                                    'current_version': 'N/A',
                                    'higher_versions': [],
                                    'version_from': version_from,
                                    'error': 'No current version found'
                                })
                        else:
                            output.append({
                                'name': name,
                                'current_version': 'N/A',
                                'higher_versions': [],
                                'version_from': version_from,
                                'error': 'Invalid version_from URL or not a Docker Hub URL'
                            })

    output_path = 'output.json'
    if output:
        with open(output_path, 'w') as outfile:
            json.dump(output, outfile, indent=4)

if __name__ == '__main__':
    main()
