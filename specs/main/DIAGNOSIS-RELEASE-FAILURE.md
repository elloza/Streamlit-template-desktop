# Diagnosis: v0.1.6 Release Executable Failure (Exit Code 2)

**Date**: 2025-10-19
**Issue**: GitHub Actions CI-built executable fails immediately with exit code 2
**Affected Platform**: Windows (primary), likely all platforms
**Severity**: CRITICAL - No working release available

---

## Problem Statement

The v0.1.6 release executable built by GitHub Actions crashes immediately when launched:

```
[2025-10-18 22:40:02] [ERROR] [root] Streamlit process terminated unexpectedly
[2025-10-18 22:40:02] [ERROR] [root] Process exit code: 2
```

The Streamlit worker process:
1. Starts successfully (PID assigned)
2. Never becomes ready on port 8501
3. Terminates after 15 seconds with exit code 2

---

## Root Cause Analysis

### Exit Code 2 Meaning

In Python/Streamlit context, exit code 2 typically indicates:
- **Command-line usage error** (invalid arguments to streamlit CLI)
- **FileNotFoundError** (can't find the script to run)
- **ImportError during startup** (missing required modules)

### Critical Issue #1: Relative Path Resolution ⚠️ CRITICAL

**Location**: `app.py` line 40

```python
def _streamlit_worker(port: int):
    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        "src/ui/main_app.py",  # ← RELATIVE PATH - PROBLEM!
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--server.address=127.0.0.1"
    ]

    sys.exit(stcli.main())
```

**Why this fails in CI builds:**

1. **PyInstaller bundle structure**:
   ```
   dist/StreamlitApp/
   ├── StreamlitApp.exe
   └── _internal/
       ├── src/ui/main_app.py
       ├── config/app.yaml
       └── [all bundled files]
   ```

2. **Working directory when .exe launches**:
   - Depends on WHERE the user double-clicks the .exe
   - Could be: Desktop, Downloads, C:\Users\..., anywhere
   - NOT guaranteed to be `dist/StreamlitApp/`

3. **Worker process spawn**:
   - Uses `multiprocessing.Process` with `spawn` context
   - Worker inherits parent's working directory
   - Tries to find `src/ui/main_app.py` relative to THAT directory
   - **File doesn't exist** → Streamlit CLI returns exit code 2

**Proof**: Log shows config file warning but NOT a direct error about main_app.py because the error happens in the worker subprocess which we don't capture.

```
[WARNING] Config file config/app.yaml not found, using defaults
```

This warning shows that relative paths ARE being resolved from the wrong directory!

---

### Critical Issue #2: Missing .streamlit/config.toml ⚠️ CRITICAL

**Location**: Project root - File doesn't exist

**Current bundle contents**:
```bash
dist/StreamlitApp/_internal/
├── src/          ✅ Included
├── assets/       ✅ Included
├── config/       ✅ Included
└── .streamlit/   ❌ MISSING!
```

**Why this matters**:

When Streamlit starts, it looks for configuration in this order:
1. `.streamlit/config.toml` in current directory
2. `.streamlit/config.toml` in user's home directory
3. Environment variables
4. Built-in defaults

Without `.streamlit/config.toml`, Streamlit:
- May try to create state directories in restricted locations
- May fail to run in headless mode properly
- May have conflicting default configurations

**Expected config** (should be created):
```toml
[logger]
level = "info"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[server]
headless = true
runOnSave = false
maxUploadSize = 200

[browser]
gatherUsageStats = false
serverAddress = "127.0.0.1"
```

---

### Critical Issue #3: No Error Capture from Worker Process ⚠️ HIGH

**Location**: `app.py` lines 22-48, 195-206

**Current code**:
```python
streamlit_process = start_streamlit_server(port, logger)

if not wait_for_server(port, timeout=15):
    logger.error("Streamlit server failed to start within timeout")
    if not streamlit_process.is_alive():
        logger.error("Streamlit process terminated unexpectedly")
        logger.error(f"Process exit code: {streamlit_process.exitcode}")
    # ← NO CAPTURE OF ACTUAL ERROR MESSAGE!
```

**Problem**: We see exit code 2, but NOT:
- The actual Python exception
- Streamlit CLI error message
- Stack trace from worker

**Why this happens**:
- `multiprocessing.Process` runs in separate process
- stdout/stderr go to separate streams
- We don't capture or log them

---

### Issue #4: Missing Streamlit Runtime Hidden Imports ⚠️ MEDIUM

**Location**: `StreamlitApp.spec` line 14

**Current hidden imports**:
```python
hiddenimports=[
    'streamlit',
    'streamlit.web.cli',
    'streamlit.web.bootstrap',
    'pywebview',
    # ... etc
]
```

**Potentially missing modules** (based on Streamlit internals):
- `streamlit.runtime.scriptrunner` - Runs the script
- `streamlit.runtime.app_session` - App state management
- `streamlit.runtime.state` - Session state
- `streamlit.proto` - Protocol buffers
- `importlib.metadata` - For version detection

**Impact**: If any of these are missing, worker process will fail with ImportError (exit code 2)

---

### Issue #5: Build Script Differences (CI vs Local) ⚠️ LOW

**GitHub Actions build** (line 39 of `.github/workflows/build-binaries.yml`):
```yaml
- name: Build Windows binary
  run: |
    bash build/scripts/build_windows.sh
  shell: bash
```

**build_windows.sh uses**:
- `python` command (system Python 3.11 from actions/setup-python)
- No `.conda` directory (doesn't exist in CI)
- Hardcoded flags in the script

**Local build might use**:
- `.conda/python.exe` if available
- Local conda DLLs
- Different environment variables

**Difference impact**: Minimal, but environment differences could cause subtle issues

---

## Evidence Summary

### What We Know ✅

1. Worker process STARTS (PID is assigned)
2. Worker process EXITS with code 2 (command line / file not found error)
3. Port 8501 never becomes ready (worker never gets to server startup)
4. Config file warning shows relative path resolution is failing
5. No error capture from worker subprocess

### What We DON'T Know ❌

1. Actual Python exception that caused exit code 2
2. Whether it's a FileNotFoundError or ImportError
3. Exact command-line args that Streamlit CLI received
4. Working directory of worker process at spawn time

---

## Reproduction Steps

1. Download `StreamlitApp-Windows.zip` from v0.1.6 release
2. Extract to any location (e.g., `C:\Users\YourName\Downloads\StreamlitApp\`)
3. Navigate to extracted folder
4. Double-click `StreamlitApp.exe`
5. Observe: App window may flash briefly, then closes
6. Check `logs/app.log` - see exit code 2 error

---

## Proposed Fixes (Priority Order)

### FIX #1: Use Absolute Path for main_app.py ⭐ CRITICAL

**File**: `app.py`
**Lines**: 22-48

**Change**:
```python
def _streamlit_worker(port: int):
    """Entry point for Streamlit worker process."""
    from streamlit.web import cli as stcli
    from pathlib import Path
    import sys
    import os

    # Get absolute path to main_app.py
    # In PyInstaller: _internal/app.py → _internal/src/ui/main_app.py
    # In source: project_root/app.py → project_root/src/ui/main_app.py
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        bundle_dir = Path(sys.executable).parent / "_internal"
        main_app_path = bundle_dir / "src" / "ui" / "main_app.py"
    else:
        # Running from source
        main_app_path = Path(__file__).parent / "src" / "ui" / "main_app.py"

    # Set working directory to bundle root so config/ and assets/ can be found
    if getattr(sys, 'frozen', False):
        os.chdir(Path(sys.executable).parent)

    sys.argv = [
        "streamlit",
        "run",
        str(main_app_path.absolute()),  # ← ABSOLUTE PATH!
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--server.address=127.0.0.1"
    ]

    sys.exit(stcli.main())
```

**Impact**: HIGH - Fixes the primary cause of exit code 2

---

### FIX #2: Add .streamlit/config.toml ⭐ CRITICAL

**Action**: Create new file

**File**: `.streamlit/config.toml`

**Content**:
```toml
[logger]
level = "info"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[server]
headless = true
runOnSave = false
maxUploadSize = 200

[browser]
gatherUsageStats = false
serverAddress = "127.0.0.1"

[runner]
magicEnabled = true
fastReruns = true
```

**Then update**:

**File**: `StreamlitApp.spec` (line 4)
```python
datas = [
    ('src', 'src'),
    ('assets', 'assets'),
    ('config', 'config'),
    ('.streamlit', '.streamlit'),  # ← ADD THIS
]
```

**File**: `build/scripts/build_windows.sh` (line 39)
```bash
--add-data="src;src" \
--add-data="assets;assets" \
--add-data="config;config" \
--add-data=".streamlit;.streamlit" \  # ← ADD THIS
```

**File**: `build/scripts/build_unix.sh` (line ~41)
```bash
--add-data="src:src" \
--add-data="assets:assets" \
--add-data="config:config" \
--add-data=".streamlit:.streamlit" \  # ← ADD THIS
```

**Impact**: HIGH - Ensures Streamlit runs with correct configuration

---

### FIX #3: Capture Worker Errors ⭐ HIGH

**File**: `app.py`

**Add error queue**:
```python
def _streamlit_worker(port: int, error_queue=None):
    """Entry point for Streamlit worker process."""
    try:
        from streamlit.web import cli as stcli
        from pathlib import Path
        import sys
        import os

        # ... (path resolution code from FIX #1)

        sys.exit(stcli.main())

    except Exception as e:
        # Capture error and send to parent process
        import traceback
        error_msg = f"Worker process error: {e}\n{traceback.format_exc()}"
        if error_queue:
            error_queue.put(error_msg)
        raise


def start_streamlit_server(port: int, logger):
    """Start Streamlit server in separate process."""
    try:
        logger.info(f"Starting Streamlit server on port {port}")

        # Create error queue for worker communication
        ctx = multiprocessing.get_context('spawn')
        error_queue = ctx.Queue()

        # Create process with error queue
        process = ctx.Process(
            target=_streamlit_worker,
            args=(port, error_queue),
            daemon=False,
            name="StreamlitServer"
        )

        process.start()
        logger.info(f"Streamlit server process started (PID: {process.pid})")

        # Check for immediate errors (non-blocking)
        import queue
        try:
            error_msg = error_queue.get(block=False)
            logger.error(f"Worker startup error: {error_msg}")
        except queue.Empty:
            pass  # No immediate error

        return process, error_queue

    except Exception as e:
        logger.error(f"Failed to start Streamlit server: {e}", exc_info=True)
        raise
```

**Then in main()**:
```python
# Start Streamlit in separate process
streamlit_process, error_queue = start_streamlit_server(port, logger)

# Wait for server to be ready
if not wait_for_server(port, timeout=30):  # Increased timeout
    logger.error("Streamlit server failed to start within timeout")

    # Check error queue for worker errors
    try:
        error_msg = error_queue.get(block=False)
        logger.error(f"Worker error message:\n{error_msg}")
    except:
        pass

    if not streamlit_process.is_alive():
        logger.error("Streamlit process terminated unexpectedly")
        logger.error(f"Process exit code: {streamlit_process.exitcode}")

    cleanup_streamlit(streamlit_process, logger)
    sys.exit(1)
```

**Impact**: MEDIUM - Helps diagnose future issues, but doesn't fix current crash

---

### FIX #4: Add Missing Hidden Imports ⭐ MEDIUM

**File**: `StreamlitApp.spec` (line 14)

**Add**:
```python
hiddenimports=[
    'streamlit',
    'streamlit.web.cli',
    'streamlit.web.bootstrap',
    'streamlit.runtime.scriptrunner',      # ← ADD
    'streamlit.runtime.app_session',       # ← ADD
    'streamlit.runtime.state',             # ← ADD
    'streamlit.runtime.state.session_state',  # ← ADD
    'streamlit.proto',                     # ← ADD
    'streamlit.logger',                    # ← ADD
    'pywebview',
    'pywebview.platforms.winforms',
    'yaml',
    'watchdog',
    'click',
    'tornado',
    'altair',
    'pandas',
    'numpy',
    'PIL',
    'pydantic',                            # ← ADD
    'typing_extensions',                   # ← ADD
    'importlib.metadata',                  # ← ADD
],
```

**Also update build scripts** to include these in --hidden-import flags

**Impact**: MEDIUM - May prevent ImportError-based exit code 2

---

## Testing Strategy

### Test 1: Local Build with Fixes
```bash
# Apply FIX #1 and FIX #2
# Build locally
bash build/scripts/build_windows.sh

# Test from project directory
./dist/StreamlitApp/StreamlitApp.exe

# Test from different directory
cp -r dist/StreamlitApp ~/Desktop/
cd ~/Desktop/StreamlitApp
./StreamlitApp.exe
```

### Test 2: CI Build
```bash
# Apply all fixes
git add .
git commit -m "fix: Resolve exit code 2 in CI builds - absolute paths + config"
git tag v0.1.7
git push origin v0.1.7

# Wait for GitHub Actions build
# Download artifact
# Test on clean Windows machine
```

### Test 3: Verify Error Capture
```bash
# Intentionally break main_app.py
echo "import nonexistent_module" >> src/ui/main_app.py

# Build and run
# Verify that logs now show the actual ImportError
```

---

## Success Criteria

- ✅ PyInstaller executable launches from any directory
- ✅ Streamlit worker process starts within 30 seconds
- ✅ Server becomes ready on port 8501
- ✅ Desktop window opens and shows Streamlit UI
- ✅ No exit code 2 errors in logs
- ✅ Worker errors (if any) are captured in logs

---

## Rollout Plan

1. **Phase 1**: Apply FIX #1 and FIX #2 (absolute paths + config)
2. **Phase 2**: Test local build
3. **Phase 3**: Apply FIX #3 (error capture)
4. **Phase 4**: Apply FIX #4 (hidden imports)
5. **Phase 5**: Test CI build (push tag)
6. **Phase 6**: Verify v0.1.7 release works

---

## Related Files

- [app.py](../../../app.py) - Main application entry point
- [StreamlitApp.spec](../../../StreamlitApp.spec) - PyInstaller spec file
- [build/scripts/build_windows.sh](../../../build/scripts/build_windows.sh) - Windows build script
- [build/scripts/build_unix.sh](../../../build/scripts/build_unix.sh) - Unix/MacOS build script
- [.github/workflows/build-binaries.yml](../../../.github/workflows/build-binaries.yml) - CI workflow

---

## Conclusion

The root cause of exit code 2 is **relative path resolution failure** in the Streamlit worker process when launched from arbitrary directories. The fix requires:

1. Converting relative path to absolute path using PyInstaller detection
2. Adding `.streamlit/config.toml` to the bundle
3. Setting correct working directory in worker process

Priority: **FIX #1 and FIX #2 must be implemented immediately** for a working release.
