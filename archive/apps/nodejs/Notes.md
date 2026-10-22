# Node

All Node image is from Dockerhub ofifcial image, Websoft9 has not made any changes to it.  

Wesoft9 just give user a quick Node deployment template which includes:

- git repository: stored install files or source code if you need
- docker-compose.yml sample that can help your install application
- quick start docs

#### How to use it?

Give your example to install [docusaurus](https://docusaurus.io/docs)

1. Run Node application
2. docker exec to container and run below commands
   ```
   cd /home/node/app && npx create-docusaurus@latest classic
   cd classic && yarn install
   ```

4. You can see that application have install to */home/node/app/classic*

3. Enable and set below items at docker-comopse.yml and rebuild application

   - command: sh -c "cd /home/node/app/classic && npm run start -- --host 0.0.0.0"

#### How to add your commands at docker-compose.yml?

You can add your commands at **command**, and it supports multiple lines and the syntax of the shell, and supports the introduction of environment variables, that is, it can do anything you want to do. below is the sample:  

```
    command: |
      /bin/bash -c "
      if [ -z \"$W9_URL\" ]; then
        echo 'W9_URL is empty, not need to change, exiting...'
        exit 0
      fi
      "
```