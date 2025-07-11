# src/arxml_viewer/utils/logger.py - SIMPLIFIED VERSION
"""
Logging Configuration - SIMPLIFIED loguru setup
FIXES APPLIED per guide:
- Option 2: Simplify loguru setup - console only, no file logging
- Remove complex configuration - hardcode INFO level
- Remove rotation, compression, multiple handlers
- Keep it simple and reliable
"""

import sys
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
    SIMPLIFIED logging setup - console only by default
    Hardcoded simple configuration for reliability
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR) - defaults to INFO
        log_file: Optional log file path (simplified, no rotation)
        enable_console: Whether to enable console logging (default True)
    """
    
    # SIMPLIFIED console logging - always enabled by default
    if enable_console:
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan> | "
                   "<level>{message}</level>",
            colorize=True
        )
    
    # SIMPLIFIED file logging - basic only, no rotation or compression
    if log_file:
        try:
            from pathlib import Path
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.add(
                log_file,
                level=log_level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}",
                # REMOVED: rotation, retention, compression - keep it simple
            )
        except Exception as e:
            # Silent failure for file logging - don't crash the app
            print(f"Warning: Could not setup file logging: {e}")

def get_logger(name: str):
    """Get a logger instance for a module - SIMPLIFIED"""
    return logger.bind(name=name)

def disable_logging():
    """Disable all logging - utility function"""
    logger.remove()

def enable_debug_logging():
    """Enable debug logging to console - utility function"""
    logger.remove()
    setup_logging(log_level="DEBUG", enable_console=True)

def enable_quiet_logging():
    """Enable only error logging - utility function"""
    logger.remove()
    setup_logging(log_level="ERROR", enable_console=True)

def log_application_start():
    """Log application startup - utility function"""
    app_logger = get_logger("arxml_viewer")
    app_logger.info("ARXML Viewer Pro starting...")

def log_application_stop():
    """Log application shutdown - utility function"""
    app_logger = get_logger("arxml_viewer")
    app_logger.info("ARXML Viewer Pro shutting down...")

# SIMPLIFIED default setup for the application
# Hardcoded INFO level, console only - no complex configuration
setup_logging(
    log_level="INFO",
    enable_console=True
)

# Export essential functions
__all__ = [
    'setup_logging', 
    'get_logger', 
    'disable_logging',
    'enable_debug_logging',
    'enable_quiet_logging',
    'log_application_start',
    'log_application_stop'
]