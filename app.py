"""
Desktop application entry point.
Starts Streamlit server and launches pywebview window.
"""
import sys
import subprocess
import atexit
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.logic.server_manager import find_free_port, wait_for_server
from src.logic.logger import setup_logging
from src.logic.config_loader import load_config, get_server_config, get_icon_path

# Setup logging
logger = setup_logging()

# Global reference to subprocess for cleanup
_streamlit_process = None


def start_streamlit_server(port: int):
    """
    Start Streamlit server in separate subprocess.

    Args:
        port: Port number to run server on

    Returns:
        subprocess.Popen: The Streamlit server process
    """
    global _streamlit_process

    try:
        # Prepare Streamlit command
        streamlit_cmd = [
            sys.executable,  # Use same Python interpreter
            "-m",
            "streamlit",
            "run",
            "src/ui/main_app.py",
            f"--server.port={port}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.address=127.0.0.1"
        ]

        logger.info(f"Starting Streamlit server on port {port}")
        logger.debug(f"Command: {' '.join(streamlit_cmd)}")

        # Start Streamlit in subprocess (not thread)
        _streamlit_process = subprocess.Popen(
            streamlit_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        return _streamlit_process

    except Exception as e:
        logger.error(f"Failed to start Streamlit server: {e}")
        raise


def cleanup_streamlit():
    """Clean up Streamlit subprocess on exit."""
    global _streamlit_process
    if _streamlit_process and _streamlit_process.poll() is None:
        logger.info("Terminating Streamlit server...")
        _streamlit_process.terminate()
        try:
            _streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Streamlit server did not terminate gracefully, killing...")
            _streamlit_process.kill()
        logger.info("Streamlit server stopped")


def load_window_icon(config: dict) -> str:
    """
    Load window icon with fallback to default.

    Args:
        config: Application configuration dictionary

    Returns:
        Path to valid icon file, or None if no valid icon found
    """
    icon_path = get_icon_path(config)
    icon_file = Path(icon_path)

    # Check if user icon exists and is valid
    if icon_file.exists() and icon_file.is_file():
        # Check file extension
        if icon_file.suffix.lower() in ['.ico', '.png', '.jpg', '.jpeg']:
            logger.info(f"Using window icon: {icon_path}")
            return str(icon_file.absolute())
        else:
            logger.warning(f"Icon file has unsupported format: {icon_path}")
    else:
        logger.warning(f"Icon file not found: {icon_path}")

    # Fallback to default icon
    default_icon = Path("assets/icon_default.png")
    if default_icon.exists() and default_icon.is_file():
        logger.info(f"Using default icon: {default_icon}")
        return str(default_icon.absolute())

    # No icon available
    logger.warning("No valid icon found, window will use system default")
    return None


def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("Streamlit Desktop App Starting...")
    logger.info("=" * 60)

    # Register cleanup handler
    atexit.register(cleanup_streamlit)

    try:
        # Load configuration
        config = load_config()
        server_config = get_server_config(config)

        # Find available port
        port = find_free_port(
            start_port=server_config.get('port_start', 8501),
            port_range=server_config.get('port_range', 10)
        )

        if port is None:
            logger.error("No available ports found. Please close other applications and try again.")
            sys.exit(1)

        # Start Streamlit in subprocess (not thread - fixes Windows signal handler issue)
        streamlit_process = start_streamlit_server(port)

        # Wait for server to be ready
        if not wait_for_server(port, timeout=15):
            logger.error("Streamlit server failed to start within timeout")
            # Check if process crashed
            if streamlit_process.poll() is not None:
                stdout, stderr = streamlit_process.communicate()
                logger.error(f"Streamlit stderr: {stderr.decode('utf-8', errors='ignore')}")
            cleanup_streamlit()
            sys.exit(1)

        logger.info("Streamlit server is ready")

        # Launch desktop window with pywebview
        try:
            import webview

            url = f"http://127.0.0.1:{port}"
            logger.info(f"Launching desktop window: {url}")

            # Load window icon with validation and fallback
            icon_path = load_window_icon(config)

            # Create window configuration
            window_params = {
                'title': config.get('app_title', 'Streamlit Desktop App'),
                'url': url,
                'width': 1280,
                'height': 800,
                'resizable': True,
                'fullscreen': False
            }

            # Add icon if available (pywebview parameter varies by platform)
            if icon_path:
                # On Windows, pywebview doesn't support icon parameter directly
                # The icon needs to be set via other means (e.g., resource hacker for compiled exe)
                # For now, we log it for future implementation
                logger.debug(f"Icon path for future implementation: {icon_path}")

            # Create and start window
            window = webview.create_window(**window_params)

            # This blocks until window is closed
            webview.start()

            logger.info("Desktop window closed")

        except ImportError:
            logger.error("pywebview is not installed. Install it with: pip install pywebview")
            logger.info(f"You can access the app in your browser at: http://127.0.0.1:{port}")
            cleanup_streamlit()
            sys.exit(1)

        except Exception as e:
            logger.error(f"Failed to launch desktop window: {e}")
            logger.info(f"You can access the app in your browser at: http://127.0.0.1:{port}")
            cleanup_streamlit()
            sys.exit(1)

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        cleanup_streamlit()
        sys.exit(1)

    logger.info("Application closed")
    cleanup_streamlit()


if __name__ == "__main__":
    main()
