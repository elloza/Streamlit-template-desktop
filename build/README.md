# Building Desktop Binaries

**Purpose**: Package the Streamlit desktop application as a standalone executable that runs without Python installed.

**Supported Platforms**: Windows 11, Linux, MacOS

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Build Process](#build-process)
4. [Platform-Specific Instructions](#platform-specific-instructions)
5. [Troubleshooting](#troubleshooting)
6. [Distribution](#distribution)
7. [Advanced Configuration](#advanced-configuration)

---

## Quick Start

### Windows 11

```bash
# From repository root
bash build/scripts/build_windows.sh
```

Output: `dist/StreamlitApp/StreamlitApp.exe`

### Linux / MacOS

```bash
# From repository root
bash build/scripts/build_unix.sh
```

Output: `dist/StreamlitApp/StreamlitApp` (Linux) or `dist/StreamlitApp.app` (MacOS)

---

## Prerequisites

### All Platforms

1. **Python 3.11+** installed and in PATH
2. **PyInstaller** installed:
   ```bash
   pip install pyinstaller
   ```
3. **All application dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

### Windows-Specific

- **Git Bash** or **WSL** (for running .sh build scripts)
- Alternatively, use PowerShell with compatible shell (adjust script syntax)

### Linux-Specific

- **GTK3** and **WebKit2GTK** (required for pywebview):
  ```bash
  sudo apt-get install libgtk-3-0 libwebkit2gtk-4.0-37
  ```

### MacOS-Specific

- **Xcode Command Line Tools**:
  ```bash
  xcode-select --install
  ```

---

## Build Process

### Overview

The build process uses **PyInstaller** to bundle the Python application, all dependencies, and assets into a standalone executable.

**Build Mode**: `--onedir` (directory-based distribution)

**Why onedir**: Faster startup, smaller overall size compared to `--onefile`, easier debugging.

### Build Steps (Automatic via Scripts)

1. **Clean previous builds** - Remove `dist/`, `build/`, and `.spec` files
2. **Run PyInstaller** - Bundle application with all dependencies
3. **Include assets** - Copy `src/`, `assets/`, `config/` into binary
4. **Set hidden imports** - Ensure Streamlit and pywebview modules are included
5. **Create executable** - Output to `dist/StreamlitApp/`

### Manual Build (Advanced)

If you prefer to build manually without scripts:

**Windows**:
```bash
pyinstaller --name=StreamlitApp \
            --onedir \
            --windowed \
            --noconfirm \
            --clean \
            --icon=assets/icon_default.png \
            --add-data="src;src" \
            --add-data="assets;assets" \
            --add-data="config;config" \
            --hidden-import=streamlit \
            --hidden-import=streamlit.web.cli \
            --hidden-import=streamlit.web.bootstrap \
            --hidden-import=pywebview \
            --hidden-import=yaml \
            app.py
```

**Linux/MacOS**:
```bash
pyinstaller --name=StreamlitApp \
            --onedir \
            --windowed \
            --noconfirm \
            --clean \
            --icon=assets/icon_default.png \
            --add-data="src:src" \
            --add-data="assets:assets" \
            --add-data="config:config" \
            --hidden-import=streamlit \
            --hidden-import=streamlit.web.cli \
            --hidden-import=streamlit.web.bootstrap \
            --hidden-import=pywebview \
            --hidden-import=yaml \
            app.py
```

**Note**: The difference is the path separator in `--add-data`:
- Windows: `;` (semicolon)
- Unix: `:` (colon)

---

## Platform-Specific Instructions

### Windows 11

#### Prerequisites
- Windows 11 (64-bit)
- Python 3.11+
- Git Bash or WSL

#### Build
```bash
# Navigate to repository root
cd /path/to/Streamlit-template-desktop

# Run build script
bash build/scripts/build_windows.sh
```

#### Output
- Directory: `dist/StreamlitApp/`
- Executable: `dist/StreamlitApp/StreamlitApp.exe`
- Size: ~150-200MB

#### Testing
```bash
# Run the executable
dist/StreamlitApp/StreamlitApp.exe
```

#### Known Issues
- **Antivirus false positives**: Some antivirus software may flag PyInstaller binaries. Add exception or use code signing.
- **Slow first launch**: Windows Defender may scan the executable on first run.

---

### Linux

#### Prerequisites
- Linux (64-bit, tested on Ubuntu 20.04+)
- Python 3.11+
- GTK3 and WebKit2GTK:
  ```bash
  sudo apt-get update
  sudo apt-get install libgtk-3-0 libwebkit2gtk-4.0-37
  ```

#### Build
```bash
# Navigate to repository root
cd /path/to/Streamlit-template-desktop

# Run build script
bash build/scripts/build_unix.sh
```

#### Output
- Directory: `dist/StreamlitApp/`
- Executable: `dist/StreamlitApp/StreamlitApp`
- Size: ~150-200MB

#### Testing
```bash
# Run the executable
./dist/StreamlitApp/StreamlitApp
```

#### Known Issues
- **Missing GTK**: If the binary doesn't launch, ensure GTK3 is installed (see Prerequisites).
- **Permission denied**: Make executable with `chmod +x dist/StreamlitApp/StreamlitApp`.

---

### MacOS

#### Prerequisites
- MacOS 10.15+ (Catalina or newer)
- Python 3.11+
- Xcode Command Line Tools

#### Build
```bash
# Navigate to repository root
cd /path/to/Streamlit-template-desktop

# Run build script
bash build/scripts/build_unix.sh
```

#### Output
- App Bundle: `dist/StreamlitApp.app/`
- Executable: `dist/StreamlitApp.app/Contents/MacOS/StreamlitApp`
- Size: ~150-200MB

#### Testing
```bash
# Run the app
open dist/StreamlitApp.app

# Or run executable directly
./dist/StreamlitApp.app/Contents/MacOS/StreamlitApp
```

#### Known Issues
- **Gatekeeper warning**: MacOS may block unsigned apps. Right-click → Open, or use:
  ```bash
  xattr -cr dist/StreamlitApp.app
  ```
- **Code signing**: For production distribution, sign with Apple Developer Certificate.

---

## Troubleshooting

### Build Fails with "ModuleNotFoundError"

**Cause**: PyInstaller didn't detect all required modules.

**Solution**: Add missing module to `--hidden-import` in build script.

Example:
```bash
--hidden-import=missing_module_name
```

### Binary Size Too Large (>500MB)

**Cause**: Too many dependencies bundled.

**Solution**: Exclude unnecessary modules with `--exclude-module`:

```bash
--exclude-module=matplotlib \
--exclude-module=scipy \
--exclude-module=torch
```

Check `build/config.json` for list of excluded modules.

### App Doesn't Launch (No Window Appears)

**Checklist**:
1. **Check logs**: Look at `logs/app.log` in the same directory as executable
2. **Try non-windowed mode**: Build with `--console` instead of `--windowed` to see error messages
3. **Verify dependencies**: Ensure all required system libraries are installed (GTK on Linux, etc.)

### Streamlit Server Fails to Start

**Cause**: Port conflicts or missing Streamlit files.

**Solution**:
1. Check if port 8501-8510 range is available
2. Verify `src/` directory was included in build:
   ```bash
   # Inside dist/StreamlitApp/
   ls -la src/
   ```

### Icon Doesn't Appear

**Cause**: Icon file not bundled or wrong format.

**Solution**:
- **Windows**: Use `.ico` format (create with online converter from PNG)
- **Linux/MacOS**: Use `.png` format
- Ensure `assets/icon_default.png` exists

---

## Distribution

### What to Distribute

**Distribute the entire directory**, not just the executable:

- Windows: `dist/StreamlitApp/` folder (includes `.exe` and dependencies)
- Linux: `dist/StreamlitApp/` folder
- MacOS: `dist/StreamlitApp.app/` bundle

### Distribution Methods

#### 1. ZIP Archive (Simple)

```bash
# Windows/Linux
cd dist
zip -r StreamlitApp.zip StreamlitApp/

# MacOS
cd dist
zip -r StreamlitApp.zip StreamlitApp.app/
```

#### 2. Installer (Professional)

- **Windows**: Use [Inno Setup](https://jrsoftware.org/isinfo.php) or [NSIS](https://nsis.sourceforge.io/)
- **MacOS**: Use `create-dmg` or Apple's native tools
- **Linux**: Create `.deb` or `.rpm` package

#### 3. Portable Executable (Advanced)

For true single-file distribution, use `--onefile` mode (tradeoff: slower startup):

```bash
pyinstaller --onefile --windowed app.py
```

### Size Expectations

| Platform | Typical Size | Max Size (Limit) |
|----------|--------------|------------------|
| Windows  | 150-200 MB   | 500 MB           |
| Linux    | 140-190 MB   | 500 MB           |
| MacOS    | 160-210 MB   | 500 MB           |

If exceeding limits, review excluded modules in `build/config.json`.

---

## Advanced Configuration

### Customizing Build Settings

Edit `build/config.json` to configure:

- **App name and version**
- **Icon path**
- **Hidden imports** (modules to force-include)
- **Excluded modules** (large libraries to skip)
- **Asset paths** (additional files to bundle)

Example:
```json
{
  "app_name": "MyCustomApp",
  "version": "1.0.0",
  "icon": "assets/custom_icon.png",
  "pyinstaller": {
    "hidden_imports": ["mymodule"],
    "exclude_modules": ["large_unused_lib"]
  }
}
```

### Creating a PyInstaller Spec File

For full control, generate and customize a `.spec` file:

```bash
pyi-makespec --onedir --windowed app.py
```

Edit `app.spec`, then build with:
```bash
pyinstaller app.spec
```

### Optimizing Binary Size

1. **Remove unused dependencies**: Uninstall packages not needed for production
2. **Use `--exclude-module`**: Skip large libraries (matplotlib, scipy, etc.)
3. **Compress assets**: Optimize images in `assets/` folder
4. **Use `--onefile`** (tradeoff: slower startup, but single file)

### Hidden Imports Reference

**Core Requirements** (always include):
- `streamlit`
- `streamlit.web.cli`
- `streamlit.web.bootstrap`
- `pywebview`
- `yaml`

**Platform-Specific**:
- **Windows**: `pywebview.platforms.winforms`
- **Linux**: `pywebview.platforms.gtk`
- **MacOS**: `pywebview.platforms.cocoa`

**Streamlit Dependencies** (usually auto-detected, but add if missing):
- `watchdog`
- `click`
- `tornado`
- `altair`
- `pandas`
- `numpy`
- `PIL`

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Binaries

on:
  release:
    types: [created]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: bash build/scripts/build_windows.sh
      - uses: actions/upload-artifact@v3
        with:
          name: StreamlitApp-Windows
          path: dist/StreamlitApp/

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: sudo apt-get install libgtk-3-0 libwebkit2gtk-4.0-37
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: bash build/scripts/build_unix.sh
      - uses: actions/upload-artifact@v3
        with:
          name: StreamlitApp-Linux
          path: dist/StreamlitApp/
```

---

## Testing Checklist

Before distributing binaries, verify:

- [ ] **Executable launches** without errors
- [ ] **Desktop window appears** (not just console)
- [ ] **All menu items work** (Home, Feature 1, Feature 2, About, Test Custom)
- [ ] **Logo displays** in sidebar
- [ ] **Window icon** appears in title bar (Windows/Linux)
- [ ] **Configuration loads** from `config/app.yaml`
- [ ] **Logs created** in `logs/app.log`
- [ ] **Startup time** < 10 seconds on modern hardware
- [ ] **Binary size** < 500 MB
- [ ] **No Python required** on clean test machine
- [ ] **Tested on target OS** (fresh VM or test machine)

---

## FAQ

### Q: Can I use `--onefile` instead of `--onedir`?

**A**: Yes, but with tradeoffs:
- **Pros**: Single .exe file, easier distribution
- **Cons**: Slower startup (~3-5 seconds unpacking to temp), larger perceived size

Change in build script: Replace `--onedir` with `--onefile`.

### Q: Why is the binary so large?

**A**: Python binaries include:
- Python interpreter (~50MB)
- Streamlit framework (~50-80MB)
- Dependencies (pandas, numpy, etc.)
- Your application code and assets

This is normal for Python desktop applications. <500MB is the acceptable limit.

### Q: How do I reduce startup time?

**A**:
- Use `--onedir` mode (not `--onefile`)
- Exclude unnecessary modules
- Optimize asset loading (lazy import heavy libraries)
- Profile with `--debug=imports` to find bottlenecks

### Q: Can I cross-compile (build for Windows on Linux)?

**A**: PyInstaller doesn't support cross-compilation. Build on the target platform:
- Windows binaries → Build on Windows
- Linux binaries → Build on Linux
- MacOS binaries → Build on MacOS

Use CI/CD (GitHub Actions) to build all platforms automatically.

### Q: How do I handle updates?

**A**: Options:
1. **Manual**: Users download new ZIP/installer
2. **Auto-update**: Implement update checker in app (e.g., compare versions with GitHub releases)
3. **Package manager**: Use Microsoft Store (Windows), App Store (MacOS), or Linux repos

---

## References

- **PyInstaller Documentation**: https://pyinstaller.org/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **pywebview Documentation**: https://pywebview.flowrl.com/
- **Template Architecture**: See `docs/architecture.md`
- **Troubleshooting Guide**: See `docs/troubleshooting.md`

---

**Need Help?** Check `logs/app.log` for detailed error messages, or review build output for specific error codes.
