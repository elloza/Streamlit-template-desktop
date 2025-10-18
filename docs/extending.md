# Extending the Template: Adding New Pages

**For**: Template users who want to add custom functionality
**Time to complete**: ~5 minutes per page

## Overview

This template uses a simple, configuration-driven approach to add new pages. No complex routing code needed—just create a Python module and update a YAML file.

---

## Quick Start (3 Steps)

### Step 1: Create Your Page Module

Create a new Python file in `src/ui/pages/` with a `render()` function:

```python
# src/ui/pages/my_feature.py
import streamlit as st

def render():
    """Your custom page content"""
    st.title("My Custom Feature")
    st.write("Add your Streamlit components here...")

    # Example widgets
    user_input = st.text_input("Enter something:")
    if user_input:
        st.success(f"You entered: {user_input}")
```

**Requirements**:
- ✅ File must be in `src/ui/pages/` directory
- ✅ Must have a `render()` function (no parameters)
- ✅ Use Streamlit components (`st.*`) for UI
- ✅ No return value needed

### Step 2: Add Menu Item to Config

Edit `config/app.yaml` and add your page to the `menu_items` list:

```yaml
menu_items:
  - id: home           # existing items...
    label: Home
    icon: 🏠
    page: src.ui.pages.home

  - id: my_feature     # YOUR NEW PAGE
    label: My Feature
    icon: 🚀
    page: src.ui.pages.my_feature  # must match your filename
```

**Configuration Fields**:
- `id`: Unique identifier (lowercase, no spaces)
- `label`: Display name in sidebar menu
- `icon`: Emoji or Unicode icon (optional)
- `page`: Python module path (use `.` not `/`)

### Step 3: Restart the App

```bash
python app.py
```

Your new page will appear in the sidebar menu automatically!

---

## Page Interface Contract

Every page must follow this simple contract to work with the navigation system.

### Required: `render()` Function

```python
def render() -> None:
    """Display page content using Streamlit components"""
    pass
```

**Rules**:
- ✅ Must be named exactly `render`
- ✅ Must accept zero parameters
- ✅ Must not return a value
- ✅ Should use Streamlit components for UI

### Error Handling (Recommended)

Handle errors gracefully so one page doesn't crash the entire app:

```python
import streamlit as st
import traceback

def render():
    try:
        # Your page logic here
        st.title("My Page")
        # ...
    except Exception as e:
        st.error("⚠️ An error occurred")
        st.code(str(e))

        # Optional: Show debug info
        with st.expander("Technical Details"):
            st.code(traceback.format_exc())
```

### Using Session State

For stateful pages (forms, counters, etc.), use Streamlit's session state:

```python
import streamlit as st

def render():
    st.title("Counter Example")

    # Initialize state on first run
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    # Display current value
    st.write(f"Count: {st.session_state.counter}")

    # Modify state
    if st.button("Increment"):
        st.session_state.counter += 1
        st.rerun()
```

---

## Examples

### Minimal Page

```python
# src/ui/pages/minimal.py
import streamlit as st

def render():
    st.title("Minimal Page")
    st.write("This is the simplest possible page.")
```

### Page with Form

```python
# src/ui/pages/contact.py
import streamlit as st

def render():
    st.title("Contact Form")

    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Message")

        submitted = st.form_submit_button("Send")
        if submitted:
            st.success(f"Thanks, {name}! Message sent.")
```

### Page with Data Visualization

```python
# src/ui/pages/dashboard.py
import streamlit as st
import pandas as pd
import numpy as np

def render():
    st.title("Dashboard Example")

    # Generate sample data
    data = pd.DataFrame({
        'x': range(100),
        'y': np.random.randn(100).cumsum()
    })

    # Display chart
    st.line_chart(data.set_index('x'))

    # Display table
    st.dataframe(data)
```

### Page with Multi-Column Layout

```python
# src/ui/pages/layout_demo.py
import streamlit as st

def render():
    st.title("Layout Demo")

    # Two columns
    col1, col2 = st.columns(2)

    with col1:
        st.header("Left Column")
        st.info("Content here...")

    with col2:
        st.header("Right Column")
        st.success("More content...")

    # Three columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Metric 1", "42")
    with col2:
        st.metric("Metric 2", "87")
    with col3:
        st.metric("Metric 3", "99")
```

---

## What Happens If...

### ...I forget the `render()` function?

The template will show a **placeholder page** with instructions:

> ⚠️ **Page Not Implemented**
>
> This page is missing a `render()` function.
>
> Add the following to `src/ui/pages/your_page.py`:
> ```python
> def render():
>     # Your code here
> ```

### ...my page module doesn't exist?

Same as above—placeholder page appears with helpful error message.

### ...my page crashes with an error?

The template catches the error and displays an **error page** instead of crashing the entire app. The error is logged to `logs/app.log` for debugging.

### ...I have a typo in the module path?

If `config/app.yaml` has `page: src.ui.pages.my_featrue` (typo), the placeholder page will appear when you click that menu item.

---

## Configuration Deep Dive

### Menu Item Schema

```yaml
menu_items:
  - id: unique_id        # Required: unique identifier (a-z, 0-9, underscore)
    label: Display Name  # Required: shown in sidebar
    icon: 🎨            # Optional: emoji or Unicode character
    page: module.path    # Required: Python module path (dot notation)
```

