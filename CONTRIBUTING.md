# Contributing

From opening a bug report to creating a pull request: every contribution is appreciated and welcome.

If you're planning to implement a new feature or change this repository, please [create an issue](https://github.com/websoft9/docker-library/issues/new/choose) first. This way we can ensure that your precious work is not in vain.

## Quick start for contributing new application

Below is the steps for contributing new application:  

1. Create issue by template **New docker compose request**
2. Waiting for Maintainers/owner Assessment until it is completed.
3. Install Websoft9 at your server or apply online development account from Websoft9
4. SSH to develoment host machine and running below command to upgrade latest Apps listing
   ```
   docker exec -it websoft9-apphub apphub upgrade apps --dev
   ```
5. Login to Websoft9 Console and install this application from **App Store**
6. Develop and test it by **[App compose](https://support.websoft9.com/en/docs/next/app-compose/)** at Websoft9 Console
7. Complete your issue checklist
8. Docker exec **websoft9-apphub** container and pull request to repository
   ```
   # sample for your, --appid get from Websoft9 Console, it not appname
   docker exec -it websoft9-apphub  apphub commit --appid "wordpress_o2qjz" --github_token "yourgithubtoken"
   ```

## Copilot-Assisted Development

GitHub Copilot can significantly accelerate the development of Docker Compose applications. Follow these steps to leverage AI assistance:

### Prerequisites

1. **Enable GitHub Copilot** in your IDE (VS Code, JetBrains, etc.)
2. **Reference Materials**: Provide Copilot with the official Docker Compose or container run command from the application's documentation
3. **Template Files**: Use `docker-library/template/docker-compose.yml` and `docker-library/template/.env` as base templates

### Development Workflow

**Using GitHub Copilot in Agent Mode**

When developing new Docker Compose applications with Copilot, use **Agent mode** with advanced models (Claude Sonnet, GPT-4, etc.) for best results.

**Example Prompt Pattern:**

```
Based on the official [appname] deployment documentation:
- https://github.com/[official-repo]/docker-compose.yml
- https://github.com/[official-repo]/.env
- https://github.com/[official-repo]/README.md

Following our unified template: docker-library\template

Please help me complete the docker-compose orchestration for docker-library\apps\[appname]
```

**Workflow Steps:**

1. **Gather Official Documentation**
   - Find official docker-compose.yml and .env files
   - Review README for configuration requirements
   - Check for any Docker-specific documentation

2. **Provide Context to Copilot**
   - Share official repository URLs
   - Reference template files: `docker-library\template\docker-compose.yml` and `docker-library\template\.env`
   - Specify the target app directory: `docker-library\apps\[appname]`

By combining GitHub Copilot's AI capabilities with proper context and templates, you can dramatically speed up the development process while maintaining quality and consistency.

## Process diagram

[Bug report flow](https://www.canva.cn/design/DAFrBuGNCNs/-WGd-D0mQHBu1eZM07d8vQ/edit) as following:

![Alt text](./docs/image/bug_report_flow.png)

[Feature request flow](https://www.canva.cn/design/DAFrBuGNCNs/-WGd-D0mQHBu1eZM07d8vQ/edit) as following:

![Alt text](./docs/image/feature_request_flow.png)

## Development Specification

If you want to start to develop this repository, it is very useful for you to read [the develop documentation](docs/code_owner.md)

## Branch

This repository have these branchs:

- **dev branch**: Contributor only allow to fork [dev branch](https://github.com/Websoft9/docker-library/tree/dev) and pull request for it. 
- **main branch**: It is expected to contain code that is stable and ready for deployment.

> Maintainers/owner don't accept any pr to **main branch** from developer directly.

## Pull request

[Pull request](https://docs.github.com/pull-requests) let you tell others about changes you've pushed to a branch in a repository on GitHub.

#### When is PR produced?

- Contributor commit to dev branch

#### How to deal with PR?

1. [pull request reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews)
2. Merge RP and CI/CD for it

## DevOps principle

DevOps thinks the same way **[5m1e](https://www.dgmfmoldclamps.com/what-is-5m1e-in-injection-molding-industry/)** for manufacturing companies

We follow the development principle of minimization, rapid release

### Version

Use _[[major].[minor].[patch]](https://semver.org/lang/zh-CN/)_ for version serial number and [version.json](../version.json) for version dependencies

### Artifact

Websoft9 use below [Artifact](https://jfrog.com/devops-tools/article/what-is-a-software-artifact/) for different usage:

- **Dockerhub for image**: Access [Websoft9 docker images](https://hub.docker.com/u/websoft9dev) on Dockerhub
- **Azure Storage for files**: Access [packages list](https://artifact.azureedge.net/release?restype=container&comp=list) at [Azure Storage](https://learn.microsoft.com/en-us/azure/storage/storage-dotnet-how-to-use-blobs#list-the-blobs-in-a-container)

### Tags

- Type tags: RRD, Bug, enhancement, Documetation
- Stages Tags: S-develop, S-fixed and all tags started with `S-`

### WorkFlow

Websoft9 use the [Github flow](https://docs.github.com/en/get-started/quickstart/github-flow) for development collaboration

## licensing

See the [LICENSE](https://github.com/Websoft9/docker-library/blob/main/LICENSE.md) file for our project's licensing. We will ask you to confirm the licensing of your contribution.

We may ask you to sign a [Contributor License Agreement (CLA)](http://en.wikipedia.org/wiki/Contributor_License_Agreement) for larger changes.
