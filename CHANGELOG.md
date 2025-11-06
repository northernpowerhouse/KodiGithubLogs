# Changelog

All notable changes to the Kodi Log Uploader addon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-06

### Added
- Initial release of Kodi Log Uploader addon
- GitHub Device Flow OAuth authentication
- Repository selection from user's writable repos
- Folder navigation and selection within repositories
- **Folder creation** - create new folders in target repository via UI
- Log upload to GitHub with timestamped filenames (kodilogYYYYMMDDHHMM.txt)
- Log level filtering:
  - Regular: Filters DEBUG and TRACE lines
  - Debug: Includes DEBUG, filters TRACE
  - Trace: All log lines included
- Option to include older rotated logs (kodi.old)
- **Improved startup log trimming** with multi-pattern heuristics:
  - Detects "Starting Kodi", "Kodi started", etc.
  - Finds application initialization complete
  - Detects first user action or service start
  - Fallback: Skips first 15% if log is very long
- **Fallback client_id** support (optional, configurable in code)
- Comprehensive settings UI
- GitHub Actions workflow for automated builds
- Kodi addon repository structure for easy installation and updates
- Automated release creation with GitHub Releases
- Repository addon for one-click installation in Kodi

### Technical
- Pure Python standard library implementation (no external dependencies)
- Compatible with Kodi 21 (xbmc.python 3.0.0+)
- MIT License
- Automated build script (`scripts/build.sh`)
- Automated repo updates via GitHub Actions

### Security
- OAuth Device Flow (no password required)
- Access tokens stored in Kodi addon settings
- Security notes documented in README

### Documentation
- Comprehensive README with installation and usage instructions
- Setup guide for creating GitHub OAuth Apps
- Build and release documentation
- Repository installation guide
- API usage documentation

[0.1.0]: https://github.com/northernpowerhouse/KodiGithubLogs/releases/tag/v0.1.0
