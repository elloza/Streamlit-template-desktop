# Research: Streamlit Desktop Application Architecture

**Feature**: 001-streamlit-app-scaffold
**Date**: 2025-10-17
**Purpose**: Resolve technical unknowns for converting Streamlit web app to desktop application

## Research Questions

1. Desktop Wrapper Solution (BLOCKING)
2. Binary Packaging Approach
3. Streamlit Desktop Integration Patterns

---

## 1. Desktop Wrapper Solution

### Decision: **Streamlit + PyInstaller + pywebview**

### Rationale

After evaluating approaches for packaging Streamlit as a desktop application while maintaining Python-only codebase:

**Selected Approach**: Use `pywebview` library to create a native desktop window that embeds a web browser control, with Streamlit running as a local server in the background.

**Why this works**:
- **Python-only**: pywebview is a Python library with no JavaScript required in application code
- **Cross-platform**: Supports Win11 (uses Edge/WebView2), Linux (uses GTK/WebKit), and MacOS (uses Cocoa/WebKit)
- **Minimal dependencies**: Lightweight wrapper around native platform webview components
- **Streamlit compatible**: Streamlit continues running as normal web server on localhost, pywebview displays it
- **No browser required**: Uses native OS webview components, not external browser
- **Desktop integration**: Provides native window controls, menus, system tray, etc.

### Architecture Flow

```
app.py (entry point)
  ├─> Start Streamlit server on localhost:PORT (background thread)
  ├─> Wait for server ready
  └─> Launch pywebview window pointing to localhost:PORT
      └─> Native desktop window displays Streamlit UI
```

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Electron + Python** | Full desktop app features | Requires JavaScript/Node.js, violates Python-only principle | ❌ Rejected |
| **CEF Python** | Chromium Embedded Framework | Large binary size (>100MB), complex build | ❌ Rejected |
| **Eel** | Simple Python+JS desktop apps | Requires JavaScript for UI | ❌ Rejected |
| **pywebview** | Lightweight, Python-only, cross-platform | Depends on OS webview quality | ✅ **Selected** |
| **Browser automation (Selenium)** | No special dependencies | Ugly, requires browser install, not native feel | ❌ Rejected |

### Implementation Details

**Dependencies added**:
- `streamlit` (UI framework)
- `pywebview` (desktop window wrapper)
- No JavaScript, HTML, or CSS required in codebase

**Desktop window initialization** (app.py):
```python
import webview
import streamlit.web.cli as stcli
import threading
import sys

def start_streamlit():
    sys.argv = ["streamlit", "run", "src/ui/main_app.py",
                "--server.headless=true",
                "--server.port=8501",
                "--browser.gatherUsageStats=false"]
    stcli.main()

if __name__ == '__main__':
    # Start Streamlit in background thread
    t = threading.Thread(target=start_streamlit, daemon=True)
    t.start()

    # Wait for Streamlit to start
    time.sleep(2)

    # Create desktop window
    webview.create_window('Streamlit App', 'http://localhost:8501')
    webview.start()
```

### Constitution Compliance

- ✅ **Python-Only Codebase**: pywebview is pure Python library
- ✅ **Cross-Platform**: Native support for Win11, Linux, MacOS
- ✅ **Minimal Dependencies**: pywebview is lightweight (~1MB)
- ✅ **Desktop-First**: Native window, no browser chrome
- ⚠️ **Binary Size**: Estimated 50-150MB (Streamlit + dependencies + Python runtime), within <500MB target

---

## 2. Binary Packaging Approach

### Decision: **PyInstaller**

### Rationale

PyInstaller is the most mature and widely-used solution for creating standalone Python executables with good cross-platform support.

**Why PyInstaller**:
- **Proven track record**: Industry standard for Python binary packaging
- **Cross-platform**: Single codebase produces binaries for Win11, Linux, MacOS
- **Streamlit compatible**: Known to work with Streamlit applications
- **pywebview compatible**: Handles native library dependencies
- **One-file mode**: Can produce single executable (optional, easier distribution)
- **Active development**: Well-maintained with large community

### Build Process

**Windows (Win11)**:
```bash
pyinstaller --name=StreamlitApp \
            --onefile \
            --windowed \
            --add-data="src;src" \
            --add-data="assets;assets" \
            --add-data="config;config" \
            --hidden-import=streamlit \
            --hidden-import=pywebview \
            app.py
```

**Unix/Linux**:
```bash
pyinstaller --name=StreamlitApp \
            --onedir \
            --windowed \
            --add-data="src:src" \
            --add-data="assets:assets" \
            --add-data="config:config" \
            --hidden-import=streamlit \
            --hidden-import=pywebview \
            app.py
```

### Alternatives Considered

| Tool | Pros | Cons | Verdict |
|------|------|------|---------|
| **PyInstaller** | Mature, widely used, cross-platform | Can be large binaries | ✅ **Selected** |
| **cx_Freeze** | Cross-platform, modular | Less Streamlit testing | ⚠️ Backup option |
| **Nuitka** | Compiles to C, faster | Complex, longer build times | ❌ Overkill for template |
| **py2exe** | Simple | Windows-only | ❌ Rejected (no Unix support) |
| **py2app** | Native MacOS | MacOS-only | ❌ Rejected (not cross-platform) |

