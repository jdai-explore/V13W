# src/arxml_viewer/main.py - SIMPLIFIED VERSION
"""
ARXML Viewer Pro - Main Entry Point - SIMPLIFIED
FIXES APPLIED per guide:
- Simplify argument parsing: Only file path argument needed
- Remove theme/splash/debug options - hardcode sensible defaults
- Simplify setup_application(): Basic PyQt5 setup only
- Remove complex validation - basic file existence check only
- Single main() function - no complex error handling
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# PyQt5 imports
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Application imports
from .core.application import ARXMLViewerApplication
from .config import ConfigManager
from .utils.logger import setup_logging, get_logger, log_application_start, log_application_stop
from .utils.constants import AppConstants

def setup_application() -> QApplication:
    """SIMPLIFIED Qt application setup - basic PyQt5 setup only"""
    
    # Basic high DPI scaling (PyQt5 style)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    
    # SIMPLIFIED application properties
    app.setApplicationName(AppConstants.APP_NAME)
    app.setApplicationVersion(AppConstants.APP_VERSION)
    app.setOrganizationName(AppConstants.ORGANIZATION)
    app.setOrganizationDomain("arxmlviewer.com")
    
    # SIMPLIFIED icon setup - no complex resource loading
    try:
        icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
    except Exception:
        # Silent failure - don't crash on missing icon
        pass
    
    return app

def parse_arguments():
    """SIMPLIFIED command line argument parsing - file path only"""
    parser = argparse.ArgumentParser(
        description="ARXML Viewer Pro - Professional AUTOSAR ARXML file viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  arxml-viewer                    # Start with empty workspace
  arxml-viewer file.arxml        # Open specific ARXML file
        """
    )
    
    # SIMPLIFIED arguments - only file path needed
    parser.add_argument(
        'file',
        nargs='?',
        help='ARXML file to open on startup'
    )
    
    # SIMPLIFIED options - only essential ones
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {AppConstants.APP_VERSION}'
    )
    
    return parser.parse_args()

def validate_file_argument(file_path: Optional[str]) -> Optional[Path]:
    """SIMPLIFIED file validation - basic existence check only"""
    if not file_path:
        return None
    
    path = Path(file_path)
    
    # SIMPLIFIED validation - basic checks only
    if not path.exists():
        print(f"Error: File '{file_path}' does not exist")
        sys.exit(1)
    
    if not path.is_file():
        print(f"Error: '{file_path}' is not a file")
        sys.exit(1)
    
    # SIMPLIFIED extension check - warning only
    if path.suffix.lower() not in AppConstants.SUPPORTED_EXTENSIONS:
        print(f"Warning: '{file_path}' may not be a valid ARXML file")
    
    return path

def main():
    """SIMPLIFIED main entry point - no complex error handling"""
    
    # Parse SIMPLIFIED command line arguments
    args = parse_arguments()
    
    # SIMPLIFIED logging setup - hardcode sensible defaults
    if args.debug:
        setup_logging(log_level="DEBUG", enable_console=True)
    else:
        setup_logging(log_level="INFO", enable_console=True)
    
    logger = get_logger(__name__)
    log_application_start()
    logger.info(f"Starting {AppConstants.APP_NAME} v{AppConstants.APP_VERSION}")
    
    # SIMPLIFIED file validation
    startup_file = validate_file_argument(args.file)
    if startup_file:
        logger.info(f"Will open file on startup: {startup_file}")
    
    try:
        # SIMPLIFIED Qt application setup
        qt_app = setup_application()
        
        # SIMPLIFIED configuration manager - no custom config directory
        config_manager = ConfigManager()
        
        # SIMPLIFIED main application - no splash screen option
        app = ARXMLViewerApplication(
            config_manager=config_manager,
            show_splash=False  # Hardcoded - no splash complexity
        )
        
        # Open startup file if provided
        if startup_file:
            success = app.open_file(str(startup_file))
            if not success:
                print(f"Warning: Failed to open file: {startup_file}")
        
        # Show main window
        app.show()
        
        logger.info("Application started successfully")
        
        # Run SIMPLIFIED application event loop
        exit_code = qt_app.exec_()
        
        log_application_stop()
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        log_application_stop()
        return 0
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        print(f"❌ Application failed to start: {e}")
        log_application_stop()
        return 1

if __name__ == "__main__":
    sys.exit(main())