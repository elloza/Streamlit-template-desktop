# Research: PyInstaller + Streamlit Subprocess Architecture

**Feature**: Fix Windows infinite process spawn bug
**Date**: 2025-10-18
**Status**: Complete

## Problem Statement

The application spawns infinite processes on Windows when built with PyInstaller, requiring system restart. The root cause is using `subprocess.Popen([sys.executable, "-m", "streamlit"])` where `sys.executable` points to the frozen .exe, not Python.

## Research Questions

### Q1: Can we use subprocess with PyInstaller for Streamlit?

**Answer**: Not directly with `sys.executable`, but yes with `multiprocessing.Process`.

**Rationale**:
- In PyInstaller bundles, `sys.executable` = `StreamlitApp.exe` (not python.exe)
- Calling `subprocess.Popen([sys.executable, ...])` spawns the .exe again
- `multiprocessing.Process` has built-in PyInstaller support via runtime hooks

### Q2: Will threading prevent using Playwright/browser automation?

**Answer**: No, threading is fine for Playwright.

**Rationale**:
- Playwright spawns **browser driver processes** (chromium, firefox), not Python
- Browser drivers are external binaries that work from any Python context
- Threading vs multiprocessing doesn't affect external process spawning
- Confirmed by Playwright docs and production examples

### Q3: What's the best architecture for isolation + PyInstaller?

**Answer**: `multiprocessing.Process` with `spawn` context.

**Comparison Table**:

| Aspect | Thread (Option 1) | Multiprocessing (Option 2) | Bundle python.exe (Option 3) |
|--------|-------------------|---------------------------|------------------------------|
| Process Isolation | ❌ Same process | ✅ Separate process | ✅ Separate process |
| PyInstaller Support | ✅ No issues | ✅ Built-in hooks | ⚠️ Manual bundling |
| Bundle Size | ~150MB | ~150MB | ~200MB (+50MB) |
| Complexity | Low | Medium | High |
| Playwright Support | ✅ Full | ✅ Full | ✅ Full |
| License Issues | ✅ None | ✅ None | ⚠️ Potential Python license |
| Maintainability | ✅ Simple | ✅ Standard | ❌ Complex |

## Decision: Use Multiprocessing (Option 2)

### Chosen Solution

Use `multiprocessing.Process` with explicit `spawn` context to run Streamlit in a separate process.

### Why NOT Option 1 (Threading)

While simpler, threading doesn't provide:
- Process isolation (crash in Streamlit crashes main app)
- Ability to restart Streamlit without restarting app
- Memory isolation (Streamlit leaks affect main app)

### Why NOT Option 3 (Bundle python.exe)

Bundling python.exe separately is:
- ❌ Against PyInstaller philosophy (defeats purpose of embedding)
- ❌ Increases bundle size by ~50MB unnecessarily
- ❌ Complex to maintain (must bundle stdlib, site-packages)
- ❌ May violate Python license redistribution terms
- ❌ Platform-specific (different structure per OS)

### Why YES Option 2 (Multiprocessing)

- ✅ **Full process isolation**: Streamlit crashes don't affect main app
- ✅ **PyInstaller native support**: Runtime hooks handle `freeze_support()`
- ✅ **No size penalty**: Uses embedded Python interpreter
- ✅ **Standard Python**: No custom bundling logic
- ✅ **Cross-platform**: `spawn` context works on Win/Unix/Mac
- ✅ **Playwright compatible**: External processes work normally

## Technical Implementation

### Architecture Pattern

```python
import multiprocessing
from streamlit.web import cli as stcli

# Worker function runs in child process
def _streamlit_worker(port: int):
    """Entry point for Streamlit subprocess."""
    import sys
    sys.argv = ["streamlit", "run", "src/ui/main_app.py",
                f"--server.port={port}", ...]
    stcli.main()

# Main app spawns worker
def start_streamlit_server(port: int, logger):
    ctx = multiprocessing.get_context('spawn')  # Explicit spawn
    process = ctx.Process(target=_streamlit_worker, args=(port,))
    process.start()
    return process

# Main guard required
if __name__ == "__main__":
    multiprocessing.freeze_support()  # CRITICAL for PyInstaller
    main()
```

### How It Works with PyInstaller

1. **PyInstaller's multiprocessing hook** (`pyi_rth_multiprocessing.py`) automatically handles:
   - Detecting frozen vs unfrozen execution
   - Setting up worker process environment
   - Reusing the embedded Python interpreter

2. **`freeze_support()` call** tells multiprocessing:
   - "I'm running from a frozen executable"
   - "Use special spawn logic for worker processes"

3. **Worker process spawning**:
   - Parent calls `process.start()`
   - PyInstaller hook spawns `StreamlitApp.exe --multiprocessing-fork`
   - Worker process executes `_streamlit_worker()` function
   - No infinite loop because worker doesn't call `main()`

### Why This Avoids Infinite Spawn

