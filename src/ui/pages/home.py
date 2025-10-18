"""
Home page - Landing page with template overview.
"""
import streamlit as st


def render():
    """Render the home page."""
    st.title("🏠 Welcome to Streamlit Desktop App Template")

    st.markdown("""
    This is a **minimalist desktop application template** built with Streamlit and pywebview.

    ### Features

    - ✅ **Desktop Application**: Runs as a native desktop window (not in browser)
    - ✅ **Cross-Platform**: Works on Windows 11 and Unix/Linux
    - ✅ **Customizable**: Easy branding with logo and configuration
    - ✅ **Extensible**: Add new pages by creating Python modules
    - ✅ **Python-Only**: No JavaScript, HTML, or CSS required

    ### Getting Started

    1. **Explore the Example Pages**: Use the sidebar to navigate between pages
    2. **Customize Branding**: Edit `config/app.yaml` and replace `assets/logo.png`
    3. **Add Your Own Pages**: Create new modules in `src/ui/pages/`
    4. **Build Binaries**: Use `build/scripts/` to create standalone executables

    ### Quick Links

    - 📖 [Extension Guide](../../../docs/extending.md)
    - 🏗️ [Architecture](../../../docs/architecture.md)
    - 🔧 [Troubleshooting](../../../docs/troubleshooting.md)
    - 📋 [Quickstart](../../../specs/001-streamlit-app-scaffold/quickstart.md)
    """)

    st.markdown("---")

    # Example of Streamlit components
    st.subheader("Example: Basic Interaction")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("What's your name?", "")
        if name:
            st.success(f"Hello, {name}! 👋")

    with col2:
        selected_option = st.selectbox(
            "Choose an option",
            ["Option 1", "Option 2", "Option 3"]
        )
        st.info(f"You selected: {selected_option}")

    st.markdown("---")
    st.caption("This is a template application. Customize it to build your own desktop app!")
