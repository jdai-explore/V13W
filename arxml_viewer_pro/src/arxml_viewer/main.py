# src/arxml_viewer/main.py - COMPREHENSIVE FIX
"""
ARXML Viewer Pro - Main Entry Point - COMPREHENSIVE FIX
FIXES APPLIED:
1. Enhanced error handling for component loading
2. Better fallback mechanisms
3. Improved logging and debugging
4. Robust application startup
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# PyQt5 imports
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Application imports
from .core.application import ARXMLViewerApplication
from .config import ConfigManager
from .utils.logger import setup_logging, get_logger, log_application_start, log_application_stop
from .utils.constants import AppConstants

def setup_application() -> QApplication:
    """Enhanced Qt application setup with comprehensive error handling"""
    
    try:
        # Enhanced high DPI scaling
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication(sys.argv)
        
        # Enhanced application properties
        app.setApplicationName(AppConstants.APP_NAME)
        app.setApplicationVersion(AppConstants.APP_VERSION)
        app.setOrganizationName(AppConstants.ORGANIZATION)
        app.setOrganizationDomain("arxmlviewer.com")
        
        # Enhanced icon setup with fallback
        try:
            icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.png"
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
            else:
                print("⚠️ Application icon not found, using default")
        except Exception as e:
            print(f"⚠️ Icon setup failed: {e}")
        
        print("✅ Qt Application setup successful")
        return app
        
    except Exception as e:
        print(f"❌ Qt Application setup failed: {e}")
        # Try minimal fallback
        try:
            app = QApplication(sys.argv)
            app.setApplicationName("ARXML Viewer Pro")
            return app
        except Exception as e2:
            print(f"❌ Fallback Qt Application setup also failed: {e2}")
            raise

def parse_arguments():
    """Enhanced command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="ARXML Viewer Pro - Professional AUTOSAR ARXML file viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  arxml-viewer                    # Start with empty workspace
  arxml-viewer file.arxml        # Open specific ARXML file
  arxml-viewer --debug file.arxml # Open with debug logging
        """
    )
    
    # File argument
    parser.add_argument(
        'file',
        nargs='?',
        help='ARXML file to open on startup'
    )
    
    # Debug option
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    # Verbose option
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Version
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {AppConstants.APP_VERSION}'
    )
    
    return parser.parse_args()

def validate_file_argument(file_path: Optional[str]) -> Optional[Path]:
    """Enhanced file validation with comprehensive checks"""
    if not file_path:
        return None
    
    try:
        path = Path(file_path).resolve()
        
        # Check existence
        if not path.exists():
            print(f"❌ Error: File '{file_path}' does not exist")
            sys.exit(1)
        
        # Check if it's a file
        if not path.is_file():
            print(f"❌ Error: '{file_path}' is not a file")
            sys.exit(1)
        
        # Check file size
        file_size = path.stat().st_size
        if file_size == 0:
            print(f"⚠️ Warning: File '{file_path}' is empty")
        elif file_size > AppConstants.MAX_FILE_SIZE_MB * 1024 * 1024:
            print(f"⚠️ Warning: File '{file_path}' is very large ({file_size/1024/1024:.1f} MB)")
            print("   Parsing may take a long time")
        
        # Check extension
        if path.suffix.lower() not in AppConstants.SUPPORTED_EXTENSIONS:
            print(f"⚠️ Warning: '{file_path}' may not be a valid ARXML file")
            print(f"   Expected extensions: {AppConstants.SUPPORTED_EXTENSIONS}")
        
        # Check readability
        try:
            with open(path, 'r', encoding='utf-8') as f:
                f.read(100)  # Try to read first 100 characters
        except UnicodeDecodeError:
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    f.read(100)
                print(f"⚠️ Warning: File encoding may not be UTF-8")
            except Exception:
                print(f"❌ Error: Cannot read file '{file_path}'")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error: Cannot read file '{file_path}': {e}")
            sys.exit(1)
        
        return path
        
    except Exception as e:
        print(f"❌ Error validating file '{file_path}': {e}")
        sys.exit(1)

def setup_enhanced_logging(debug: bool = False, verbose: bool = False):
    """Setup enhanced logging with multiple levels"""
    try:
        if debug:
            log_level = "DEBUG"
            enable_console = True
            print("🔧 Debug logging enabled")
        elif verbose:
            log_level = "INFO"
            enable_console = True
            print("🔧 Verbose logging enabled")
        else:
            log_level = "INFO"
            enable_console = True
        
        # Setup logging with optional file output
        setup_logging(
            log_level=log_level,
            enable_console=enable_console,
            log_file=None  # No file logging by default
        )
        
        return True
        
    except Exception as e:
        print(f"⚠️ Logging setup failed: {e}")
        print("   Continuing with minimal logging...")
        return False

def create_config_manager() -> Optional[ConfigManager]:
    """Create configuration manager with error handling"""
    try:
        config_manager = ConfigManager()
        print("✅ Configuration manager created")
        return config_manager
    except Exception as e:
        print(f"⚠️ Configuration manager creation failed: {e}")
        print("   Continuing with default configuration...")
        try:
            # Try minimal config
            config_manager = ConfigManager()
            return config_manager
        except Exception as e2:
            print(f"❌ Minimal configuration also failed: {e2}")
            return None

def create_main_application(config_manager: Optional[ConfigManager]) -> Optional[ARXMLViewerApplication]:
    """Create main application with comprehensive error handling"""
    try:
        print("🚀 Creating main application...")
        
        # Use default config if none provided
        if config_manager is None:
            print("⚠️ Using minimal configuration")
            config_manager = ConfigManager()
        
        # Create application
        app = ARXMLViewerApplication(
            config_manager=config_manager,
            show_splash=False  # Disable splash for stability
        )
        
        print("✅ Main application created successfully")
        return app
        
    except Exception as e:
        print(f"❌ Main application creation failed: {e}")
        
        # Try to show error dialog if Qt is available
        try:
            QMessageBox.critical(
                None,
                "Application Error",
                f"Failed to create main application:\n\n{str(e)}\n\n"
                "Please check the installation and try again."
            )
        except Exception:
            pass
        
        return None

def open_startup_file(app: ARXMLViewerApplication, startup_file: Optional[Path], logger) -> bool:
    """Open startup file with enhanced error handling"""
    if not startup_file:
        return True
    
    try:
        logger.info(f"Opening startup file: {startup_file}")
        print(f"📂 Opening startup file: {startup_file.name}")
        
        success = app.open_file(str(startup_file))
        
        if success:
            print(f"✅ Successfully opened: {startup_file.name}")
            logger.info(f"Successfully opened startup file: {startup_file}")
            return True
        else:
            print(f"⚠️ Failed to open: {startup_file.name}")
            logger.warning(f"Failed to open startup file: {startup_file}")
            
            # Show user-friendly error
            try:
                QMessageBox.warning(
                    None,
                    "File Opening Warning",
                    f"Could not open the file:\n{startup_file}\n\n"
                    "The file may be corrupted or in an unsupported format.\n"
                    "You can try opening it manually from the File menu."
                )
            except Exception:
                pass
            
            return False
            
    except Exception as e:
        print(f"❌ Error opening startup file: {e}")
        logger.error(f"Error opening startup file {startup_file}: {e}")
        
        # Show detailed error to user
        try:
            QMessageBox.critical(
                None,
                "File Opening Error",
                f"An error occurred while opening the file:\n{startup_file}\n\n"
                f"Error: {str(e)}\n\n"
                "Please check that the file is a valid ARXML file."
            )
        except Exception:
            pass
        
        return False

def run_application_event_loop(qt_app: QApplication, logger) -> int:
    """Run the Qt application event loop with error handling"""
    try:
        logger.info("Starting application event loop")
        print("🖥️  Starting application...")
        
        # Run the event loop
        exit_code = qt_app.exec_()
        
        logger.info(f"Application event loop finished with exit code: {exit_code}")
        print(f"📊 Application finished with exit code: {exit_code}")
        
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user (Ctrl+C)")
        print("\n⚠️ Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application event loop failed: {e}")
        print(f"❌ Application event loop failed: {e}")
        
        # Show final error dialog
        try:
            QMessageBox.critical(
                None,
                "Application Error",
                f"The application encountered a critical error:\n\n{str(e)}\n\n"
                "The application will now exit."
            )
        except Exception:
            pass
        
        return 1

def main():
    """COMPREHENSIVE main entry point with enhanced error handling"""
    
    # Print startup banner
    print(f"🚀 {AppConstants.APP_NAME} v{AppConstants.APP_VERSION}")
    print("=" * 60)
    
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup enhanced logging
        logging_ok = setup_enhanced_logging(args.debug, args.verbose)
        
        # Get logger
        logger = get_logger(__name__)
        log_application_start()
        logger.info(f"Starting {AppConstants.APP_NAME} v{AppConstants.APP_VERSION}")
        
        # Validate startup file
        startup_file = validate_file_argument(args.file)
        if startup_file:
            logger.info(f"Startup file validated: {startup_file}")
            print(f"📁 Startup file: {startup_file.name}")
        
        # Setup Qt application
        print("\n🔧 Setting up Qt application...")
        qt_app = setup_application()
        
        # Create configuration manager
        print("🔧 Setting up configuration...")
        config_manager = create_config_manager()
        
        # Create main application
        print("🔧 Creating main application...")
        app = create_main_application(config_manager)
        
        if not app:
            print("❌ Failed to create main application")
            logger.error("Failed to create main application")
            return 1
        
        # Open startup file if provided
        if startup_file:
            file_opened = open_startup_file(app, startup_file, logger)
            if not file_opened and args.debug:
                print("🔧 Debug mode: Continuing despite file opening failure")
        
        # Show main window
        print("🖥️  Showing main application window...")
        try:
            app.show()
            logger.info("Main application window shown")
            print("✅ Application window displayed")
        except Exception as e:
            logger.error(f"Failed to show main window: {e}")
            print(f"❌ Failed to show main window: {e}")
            return 1
        
        # Run application event loop
        exit_code = run_application_event_loop(qt_app, logger)
        
        # Cleanup
        log_application_stop()
        logger.info(f"Application exiting with code: {exit_code}")
        print(f"\n👋 Application exiting with code: {exit_code}")
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Application interrupted by user")
        try:
            log_application_stop()
        except:
            pass
        return 0
        
    except SystemExit as e:
        # Handle sys.exit() calls
        try:
            log_application_stop()
        except:
            pass
        return e.code if e.code is not None else 0
        
    except Exception as e:
        print(f"\n❌ Critical application error: {e}")
        
        try:
            logger = get_logger(__name__)
            logger.critical(f"Critical application error: {e}")
            log_application_stop()
        except:
            pass
        
        # Show final error dialog if possible
        try:
            QApplication.instance()
            QMessageBox.critical(
                None,
                "Critical Error",
                f"A critical error occurred:\n\n{str(e)}\n\n"
                "Please report this issue to the developers."
            )
        except Exception:
            pass
        
        # Print stack trace in debug mode
        import traceback
        traceback.print_exc()
        
        return 1

if __name__ == "__main__":
    sys.exit(main())