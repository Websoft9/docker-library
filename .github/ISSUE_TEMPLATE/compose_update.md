---
name: Update application's version
about: Update application's version
title: 'Update version to [x.x.x] for [appname]'
labels: 'update,S-research'
assignees: ''
---

**What type of your feature request?**  

Change the W9_VERSION to target version number at `.env` and test it

**Research and development steps your need to do**  

- [ ] Check the official installation docs of this application
- [ ] Add a comment with docker logs
- [ ] If need to update documentation, add issue at [Websoft9 docs](https://github.com/websoft9/doc.websoft9.com)

**How to commit your change to [docker-library](https://github.com/Websoft9/docker-library)?**   

   ```
   docker exec -it websoft9-apphub bash
   apphub commit --appid --github_token
   ```

**Testing steps**   

- [ ] Upload your sreenshoot to PR
- [ ] Automation testing when submit PR to dev branch
- [ ] System testing for dev branch
