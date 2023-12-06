# update the apps's README file that it variables.json file changed

import os
import json  # Add this line
from jinja2 import Environment, FileSystemLoader

# Get the list of apps from the environment variable
app_list = os.getenv('APP_LISTS_ALL')

# Split the list on commas to get a list of apps
apps = app_list.split(',')

# Remove any empty strings from the list
apps = [app for app in apps if app]

# Set up the jinja2 environment
env = Environment(loader=FileSystemLoader('template'))

# Get the template
template = env.get_template('README.jinja2')

for app in apps:
    # Open the variables.json file
    with open(f'apps/{app}/variables.json', 'r') as f:
        variables = json.load(f)

    # Render the template with the variables
    output = template.render(variables)

    # Write the output to the README.md file
    with open(f'apps/{app}/README.md', 'w') as f:
        f.write(output)