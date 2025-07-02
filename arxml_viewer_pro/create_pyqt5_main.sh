#!/bin/bash
# create_pyqt5_main.sh - Replace main.py with PyQt5 version

echo "🔧 Updating main.py for PyQt5..."

# Backup the original file
if [ -f "src/arxml_viewer/main.py" ]; then
    cp "src/arxml_viewer/main.py" "src/arxml_viewer/main_pyqt6_backup.py"
    echo "✅ Backed up original main.py to main_pyqt6_backup.py"
fi

# Create the new PyQt5 main.py
cat > src/arxml_viewer/main.py << 'EOF'
# src/arxml_viewer/main.py
"""
ARXML Viewer Pro - Main Entry Point (PyQt5 Version)
Professional AUTOSAR ARXML file viewer for automotive engineers
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# PyQt5 imports (updated from PyQt6)
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QIcon

# Application imports
from .core.application import ARXMLViewerApplication
from .config import ConfigManager
from .utils.logger import setup_logging, get_logger
from .utils.constants import AppConstants

def setup_application() -> QApplication:
    """Setup Qt application with proper configuration"""
    
    # Enable high DPI scaling (PyQt5 style)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName(AppConstants.APP_NAME)
    app.setApplicationVersion(AppConstants.APP_VERSION)
    app.setOrganizationName(AppConstants.ORGANIZATION)
    app.setOrganizationDomain("arxmlviewer.com")
    
    # Set application icon
    icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ARXML Viewer Pro - Professional AUTOSAR ARXML file viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  arxml-viewer                           # Start with empty workspace
  arxml-viewer file.arxml               # Open specific ARXML file
  arxml-viewer --debug file.arxml       # Open with debug logging
  arxml-viewer --config /path/config    # Use custom config directory
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='ARXML file to open on startup'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Custom log file path'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Custom configuration directory'
    )
    
    parser.add_argument(
        '--theme',
        choices=['dark', 'light'],
        help='Override theme setting'
    )
    
    parser.add_argument(
        '--no-splash',
        action='store_true',
        help='Skip splash screen'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {AppConstants.APP_VERSION}'
    )
    
    return parser.parse_args()

def validate_file_argument(file_path: Optional[str]) -> Optional[Path]:
    """Validate and convert file argument to Path"""
    if not file_path:
        return None
    
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File '{file_path}' does not exist")
        sys.exit(1)
    
    if not path.is_file():
        print(f"Error: '{file_path}' is not a file")
        sys.exit(1)
    
    if path.suffix.lower() not in AppConstants.SUPPORTED_EXTENSIONS:
        print(f"Warning: '{file_path}' may not be a valid ARXML file")
    
    return path

def main():
    """Main entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(
        log_level=log_level,
        log_file=args.log_file,
        enable_console=True
    )
    
    logger = get_logger(__name__)
    logger.info(f"Starting {AppConstants.APP_NAME} v{AppConstants.APP_VERSION}")
    
    # Validate file argument
    startup_file = validate_file_argument(args.file)
    if startup_file:
        logger.info(f"Will open file on startup: {startup_file}")
    
    try:
        # Setup Qt application
        qt_app = setup_application()
        
        # Create configuration manager
        config_manager = ConfigManager(args.config)
        
        # Override theme if specified
        if args.theme:
            config_manager.update_config(theme=args.theme)
        
        # Create main application
        app = ARXMLViewerApplication(
            config_manager=config_manager,
            show_splash=not args.no_splash
        )
        
        # Open startup file if provided
        if startup_file:
            app.open_file(str(startup_file))
        
        # Show main window
        app.show()
        
        logger.info("Application started successfully")
        
        # Run application event loop
        exit_code = qt_app.exec_()
        
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

echo "✅ Created new PyQt5 main.py file"
echo "🚀 Ready to launch ARXML Viewer Pro with PyQt5!"