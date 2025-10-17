"""
Configuration loader with schema validation and built-in defaults.
Implements FR-017: Use built-in defaults when config is missing or malformed.
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Built-in default configuration
DEFAULT_CONFIG = {
    "app_title": "Streamlit Desktop App",
    "logo_path": "assets/logo.png",
    "icon_path": "assets/icon.png",
    "menu_items": [
        {
            "id": "home",
            "label": "Home",
            "icon": "🏠",
            "page": "src.ui.pages.home"
        },
        {
            "id": "feature1",
            "label": "Feature 1",
            "icon": "⚙️",
            "page": "src.ui.pages.feature1"
        },
        {
            "id": "feature2",
            "label": "Feature 2",
            "icon": "📊",
            "page": "src.ui.pages.feature2"
        },
        {
            "id": "about",
            "label": "About the Project",
            "icon": "ℹ️",
            "page": "src.ui.pages.about"
        }
    ],
    "theme": {
        "primaryColor": "#1f77b4",
        "backgroundColor": "#ffffff",
        "secondaryBackgroundColor": "#f0f2f6",
        "textColor": "#262730",
        "font": "sans serif"
    },
    "server": {
        "port_start": 8501,
        "port_range": 10,
        "host": "127.0.0.1"
    }
}


def load_config(config_path: str = "config/app.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file with fallback to defaults.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary with all required fields
    """
    config_file = Path(config_path)

    # Try to load config file
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)

            if user_config is None:
                logger.warning(f"Config file {config_path} is empty, using defaults")
                return DEFAULT_CONFIG.copy()

            # Merge user config with defaults
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)

            # Validate critical fields
            if not _validate_config(config):
                logger.warning(f"Config validation failed, using defaults")
                return DEFAULT_CONFIG.copy()

            logger.info(f"Configuration loaded from {config_path}")
            return config

        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse {config_path}: {e}. Using defaults")
            return DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.warning(f"Error loading {config_path}: {e}. Using defaults")
            return DEFAULT_CONFIG.copy()
    else:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return DEFAULT_CONFIG.copy()


def _validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        # Check required fields
        if "app_title" not in config or not config["app_title"]:
            return False

        if "menu_items" not in config or not isinstance(config["menu_items"], list):
            return False

        if len(config["menu_items"]) == 0:
            return False

        # Validate menu items
        menu_ids = set()
        for item in config["menu_items"]:
            if not isinstance(item, dict):
                return False
            if "id" not in item or "label" not in item or "page" not in item:
                return False
            # Check for duplicate IDs
            if item["id"] in menu_ids:
                logger.warning(f"Duplicate menu ID: {item['id']}")
                return False
            menu_ids.add(item["id"])

        return True

    except Exception as e:
        logger.error(f"Config validation error: {e}")
        return False


def get_menu_items(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract menu items from configuration."""
    return config.get("menu_items", DEFAULT_CONFIG["menu_items"])


def get_app_title(config: Dict[str, Any]) -> str:
    """Extract app title from configuration."""
    return config.get("app_title", DEFAULT_CONFIG["app_title"])


def get_logo_path(config: Dict[str, Any]) -> str:
    """Extract logo path from configuration."""
    return config.get("logo_path", DEFAULT_CONFIG["logo_path"])


def get_icon_path(config: Dict[str, Any]) -> str:
    """Extract window icon path from configuration."""
    return config.get("icon_path", DEFAULT_CONFIG["icon_path"])


def get_theme(config: Dict[str, Any]) -> Dict[str, str]:
    """Extract theme configuration."""
    return config.get("theme", DEFAULT_CONFIG["theme"])


def get_server_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract server configuration."""
    return config.get("server", DEFAULT_CONFIG["server"])
