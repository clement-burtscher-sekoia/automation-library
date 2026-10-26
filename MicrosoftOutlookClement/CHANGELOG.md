# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Changed

- Upgrade `sekoia-automation-sdk` to `1.27.0`
- Remove the logo background
- Raise the minimum supported Python version to `3.14`
- Migrate project dependency management from Poetry to uv (`pyproject.toml` PEP 621 + `uv.lock`)

### Fixed

- Fix uv bootstrap in the Docker image by installing `uv` directly in `Dockerfile` instead of relying on a GHCR copy stage
