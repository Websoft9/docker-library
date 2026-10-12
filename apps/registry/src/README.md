# About

This folder contains optional reference files for Docker Registry packaging.

- Files under `src/` are not mounted by default in the current package.
- `config.yml.example` is a reference-only upstream-style configuration example.
- If the package later mounts a custom config from `src/`, the compose file must reference it explicitly.
