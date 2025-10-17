# Contract: Page Interface

**Feature**: 001-streamlit-app-scaffold
**Date**: 2025-10-17
**Purpose**: Define the contract that all page modules must implement

## Overview

Every page in the application (located in `src/ui/pages/`) must adhere to this interface contract to ensure compatibility with the navigation system.

---

## Required Interface

### Function: `render()`

**Signature**:
```python
def render() -> None:
    """Render page content using Streamlit components"""
    pass
```

**Purpose**: Display the page content using Streamlit's declarative UI API

**Parameters**: None

**Return Value**: None

**Behavior**:
- MUST use Streamlit components (`st.*`) to render UI
- MUST NOT return any value
- MUST handle its own errors gracefully (try/except with user-friendly messages)
- MAY use Streamlit session state (`st.session_state`) for page-specific state
- MUST NOT modify global navigation state (managed by sidebar)

**Example Implementation**:
```python
import streamlit as st

def render():
    """Home page content"""
    st.title("Welcome to the Template")
    st.write("This is a minimalist Streamlit desktop application template.")

    col1, col2 = st.columns(2)
    with col1:
        st.info("Edit this page in src/ui/pages/home.py")
    with col2:
        st.success("Template is working correctly!")
```

---

## Contract Validation

### Valid Page Module

A page module is considered **valid** if:
1. ✅ Module is importable via Python `import` statement
2. ✅ Module contains a top-level function named `render`
3. ✅ `render()` function accepts zero arguments
4. ✅ `render()` function executes without raising unhandled exceptions
5. ✅ `render()` uses only Streamlit-compatible code (no blocking operations)

### Invalid Page Module

A page module is **invalid** if:
1. ❌ Module cannot be imported (syntax errors, missing dependencies)
2. ❌ Module does not have `render()` function
3. ❌ `render()` function has required parameters
4. ❌ `render()` function raises unhandled exceptions
5. ❌ `render()` contains blocking I/O without proper error handling

---

## Error Handling Contract

### Page-Level Error Handling

Pages SHOULD handle their own errors using this pattern:

```python
import streamlit as st
import traceback

def render():
    try:
        # Page logic here
        st.title("My Page")
        # ...
    except Exception as e:
        st.error("An error occurred while rendering this page.")
        st.code(str(e))

        # Optional: Show details in expander for debugging
        with st.expander("Technical Details"):
            st.code(traceback.format_exc())
```

### Framework-Level Error Handling

If a page's `render()` function raises an unhandled exception:
1. Navigation system catches the exception
2. Error page (`src/ui/components/error_page.py`) is displayed
3. Error is logged to `logs/app.log`
4. User can navigate back to other pages

---

## Page Lifecycle

```
[Module Import]
    ↓
[Validation: has render()?]
    ↓ YES                          ↓ NO
[render() called]          [Show placeholder_page.py]
    ↓
[Streamlit renders UI]
    ↓
[User navigates away]
    ↓
[Page unloaded]
```

**Notes**:
- Each page navigation triggers a fresh call to `render()`
- No explicit initialization or cleanup functions (handled by Streamlit's rerun model)
- State persistence via `st.session_state` if needed

---

## Navigation Integration

### How Pages Are Invoked

From `src/ui/sidebar.py` (navigation system):

```python
import importlib
import streamlit as st

def load_and_render_page(module_path: str):
    """Load and render a page module"""
    try:
        # Import the page module
        module = importlib.import_module(module_path)

        # Validate contract
        if not hasattr(module, 'render'):
            # Show placeholder page with implementation instructions
            from src.ui.components.placeholder_page import render as placeholder_render
            placeholder_render(module_path)
            return

        # Call render function
        module.render()

    except ImportError as e:
        # Module doesn't exist - show placeholder
        from src.ui.components.placeholder_page import render as placeholder_render
        placeholder_render(module_path)

    except Exception as e:
        # Runtime error - show error page
        from src.ui.components.error_page import render as error_render
        error_render(e, module_path)
```

---

## Built-In Page Examples

### Minimal Page

```python
# src/ui/pages/minimal.py
import streamlit as st

def render():
    st.title("Minimal Page")
    st.write("This is a minimal page implementation.")
```

### Page with Widgets

```python
# src/ui/pages/example_widgets.py
import streamlit as st

def render():
    st.title("Example: Widgets")

    # Input widgets
    name = st.text_input("Enter your name")
    age = st.number_input("Enter your age", min_value=0, max_value=120)

    # Display
    if name:
        st.success(f"Hello, {name}! You are {age} years old.")
```

### Page with State

```python
# src/ui/pages/example_state.py
import streamlit as st

def render():
    st.title("Example: Session State")

    # Initialize state
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    # Display and modify state
    st.write(f"Counter: {st.session_state.counter}")

    if st.button("Increment"):
        st.session_state.counter += 1
        st.rerun()
```

---

## Testing Contract Compliance

### Unit Test Template

```python
# tests/unit/test_page_contract.py
import importlib
import pytest

def test_page_has_render_function():
    """Verify page module has render() function"""
    module = importlib.import_module("src.ui.pages.home")
    assert hasattr(module, 'render'), "Page must have render() function"
    assert callable(module.render), "render must be callable"

def test_render_accepts_no_args():
    """Verify render() accepts zero arguments"""
    import inspect
    module = importlib.import_module("src.ui.pages.home")
    sig = inspect.signature(module.render)
    assert len(sig.parameters) == 0, "render() must accept zero arguments"

def test_render_returns_none():
    """Verify render() returns None (not a value)"""
    module = importlib.import_module("src.ui.pages.home")
    # Can't easily test Streamlit rendering, but can verify it doesn't crash
    # Actual rendering test requires Streamlit test framework
    pass
```

---

## Extension Guide Reference

For template users adding new pages, see:
- `docs/extending.md` - Step-by-step guide for adding new pages
- `src/ui/pages/home.py` - Example implementation
- `config/app.yaml` - Add menu item for new page

---

## Contract Version

**Version**: 1.0.0
**Date**: 2025-10-17
**Status**: Stable

**Breaking Changes Policy**: Any changes to this contract that affect existing page implementations will require a MAJOR version increment and migration guide.
