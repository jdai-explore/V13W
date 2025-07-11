# src/arxml_viewer/utils/logger.py - FIXED VERSION with standard library fallback
"""
Logging Configuration - FIXED with standard library fallback
Falls back to Python's standard logging if loguru is not available
"""

import sys
import logging
from typing import Optional

# Try to use loguru if available, otherwise fallback to standard logging
try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
    # Remove default logger if we're using loguru
    loguru_logger.remove()
except ImportError:
    LOGURU_AVAILABLE = False
    loguru_logger = None

class LoguruFallback:
    """Fallback logger that mimics loguru interface using standard logging"""
    
    def __init__(self):
        self.logger = logging.getLogger("arxml_viewer")
        self._setup_standard_logging()
    
    def _setup_standard_logging(self):
        """Setup standard Python logging"""
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Set level
        self.logger.setLevel(logging.INFO)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stderr)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler
        self.logger.addHandler(handler)
    
    def add(self, sink, level="INFO", format=None, **kwargs):
        """Add a new log handler (simplified)"""
        if sink == sys.stderr:
            # Console logging is already set up
            pass
        elif isinstance(sink, str):
            # File logging
            try:
                file_handler = logging.FileHandler(sink)
                file_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
            except Exception:
                pass  # Silent failure
    
    def remove(self):
        """Remove all handlers"""
        self.logger.handlers.clear()
    
    def bind(self, name=None, **kwargs):
        """Bind context (simplified)"""
        if name:
            return BoundLogger(name)
        return self
    
    def info(self, message):
        self.logger.info(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)

class BoundLogger:
    """Bound logger for specific modules"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(f"arxml_viewer.{name}")
        self.logger.setLevel(logging.INFO)
        
        # Ensure it uses the parent logger's handlers
        self.logger.propagate = True
    
    def info(self, message):
        self.logger.info(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)

# Create the global logger instance
if LOGURU_AVAILABLE:
    logger = loguru_logger
else:
    logger = LoguruFallback()

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """
    Setup logging with fallback support
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        enable_console: Whether to enable console logging
    """
    
    if LOGURU_AVAILABLE:
        # Use loguru if available
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
        
        if log_file:
            try:
                from pathlib import Path
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                logger.add(
                    log_file,
                    level=log_level,
                    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}",
                )
            except Exception as e:
                print(f"Warning: Could not setup file logging: {e}")
    else:
        # Use standard logging fallback
        root_logger = logging.getLogger("arxml_viewer")
        root_logger.handlers.clear()
        
        # Set level
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        root_logger.setLevel(level_map.get(log_level.upper(), logging.INFO))
        
        if enable_console:
            # Console handler
            console_handler = logging.StreamHandler(sys.stderr)
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        if log_file:
            try:
                from pathlib import Path
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file)
                file_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                root_logger.addHandler(file_handler)
            except Exception as e:
                print(f"Warning: Could not setup file logging: {e}")

def get_logger(name: str):
    """Get a logger instance for a module"""
    if LOGURU_AVAILABLE:
        return logger.bind(name=name)
    else:
        return BoundLogger(name)

def disable_logging():
    """Disable all logging"""
    if LOGURU_AVAILABLE:
        logger.remove()
    else:
        logging.getLogger("arxml_viewer").handlers.clear()

def enable_debug_logging():
    """Enable debug logging to console"""
    if LOGURU_AVAILABLE:
        logger.remove()
    setup_logging(log_level="DEBUG", enable_console=True)

def enable_quiet_logging():
    """Enable only error logging"""
    if LOGURU_AVAILABLE:
        logger.remove()
    setup_logging(log_level="ERROR", enable_console=True)

def log_application_start():
    """Log application startup"""
    app_logger = get_logger("arxml_viewer")
    app_logger.info("ARXML Viewer Pro starting...")

def log_application_stop():
    """Log application shutdown"""
    app_logger = get_logger("arxml_viewer")
    app_logger.info("ARXML Viewer Pro shutting down...")

# Initialize logging with sensible defaults
setup_logging(
    log_level="INFO",
    enable_console=True
)

# Print status message
if LOGURU_AVAILABLE:
    print("✅ Using loguru for logging")
else:
    print("⚠️ loguru not available, using standard logging fallback")

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