"""Utility functions for the Deep Research Agent."""

from datetime import datetime
from pathlib import Path


def get_today_str() -> str:
    """Get current date in a human-readable format.
    
    Returns:
        Formatted date string (e.g., "Mon Dec 30, 2025")
    """
    dt = datetime.now()
    return f"{dt.strftime('%a %b')} {dt.day}, {dt.strftime('%Y')}"


def get_current_dir() -> Path:
    """Get the current directory of the module.
    
    Returns:
        Path object representing current directory
    """
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()