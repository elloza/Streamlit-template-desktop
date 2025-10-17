# Quickstart Guide: Streamlit Desktop App Template

**Feature**: 001-streamlit-app-scaffold
**Date**: 2025-10-17
**Audience**: Template users (developers using this template to build their own desktop apps)

## Overview

This guide helps you get the Streamlit Desktop App Template running in under 10 minutes and shows you how to customize it for your needs.

---

## Prerequisites

- **Python 3.11+** installed on your system
- **Git** (optional, for cloning repository)
- **Windows 11** or **Linux/Unix** operating system
- Basic Python knowledge

---

## Quick Start (Development Mode)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Streamlit-template-desktop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
# Run in development mode
python app.py
```

**Expected Result**: A desktop window opens displaying the Streamlit application with sidebar navigation showing Home, Feature 1, Feature 2, and About pages.

**Troubleshooting**:
- If port 8501 is in use, the app will automatically try ports 8502-8510
- Check `logs/app.log` for any error messages
- Ensure all dependencies installed successfully

---

## Project Structure Overview

```
Streamlit-template-desktop/
├── app.py                  # Entry point - run this to start the app
├── src/
│   ├── ui/                 # UI components and pages
│   │   ├── sidebar.py      # Sidebar navigation
│   │   ├── pages/          # Your pages go here
│   │   │   ├── home.py
│   │   │   ├── feature1.py
│   │   │   ├── feature2.py
│   │   │   └── about.py
│   │   └── components/     # Reusable components
│   └── logic/              # Business logic
│       └── config_loader.py
├── config/
│   └── app.yaml            # Application configuration (EDIT THIS!)
├── assets/
│   ├── logo.png            # Your logo here (REPLACE THIS!)
│   └── logo_default.png    # Default placeholder
├── logs/                   # Application logs (auto-created)
└── docs/                   # Documentation
    ├── architecture.md
    ├── extending.md        # How to add new features
    └── troubleshooting.md
```

---

## Customization Guide

### 1. Change App Title and Branding

**Edit** `config/app.yaml`:

```yaml
app_title: "My Awesome App"  # Change this
logo_path: "assets/logo.png"  # Your logo file
```

**Replace** `assets/logo.png` with your own logo:
- Recommended size: 200x200 pixels
- Supported formats: PNG, JPG, SVG
- If missing, app uses default placeholder

**Restart app** to see changes.

---

### 2. Add a New Page

#### Step 2a: Create Page Module

Create `src/ui/pages/my_feature.py`:

```python
import streamlit as st

def render():
    """Your new page content"""
    st.title("My Feature")
    st.write("This is my custom feature page!")

    # Add your widgets here
    name = st.text_input("Enter your name")
    if name:
        st.success(f"Hello, {name}!")
```

#### Step 2b: Add to Menu

Edit `config/app.yaml`:

```yaml
menu_items:
  - id: "home"
    label: "Home"
    icon: "🏠"
    page: "src.ui.pages.home"

  # ADD YOUR NEW PAGE HERE
  - id: "my_feature"
    label: "My Feature"
    icon: "✨"
    page: "src.ui.pages.my_feature"

  - id: "about"
    label: "About the Project"
    icon: "ℹ️"
    page: "src.ui.pages.about"
```

**Restart app** and your new page appears in the sidebar!

**See also**: `docs/extending.md` for detailed instructions

---

### 3. Customize Theme

Edit `config/app.yaml`:

```yaml
theme:
  primaryColor: "#ff6b6b"       # Accent color
  backgroundColor: "#1a1a1a"    # Main background
  secondaryBackgroundColor: "#2d2d2d"
  textColor: "#ffffff"
  font: "sans serif"  # or "serif", "monospace"
```

**Restart app** to see theme changes.

---

## Building Desktop Binaries

### Windows 11

```bash
# From project root
cd build/scripts
./build_windows.sh

# Binary created in: dist/StreamlitApp/
```

### Linux/Unix

```bash
# From project root
cd build/scripts
./build_unix.sh

# Binary created in: dist/StreamlitApp/
```

**See also**: `build/README.md` for detailed build instructions

---

## Common Tasks

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

### Check Logs

```bash
# View application logs
cat logs/app.log

# Or on Windows:
type logs\app.log
```

### Reset to Defaults

```bash
# Restore default configuration
cp config/app.yaml.template config/app.yaml

# Restore default logo
cp assets/logo_default.png assets/logo.png
```

---

## Development Workflow

### Typical Development Cycle

1. **Edit code** in `src/ui/pages/` or `config/app.yaml`
2. **Restart app** (Ctrl+C, then `python app.py` again)
3. **Test changes** in desktop window
4. **Check logs** if something doesn't work (`logs/app.log`)
5. **Repeat**

**Tips**:
- Streamlit auto-reloads on file changes (in development mode)
- If sidebar doesn't update, restart the app
- Configuration changes always require restart

---

## Example: Complete Feature Addition

Let's add a "Calculator" feature from scratch:

### 1. Create the page

`src/ui/pages/calculator.py`:

```python
import streamlit as st

def render():
    st.title("🧮 Simple Calculator")

    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("First number", value=0.0)
    with col2:
        b = st.number_input("Second number", value=0.0)

    operation = st.selectbox("Operation", ["Add", "Subtract", "Multiply", "Divide"])

    if st.button("Calculate"):
        if operation == "Add":
            result = a + b
        elif operation == "Subtract":
            result = a - b
        elif operation == "Multiply":
            result = a * b
        elif operation == "Divide":
            result = a / b if b != 0 else "Error: Division by zero"

        st.success(f"Result: {result}")
```

### 2. Add to menu

`config/app.yaml`:

```yaml
menu_items:
  - id: "home"
    label: "Home"
    icon: "🏠"
    page: "src.ui.pages.home"

  - id: "calculator"
    label: "Calculator"
    icon: "🧮"
    page: "src.ui.pages.calculator"

  # ... rest of menu items
```

### 3. Run and test

```bash
python app.py
```

Click "Calculator" in sidebar → Your calculator is live!

---

## Next Steps

- 📖 Read `docs/extending.md` for advanced customization
- 🏗️ Read `docs/architecture.md` to understand how it works
- 🔧 Read `docs/troubleshooting.md` if you encounter issues
- 📦 Read `build/README.md` to create distributable binaries

---

## Getting Help

**Documentation**:
- `docs/extending.md` - Adding features
- `docs/architecture.md` - How it works
- `docs/troubleshooting.md` - Common issues

**Logs**: Always check `logs/app.log` for error details

**Template Issues**: Report bugs or ask questions in the GitHub repository issues

---

## Success Criteria

✅ You've completed quickstart successfully if:
1. App launches in a desktop window (not browser)
2. You can navigate between all menu pages
3. You've customized the app title or logo
4. You've added at least one new page

**Time to complete**: ~10-15 minutes for first-time setup
