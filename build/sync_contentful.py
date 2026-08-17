import json
import os
from pathlib import Path

from contentful_management import Client
from contentful_management.errors import HTTPError

from maintenance_metadata import contentful_override, load_maintenance_metadata

# 设置 Contentful API 访问参数
ACCESS_TOKEN = os.environ['CONTENTFUL_ACCESS_TOKEN']
SPACE_ID = "ffrhttfighww"

# 初始化 Contentful 管理客户端
client = Client(ACCESS_TOKEN)
def app_path(product_name):
    active = Path('apps') / product_name
    if active.exists():
        return active

    archived = Path('archive/apps') / product_name
    if archived.exists():
        return archived

    return active
def update_contentful(product_name, editions, requirements, production):
    try:
        # 获取 Contentful 中的 Product entry
        entries = client.entries(SPACE_ID, 'master').all({'content_type': 'product', 'fields.key': product_name})

        if entries:
            entry = entries[0]
            # 准备 distribution 更新的数据
            distribution = [{"key": edition['dist'], "value": edition['version']} for edition in editions]
            entry.fields('en-US')['distribution'] = distribution 

            # 准备 requirements 更新的数据
            entry.fields('en-US')['vcpu'] = int(requirements['cpu'])
            entry.fields('en-US')['memory'] = int(requirements['memory'])
            entry.fields('en-US')['storage'] = int(requirements['disk'])
            
            entry.fields('en-US')['production'] = bool(production)

            # 保存和发布更新
            entry.save()
            entry.publish()
            return True
        else:
            print(f"No entry found for product '{product_name}'.")
            return False
    except HTTPError as http_error:
        print(f"Failed to update entry for product '{product_name}'. HTTPError: {http_error}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while updating entry for product '{product_name}': {e}")
        return False

# 初始化计数器
total_updates = 0
successful_updates = 0
failed_updates = 0
failed_products = []
maintenance = load_maintenance_metadata()

# 遍历 apps 或 archive/apps 下 app_lists 的 variables.json 文件
app_lists_str = os.getenv('APP_LISTS', '')
app_lists = app_lists_str.split(',') 

for product_name in app_lists:
    if not product_name:
        continue

    variables_file = app_path(product_name) / 'variables.json'
    try:
        with open(variables_file) as file:
            data = json.load(file)
            editions = data['edition']
            requirements = data['requirements']
            production = data['release']
            override = contentful_override(maintenance, product_name)
            if 'production' in override:
                production = override['production']
            
            total_updates += 1
            if update_contentful(product_name, editions, requirements,production):
                successful_updates += 1
            else:
                failed_updates += 1
                failed_products.append(product_name)
    except FileNotFoundError:
        print(f"File not found: {variables_file}")
        failed_updates += 1
        failed_products.append(product_name)
    except json.JSONDecodeError as e:
        print(f"JSON decode error in file {variables_file}: {e}")
        failed_updates += 1
        failed_products.append(product_name)
    except Exception as e:
        print(f"An unexpected error occurred while processing file {variables_file}: {e}")
        failed_updates += 1
        failed_products.append(product_name)


# 打印更新报告
print(f"Total updates attempted: {total_updates}")
print(f"Successful updates: {successful_updates}")
print(f"Failed updates: {failed_updates}")
if failed_updates > 0:
    print(f"Failed products: {failed_products}")
