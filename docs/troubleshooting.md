# Troubleshooting Guide

Common issues and solutions for Streamlit Desktop Application.

---

## Table of Contents

1. [Startup Issues](#startup-issues)
2. [Runtime Errors](#runtime-errors)
3. [Performance Problems](#performance-problems)
4. [Build Issues](#build-issues)
5. [Platform-Specific Issues](#platform-specific-issues)

---

## Startup Issues

### Application Won't Start (No Window Appears)

**Symptoms**: Double-clicking executable does nothing

**Diagnosis**:
```bash
# Run from command line to see error messages
./StreamlitApp  # Linux/MacOS
StreamlitApp.exe  # Windows (in cmd/powershell)
```

**Solutions**:

1. **Check logs**:
   - Location: `logs/app.log`
   - Look for error messages

2. **Port conflict**:
   - Error: "No free ports available"
   - Solution: Close apps using ports 8501-8510
   - Check: `netstat -an | findstr "850"` (Windows) or `lsof -i :8501` (Unix)

3. **Missing dependencies** (source install):
   ```bash
   pip install -r requirements.txt
   ```

4. **Permission issues**:
   - Linux/MacOS: `chmod +x StreamlitApp`
   - Windows: Right-click → Properties → Unblock

### "Signal only works in main thread" Error

**Cause**: Running Streamlit in thread instead of subprocess

**Solution**: Already fixed in Phase 0 (T000). If you see this:
- Check `app.py` uses `subprocess.Popen()` not `threading.Thread()`
- Update to latest version of template

### Server Timeout

**Symptoms**: "Failed to start Streamlit server within timeout"

**Solutions**:
1. Increase timeout in `src/logic/server_manager.py`:
   ```python
   wait_for_server(port, timeout=20)  # Increase from 10 to 20
   ```

2. Check firewall isn't blocking localhost connections

3. Check antivirus isn't delaying startup

---

## Runtime Errors

### Page Shows Placeholder Instead of Content

**Symptoms**: "Page Not Implemented" message appears

**Causes**:
1. Page module missing from `src/ui/pages/`
2. Page module missing `render()` function
3. Syntax error in page module

**Solutions**:
1. **Check module exists**:
   ```bash
   ls src/ui/pages/my_page.py  # Should exist
   ```

2. **Check render function**:
   ```python
   # Page must have this exact function
   def render():
       st.title("My Page")
   ```

3. **Check for syntax errors**:
   ```bash
   python -m py_compile src/ui/pages/my_page.py
   ```

4. **Check config/app.yaml**:
   ```yaml
   - id: "my_page"
     page: "src.ui.pages.my_page"  # Must match filename
   ```

### Configuration Not Loading

**Symptoms**: App uses default title/logo despite having `config/app.yaml`

**Solutions**:
1. **Check YAML syntax**:
   ```bash
   python -c "import yaml; yaml.safe_load(open('config/app.yaml'))"
   ```

2. **Check indentation** (YAML is whitespace-sensitive):
   ```yaml
   # CORRECT
   menu_items:
     - id: "home"
       label: "Home"

   # WRONG (bad indentation)
   menu_items:
   - id: "home"
   label: "Home"
   ```

3. **Check logs** for validation errors:
   ```
   WARNING - Config validation failed, using defaults
   ```

### Logo/Icon Not Displaying

**Symptoms**: Text placeholder "ST" instead of logo

**Solutions**:
1. **Check file exists**:
   ```bash
   ls assets/logo.png
   ```

2. **Check file format** (PNG, JPG, JPEG, SVG only):
   ```bash
   file assets/logo.png  # Should show: PNG image data
   ```

3. **Check path in config**:
   ```yaml
   logo_path: "assets/logo.png"  # Relative to app root
   ```

4. **Try default logo**:
   ```yaml
   logo_path: "assets/logo_default.png"
   ```

---

## Performance Problems

### Slow Startup (>10 seconds)

**Normal startup**: 2-5 seconds

**Causes and Solutions**:

1. **Antivirus scanning**:
   - Add executable to antivirus exclusions
   - Windows Defender especially slow on first run

2. **Large config file**:
   - Keep `config/app.yaml` under 100KB
   - Remove unnecessary menu items

3. **Too many dependencies**:
   - Only import heavy libraries when needed:
     ```python
     def render():
         import pandas as pd  # Import here, not at top
         # Use pandas...
     ```

### High Memory Usage (>500MB)

**Normal usage**: 100-150MB

**Solutions**:
1. **Check for memory leaks** in custom pages
2. **Clear Streamlit cache** periodically:
   ```python
   st.cache_data.clear()
   ```
3. **Limit data loading**:
   ```python
   df = pd.read_csv("data.csv", nrows=1000)  # Limit rows
   ```

### App Freezes/Hangs

**Causes**:
1. **Blocking operations** in page render:
   ```python
   # BAD - blocks Streamlit
   time.sleep(10)

   # GOOD - use Streamlit's progress
   with st.spinner("Loading..."):
       # Long operation
   ```

2. **Infinite loops**:
   - Check page code for loops that never exit

3. **Large file operations**:
   - Use chunked reading for large files
   - Show progress with `st.progress()`

---

## Build Issues

### PyInstaller Import Errors

**Symptoms**: Built binary crashes with "ModuleNotFoundError"

**Solution**: Add missing module to `--hidden-import`:

```bash
# In build script
--hidden-import=missing_module_name
```

**Common missing imports**:
- `streamlit.web.bootstrap`
- `streamlit.web.cli`
- `watchdog`
- `altair`

### Binary Too Large (>500MB)

**Solution**: Exclude unused modules:

```bash
--exclude-module=matplotlib \
--exclude-module=scipy \
--exclude-module=torch
```

**Check what's included**:
```bash
# After build
du -h dist/StreamlitApp/* | sort -h
```

### Build Fails on Linux

**Error**: "GTK not found"

**Solution**:
```bash
sudo apt-get update
sudo apt-get install libgtk-3-0 libwebkit2gtk-4.0-37 libgirepository1.0-dev
```

---

## Platform-Specific Issues

### Windows

**Antivirus False Positive**:
- **Problem**: Windows Defender flags executable
- **Solution**:
  1. Add to exclusions
  2. Or code-sign the executable (production)

**Icon Not Showing in Taskbar**:
- **Problem**: Icon appears only after compilation with PyInstaller
- **Solution**: In development, this is expected. Icon shows after building binary.

**"DLL load failed" Error**:
- **Problem**: Missing Visual C++ Redistributable
- **Solution**: Install VC++ Redist from Microsoft

### Linux

**"Cannot open display" Error**:
- **Problem**: Running without X server
- **Solution**: Install and configure X11

**GTK Warnings**:
- **Problem**: `Gtk-WARNING **: cannot open display`
- **Solution**:
  ```bash
  export DISPLAY=:0
  sudo apt-get install libgtk-3-0
  ```

**Permission Denied**:
- **Solution**: `chmod +x StreamlitApp`

### MacOS

**"Cannot be opened because the developer cannot be verified"**:
- **Problem**: Gatekeeper blocking unsigned app
- **Solution**:
  1. Right-click app → Open
  2. Or: `xattr -cr StreamlitApp.app`

**"damaged and can't be opened"**:
- **Problem**: Quarantine attribute
- **Solution**:
  ```bash
  xattr -d com.apple.quarantine StreamlitApp.app
  ```

---

## Getting Help

### Check Logs First

**Location**: `logs/app.log` (in same directory as executable)

**What to look for**:
```
ERROR - Failed to import module: xyz
WARNING - Config validation failed
INFO - Server is ready on port 8501
```

### Debug Mode

Run with console output (development):

**Windows**:
```bash
python app.py
```

**Linux/MacOS**:
```bash
python3 app.py
```

### Report Issues

When reporting issues, include:
1. **Platform**: Windows 11, Ubuntu 22.04, MacOS 13, etc.
2. **Error message**: From `logs/app.log`
3. **Steps to reproduce**
4. **Expected vs actual behavior**

### Useful Commands

**Check Python version**:
```bash
python --version  # Should be 3.11+
```

**Check dependencies**:
```bash
pip list | grep streamlit
pip list | grep pywebview
```

**Test Streamlit separately**:
```bash
streamlit run src/ui/main_app.py
```

**Test pywebview separately**:
```python
import webview
webview.create_window('Test', 'https://google.com')
webview.start()
```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "signal only works in main thread" | Threading issue | Use subprocess (already fixed) |
| "No free ports available" | Port conflict | Close apps on 8501-8510 |
| "Module not found" | Missing dependency | `pip install -r requirements.txt` |
| "Config validation failed" | Invalid YAML | Check syntax, indentation |
| "Logo not found" | Missing file | Check file exists, path correct |
| "Cannot bind to port" | Port in use | Change port or close other app |
| "GTK not found" | Missing library (Linux) | Install libgtk-3-0 |
| "Server timeout" | Slow startup | Increase timeout, check antivirus |

---

## Still Having Issues?

1. **Re-read this guide** - solution might be here
2. **Check logs** - `logs/app.log` has details
3. **Try minimal config** - rename `config/app.yaml` temporarily
4. **Reinstall** - delete and re-extract application
5. **Contact support** - provide logs and error details

---

**Last Updated**: 2025-10-18
**Version**: 1.0.0
