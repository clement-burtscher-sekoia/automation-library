# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Added

- Add regression coverage for action `Resolve a message` fallback pagination across next-link pages to prevent playbook ValueError

### Changed

- Generalize repetitive unit tests with `pytest.mark.parametrize` for payload fallbacks and network message id extraction cases

### Fixed

- Fix action `Resolve a message`:
  - Improve resolution by `email_local_id` when the Graph `NetworkMessageId` filter returns no result
  - Add a paginated fallback scan over `/messages` using `@odata.nextLink` so low `top` values do not cause false not-found results and `ValueError`
  - Bound fallback scanning (`FALLBACK_PAGE_SIZE=50`, `FALLBACK_MAX_MESSAGES_SCANNED=1000`) to keep execution deterministic
