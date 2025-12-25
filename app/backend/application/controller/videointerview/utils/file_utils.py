"""
File operation utilities
"""
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def create_session_directory(session_id, base_recordings_folder):
    try:
        # Use os.path.join instead of / operator
        session_path = os.path.join(base_recordings_folder, str(session_id))
        os.makedirs(session_path, exist_ok=True)
        return session_path
    except Exception as e:
        logger.error(f"Failed to create session directory: {e}")
        return None


def safe_open_file(filepath: str, mode: str = 'wb'):
    """
    Safely open file with error handling.
    Returns file handle or None.
    """
    try:
        return open(filepath, mode)
    except Exception as e:
        logger.error(f"Failed to open file {filepath}: {e}")
        return None


def safe_write_file(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write content to file.
    Returns True on success, False on failure.
    """
    try:
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to write file {filepath}: {e}")
        return False

