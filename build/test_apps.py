import os
import time
import requests
from dotenv import load_dotenv
import subprocess


# Get the list of apps from the environment variable
appnames = os.getenv('APP_LISTS')

# Split the list on commas to get a list of apps
appnames = appnames.split(',')

# Remove any empty strings from the list
appnames = [appname for appname in appnames if appname]

for appname in appnames:
    print(f"############### {appname} start #################################")
    
    path = os.path.join('apps', appname)
    file = os.path.join(path, 'docker-compose.yml')
    
    subprocess.run(['docker-compose', '-f', file, 'up', '-d'])
    time.sleep(30)  # Wait for the service to start
    subprocess.run(['docker', 'ps'])
    
    env_file = os.path.join(path, '.env')
    if os.path.isfile(env_file):
        load_dotenv(dotenv_path=env_file)  # load .env file
        port = os.getenv('W9_HTTP_PORT_SET')
        if not port:
            print("It is not a web app")
            exit(1)
        else:
            print("It is a web app")
    else:
        print(f"{env_file} does not exist")
        exit(1)
    
    url = f"http://localhost:{port}"
    retry = 0
    while retry < 3:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"{appname} is up and running.")
            exit(0)
        else:
            print(f"Waiting for {appname} to start...")
            time.sleep(10)
            retry += 1
    
    output = requests.get(url).text
    with open('/tmp/output', 'a') as f:
        if "Failed" in output:
            f.write(f"{appname}: cannot access\n")
        else:
            f.write(f"{appname}: can access\n")
    
    subprocess.run(['docker-compose', '-f', file, 'down', '-v'])

with open('/tmp/output', 'r') as f:
    print(f.read())