"""
Server management utilities for Streamlit desktop application.
Implements port allocation, server lifecycle, and health checking.
"""
import socket
import time
import logging
from contextlib import closing
from typing import Optional

logger = logging.getLogger(__name__)


def find_free_port(start_port: int = 8501, port_range: int = 10) -> Optional[int]:
    """
    Find an available port starting from start_port.

    Args:
        start_port: Starting port number to try
        port_range: Number of ports to attempt

    Returns:
        Available port number, or None if no ports available
    """
    for port in range(start_port, start_port + port_range):
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.bind(('127.0.0.1', port))
                logger.info(f"Found free port: {port}")
                return port
        except OSError:
            logger.debug(f"Port {port} is in use, trying next")
            continue

    logger.error(f"No free ports found in range {start_port}-{start_port + port_range}")
    return None


def wait_for_server(port: int, timeout: int = 10) -> bool:
    """
    Wait for Streamlit server to be ready by polling the port.

    Args:
        port: Port number to check
        timeout: Maximum time to wait in seconds

    Returns:
        True if server is ready, False if timeout
    """
    start_time = time.time()
    logger.info(f"Waiting for server on port {port}...")

    while time.time() - start_time < timeout:
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                if result == 0:
                    logger.info(f"Server is ready on port {port}")
                    return True
        except (ConnectionRefusedError, OSError):
            pass

        time.sleep(0.5)

    logger.error(f"Server failed to start within {timeout} seconds")
    return False


def is_port_in_use(port: int, host: str = '127.0.0.1') -> bool:
    """
    Check if a specific port is in use.

    Args:
        port: Port number to check
        host: Host address (default localhost)

    Returns:
        True if port is in use, False otherwise
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind((host, port))
            return False
        except OSError:
            return True
