"""
Sidebar navigation component with logo display and page routing.
Implements FR-001, FR-002, FR-004, FR-005, FR-013, FR-016, FR-019.
"""
import streamlit as st
import importlib
import logging
import toml
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def get_app_version() -> str:
    """Get application version from pyproject.toml."""
    try:
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            # Try _internal directory for bundled apps
            pyproject_path = Path("_internal/pyproject.toml")

        if pyproject_path.exists():
            data = toml.load(pyproject_path)
            return data.get("project", {}).get("version", "0.1.0")
    except Exception as e:
        logger.warning(f"Failed to read version from pyproject.toml: {e}")

    return "0.1.0"  # Default fallback


def render_sidebar(config: Dict[str, Any]) -> str:
    """
    Render sidebar with logo and navigation menu.

    Args:
        config: Application configuration dictionary

    Returns:
        Selected page module path
    """
    with st.sidebar:
        # Display logo
        _render_logo(config.get("logo_path", "assets/logo.png"))

        st.markdown("---")

        # Render menu
        menu_items = config.get("menu_items", [])
        selected_page = _render_menu(menu_items)

        st.markdown("---")
        version = get_app_version()
        st.caption(f"📱 Desktop App Template v{version}")

    return selected_page


def _render_logo(logo_path: str):
    """
    Render logo with fallback to default.
    Implements FR-013: Handle missing logo gracefully.
    """
    # Check if custom logo exists
    logo_file = Path(logo_path)
    default_logo = Path("assets/logo_default.png")

    try:
        if logo_file.exists() and logo_file.suffix in ['.png', '.jpg', '.jpeg', '.svg']:
            st.image(str(logo_file), use_container_width=True)
        elif default_logo.exists():
            logger.warning(f"Logo not found at {logo_path}, using default")
            st.image(str(default_logo), use_container_width=True)
        else:
            # Fallback to text if no logo available
            st.title("ST")
            logger.warning("No logo files found, using text placeholder")
    except Exception as e:
        logger.error(f"Error loading logo: {e}")
        st.title("ST")


def _render_menu(menu_items: List[Dict[str, str]]) -> str:
    """
    Render navigation menu and return selected page.

    Args:
        menu_items: List of menu item dictionaries

    Returns:
        Module path of selected page
    """
    # Initialize session state for selected page
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = menu_items[0]['page'] if menu_items else None

    # Render menu buttons
    for item in menu_items:
        icon = item.get('icon', '')
        label = item.get('label', 'Unnamed')
        page = item.get('page', '')

        # Create button with icon and label
        button_label = f"{icon} {label}" if icon else label

        # Highlight active page
        button_type = "primary" if st.session_state.selected_page == page else "secondary"

        if st.button(button_label, key=f"nav_{item.get('id', label)}", use_container_width=True, type=button_type):
            st.session_state.selected_page = page
            st.rerun()

    return st.session_state.selected_page


def load_and_render_page(module_path: str):
    """
    Load and render the selected page module.
    Implements FR-016 (error page) and FR-019 (placeholder page).

    Args:
        module_path: Python module path to load (e.g., "src.ui.pages.home")
    """
    try:
        # Import the page module
        module = importlib.import_module(module_path)

        # Check if module has render function
        if not hasattr(module, 'render'):
            logger.warning(f"Module {module_path} missing render() function")
            from src.ui.components import placeholder_page
            placeholder_page.render(module_path)
            return

        # Call the render function
        module.render()

    except ImportError as e:
        logger.error(f"Failed to import module {module_path}: {e}")
        from src.ui.components import placeholder_page
        placeholder_page.render(module_path)

    except Exception as e:
        logger.error(f"Error rendering page {module_path}: {e}")
        from src.ui.components import error_page
        error_page.render(error=e, context=f"Page: {module_path}")