**Validation Rules**:
- ✅ Each `id` must be unique across all menu items
- ✅ All three required fields must be present
- ✅ `menu_items` must contain at least one item
- ❌ Duplicate IDs will cause config validation failure (app uses defaults)

### Invalid Configuration Example

```yaml
# ❌ INVALID - will fail validation
menu_items:
  - id: home
    label: Home
    page: src.ui.pages.home

  - id: home            # ❌ Duplicate ID
    label: Home 2
    page: src.ui.pages.home2

  - label: About        # ❌ Missing required 'id' and 'page'
```

If configuration is invalid, the app will:
1. Log a warning to `logs/app.log`
2. Fall back to built-in default menu (Home, Feature 1, Feature 2, About)
3. Continue running normally

---

## Advanced: Dynamic Content

### Loading External Data

```python
# src/ui/pages/data_viewer.py
import streamlit as st
import pandas as pd
from pathlib import Path

def render():
    st.title("Data Viewer")

    data_file = Path("data/sample.csv")

    if not data_file.exists():
        st.warning("No data file found")
        st.info("Place `sample.csv` in the `data/` directory")
        return

    try:
        df = pd.read_csv(data_file)
        st.dataframe(df)

        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="data_export.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error loading data: {e}")
```

### File Upload

```python
# src/ui/pages/upload.py
import streamlit as st
import pandas as pd

def render():
    st.title("File Upload Example")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview:")
        st.dataframe(df.head())

        st.success(f"Loaded {len(df)} rows")
```

---

## Best Practices

### ✅ DO

- **Keep pages focused**: One page = one feature or view
- **Handle errors**: Use try/except for external resources (files, APIs, databases)
- **Use session state**: For interactive features that need to persist across reruns
- **Test incrementally**: Create page, add to config, test, then add more features
- **Follow naming conventions**: Use lowercase with underscores (e.g., `my_feature.py`)

### ❌ DON'T

- **Don't modify navigation state**: Let the sidebar handle navigation
- **Don't use blocking operations**: No `time.sleep()` without proper async handling
- **Don't hardcode paths**: Use `Path()` from pathlib for cross-platform compatibility
- **Don't return values from `render()`**: Streamlit pages don't return anything
- **Don't import from other pages**: Keep pages independent

---

## Troubleshooting

### Page doesn't appear in sidebar

**Checklist**:
1. ✅ File is in `src/ui/pages/` directory
2. ✅ Filename matches `page:` value in `config/app.yaml` (use dots, not slashes)
3. ✅ `id` is unique (not used by another menu item)
4. ✅ Config file syntax is valid YAML (indentation matters!)
5. ✅ App was restarted after config change

### Placeholder page shows instead of my content

**Checklist**:
1. ✅ File has a `render()` function (exact name, lowercase)
2. ✅ `render()` takes zero parameters: `def render():` not `def render(self):`
3. ✅ Module path in config matches file location (e.g., `src.ui.pages.my_page` for `src/ui/pages/my_page.py`)
4. ✅ No syntax errors in your Python file (check `logs/app.log`)

### Error page appears when clicking menu item

**Checklist**:
1. ✅ Check `logs/app.log` for detailed error message
2. ✅ Verify all imports work (e.g., `import pandas as pd` requires pandas installed)
3. ✅ Test page has proper error handling (try/except blocks)
4. ✅ No unhandled exceptions in `render()` function

### Config changes don't take effect

**Solution**: Restart the app. The configuration is loaded once at startup.

```bash
# Stop app (Ctrl+C in terminal)
# Start again
python app.py
```

---

## Migration Guide

### Adding to an Existing Template Installation

If you cloned this template and already have pages, here's how to add more:

1. **Create new page module** → `src/ui/pages/new_page.py`
2. **Edit config** → Add menu item to `config/app.yaml`
3. **Restart app** → Run `python app.py`

### Removing a Page

1. **Remove menu item** from `config/app.yaml`
2. **Optional**: Delete the page file from `src/ui/pages/`
3. **Restart app**

### Reordering Menu Items

Just reorder the list in `config/app.yaml`:

```yaml
menu_items:
  # First item appears at top of sidebar
  - id: about
    label: About
    page: src.ui.pages.about

  # Second item
  - id: home
    label: Home
    page: src.ui.pages.home

  # ... and so on
```

---

## Next Steps

- **See example pages**: Check `src/ui/pages/feature1.py` and `feature2.py` for examples
- **Learn Streamlit**: Visit [Streamlit documentation](https://docs.streamlit.io)
- **Customize theme**: Edit `config/app.yaml` theme section
- **Build desktop app**: See `build/README.md` for creating standalone executables

---

## Reference

- **Page Interface Contract**: See `specs/001-streamlit-app-scaffold/contracts/page_interface.md`
- **Example Pages**: See `src/ui/pages/` directory
- **Configuration Schema**: See `specs/001-streamlit-app-scaffold/contracts/configuration_schema.yaml`
- **Architecture**: See `docs/architecture.md` (if available)

---

**Need help?** Check the logs at `logs/app.log` for detailed error messages and debugging information.
