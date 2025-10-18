# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2025-10-18

### Fixed
- **CRITICAL**: Fixed infinite process spawning on Windows when built with PyInstaller
  - Migrated from `subprocess.Popen` to `multiprocessing.Process` architecture
  - Root cause: `sys.executable` in PyInstaller points to frozen .exe, not python.exe
  - Solution: Use PyInstaller's native multiprocessing runtime hooks (`pyi_rth_multiprocessing.py`)
  - Benefits: Process isolation, no bundle size increase, maintains Playwright/Selenium compatibility
  - Technical details: See [HOTFIX-MULTIPROCESSING.md](specs/main/HOTFIX-MULTIPROCESSING.md)

### Changed
- Streamlit server now runs in separate process via `multiprocessing.Process` instead of `subprocess.Popen`
- Added `multiprocessing.freeze_support()` call in main guard for Windows compatibility
- Worker function `_streamlit_worker()` executes Streamlit CLI directly via `stcli.main()`

## [0.1.2] - 2025-10-18

### Fixed
- Previous bugfix attempt (removed input() calls)

## [0.1.1] - 2025-10-18

### Fixed
- Attempted fix for process issues (superseded by 0.1.3)

## [0.1.0] - 2025-10-17

### Added
- Initial release of Streamlit Desktop App Template
- Basic project structure
- Template-first design philosophy
- Python-only codebase
- Documentation and quickstart guide
