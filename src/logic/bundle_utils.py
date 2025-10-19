"""
Bundle utility functions for PyInstaller frozen applications.
Provides path resolution and freeze detection for bundled executables.
"""
import sys
from pathlib import Path
from typing import Optional


def is_frozen() -> bool:
    """
    Detect if the application is running as a PyInstaller frozen executable.

    Returns:
        True if running from PyInstaller bundle, False if running from source
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_bundle_root() -> Path:
    """
    Get the root directory of the application bundle or source.

    For PyInstaller bundles:
        - Returns the directory containing the executable (dist/StreamlitApp/)
        - NOT the _MEIPASS temporary extraction directory

    For source code:
        - Returns the project root directory

    Returns:
        Absolute path to the bundle root or project root

    Example:
        PyInstaller: C:\\Users\\Name\\Desktop\\StreamlitApp\\
        Source: C:\\Projects\\Streamlit-template-desktop\\
    """
    if is_frozen():
        # Running in PyInstaller bundle
        # sys.executable = C:\\...\\StreamlitApp\\StreamlitApp.exe
        # We want the directory containing the .exe
        return Path(sys.executable).parent
    else:
        # Running from source
        # __file__ = C:\\...\\Streamlit-template-desktop\\src\\logic\\bundle_utils.py
        # We want the project root (3 levels up)
        return Path(__file__).parent.parent.parent


def get_internal_dir() -> Path:
    """
    Get the _internal directory where bundled files are located in PyInstaller.

    For PyInstaller bundles:
        - Returns dist/StreamlitApp/_internal/ where all data files are bundled

    For source code:
        - Returns project root (same as get_bundle_root())

    Returns:
        Absolute path to the _internal directory or project root
    """
    if is_frozen():
        # PyInstaller bundles files in _internal subdirectory
        return get_bundle_root() / "_internal"
    else:
        # Running from source - no _internal directory
        return get_bundle_root()


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to a bundled resource file.

    Resolves paths correctly for both PyInstaller bundles and source code.

    Args:
        relative_path: Path relative to project root (e.g., "config/app.yaml")

    Returns:
        Absolute path to the resource

    Example:
        >>> get_resource_path("config/app.yaml")
        Path("C:/Users/.../StreamlitApp/_internal/config/app.yaml")  # Frozen
        Path("C:/Projects/.../config/app.yaml")                      # Source
    """
    internal_dir = get_internal_dir()
    return (internal_dir / relative_path).resolve()


def get_script_path(script_name: str) -> Path:
    """
    Get absolute path to a Python script bundled with the application.

    Args:
        script_name: Script path relative to project root (e.g., "src/ui/main_app.py")

    Returns:
        Absolute path to the script file

    Example:
        >>> get_script_path("src/ui/main_app.py")
        Path("C:/Users/.../StreamlitApp/_internal/src/ui/main_app.py")
    """
    return get_resource_path(script_name)


def get_meipass() -> Optional[Path]:
    """
    Get the PyInstaller temporary extraction directory (_MEIPASS).

    This is where PyInstaller extracts bundled files at runtime.
    Only available when running as a frozen executable.

    Returns:
        Path to _MEIPASS if frozen, None otherwise

    Warning:
        Files in _MEIPASS are temporary and may be cleaned up on exit.
        Use get_internal_dir() for accessing bundled data files instead.
    """
    if is_frozen() and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return None


def log_environment_info(logger) -> None:
    """
    Log diagnostic information about the runtime environment.

    Useful for debugging path resolution issues in frozen executables.

    Args:
        logger: Logger instance to write diagnostic info
    """
    logger.debug("=" * 60)
    logger.debug("Bundle Environment Information")
    logger.debug("=" * 60)
    logger.debug(f"Frozen: {is_frozen()}")
    logger.debug(f"sys.executable: {sys.executable}")
    logger.debug(f"sys.argv[0]: {sys.argv[0] if sys.argv else 'N/A'}")
    logger.debug(f"__file__: {__file__}")

    logger.debug(f"Bundle root: {get_bundle_root()}")
    logger.debug(f"Internal dir: {get_internal_dir()}")

    if is_frozen():
        meipass = get_meipass()
        logger.debug(f"_MEIPASS: {meipass}")

        # Log sample resource paths
        logger.debug("Sample resource paths:")
        logger.debug(f"  config/app.yaml: {get_resource_path('config/app.yaml')}")
        logger.debug(f"  src/ui/main_app.py: {get_script_path('src/ui/main_app.py')}")
        logger.debug(f"  .streamlit/config.toml: {get_resource_path('.streamlit/config.toml')}")

    logger.debug("=" * 60)
