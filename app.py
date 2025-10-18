"""
Desktop application entry point.
Starts Streamlit server and launches pywebview window.

CRITICAL FIX FOR WINDOWS PYINSTALLER:
This application uses multiprocessing.Process to start the Streamlit server.
PyInstaller has native support for multiprocessing via freeze_support().
This prevents infinite process spawning that occurs with subprocess.Popen.

Architecture: Multiprocessing with spawn context
- Streamlit runs in separate process for isolation
- PyInstaller's multiprocessing hooks handle frozen execution
- Compatible with subprocess-based tools (Playwright, Selenium, etc.)
"""
import sys
import atexit
import logging
import multiprocessing
from pathlib import Path


def _streamlit_worker(port: int):
    """
    Entry point for Streamlit worker process.

    This function runs in a separate process spawned by multiprocessing.Process.
    PyInstaller's multiprocessing hook ensures this worker uses the embedded
    Python interpreter without spawning the main .exe again.

    Args:
        port: Port number for Streamlit server
    """
    # Import Streamlit CLI here to avoid import-time side effects in main process
    from streamlit.web import cli as stcli

    # Configure Streamlit via sys.argv (simulates command-line execution)
    sys.argv = [
        "streamlit",
        "run",
        "src/ui/main_app.py",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--server.address=127.0.0.1"
    ]

    # Run Streamlit CLI (blocks until server stops)
    sys.exit(stcli.main())


def start_streamlit_server(port: int, logger):
    """
    Start Streamlit server in separate process using multiprocessing.

    This uses multiprocessing.Process instead of subprocess.Popen to avoid
    the PyInstaller sys.executable issue where sys.executable points to the
    frozen .exe instead of python.exe.

    Args:
        port: Port number to run server on
        logger: Logger instance

    Returns:
        multiprocessing.Process: The Streamlit server process
    """
    try:
        logger.info(f"Starting Streamlit server on port {port}")

        # Use spawn context explicitly for Windows compatibility
        # spawn = fresh Python interpreter, no inherited state
        ctx = multiprocessing.get_context('spawn')

        # Create process targeting the worker function
        process = ctx.Process(
            target=_streamlit_worker,
            args=(port,),
            daemon=False,  # Not daemon - we want explicit control over termination
            name="StreamlitServer"
        )

        # Start the process
        process.start()
        logger.info(f"Streamlit server process started (PID: {process.pid})")

        return process

    except Exception as e:
        logger.error(f"Failed to start Streamlit server: {e}", exc_info=True)
        raise


def cleanup_streamlit(streamlit_process, logger):
    """
    Clean up Streamlit process on exit.

    Args:
        streamlit_process: multiprocessing.Process instance
        logger: Logger instance
    """
    if streamlit_process and streamlit_process.is_alive():
        logger.info("Terminating Streamlit server...")
        streamlit_process.terminate()

        # Wait for graceful shutdown
        streamlit_process.join(timeout=5)

        # Force kill if still alive
        if streamlit_process.is_alive():
            logger.warning("Streamlit server did not terminate gracefully, killing...")
            streamlit_process.kill()
            streamlit_process.join()

        logger.info("Streamlit server stopped")


def load_window_icon(config: dict, get_icon_path, logger) -> str:
    """
    Load window icon with fallback to default.

    Args:
        config: Application configuration dictionary
        get_icon_path: Function to get icon path from config
        logger: Logger instance

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
    # Add project root to path
    sys.path.insert(0, str(Path(__file__).parent))

    # Import modules INSIDE main to avoid import-time side effects
    from src.logic.server_manager import find_free_port, wait_for_server
    from src.logic.logger import setup_logging
    from src.logic.config_loader import load_config, get_server_config, get_icon_path

    # Initialize logging in main process only
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("Streamlit Desktop App Starting...")
    logger.info("=" * 60)

    # Process reference for cleanup
    streamlit_process = None

    # Register cleanup handler
    def cleanup_handler():
        nonlocal streamlit_process
        cleanup_streamlit(streamlit_process, logger)

    atexit.register(cleanup_handler)

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

        # Start Streamlit in separate process using multiprocessing
        streamlit_process = start_streamlit_server(port, logger)

        # Wait for server to be ready
        if not wait_for_server(port, timeout=15):
            logger.error("Streamlit server failed to start within timeout")
            # Check if process crashed
            if not streamlit_process.is_alive():
                logger.error("Streamlit process terminated unexpectedly")
                logger.error(f"Process exit code: {streamlit_process.exitcode}")
            cleanup_streamlit(streamlit_process, logger)
            sys.exit(1)

        logger.info("Streamlit server is ready")

        # Launch desktop window with pywebview
        try:
            import webview

            url = f"http://127.0.0.1:{port}"
            logger.info(f"Launching desktop window: {url}")

            # Load window icon with validation and fallback
            icon_path = load_window_icon(config, get_icon_path, logger)

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
            cleanup_streamlit(streamlit_process, logger)
            sys.exit(1)

        except Exception as e:
            logger.error(f"Failed to launch desktop window: {e}")
            logger.info(f"You can access the app in your browser at: http://127.0.0.1:{port}")
            cleanup_streamlit(streamlit_process, logger)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        cleanup_streamlit(streamlit_process, logger)
        sys.exit(1)

    logger.info("Application closed")
    cleanup_streamlit(streamlit_process, logger)


if __name__ == "__main__":
    # CRITICAL: freeze_support() MUST be the first call in __main__
    # This enables PyInstaller's multiprocessing hooks to handle worker processes correctly
    # Without this, Windows will spawn infinite processes
    multiprocessing.freeze_support()
    main()
