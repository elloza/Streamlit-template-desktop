"""
Main Streamlit application.
Configures page settings and coordinates sidebar with content rendering.
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.logic import config_loader, logger
from src.ui import sidebar as sidebar_module

# Setup logging
logger.setup_logging()

# Load configuration
config = config_loader.load_config()


def main():
    """Main application entry point."""
    # Configure page
    st.set_page_config(
        page_title=config_loader.get_app_title(config),
        page_icon="🖥️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Hide Streamlit's default navigation and deploy button
    _hide_streamlit_navigation()

    # Apply custom theme if configured
    theme = config_loader.get_theme(config)
    if theme:
        _apply_theme(theme)

    # Render sidebar and get selected page
    selected_page = sidebar_module.render_sidebar(config)

    # Render the selected page content
    if selected_page:
        sidebar_module.load_and_render_page(selected_page)
    else:
        st.error("No page selected")


def _hide_streamlit_navigation():
    """
    Hide Streamlit's default navigation elements.
    This prevents the auto-generated page navigation from appearing
    since we're using custom sidebar navigation.
    """
    hide_nav_css = """
        <style>
        /* Hide the default Streamlit page navigation */
        [data-testid="stSidebarNav"] {
            display: none;
        }

        /* Hide the Deploy button in the top-right */
        [data-testid="stToolbar"] {
            display: none;
        }

        /* Hide the "ST" menu button */
        #MainMenu {
            visibility: hidden;
        }

        /* Hide footer */
        footer {
            visibility: hidden;
        }
        </style>
    """
    st.markdown(hide_nav_css, unsafe_allow_html=True)


def _apply_theme(theme: dict):
    """
    Apply custom theme configuration.
    Note: Streamlit themes are best configured via .streamlit/config.toml
    This is a placeholder for dynamic theming.
    """
    # Theme application would go here
    # For now, themes are applied via Streamlit's config system
    pass


if __name__ == "__main__":
    main()
