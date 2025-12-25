"""
Path validation utilities for security
"""
from __future__ import annotations

import os
import re
import logging
from pathlib import Path
from typing import Iterable, List, Optional

logger = logging.getLogger(__name__)


def _normalize_extensions(exts: Iterable[str]) -> List[str]:
    """Normalize extensions to lower-case and ensure they start with a dot."""
    normalized = []
    for e in exts:
        if not e:
            continue
        e_str = str(e).strip().lower()
        if not e_str:
            continue
        if not e_str.startswith("."):
            e_str = "." + e_str
        normalized.append(e_str)
    return normalized


def is_safe_path(base_dir: str, target_path: str) -> bool:
    """
    Check if target_path is safely within base_dir (no traversal outside base).

    This function resolves paths (without requiring the target to exist) and then
    checks whether the target is either equal to the base directory or a descendant.

    Args:
        base_dir: Base directory that should contain the target
        target_path: Path to validate

    Returns:
        bool: True if path is safe (target inside base), False otherwise.
    """
    try:
        base = Path(base_dir).resolve(strict=False)
        target = Path(target_path).resolve(strict=False)

        # On some platforms, resolve(strict=False) may still raise for malformed paths,
        # so we keep this in try/except. Now check containment:
        return base == target or base in target.parents
    except Exception as e:
        logger.exception("Path validation error in is_safe_path: %s", e)
        return False


def validate_file_path(file_path: str, allowed_dir: str, allowed_extensions: Optional[Iterable[str]] = None) -> bool:
    """
    Validate file path for safety and constraints.

    Checks performed:
      - path traversal (target must be inside `allowed_dir`)
      - file existence
      - allowed extension (if provided)

    Args:
        file_path: Path to validate
        allowed_dir: Directory that must contain the file
        allowed_extensions: Iterable of allowed extensions (e.g., ['.webm', 'mp4'])

    Returns:
        bool: True if path is valid, False otherwise
    """
    try:
        # Ensure the file path is inside the allowed directory
        if not is_safe_path(allowed_dir, file_path):
            logger.warning("⚠️ Path traversal attempt blocked: %s", file_path)
            return False

        p = Path(file_path)

        # Check file exists
        if not p.exists():
            logger.warning("⚠️ File does not exist: %s", file_path)
            return False

        # If extensions provided, normalize and check
        if allowed_extensions:
            allowed = _normalize_extensions(allowed_extensions)
            ext = p.suffix.lower()
            if ext not in allowed:
                logger.warning("⚠️ Invalid file extension for %s: %s (allowed: %s)", file_path, ext, allowed)
                return False

        return True
    except Exception as e:
        logger.exception("Unexpected error validating file path %s: %s", file_path, e)
        return False


# Characters considered unsafe in filenames (control chars, path separators)
_FILENAME_BAD_CHARS_RE = re.compile(r"[\/\\\x00]")  # slash, backslash, null byte
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")  # control characters


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename to prevent security issues.

    Steps:
      - Strip surrounding whitespace
      - Replace path separators with underscore
      - Remove null bytes and control characters
      - Collapse multiple dots to a single dot (preserve extension)
      - Trim to max_length while preserving extension

    Args:
        filename: Original filename
        max_length: Maximum length

    Returns:
        str: Sanitized filename (never empty — if result would be empty returns 'file')
    """
    if not filename:
        return "file"

    name = filename.strip()

    # Replace path separators and null bytes
    name = _FILENAME_BAD_CHARS_RE.sub("_", name)

    # Remove control characters
    name = _CONTROL_CHARS_RE.sub("", name)

    # Collapse consecutive dots except the leading dot for hidden files
    if name.startswith("."):
        # preserve the leading dot (hidden file) then collapse further runs
        name = "." + re.sub(r"\.{2,}", ".", name[1:])
    else:
        name = re.sub(r"\.{2,}", ".", name)

    # Remove any remaining directory traversal tokens
    name = name.replace("..", "_")

    # If empty now, fallback
    if not name or name in {".", ".."}:
        name = "file"

    # Preserve extension when trimming
    base, ext = os.path.splitext(name)
    if len(name) > max_length:
        # Ensure ext stays intact
        keep = max_length - len(ext)
        if keep <= 0:
            # extension itself too long (unlikely) — truncate whole name
            name = (base + ext)[:max_length]
        else:
            name = base[:keep] + ext

    return name

