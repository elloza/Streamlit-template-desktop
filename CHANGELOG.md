# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2025-10-18

### Fixed
- **CI/CD**: Fixed GitHub Actions build failures caused by hardcoded `.conda` paths
  - Build scripts now detect environment (local vs CI) automatically
  - Use local `.conda/python.exe` when available, fallback to system `python`
  - Only include conda-specific binary flags when `.conda` directory exists
  - All three platforms (Windows, Linux, MacOS) now build successfully in CI

## [0.1.4] - 2025-10-18

### Fixed
- **CRITICAL**: Fixed `PackageNotFoundError: No package metadata was found for streamlit` when running PyInstaller build
  - Root cause: PyInstaller doesn't bundle package metadata by default
  - Solution: Added `--copy-metadata streamlit` and `--copy-metadata altair` to PyInstaller build command
  - Impact: Application now starts correctly in PyInstaller builds without metadata errors

### Added
- Created build scripts infrastructure in `build/scripts/`
  - `build_windows.sh`: Windows build script with proper metadata bundling
  - `build_unix.sh`: Unix/Linux/MacOS build script with proper metadata bundling
- Build scripts now use local `.conda` Python environment for consistent builds
- Build scripts preserve `build/scripts/` directory during clean operations

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
