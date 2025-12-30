# Changelog

All notable changes to this project will be documented in this file.

## [1.1.3] - 2025-12-30

### Fixed
- Fixed media matching issues where colons in titles were replaced with dashes using inconsistent spacing (e.g., "Title: Subtitle" vs "Title - Subtitle").
- Fixed inconsistent media matching logic by expanding the enhanced matcher to all file processing locations.

### Optimized
- **Performance:** Implemented directory listing caching to reduce filesystem I/O overhead.
- **Performance:** Optimized logger instantiation to reduce object creation overhead during processing.

## [1.1.2] - 2025-04-15

### Fixed
- Fixed tag versioning and push workflows.
- Fixed existing assets not being deleted correctly.
- Fixed logging consistency across modules.
- Fixed logs not posting in some scenarios.
- Fixed various typos in documentation.

### Added
- Added compression settings to output summary.
- Added `config.yml` to container and switched to entrypoint script.
- Added new environment variables and Docker Compose example.
- Added GitHub Actions workflow for Docker builds (`docker-build.yml`).

### Changed
- Tidied up Docker Compose example.
- Renamed `docker.yml` to `docker-build.yml`.
- Updated logging to ensure all modules use the same instance.
- Set default paths and added environment variable overrides for configuration.

## [1.1.1] - 2025-04-12

### Fixed
- Fixed logging issues.

### Added
- Initial image compression support.
