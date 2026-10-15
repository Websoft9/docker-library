# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions prior to 0.8.0 do not strictly follow this format.

## [0.8.0] - Unreleased

### Added
- `make dns-bind` / `make dns-delete` for Aliyun DNS wildcard records
- Generic DNS credentials in `make connector` (`dns` → `.secrets/dns.env` with `DNS_PROVIDER`/`DNS_KEY_ID`/`DNS_KEY_SECRET`/`DNS_DOMAIN`), plus cloud-provider options `alibabacloud` (`.secrets/aliyun.env`), `aws` (`.secrets/aws.env`), and `azure` (`.secrets/azure.env`)
- `make create-aliyun-ecs` to launch a spot Aliyun ECS instance from the fixed `ci/cloud/aliyun-ecs.json` config, with interactive disk size (bounded by the config range) and auto-release time; the marketplace `ImageId` is resolved from the product code via ECS `DescribeImages`, the instance is named `libs-test-<random>`, and the public IP is printed after creation
- Appstore Publish workflow with v2/catalog/library/manifest output model
- Channel-aware distribution merge for dev channel
- `workflow_dispatch` support for manual dev/rc/release publishing
- Contentful GraphQL catalog fetching (`build/fetch_catalog.py`)

### Changed
- Moved `dns-bind`, `dns-delete`, and `websoft9-upgrade` from `libs` commands to `make` targets (`make dns-bind`, `make dns-delete`, `make websoft9-upgrade`)
- Simplified `library.json` to only retain `Version` field
- GitHub Release tag now uses `library.json` Version instead of run_number
- Removed legacy `release.yml` and `release-dev.yml` workflows

### Fixed
- PostgreSQL volume mount path: `/var/lib/postgresql` → `/var/lib/postgresql/data`
- Safeline `W9_HTTP_PORT=1443` for correct healthcheck probing

### Removed
- `production` return field from fetch_catalog GraphQL query
- `library.json` unused WordPress-plugin-style metadata fields

## [0.7.13] - 2026-06

### Changed
- Refactor appstore publish workflows

## [0.7.0] - 2025

### Added
- 102 new applications: AI/ML, DevOps, Security, Media, E-commerce, Infrastructure
- AI/ML stack: anythingllm, dify, langflow, librechat, lobechat, localai, ollama, openwebui, ragflow
- DevOps tools: activepieces, airflow, automatisch, awx, calcom, keycloak, kestra, windmill
- Database tools: azimutt, mathesar, milvus, opengauss, postgrest
- Monitoring: crowdsec, glance, kener, opencost, signoz
- Communication: freshrss, lemmy, listmonk, zulip
- Security: adguardhome, bunkerweb, ddnsgo, zerotier, zitadel
- Media: drawio, immich, kavita, komga, paperlessngx, photoprism
- E-commerce: akeneo, saleor, suitecrm
- Infrastructure: frp, gocd, gotify, krakend, rustdesk, sonarqube, wikijs, and more

### Changed
- Unified application template structure and configuration standards
- 1,700+ version updates and bug fixes for existing applications

## [0.6.0] - 2024

### Added
- Application edition and distribution model

## [0.5.20] - 2023

### Changed
- Application version updates

## [0.5.7] - 2023-09-27

### Added
- Edition support (`edition` field in variables.json)
- Migration from `w9_name` to `w9_id`

## [0.5.4] - 2023-08-23

### Added
- New applications online

## [0.5.3] - 2023-08-03

### Added
- Library artifacts directory: `websoft9/plugin/library`
- New apps: nocobase, affine

## [0.2.3] - 2023-06-26

### Added
- New apps: appsmith, focalboard, affine

### Changed
- Appstore page images: onlyoffice, mingdao

## [0.2.2] - 2023-06-17

### Added
- WordPress listing
- DiscuzQ and Zabbix upgrade

### Removed
- Moodle listing

### Fixed
- Redmine configuration

## [0.2.1] - 2023-06-16

### Removed
- WordPress listing

## [0.1.0] - 2023-06-08

### Added
- Initial release with application templates
