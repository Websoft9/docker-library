---
name: New docker compose request
about: Create new docker-compose this project
title: 'Create docker-compose.yml project for [appname]'
labels: 'feature'
assignees: ''
---

## Describe application with below format

```
# application name
name: "Websoft9"
# URL of the software project's homepage
website_url: "https://www.websoft9.com"
# URL where the full source code of the program can be downloaded
source_code_url: "https://gitlab.com/websoft9/websoft9"
# a brief and concise statementthat presents the main points for this application, shorter than 10 characters
summary: "Open source Application self-hosting platform"
# description of what the software does, shorter than 250 characters, sentence case
description: "GitOps-driven, multi-application hosting for cloud servers and home servers, one-click deployment of 200+ open source apps."
# list of license identifiers, see https://opensource.org/licenses for the full list of licenses
licenses:
  - LGPL-3.0
# (optional, true/false, default true) whether this application have Docker image
Docker_image: true
# (optional) link to an interactive demo of the software
demo_url: "https://www.websoft9.com/demo"
```

## Assessment Checklist by repository owner 

Before deveopment, repository owner should complete below Assessment: 

- [ ] This application have **3** containers
- [ ] official architecture research
- [ ] Complete the Contentful data for 
- [ ] Create app project structure from template


## Development Checklist by deveoper

Developer should develop this application's docker compose project at **Websoft9 Console** directly. 

- [ ] official architecture research
- [ ] follow [standardized syntax](https://github.com/Websoft9/docker-library/blob/main/docs/code_owner.md)
- [ ] specials and refers at notes.md/.env/docker-compose.yml
- [ ] test at Websoft9 Appstore and nginx proxy testing
- [ ] check siteurl or baseurl
- [ ] add official environments reference at .env
- [ ] connetion URI
- [ ] ports
- [ ] credentials environment
- [ ] i18n
- [ ] commit RP to dev branch

## Production preparation by repository owner 

- [ ] system test
- [ ] docs
- [ ] add Notes content to docs
- [ ] publish to RC release