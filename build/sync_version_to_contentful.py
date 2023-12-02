import os
import json
import requests
from pathlib import Path

# 设置 Contentful API 访问参数
CONTENTFUL_MANAGEMENT_API = "https://api.contentful.com"
ACCESS_TOKEN = os.environ['CONTENTFUL_ACCESS_TOKEN']
SPACE_ID = "ffrhttfighww"

print(f"ACCESS_TOKEN: {ACCESS_TOKEN}")

# 设置请求头
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/vnd.contentful.management.v1+json"
}

def update_contentful(product_name, editions):
    # 获取 Contentful 中的 Product entry
    response = requests.get(
        f"{CONTENTFUL_MANAGEMENT_API}/spaces/{SPACE_ID}/environments/master/entries?content_type=product&fields.key={product_name}",
        headers=headers
    )
    response.raise_for_status()
    entries = response.json()

    print(f"entries: {entries}")
    
    # 假设只有一个匹配的 entry
    if entries['total'] > 0:
        entry_id = entries['items'][0]['sys']['id']
        version = entries['items'][0]['sys']['version']
        
        # 准备更新的数据
        distribution = [{"dist": edition['dist'], "version": ",".join(edition['version'])} for edition in editions]
        update_data = {
            "fields": {
                "distribution": {
                    "en-US": distribution
                }
            }
        }
        print(f"update_data: {update_data}")
        
        # 更新 Contentful entry
        update_response = requests.put(
            f"{CONTENTFUL_MANAGEMENT_API}/spaces/{SPACE_ID}/environments/master/entries/{entry_id}",
            headers={**headers, "X-Contentful-Version": str(version)},
            data=json.dumps(update_data)
        )
        update_response.raise_for_status()
        
        # 发布更新
        publish_response = requests.put(
            f"{CONTENTFUL_MANAGEMENT_API}/spaces/{SPACE_ID}/environments/master/entries/{entry_id}/published",
            headers={**headers, "X-Contentful-Version": str(update_response.json()['sys']['version'])}
        )
        publish_response.raise_for_status()

# 遍历 apps 文件夹中的 variables.json 文件
apps_path = Path('apps')
for variables_file in apps_path.rglob('variables.json'):
    with open(variables_file) as file:
        data = json.load(file)
        product_name = data['name']
        editions = data['edition']
        update_contentful(product_name, editions)
