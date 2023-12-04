import os
from contentful_management import Client

# 设置 Contentful API 访问参数
ACCESS_TOKEN = os.environ['CONTENTFUL_ACCESS_TOKEN']
SPACE_ID = "ffrhttfighww"

# 初始化 Contentful 管理客户端
client = Client(ACCESS_TOKEN)

def update_contentful(product_name, editions):
    # 获取 Contentful 中的 Product entry
    entries = client.entries(SPACE_ID, 'master').all({'content_type': 'product', 'fields.key': product_name})

    # 假设只有一个匹配的 entry
    if entries:
        entry = entries[0]
        # 准备更新的数据
        distribution = [{"key": edition['dist'], "value": edition['version']} for edition in editions]
        entry.fields('en-US')['distribution'] = distribution 

        # 保存和发布更新
        try:
            entry.save()
            entry.publish()
            print(f"Entry '{product_name}' updated and published.")
        except Exception as e:
            print(f"Failed to update and publish entry: {e}")

# 遍历 apps 文件夹中的 variables.json 文件
# apps_path = Path('apps')
# for variables_file in apps_path.rglob('variables.json'):
#     with open(variables_file) as file:
#         data = json.load(file)
#         product_name = data['name']
#         editions = data['edition']
#         update_contentful(product_name, editions)

update_contentful("wordpress", [{"dist": "community", "version": "6.5,latest"}, {"dist": "enterprise", "version": "6.5,latest"}])
