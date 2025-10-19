# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.8] - 2025-10-19

### Fixed
- **CRITICAL**: Fixed Streamlit config conflict preventing server startup
  - Root cause: `.streamlit/config.toml` had `global.developmentMode` set to default (true)
  - Streamlit throws `RuntimeError: server.port does not work when global.developmentMode is true`
  - Solution: Explicitly set `global.developmentMode = false` in config.toml
  - Impact: Server can now use `--server.port` flag without conflicts

### Changed
- Updated `.streamlit/config.toml` to explicitly disable development mode

**Technical Details**:
When `global.developmentMode=true`, Streamlit prevents runtime port configuration to avoid conflicts with hot-reloading. For production/bundled apps, this must be `false`.

## [0.1.7] - 2025-10-19

### Fixed
- **CRITICAL**: Fixed PyInstaller executable crashing with exit code 2 on Windows
  - Root cause: Relative path `src/ui/main_app.py` could not be resolved when executable launched from different directories
  - Solution: Implemented absolute path resolution using PyInstaller freeze detection
  - Added `src/logic/bundle_utils.py` with functions for path resolution in frozen executables
  - Worker process now uses `get_script_path()` to resolve absolute path to main_app.py
  - Worker process sets working directory to bundle root for resource access

- **CRITICAL**: Added missing `.streamlit/config.toml` configuration file
  - Streamlit now runs with proper headless server configuration
  - Server configuration: headless=true, CORS disabled, XSRF enabled
  - Bundled in PyInstaller executable via updated `.spec` and build scripts

- **HIGH**: Added missing Streamlit runtime hidden imports
  - Added: `streamlit.runtime.scriptrunner`, `streamlit.runtime.app_session`
  - Added: `streamlit.runtime.state`, `streamlit.proto`, `streamlit.logger`
  - Added: `pydantic`, `typing_extensions`, `importlib.metadata`
  - Prevents ModuleNotFoundError in worker process

- **HIGH**: Improved error capturing from worker subprocess
  - Worker process now logs to separate `logs/worker.log` file
  - Added multiprocessing.Queue for error communication between processes
  - Main process captures and logs worker errors with full tracebacks
  - Increased server startup timeout from 15 to 30 seconds for slow machines

### Added
- New `src/logic/bundle_utils.py` module for PyInstaller path resolution
  - `is_frozen()`: Detect if running from PyInstaller bundle
  - `get_bundle_root()`: Get bundle root directory (where .exe lives)
  - `get_internal_dir()`: Get _internal directory with bundled files
  - `get_resource_path()`: Resolve absolute path to bundled resources
  - `get_script_path()`: Resolve absolute path to bundled Python scripts
  - `log_environment_info()`: Log diagnostic info for debugging

- New `setup_worker_logging()` function in `src/logic/logger.py`
  - Separate log file for worker process errors
  - Helps diagnose failures that would otherwise be lost

### Changed
- Updated `_streamlit_worker()` to accept error_queue parameter
- Updated `start_streamlit_server()` to return (process, error_queue) tuple
- Updated `main()` to handle error queue and increased timeout
- Updated all build scripts to include `.streamlit` directory and new hidden imports

### Technical Details
**Files Modified**:
- `app.py`: Absolute paths, error queue, bundle detection (82 lines changed)
- `StreamlitApp.spec`: Added .streamlit + 10 new hidden imports
- `build/scripts/build_windows.sh`: Added .streamlit data + hidden imports
- `build/scripts/build_unix.sh`: Added .streamlit data + hidden imports
- `src/logic/logger.py`: Added setup_worker_logging() function

**Files Created**:
- `src/logic/bundle_utils.py`: 180 lines of path resolution utilities
- `.streamlit/config.toml`: Streamlit headless configuration

**Impact**: This release fixes the primary blocker preventing any v0.1.x release from working. Users can now double-click the executable from any location (Desktop, Downloads, etc.) and the application will launch successfully.

## [0.1.6] - 2025-10-18

### Fixed
- **CI/CD**: Fixed MacOS build workflow failure in GitHub Actions
  - Handle both `.app` bundle and directory output formats from PyInstaller
  - PyInstaller creates `dist/StreamlitApp/` instead of `dist/StreamlitApp.app/` without `--windowed` flag
  - Archive step now checks for both formats and packages whichever exists
  - All three platform builds (Windows, Linux, MacOS) now complete successfully

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
