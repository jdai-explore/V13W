# src/arxml_viewer/utils/logger.py
"""
Logging Configuration - Centralized logging setup
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional

# Remove default logger
logger.remove()

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """
    Setup application logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        enable_console: Whether to enable console logging
    """
    
    # Console logging
    if enable_console:
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            colorize=True
        )
    
    # File logging
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )

def get_logger(name: str):
    """Get a logger instance for a module"""
    return logger.bind(name=name)

# Default setup for development
setup_logging(
    log_level="DEBUG",
    log_file="logs/arxml_viewer.log",
    enable_console=True
)