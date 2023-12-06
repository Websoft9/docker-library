import sys
import os
import yaml

# sys.argv[1] is the first argument passed to the script
input_arg = sys.argv[1]

# Split the input argument on commas to get a list of filenames
filenames = input_arg.split(',')

# Remove any empty strings from the list
filenames = [filename for filename in filenames if filename]

# Load the base docker-compose file
with open('docker-compose.yml', 'r') as base_file:
    base_config = yaml.safe_load(base_file)

for filename in filenames:
    # 获取文件的目录和基础名
    directory, basename = os.path.split(filename)

    # 从基础名中提取 * 部分
    name_part = basename.split('-')[2].split('.')[0]  # 从 'docker-compose-*.yml' 中提取 '*'

    # 构造新的文件名
    new_filename = os.path.join(directory, f'{name_part}.yml')

    # Load the overlay file
    with open(filename, 'r') as overlay_file:
        overlay_config = yaml.safe_load(overlay_file)

    # Merge the base and overlay configurations
    base_config.update(overlay_config)

    # Write the merged configuration to the new file
    with open(new_filename, 'w') as output_file:
        yaml.safe_dump(base_config, output_file)