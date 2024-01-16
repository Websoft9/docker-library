# Documentation for core maintainers

This documentaion is from [jenkins MAINTAINERS](https://github.com/jenkinsci/jenkins/blob/master/docs/MAINTAINERS.adoc) which have a paradigm of rigorous open source project maintenance

## Roles

| Role/job       | submit pr | review pr | assign pr | merge pr | close pr | create issue | manage issue | release |
| -------------- | --------- | --------- | --------- | -------- | -------- | ------------ | ------------ | ------- |
| Contributor    | √         |           |           |          |          | √            |              |         |
| Issue Team     | √         |           |           |          |          | √            | √            |         |
| PR Reviewer    | √         | √         |           |          |          | √            |              |         |
| Release Team   | √         |           |           |          |          | √            |              | √       |
| Maintainer     | √         | √         | √         | √        | √        | √            |              |         |
| PR Assignee    |           |           |           | √        |          | √            |              |         |
| Product Manage |           |           |           |          |          | √            |              |         |

- **Contributor**: submit pull requests to the Jenkins core and review changes submitted by others. There are no special preconditions to do so. Anyone is welcome to contribute.
- **Issue Triage Team Member**: review the incoming issues: bug reports, requests for enhancement, etc. Special permissions are not required to take this role or to contribute.
- **Core Pull Request Reviewer**: A team for contributors who are willing to regularly review pull requests and eventually become core maintainers.
- **Core Maintainer**: Get permissions in the repository, and hence they are able to merge pull requests.Their responsibility is to perform pull request reviews on a regular basis and to bring pull requests to closure, either by merging ready pull requests towards weekly releases ( branch) or by closing pull requests that are not ready for merge because of submitter inaction after an extended period of time.
- **Pull Request Assignee**: Core maintainers make a commitment to bringing a pull request to closure by becoming an Assignee. They are also responsible to monitor the weekly release status and to perform triage of critical issues.
- **Release Team Member**: Responsible for Websoft9 weekly and LTS releases

## Pull request review process

## Pull request Merge process

## Issue

### Issue triage

|        | What?                                   | How?                                  | Do                                                 |
| ------ | --------------------------------------- | ------------------------------------- | -------------------------------------------------- |
| Detail | Tags, Duplicate check, Optimize content | Split/Close, Priority, Reward, Assign | Research, Procedure Check, Coding, Test, PR DevOps |
| Role   | Issue Manager or Other Contributor      | Team                                  | Team                                               |

> Each issue closed should by Team discussion at **Monday and Wednesday**

### Issue pipline

The issues are managed through the [github projects](https://github.com/orgs/Websoft9/projects/13).

Before Team discussion, issue manager should put issues into **github projects Todo item** considering the following priorities:

1. bug  
   bugs causing the product to fail to run > bugs causing some functional abnormalities > others
2. upgrade  
   orders of application > the needs of major customers > others
3. new application  
   popularity of application > easy to develop > hard to develop

## Release process

- Create production release directly
- Release at Monday and Wednesday

## Tools

- CI/CD: Githuh Action
- Testing:

## Communication

- Wechat Group