**Old broken code**:
```python
# ❌ WRONG: sys.executable = StreamlitApp.exe
subprocess.Popen([sys.executable, "-m", "streamlit", ...])
# Spawns StreamlitApp.exe → main() runs → spawns again → infinite loop
```

**New working code**:
```python
# ✅ CORRECT: multiprocessing.Process
ctx.Process(target=_streamlit_worker, ...)
# PyInstaller hook spawns worker → _streamlit_worker() runs → ends
```

## Alternatives Considered

### Alternative 1: stlite (WASM-based Streamlit)

**Description**: Compile Streamlit to WebAssembly, run entirely in browser

**Pros**:
- No subprocess issues
- Truly standalone (no server needed)
- Smaller bundle

**Cons**:
- ❌ Alpha stage (not production-ready)
- ❌ Limited Python package support
- ❌ Different deployment model (not desktop app)

**Decision**: Rejected - too immature for template project

### Alternative 2: Electron + Python Backend

**Description**: Use Electron for UI, Python HTTP server for backend

**Pros**:
- Industry-standard desktop framework
- Better desktop integration
- Separate UI/backend concerns

**Cons**:
- ❌ Violates "Python-only" constitution (requires JavaScript/TypeScript)
- ❌ Much larger bundle (~300MB)
- ❌ Higher complexity for template users

**Decision**: Rejected - violates constitution Principle VII

### Alternative 3: Custom Webview + Flask/FastAPI

**Description**: Use pywebview with Flask/FastAPI backend instead of Streamlit

**Pros**:
- Full control over architecture
- Proven desktop pattern
- No Streamlit-specific issues

**Cons**:
- ❌ Requires manual UI development (defeats Streamlit purpose)
- ❌ Template users lose Streamlit's rapid prototyping
- ❌ Complete rewrite

**Decision**: Rejected - defeats project purpose

## Testing Strategy

### Test 1: PyInstaller Build Success
```bash
pyinstaller --onedir --windowed app.py
./dist/StreamlitApp/StreamlitApp.exe  # Should launch without spawning
```

### Test 2: Process Count Monitoring
```python
# Monitor process count during execution
import psutil
import time

initial_count = len([p for p in psutil.process_iter() if 'StreamlitApp' in p.name()])
time.sleep(10)
final_count = len([p for p in psutil.process_iter() if 'StreamlitApp' in p.name()])

assert final_count <= initial_count + 2  # Main + worker only
```

### Test 3: Playwright Integration
```python
# src/ui/pages/test_playwright.py
from playwright.sync_api import sync_playwright

def test_browser_automation():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com")
        assert page.title() == "Example Domain"
        browser.close()
```

### Test 4: Process Isolation
```python
# Kill Streamlit process, verify main app continues
def test_isolation():
    # Find Streamlit worker process
    streamlit_proc = [p for p in psutil.process_iter()
                     if p.name() == 'StreamlitApp.exe' and p.pid != os.getpid()][0]

    # Kill it
    streamlit_proc.kill()

    # Main app should still respond
    assert webview_window.is_alive()
```

## Implementation Requirements

### Code Changes
1. Replace `subprocess.Popen` with `multiprocessing.Process`
2. Move Streamlit startup to worker function
3. Ensure `freeze_support()` is first call in `__main__`
4. Update cleanup to use `process.terminate()`

### Build Script Changes
No changes required - PyInstaller detects multiprocessing automatically

### Documentation Updates
- Update `docs/architecture.md` with multiprocessing pattern
- Document why threading was rejected (isolation)
- Document why bundling python.exe was rejected (size/complexity)

## References

- **PyInstaller Multiprocessing**: https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#multi-processing
- **Python multiprocessing.spawn**: https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
- **Streamlit + PyInstaller**: https://discuss.streamlit.io/t/using-pyinstaller/902
- **Playwright Python Docs**: https://playwright.dev/python/docs/library

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Worker process crashes | Medium | Low | Process isolation prevents main app crash |
| Longer startup time | Low | Low | Workers spawn quickly (~1-2s) |
| Debugging complexity | Medium | Medium | Use `--debug` flag, check logs |
| Platform compatibility | Low | High | `spawn` context works on all platforms |

## Success Criteria

- ✅ PyInstaller build launches without infinite spawning
- ✅ Streamlit runs in separate process
- ✅ Playwright integration works
- ✅ Main app survives Streamlit crashes
- ✅ Bundle size remains <200MB
- ✅ Cross-platform (Win11 + Unix tested)

## Conclusion

**Selected Architecture**: Multiprocessing with spawn context (Option 2)

**Rationale**: Provides process isolation without complexity/size penalties of bundling python.exe, while maintaining full Playwright compatibility and PyInstaller support.

**Not Selected**:
- Threading (Option 1): Insufficient isolation
- Bundle python.exe (Option 3): Excessive complexity/size, violates PyInstaller philosophy
