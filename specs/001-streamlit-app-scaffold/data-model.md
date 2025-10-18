# Data Model: Streamlit Application Scaffolding

**Feature**: 001-streamlit-app-scaffold
**Date**: 2025-10-17
**Purpose**: Define entities, their attributes, relationships, and validation rules

## Overview

This template application has a simple data model focused on configuration and navigation. No persistent user data or database is required. All data is file-based (YAML configuration, image assets, logs).

---

## Entities

### 1. Application Configuration

**Purpose**: Stores user-configurable application settings

**File Location**: `config/app.yaml`

**Attributes**:

| Field | Type | Required | Default | Validation | Description |
|-------|------|----------|---------|------------|-------------|
| `app_title` | string | No | "Streamlit App" | 1-100 chars | Application title shown in window and header |
| `logo_path` | string | No | "assets/logo.png" | Valid file path | Path to logo image file (relative to project root) |
| `icon_path` | string | No | "assets/icon.ico" | Valid file path | Path to window icon file (relative to project root) |
| `menu_items` | array | Yes | [see default] | 1-20 items | List of navigation menu items |
| `theme` | object | No | {} | Valid theme config | Streamlit theme customization (optional) |
| `server` | object | No | {} | Valid server config | Server settings (port range, host) |

**Default Configuration** (`config/app.yaml.template`):
```yaml
app_title: "Streamlit Desktop App"
logo_path: "assets/logo.png"
icon_path: "assets/icon.ico"

menu_items:
  - id: "home"
    label: "Home"
    icon: "🏠"
    page: "src.ui.pages.home"
  - id: "feature1"
    label: "Feature 1"
    icon: "⚙️"
    page: "src.ui.pages.feature1"
  - id: "feature2"
    label: "Feature 2"
    icon: "📊"
    page: "src.ui.pages.feature2"
  - id: "about"
    label: "About the Project"
    icon: "ℹ️"
    page: "src.ui.pages.about"

theme:
  primaryColor: "#1f77b4"
  backgroundColor: "#ffffff"
  secondaryBackgroundColor: "#f0f2f6"
  textColor: "#262730"

server:
  port_start: 8501
  port_range: 10
  host: "127.0.0.1"
```

**Validation Rules**:
- `app_title`: Must not be empty or only whitespace
- `logo_path`: If specified, should reference an existing file (fallback to default if missing)
- `icon_path`: If specified, should reference an existing file (fallback to default if missing)
- `menu_items`: Must have at least 1 item, maximum 20 items
- Each `menu_item.id`: Must be unique within menu, alphanumeric + underscore/hyphen only
- Each `menu_item.page`: Must be valid Python module path
- `server.port_start`: Integer between 1024-65535
- `server.port_range`: Integer between 1-100

**Relationships**: None (standalone configuration)

---

### 2. Navigation Menu

**Purpose**: Collection of menu items displayed in sidebar

**Source**: Derived from `Application Configuration.menu_items`

**Runtime State**: Maintained in Streamlit session state

**Attributes** (per menu item):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for menu item |
| `label` | string | Yes | Display text in sidebar |
| `icon` | string | No | Emoji or icon character |
| `page` | string | Yes | Python module path to page implementation |
| `active` | boolean | Runtime | Whether this page is currently displayed |

**State Transitions**:
```
[Inactive] --user clicks menu item--> [Active]
[Active] --user clicks different item--> [Inactive]
```

**Validation Rules**:
- All `id` values must be unique
- `page` module must exist (if not, show placeholder page with implementation instructions per FR-019)
- `label` must be 1-50 characters

**Relationships**:
- Belongs to: Application Configuration
- References: Page (by module path)

---

### 3. Page

**Purpose**: Individual content view displayed in main area

**Implementation**: Python module in `src/ui/pages/`

**Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| `module_path` | string | Python import path (e.g., "src.ui.pages.home") |
| `title` | string | Page title (displayed in content area) |
| `content` | function | `render()` function that displays page content using Streamlit |

