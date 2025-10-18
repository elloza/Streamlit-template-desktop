"""
About page - Template information and guidance.
"""
import streamlit as st


def render():
    """Render the About page."""
    st.title("ℹ️ About the Project")

    st.markdown("""
    ## Streamlit Desktop App Template

    **Version**: 0.1.0

    This is a boilerplate project for creating Streamlit desktop applications
    with binary generation capabilities.

    ### Architecture

    - **Frontend**: Streamlit (Python-based UI framework)
    - **Desktop Wrapper**: pywebview (native window embedding)
    - **Build Tool**: PyInstaller (standalone executable generation)
    - **Configuration**: YAML-based configuration system

    ### Key Features

    #### 🖥️ Desktop-First
    Unlike traditional Streamlit apps that run in a browser, this template wraps
    the application in a native desktop window using pywebview.

    #### 🎨 Configuration-Driven
    All application settings (title, logo, menu items) are configured via
    `config/app.yaml` without modifying code.

    #### 🔧 Extensible
    Add new pages by creating Python modules with a `render()` function.
    The template automatically handles module loading and error cases.

    #### 📦 Distributable
    Build standalone executables for Windows and Unix using PyInstaller.
    End users don't need Python installed.

    ### How to Extend

    1. **Add a New Page**:
       - Create `src/ui/pages/my_page.py` with a `render()` function
       - Add menu entry to `config/app.yaml`
       - Restart the application

    2. **Customize Branding**:
       - Edit `app_title` in `config/app.yaml`
       - Replace `assets/logo.png` with your logo
       - Restart the application

    3. **Build for Distribution**:
       - Run `build/scripts/build_windows.sh` (Windows)
       - Run `build/scripts/build_unix.sh` (Unix/Linux)
       - Find binary in `dist/` directory

    ### Documentation

    - 📖 [Extension Guide](../../../docs/extending.md)
    - 🏗️ [Architecture Details](../../../docs/architecture.md)
    - 🔧 [Troubleshooting](../../../docs/troubleshooting.md)
    - 📋 [Quickstart Guide](../../../specs/001-streamlit-app-scaffold/quickstart.md)

    ### Technical Details

    **Python Version**: 3.11+

    **Core Dependencies**:
    - streamlit >= 1.30.0
    - pywebview >= 4.4.0
    - PyYAML >= 6.0

    **Build Tools**:
    - pyinstaller >= 6.0

    ### License

    MIT License - See LICENSE file for details.

    ### Contributing

    This is a template project. Fork it and customize for your needs!
    """)

    st.markdown("---")
    st.success("✨ Happy building with Streamlit Desktop!")
