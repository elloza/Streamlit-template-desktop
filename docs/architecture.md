# Architecture: Streamlit Desktop Application Template

**Purpose**: Explain the technical architecture of the pywebview + Streamlit desktop application

**Last Updated**: 2025-10-18

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Breakdown](#component-breakdown)
4. [Technology Stack](#technology-stack)
5. [Application Flow](#application-flow)
6. [Directory Structure](#directory-structure)
7. [Configuration System](#configuration-system)
8. [Navigation System](#navigation-system)
9. [Build and Distribution](#build-and-distribution)
10. [Design Decisions](#design-decisions)

---

## Overview

This template creates a **desktop application** using **Streamlit** (web framework) wrapped in a **native desktop window** using **pywebview**. The architecture follows a hybrid approach:

- **Backend**: Streamlit server running on localhost
- **Frontend**: pywebview native window displaying the Streamlit UI
- **Distribution**: PyInstaller bundles everything into standalone executables

### Key Characteristics

- ✅ **Python-only codebase** (no JavaScript, HTML, or CSS required)
- ✅ **Cross-platform** (Windows 11, Linux, MacOS)
- ✅ **Desktop-first UX** (native window, no browser chrome)
- ✅ **Configuration-driven** (YAML-based menu and branding)
- ✅ **Template-focused** (easy to extend with new pages)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Desktop Application                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              pywebview Window (Native)                  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │                                                   │  │ │
│  │  │         Streamlit UI (Web Content)               │  │ │
│  │  │                                                   │  │ │
│  │  │  ┌─────────────┐  ┌──────────────────────────┐  │  │ │
│  │  │  │   Sidebar   │  │     Main Content Area    │  │  │ │
│  │  │  │             │  │                          │  │  │ │
│  │  │  │ [🏠 Home]   │  │  ┌────────────────────┐  │  │  │ │
│  │  │  │ [⚙️ Feat 1] │  │  │   Active Page      │  │  │  │ │
│  │  │  │ [📊 Feat 2] │  │  │   Content          │  │  │  │ │
│  │  │  │ [ℹ️ About]  │  │  │                    │  │  │  │ │
│  │  │  │             │  │  └────────────────────┘  │  │  │ │
│  │  │  └─────────────┘  └──────────────────────────┘  │  │ │
│  │  └───────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ▲                                 │
│                            │ HTTP (localhost:PORT)           │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        Streamlit Server (Background Process)            │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ Config Loader│  │ Page Modules │  │ UI Components│ │ │
│  │  │ (YAML)       │  │ (Dynamic)    │  │ (Sidebar)    │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ Server Mgr   │  │ Logger       │  │ Error Handler│ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    Entry Point: app.py
```

---

## Component Breakdown

### 1. Entry Point (`app.py`)

**Responsibilities**:
- Initialize logging
- Load configuration from `config/app.yaml`
- Find free port for Streamlit server
- Launch Streamlit server in subprocess
- Wait for server to be ready
- Create pywebview desktop window
- Handle graceful shutdown

**Key Code**:
```python
# Find available port
port = find_free_port()

# Start Streamlit server (subprocess, not thread!)
streamlit_process = subprocess.Popen([...])

# Wait for server ready
wait_for_server(port)

# Launch desktop window
webview.create_window(title, url, icon=icon)
webview.start()
```

**Why subprocess, not thread?**
- Streamlit uses signal handlers that only work in main thread
- Subprocess allows clean isolation and shutdown
- Avoids "signal only works in main thread" error on Windows

### 2. Streamlit Server (`src/ui/main_app.py`)

**Responsibilities**:
- Configure Streamlit page settings
- Render sidebar navigation
- Load and display selected page
- Handle navigation state

**Key Code**:
```python
# Configure page
st.set_page_config(page_title=title, layout="wide")

# Hide default Streamlit navigation
_hide_streamlit_navigation()

# Render sidebar and get selected page
selected_page = sidebar.render_sidebar(config)

# Load and render the page
sidebar.load_and_render_page(selected_page)
```

### 3. Sidebar Navigation (`src/ui/sidebar.py`)

**Responsibilities**:
- Display logo
- Render menu buttons
- Track navigation state
- Dynamically load page modules
- Handle errors (missing modules, invalid pages)

**Key Features**:
- **Dynamic page loading**: Uses `importlib` to load pages at runtime
- **Graceful degradation**: Shows placeholder for missing pages
- **Error isolation**: Page errors don't crash the app
- **State management**: Tracks selected page in `st.session_state`

### 4. Page Modules (`src/ui/pages/*.py`)

**Contract**:
Every page must have a `render()` function:

```python
def render() -> None:
    """Display page content using Streamlit components"""
    st.title("Page Title")
    st.write("Content...")
```

**Benefits**:
- Simple interface (just one function)
- Easy to add new pages (create file + update config)
- No routing code needed
- Full access to Streamlit API

### 5. Configuration System (`src/logic/config_loader.py`)

**Responsibilities**:
- Load `config/app.yaml`
- Validate configuration structure
- Provide fallback defaults if config is missing/invalid
- Extract specific config values (title, logo, menu items)

**Features**:
- **Schema validation**: Checks required fields, unique IDs
- **Built-in defaults**: App works even without config file
- **Graceful degradation**: Invalid config → fallback to defaults

### 6. Server Manager (`src/logic/server_manager.py`)

**Responsibilities**:
- Find available port (8501-8510 range)
- Wait for Streamlit server to be ready
- Handle port conflicts

**Key Functions**:
```python
find_free_port(start=8501, max_attempts=10) -> int
wait_for_server(port, timeout=10) -> bool
```

### 7. Logger (`src/logic/logger.py`)

**Responsibilities**:
- Configure logging to `logs/app.log`
- Provide console output
- Log errors, warnings, info messages

**Format**:
```
2025-10-18 10:30:45 - INFO - Application starting...
2025-10-18 10:30:46 - WARNING - Logo not found, using default
2025-10-18 10:30:50 - ERROR - Failed to load module: xyz
```

### 8. Error Components

**Placeholder Page** (`src/ui/components/placeholder_page.py`):
- Shown when page module is missing
- Displays implementation instructions
- Doesn't crash the app

**Error Page** (`src/ui/components/error_page.py`):
- Shown when page crashes during render
- Displays user-friendly error message
- Shows technical details in expander
- Logs error to file

---

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Primary language |
| **Streamlit** | ≥1.30.0 | UI framework |
| **pywebview** | ≥4.4.0 | Desktop window wrapper |
| **PyYAML** | ≥6.0 | Configuration parsing |
| **PyInstaller** | ≥6.0 | Binary packaging |

### Platform-Specific Dependencies

**Windows**:
- pywebview uses `Edge WebView2` (built into Windows 11)

**Linux**:
- pywebview uses `GTK3` and `WebKit2GTK`
- Install: `sudo apt-get install libgtk-3-0 libwebkit2gtk-4.0-37`

**MacOS**:
- pywebview uses `Cocoa` and `WebKit` (built into MacOS)

---

## Application Flow

### Startup Sequence

```
1. User runs app.py (or binary)
   ↓
2. Initialize logging (logs/app.log)
   ↓
3. Load configuration (config/app.yaml)
   ├─ Success → Use user config
   └─ Failure → Use built-in defaults
   ↓
4. Find free port (8501-8510)
   ↓
5. Start Streamlit server (subprocess)
   ├─ Command: streamlit run src/ui/main_app.py
   └─ Mode: Headless (no browser)
   ↓
6. Wait for server ready (poll port)
   ├─ Timeout: 10 seconds
   └─ Retry: Check every 0.5 seconds
   ↓
7. Load window icon (or fallback)
   ↓
8. Create pywebview window
   ├─ URL: http://127.0.0.1:PORT
   └─ Title: From config (or default)
   ↓
9. Desktop window opens
   ↓
10. User interacts with app
```

### Navigation Flow

```
User clicks sidebar button
   ↓
Update st.session_state.selected_page
   ↓
Trigger Streamlit rerun
   ↓
main_app.py renders
   ↓
sidebar.load_and_render_page(selected_page)
   ↓
Try to import page module
   ├─ Success → Call module.render()
   ├─ ImportError → Show placeholder_page
   └─ RuntimeError → Show error_page
   ↓
Page content displayed
```

### Shutdown Sequence

```
User closes window
   ↓
pywebview.start() returns
   ↓
app.py main process exits
   ↓
Streamlit subprocess terminated automatically
   ↓
Clean shutdown (no orphan processes)
```

---

## Directory Structure

```
Streamlit-template-desktop/
├── app.py                      # Entry point (launches server + window)
├── requirements.txt            # Python dependencies
├── config/
│   ├── app.yaml.template       # Configuration template
│   └── app.yaml                # User configuration (customizable)
├── src/
│   ├── logic/                  # Business logic
│   │   ├── config_loader.py    # YAML config loading & validation
│   │   ├── server_manager.py   # Port management & server lifecycle
│   │   └── logger.py           # Logging setup
│   └── ui/                     # User interface
│       ├── main_app.py         # Main Streamlit app
│       ├── sidebar.py          # Sidebar navigation component
│       ├── components/         # Reusable UI components
│       │   ├── error_page.py   # Error display component
│       │   └── placeholder_page.py  # Placeholder for missing pages
│       └── pages/              # Page modules (dynamically loaded)
│           ├── home.py         # Home page
│           ├── feature1.py     # Example feature 1
│           ├── feature2.py     # Example feature 2
│           └── about.py        # About page
├── assets/
│   ├── logo.png                # App logo (sidebar)
│   ├── logo_default.png        # Default logo (fallback)
│   ├── icon.png                # Window icon (customizable)
│   └── icon_default.png        # Default icon (fallback)
├── logs/
│   └── app.log                 # Application logs
├── build/                      # Build scripts and config
│   ├── config.json             # PyInstaller configuration
│   ├── scripts/
│   │   ├── build_windows.sh    # Windows build script
│   │   └── build_unix.sh       # Linux/MacOS build script
│   └── README.md               # Build instructions
└── docs/
    ├── architecture.md         # This file
    ├── extending.md            # Guide for adding pages
    ├── user-guide.md           # End-user documentation
    └── troubleshooting.md      # Common issues and solutions
```

---

## Configuration System

### Configuration File (`config/app.yaml`)

```yaml
app_title: "My Desktop App"
logo_path: "assets/logo.png"
icon_path: "assets/icon.png"

menu_items:
  - id: "home"
    label: "Home"
    icon: "🏠"
    page: "src.ui.pages.home"

  - id: "custom"
    label: "My Custom Page"
    icon: "🚀"
    page: "src.ui.pages.custom"

theme:
  primaryColor: "#1f77b4"
  backgroundColor: "#ffffff"
```

### Built-in Defaults

If `config/app.yaml` is missing or invalid:
- Title: "Streamlit Desktop App"
- Logo: `assets/logo_default.png`
- Icon: `assets/icon_default.png`
- Menu: Home, Feature 1, Feature 2, About

### Validation Rules

- `app_title`: Must be non-empty string
- `menu_items`: Must be list with ≥1 item
- Each menu item: Must have `id`, `label`, `page`
- Menu IDs: Must be unique

---

## Navigation System

### Page Contract

Every page module in `src/ui/pages/` must implement:

```python
def render() -> None:
    """Render page content using Streamlit components"""
    pass
```

**Rules**:
- Function name: exactly `render` (lowercase)
- Parameters: zero
- Return value: `None`
- Uses Streamlit API (`st.*`) for UI

### Dynamic Loading

```python
# sidebar.py
import importlib

module = importlib.import_module("src.ui.pages.home")
module.render()  # Call the render function
```

**Error Handling**:
1. **Module not found** (`ImportError`) → Show placeholder page
2. **No render function** (`AttributeError`) → Show placeholder page
3. **Runtime error** (`Exception`) → Show error page

### State Management

Navigation state stored in Streamlit session state:

```python
st.session_state.selected_page = "src.ui.pages.home"
```

**Persistence**: State persists across Streamlit reruns but resets on app restart.

---

## Build and Distribution

### Build Process

**Tool**: PyInstaller

**Mode**: `--onedir` (directory-based, not single file)

**Why onedir**:
- Faster startup (~2-3 seconds vs 5-10 for onefile)
- Smaller total size (shared dependencies)
- Easier debugging (can inspect bundled files)

**Build Command** (Windows):
```bash
pyinstaller --name=StreamlitApp \
            --onedir \
            --windowed \
            --icon=assets/icon.png \
            --add-data="src;src" \
            --add-data="assets;assets" \
            --add-data="config;config" \
            --hidden-import=streamlit \
            --hidden-import=pywebview \
            app.py
```

**Output**:
```
dist/
└── StreamlitApp/
    ├── StreamlitApp.exe        # Main executable
    ├── _internal/              # Python runtime + dependencies
    ├── src/                    # Application code
    ├── assets/                 # Logo, icons
    └── config/                 # Configuration files
```

### Distribution

**What to distribute**: The entire `dist/StreamlitApp/` folder

**Size**: ~150-200MB (within <500MB limit)

**User experience**:
1. Download ZIP
2. Extract folder
3. Run `StreamlitApp.exe` (or `StreamlitApp` on Unix)
4. No Python installation required

---

## Design Decisions

### Why Streamlit?

**Pros**:
- ✅ Pure Python (no HTML/CSS/JavaScript)
- ✅ Rich component library
- ✅ Reactive programming model
- ✅ Fast prototyping

**Cons**:
- ❌ Web-first (not desktop-native)
- ❌ Requires server process

**Verdict**: Pros outweigh cons for a template-focused desktop app.

### Why pywebview?

**Alternatives considered**:
- **Electron**: Requires JavaScript, large binary size
- **CEF Python**: Complex build, large size (>100MB Chromium)
- **Eel**: Requires JavaScript for UI
- **Tkinter**: Limited UI capabilities

**Why pywebview**:
- ✅ Python-only
- ✅ Native OS webview (small size)
- ✅ Cross-platform
- ✅ Simple API

### Why PyInstaller?

**Alternatives**:
- **cx_Freeze**: Less tested with Streamlit
- **Nuitka**: Overkill, long compile times
- **py2exe / py2app**: Platform-specific only

**Why PyInstaller**:
- ✅ Industry standard
- ✅ Cross-platform
- ✅ Known to work with Streamlit + pywebview
- ✅ Good documentation

### Why subprocess instead of threading?

**Problem**: Streamlit uses signal handlers that only work in main thread.

**Error** (if using threading):
```
ValueError: signal only works in main thread of the main interpreter
```

**Solution**: Use `subprocess.Popen()` to run Streamlit in separate process.

**Benefits**:
- ✅ Avoids signal handler issues
- ✅ Clean process isolation
- ✅ Easier to terminate (kill subprocess)

### Why YAML config?

**Alternatives**: JSON, TOML, Python files

**Why YAML**:
- ✅ Human-readable
- ✅ Supports comments
- ✅ No code execution (safer than Python files)
- ✅ Industry standard for config

---

## Performance Considerations

### Startup Time

**Target**: <5 seconds (FR-015)

**Breakdown**:
- Python import: ~1s
- Streamlit server start: ~2-3s
- pywebview window creation: ~0.5s

**Optimizations**:
- Lazy imports (import modules only when needed)
- Precompiled bytecode (in binary)
- Fast port detection

### Memory Usage

**Typical**: 100-150MB RAM

**Components**:
- Python runtime: ~30MB
- Streamlit: ~50MB
- pywebview: ~20MB
- App code + data: ~10MB

### Binary Size

**Target**: <500MB (Constitution Principle III)

**Actual**: ~150-200MB

**Optimization**:
- Exclude unused packages (`--exclude-module`)
- onedir mode (not onefile)
- No large ML libraries by default

---

## Security Considerations

### Localhost-Only Server

Streamlit server binds to `127.0.0.1` (not `0.0.0.0`):
- ✅ No external network access
- ✅ No firewall issues
- ✅ No inbound connections

### No Web Exposure

Desktop app, not web app:
- ✅ No public URLs
- ✅ No HTTPS needed
- ✅ No CORS issues

### Configuration Validation

All user input validated:
- YAML parsing with error handling
- Schema validation for menu items
- Safe fallback to defaults

---

## Extensibility

### Adding New Pages

1. Create `src/ui/pages/my_page.py` with `render()` function
2. Add menu item to `config/app.yaml`
3. Restart app

**No code changes needed** in navigation system.

### Customizing Branding

1. Replace `assets/logo.png` and `assets/icon.png`
2. Update `app_title` in `config/app.yaml`
3. Restart app

**No code changes needed**.

### Theming

Edit `config/app.yaml` theme section:
```yaml
theme:
  primaryColor: "#FF5733"
  backgroundColor: "#FAFAFA"
```

---

## References

- **Streamlit Documentation**: https://docs.streamlit.io/
- **pywebview Documentation**: https://pywebview.flowrl.com/
- **PyInstaller Documentation**: https://pyinstaller.org/
- **Research Document**: [specs/001-streamlit-app-scaffold/research.md](../specs/001-streamlit-app-scaffold/research.md)
- **Extending Guide**: [extending.md](./extending.md)
- **Build Instructions**: [../build/README.md](../build/README.md)

---

**Last Updated**: 2025-10-18
**Version**: 1.0.0
**Status**: Complete
