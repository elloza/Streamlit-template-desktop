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
from typing import Optional


def _streamlit_worker(port: int, error_queue=None):
    """
    Entry point for Streamlit worker process.

    This function runs in a separate process spawned by multiprocessing.Process.
    PyInstaller's multiprocessing hook ensures this worker uses the embedded
    Python interpreter without spawning the main .exe again.

    Args:
        port: Port number for Streamlit server
        error_queue: Multiprocessing queue for error communication (optional)
    """
    try:
        # Import dependencies inside worker to avoid import-time side effects
        import os
        from streamlit.web import cli as stcli
        from src.logic.bundle_utils import (
            is_frozen, get_bundle_root, get_script_path, log_environment_info, get_internal_dir
        )
        from src.logic.logger import setup_worker_logging

        # Setup worker-specific logging
        worker_logger = setup_worker_logging()
        worker_logger.info(f"Worker process starting for port {port}")

        # Log environment information for debugging
        log_environment_info(worker_logger)

        # Get absolute path to main_app.py
        # CRITICAL FIX: Use absolute path instead of relative "src/ui/main_app.py"
        # The worker process may have a different working directory than the main process
        main_app_path = get_script_path("src/ui/main_app.py")
        worker_logger.info(f"Resolved main_app.py path: {main_app_path}")

        # Verify the file exists
        if not main_app_path.exists():
            error_msg = f"CRITICAL ERROR: main_app.py not found at {main_app_path}"
            worker_logger.error(error_msg)
            if error_queue:
                error_queue.put(error_msg)
            sys.exit(2)

        # Set working directory to bundle root so config/ and assets/ can be found
        # This ensures Streamlit can find config/app.yaml and other resources
        bundle_root = get_bundle_root()
        os.chdir(bundle_root)
        worker_logger.info(f"Changed working directory to: {bundle_root}")

        # CRITICAL FIX: Copy .streamlit/config.toml from _internal to bundle root
        # Streamlit looks for .streamlit/ in the current working directory
        # In PyInstaller, the config is bundled in _internal/.streamlit/
        # We need to copy it to the bundle root so Streamlit can find it
        import shutil
        streamlit_config_src = get_internal_dir() / ".streamlit"
        streamlit_config_dst = bundle_root / ".streamlit"

        if streamlit_config_src.exists() and not streamlit_config_dst.exists():
            worker_logger.info(f"Copying .streamlit config from {streamlit_config_src} to {streamlit_config_dst}")
            shutil.copytree(streamlit_config_src, streamlit_config_dst)
        elif streamlit_config_dst.exists():
            worker_logger.info(f"Streamlit config already exists at {streamlit_config_dst}")
        else:
            worker_logger.warning(f"Streamlit config not found at {streamlit_config_src}")

        # Configure Streamlit via sys.argv (simulates command-line execution)
        sys.argv = [
            "streamlit",
            "run",
            str(main_app_path.absolute()),  # ← ABSOLUTE PATH!
            f"--server.port={port}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.address=127.0.0.1"
        ]

        worker_logger.info(f"Starting Streamlit CLI with args: {sys.argv}")

        # Run Streamlit CLI (blocks until server stops)
        sys.exit(stcli.main())

    except Exception as e:
        # Capture any error and send to parent process
        import traceback
        error_msg = f"Worker process exception: {e}\n{traceback.format_exc()}"

        # Try to log to worker log file
        try:
            from src.logic.logger import setup_worker_logging
            worker_logger = setup_worker_logging()
            worker_logger.error(error_msg)
        except:
            pass  # If logging fails, still try to send error to queue

        # Send error to parent process
        if error_queue:
            error_queue.put(error_msg)

        sys.exit(2)


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
        tuple: (multiprocessing.Process, multiprocessing.Queue) - Process and error queue
    """
    try:
        logger.info(f"Starting Streamlit server on port {port}")

        # Use spawn context explicitly for Windows compatibility
        # spawn = fresh Python interpreter, no inherited state
        ctx = multiprocessing.get_context('spawn')

        # Create error queue for worker communication
        error_queue = ctx.Queue()

        # Create process targeting the worker function
        process = ctx.Process(
            target=_streamlit_worker,
            args=(port, error_queue),  # Pass error queue to worker
            daemon=False,  # Not daemon - we want explicit control over termination
            name="StreamlitServer"
        )

        # Start the process
        process.start()
        logger.info(f"Streamlit server process started (PID: {process.pid})")

        # Check for immediate errors (non-blocking)
        import queue
        try:
            error_msg = error_queue.get(block=False)
            logger.error(f"Worker startup error: {error_msg}")
        except queue.Empty:
            pass  # No immediate error

        return process, error_queue

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


def load_window_icon(config: dict, get_icon_path, logger) -> Optional[str]:
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
        streamlit_process, error_queue = start_streamlit_server(port, logger)

        # Wait for server to be ready (increased timeout for slow machines)
        if not wait_for_server(port, timeout=30):
            logger.error("Streamlit server failed to start within timeout")

            # Check error queue for worker errors
            import queue
            try:
                error_msg = error_queue.get(block=False)
                logger.error(f"Worker error message:\n{error_msg}")
            except queue.Empty:
                pass  # No error in queue

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