**Required Interface** (each page module must implement):
```python
def render():
    """Render page content using Streamlit components"""
    # Page implementation here
    pass
```

**Built-in Pages**:
1. **home** (`src/ui/pages/home.py`): Landing page with template overview
2. **feature1** (`src/ui/pages/feature1.py`): Example feature page demonstrating widgets
3. **feature2** (`src/ui/pages/feature2.py`): Example feature page demonstrating layouts
4. **about** (`src/ui/pages/about.py`): Template information and extension guidance

**Special Pages** (not in menu):
- **error** (`src/ui/components/error_page.py`): Friendly error page for invalid navigation
- **placeholder** (`src/ui/components/placeholder_page.py`): Shown when menu item has no implementation

**Validation Rules**:
- Module must be importable
- Module must have `render()` function
- `render()` must not raise unhandled exceptions

**Relationships**:
- Referenced by: Navigation Menu (via `page` attribute)

---

### 4. Logo Asset

**Purpose**: Branding image displayed in sidebar header

**File Locations**:
- User logo: `assets/logo.png` (user-replaceable)
- Default placeholder: `assets/logo_default.png` (bundled with template)

**Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | string | Path to image file |
| `format` | string | Image format (PNG, JPG, SVG) |
| `width` | integer | Display width in pixels (sidebar-constrained) |

**Supported Formats**: PNG, JPG, JPEG, SVG

**Validation Rules**:
- If `assets/logo.png` exists and is valid image → use it
- If `assets/logo.png` missing or invalid → fallback to `assets/logo_default.png`
- Maximum file size: 5MB (recommendation, not enforced)
- Recommended dimensions: 200x200 pixels or similar (auto-scaled to fit sidebar)

**Error Handling**:
- Missing file → use default placeholder (FR-013)
- Invalid format → use default placeholder
- Corrupted file → use default placeholder
- Log warning to `logs/app.log` in all fallback cases

**Relationships**:
- Referenced by: Application Configuration (`logo_path`)

---

### 4b. Window Icon Asset

**Purpose**: Application icon displayed in desktop window title bar and taskbar

**File Locations**:
- User icon: `assets/icon.ico` (user-replaceable)
- Default placeholder: `assets/icon_default.ico` (bundled with template)

**Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | string | Path to icon file |
| `format` | string | Icon format (ICO, PNG) |
| `size` | string | Icon dimensions (e.g., "32x32", "256x256") |

**Supported Formats**:
- **Windows**: ICO (recommended), PNG
- **Linux**: PNG, ICO
- **Multi-resolution**: ICO files can contain multiple sizes (16x16, 32x32, 48x48, 256x256)

**Validation Rules**:
- If `assets/icon.ico` exists and is valid → use it
- If `assets/icon.ico` missing or invalid → fallback to `assets/icon_default.ico`
- Recommended formats:
  - Windows: `.ico` file with multiple resolutions (16, 32, 48, 256 pixels)
  - Linux: `.png` file at 256x256 pixels
- Maximum file size: 1MB (recommendation)

**Error Handling**:
- Missing file → use default placeholder icon
- Invalid format → use default placeholder icon
- Corrupted file → use default placeholder icon
- Log warning to `logs/app.log` in all fallback cases

**Relationships**:
- Referenced by: Application Configuration (`icon_path`)
- Used by: Desktop Window (pywebview window icon)

---

### 5. Server Configuration

**Purpose**: Runtime configuration for Streamlit server instance

**Source**: Derived from `Application Configuration.server` or defaults

**Attributes**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `host` | string | "127.0.0.1" | Server bind address (localhost only for security) |
| `port` | integer | (dynamic) | Actual port server is running on |
| `port_start` | integer | 8501 | Starting port for dynamic allocation |
| `port_range` | integer | 10 | Number of ports to try |
| `headless` | boolean | true | Run without browser UI (desktop window handles display) |
| `gather_stats` | boolean | false | Disable usage statistics collection |

**State Lifecycle**:
```
[Not Started] --find_free_port()--> [Port Allocated]
[Port Allocated] --start_server()--> [Starting]
[Starting] --server_ready()--> [Running]
[Running] --window_closed()--> [Shutdown]
```

