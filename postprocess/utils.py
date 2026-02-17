"""
Utility functions for the Fandom mirror post-processing tool
"""
import shutil
import os
from pathlib import Path
from loguru import logger


def setup_logging():
    """
    Setup logging configuration
    """
    # Remove default handler
    logger.remove()
    
    # Add custom handler with rotation
    logger.add(
        "/workspace/postprocess.log",
        rotation="10 MB",
        retention="10 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        backtrace=True,
        diagnose=True
    )
    
    # Also log to console
    logger.add(
        lambda msg: print(msg),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"
    )


def create_backup(source_path, backup_path):
    """
    Create a backup of the source directory
    """
    if backup_path.exists():
        logger.warning(f"Backup path {backup_path} already exists. Skipping backup.")
        return False
    
    try:
        shutil.copytree(source_path, backup_path)
        logger.info(f"Backup created successfully at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return False


def ensure_directory(path):
    """
    Ensure a directory exists, creating it if necessary
    """
    path.mkdir(parents=True, exist_ok=True)


def get_file_extension(filepath):
    """
    Get the file extension in lowercase
    """
    return Path(filepath).suffix.lower()


def sanitize_filename(filename):
    """
    Sanitize filename by replacing invalid characters
    """
    # Replace invalid characters for most filesystems
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    return sanitized