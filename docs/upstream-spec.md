# Upstream Spec

This spec defines how upstream facts are discovered for app maintenance.

## Goal

Separate:
- deterministic fact collection
- AI judgment and exception handling

Rule:
- CLI collects facts
- AI interprets facts and makes workflow decisions

## Source Types

CLI-first source types:
- `dockerhub-tags`
- `github-releases`
- `github-tags`
- `raw-compose`
- `raw-env`
- `raw-yaml`
- `raw-json`

AI-only source types:
- `human-readme`
- `human-doc-page`
- `dynamic-web-page`
- `login-required-page`

Fallback rule:
- if CLI cannot parse a declared source, return `source-error`
- AI may then research and propose a corrected source

## Scan Outputs

CLI may emit:
- `version-change`
- `compose-drift`
- `config-drift`
- `source-error`

AI consumes these outputs and decides:
- `auto-update`
- `review-first`
- `defer`
- `skip`

## Minimal Upstream Descriptor

Migration rule:
- keep existing `version_from` during migration
- `upstream.version_source.url` should match `version_from` when both exist
- new upstream dimensions may be added without removing `version_from`

For image-driven apps:

```json
{
  "version_from": "https://hub.docker.com/r/grafana/grafana/tags",
  "upstream": {
    "version_source": {
      "type": "dockerhub-tags",
      "url": "https://hub.docker.com/r/grafana/grafana/tags"
    }
  }
}
```

For compose-driven apps:

```json
{
  "version_from": "https://github.com/example/project/releases",
  "upstream": {
    "version_source": {
      "type": "github-releases",
      "url": "https://github.com/example/project/releases"
    },
    "compose_source": {
      "type": "raw-compose",
      "url": "https://raw.githubusercontent.com/example/project/main/docker-compose.yml"
    }
  }
}
```

For mixed sources where CLI and AI both need references:

```json
{
  "version_from": "https://hub.docker.com/_/wordpress/tags",
  "upstream": {
    "version_source": {
      "type": "dockerhub-tags",
      "url": "https://hub.docker.com/_/wordpress/tags"
    },
    "ai_reference_sources": [
      {
        "name": "image-repository",
        "type": "human-doc-page",
        "url": "https://github.com/docker-library/wordpress"
      },
      {
        "name": "requirements-docs",
        "type": "human-doc-page",
        "url": "https://www.wordpress.org/docs/user_guide/en/install-requirements.html"
      }
    ]
  }
}
```

Rules:
- `url` must point to a stable upstream source
- CLI only handles declared source types
- AI does not replace declared deterministic scan paths in normal operation

## Drift Boundaries

`compose-drift` covers:
- services
- images
- ports
- volumes
- depends_on
- healthcheck
- command or entrypoint

`config-drift` covers:
- env keys
- default values
- required variables
- URL or login related config

## Design Rule

Do not ask CLI to understand arbitrary webpages.

Do not ask AI to perform routine deterministic scanning when a stable source type exists.