**Validation Rules**:
- `host` must be "127.0.0.1" (localhost only, no external access)
- `port_start` must be 1024-65535
- `port_range` must be 1-100
- Allocated `port` must not be in use

**Error Handling**:
- No free ports in range → show error dialog, exit gracefully
- Server fails to start → show error dialog with troubleshooting, log to `logs/app.log`
- Server crashes during runtime → show error page with restart option

**Relationships**:
- Configured by: Application Configuration
- Used by: Desktop Window (pywebview connects to server URL)

---

### 6. Application Log

**Purpose**: Runtime error and warning logging

**File Location**: `logs/app.log`

**Format**: Plain text, one entry per line

**Entry Structure**:
```
[TIMESTAMP] [LEVEL] [COMPONENT] Message
```

**Example**:
```
[2025-10-17 14:32:01] [WARNING] [ConfigLoader] Logo file not found: assets/logo.png, using default
[2025-10-17 14:32:15] [ERROR] [ServerManager] Failed to start server on port 8501: Port already in use
[2025-10-17 14:32:16] [INFO] [ServerManager] Server started successfully on port 8502
```

**Log Levels**:
- **INFO**: Normal operations (server start, page navigation)
- **WARNING**: Non-critical issues (fallback to defaults, missing optional files)
- **ERROR**: Critical failures (server crashes, unhandled exceptions)

**Rotation**: Not implemented initially (manual cleanup by user)

**Validation Rules**:
- Log directory (`logs/`) created automatically if missing
- If log file cannot be written → fallback to console output only (no error)

**Relationships**: Referenced by all components for error logging

---

## Entity Relationships Diagram

```
Application Configuration (config/app.yaml)
  ├── menu_items[] ───> Navigation Menu
  │                       └── page (module_path) ───> Page (Python module)
  ├── logo_path ───> Logo Asset (sidebar image file)
  ├── icon_path ───> Window Icon Asset (window/taskbar icon file)
  └── server ───> Server Configuration (runtime)

All Components ───log messages───> Application Log (logs/app.log)
```

---

## Data Validation Summary

| Entity | Validation | Error Handling |
|--------|------------|----------------|
| **Application Config** | Schema validation on load | Use built-in defaults if invalid (FR-017) |
| **Navigation Menu** | Unique IDs, valid module paths | Show placeholder page if module missing (FR-019) |
| **Page** | Importable module, has `render()` | Show error page with implementation guide |
| **Logo Asset** | Valid image format, file exists | Fallback to default placeholder (FR-013) |
| **Window Icon Asset** | Valid icon format (.ico/.png), file exists | Fallback to default placeholder icon |
| **Server Config** | Valid port range, localhost only | Error dialog if no free ports |
| **Application Log** | Writable log directory | Fallback to console if file write fails |

---

## File-Based Persistence

All data is file-based. No database required.

**Configuration Files**:
- `config/app.yaml` - User-editable configuration (YAML format)
- `config/app.yaml.template` - Reference template (not loaded, for user documentation)

**Asset Files**:
- `assets/logo.png` - User-replaceable sidebar logo
- `assets/logo_default.png` - Bundled default placeholder logo (read-only)
- `assets/icon.ico` - User-replaceable window icon
- `assets/icon_default.ico` - Bundled default placeholder icon (read-only)

**Runtime Files**:
- `logs/app.log` - Application log (append-only)
- `logs/` directory created automatically if missing

**No State Persistence**: Application state (current page, navigation) is session-only. Restarting app returns to default (home page).

---

## Serialization Formats

| Data Type | Format | Library |
|-----------|--------|---------|
| Configuration | YAML | PyYAML |
| Assets | PNG/JPG/SVG | Pillow (via Streamlit) |
| Logs | Plain Text | Python logging / manual |

---

## Next Steps

✅ Data model complete
➡️ Generate contracts/ (API contracts for page interface)
➡️ Generate quickstart.md
➡️ Update agent context