### Build Configuration

**build/config.json**:
```json
{
  "app_name": "StreamlitApp",
  "version": "0.1.0",
  "icon": "assets/icon.ico",
  "platforms": ["win11", "linux"],
  "pyinstaller": {
    "onefile": false,
    "windowed": true,
    "hidden_imports": ["streamlit", "pywebview", "yaml"]
  }
}
```

### Binary Size Optimization

- Use `--onedir` mode by default (smaller, faster startup than `--onefile`)
- Exclude unnecessary packages via `--exclude-module`
- Compress assets appropriately
- Expected final size: **100-200MB** (well within 500MB limit)

### Constitution Compliance

- ✅ **Cross-Platform**: PyInstaller supports Win11 and Unix (mandatory platforms)
- ✅ **Build Scripts**: Platform-specific scripts in `build/scripts/`
- ✅ **Binary Size**: Estimated 100-200MB, within <500MB constraint
- ✅ **Template-First**: Build process will be documented step-by-step in `build/README.md`

---

## 3. Streamlit Desktop Integration Patterns

### Decision: **Background Server + Port Management**

### Rationale

Streamlit requires a server process. For desktop deployment, this must be managed automatically without user intervention.

### Port Management Strategy

**Approach**: Dynamic port allocation with retry logic

```python
import socket
import time
from contextlib import closing

def find_free_port(start_port=8501, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                sock.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports available")

def wait_for_server(port, timeout=10):
    """Wait for Streamlit server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.connect(('127.0.0.1', port))
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False
```

**Benefits**:
- **No port conflicts**: Automatically finds available port
- **Robust**: Handles multiple instance scenarios
- **User-friendly**: No configuration needed
- **Fast startup**: Polling with timeout ensures quick launch

### Server Lifecycle Management

**Startup Sequence**:
1. Find free port
2. Start Streamlit server in daemon thread (dies when main process exits)
3. Wait for server ready (poll HTTP endpoint)
4. Launch pywebview window
5. Desktop window displays app

**Shutdown Sequence**:
1. User closes window → pywebview event
2. Main process exits
3. Daemon thread (Streamlit server) automatically terminated
4. Clean shutdown, no orphan processes

### Error Handling

**Server Start Failures**:
- If server fails to start within timeout → Show error dialog with troubleshooting guidance
- Log error to `logs/app.log` for debugging
- Graceful exit

**Port Conflicts**:
- Auto-retry with different ports (handled by `find_free_port`)
- Max 10 attempts before failure

**Server Crashes** (during runtime):
- pywebview detects connection loss
- Show error page with restart option
- Log crash details

### Multiple Instance Handling

**Strategy**: Allow multiple instances (each gets unique port)

**Rationale**: Desktop users may want multiple windows open for different projects/tasks. No single-instance lock required.

**Implementation**: Each launch finds its own port, no shared state.

### Offline Operation

- ✅ **No external network required**: Streamlit server binds to `127.0.0.1` (localhost only)
- ✅ **No internet needed**: All assets bundled in binary
- ✅ **Firewall friendly**: No inbound connections, local loopback only

### Constitution Compliance

- ✅ **Graceful Degradation**: Server failures handled with user-friendly error messages
- ✅ **Error Logging**: All failures logged to `logs/app.log`
- ✅ **Offline Capable**: No network dependencies
- ✅ **Desktop UX**: Clean startup/shutdown, no exposed terminal/console

---

## Summary of Decisions

| Component | Decision | Key Benefit |
|-----------|----------|-------------|
| **Desktop Wrapper** | pywebview | Python-only, cross-platform, native feel |
| **Binary Packaging** | PyInstaller | Mature, proven with Streamlit, cross-platform |
| **Server Management** | Background thread + dynamic ports | Automatic, user-friendly, robust |
| **Window Lifecycle** | Daemon thread model | Clean shutdown, no orphan processes |
| **Port Strategy** | Dynamic allocation with retry | No conflicts, multiple instances OK |

## Updated Technical Context

With research complete, the Technical Context can be updated:

**Primary Dependencies**:
- `streamlit>=1.30.0` (UI framework)
- `pywebview>=4.4.0` (desktop window wrapper)
- `PyYAML>=6.0` (configuration)
- `pyinstaller>=6.0` (binary packaging, dev dependency)

**Binary Packaging**: PyInstaller with `--onedir` mode, platform-specific build scripts

**Desktop Architecture**: pywebview wrapper creates native window displaying Streamlit running on localhost with dynamic port allocation

**Estimated Binary Size**: 100-200MB (within <500MB limit)

## Next Steps

✅ Research complete - all "NEEDS CLARIFICATION" items resolved
➡️ Proceed to Phase 1: Generate data-model.md and contracts/
➡️ Update plan.md Technical Context with specific dependencies
➡️ Re-validate Constitution Check with concrete architectural decisions
