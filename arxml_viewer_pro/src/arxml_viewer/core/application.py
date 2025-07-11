# src/arxml_viewer/core/application.py (SIMPLIFIED VERSION)
"""
Core Application Controller - SIMPLIFIED for stability
Removed all references to deleted modules and complex features
MAJOR SIMPLIFICATION: Direct parsing, basic signals only
"""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject

from ..parsers.arxml_parser import ARXMLParser, ARXMLParsingError
from ..models.package import Package
from ..models.connection import Connection
from ..config import ConfigManager
from ..utils.logger import get_logger
from ..utils.constants import AppConstants

class ARXMLViewerApplication(QObject):
    """
    SIMPLIFIED main application controller
    Removed all complex Day 3/5 enhancements for stability
    Focus: open_file() → parse → emit signals → done
    """
    
    # SIMPLIFIED signals - only basic ones
    file_opened = pyqtSignal(str)
    file_closed = pyqtSignal()
    parsing_started = pyqtSignal(str)
    parsing_finished = pyqtSignal(list, dict)  # packages, metadata
    parsing_failed = pyqtSignal(str)
    
    def __init__(self, config_manager: ConfigManager, show_splash: bool = True):
        super().__init__()
        
        self.logger = get_logger(__name__)
        self.config_manager = config_manager
        
        # SIMPLIFIED application state - basic tracking only
        self.current_file: Optional[str] = None
        self.current_packages: List[Package] = []
        self.current_metadata: Dict[str, Any] = {}
        self.current_connections: List[Connection] = []
        
        # Basic parser - no threading
        self.parser = ARXMLParser()
        
        # Create the main window
        self.main_window = self._create_main_window()
        
        # Basic setup
        if self.main_window:
            self._setup_basic_connections()
        
        self.logger.info("SIMPLIFIED ARXMLViewerApplication initialized")
    
    def _create_main_window(self):
        """Create main window with basic error handling"""
        try:
            from ..gui.main_window import MainWindow
            main_window = MainWindow(app_controller=self)
            
            # Connect basic signals only
            main_window.open_file_requested.connect(self._on_open_file_requested)
            main_window.close_file_requested.connect(self.close_file)
            main_window.exit_requested.connect(self.quit)
            
            self.logger.info("Main window created successfully")
            return main_window
            
        except ImportError as e:
            self.logger.error(f"Failed to import main window: {e}")
            print("❌ Failed to create main window - GUI components missing")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create main window: {e}")
            print(f"❌ Failed to create main window: {e}")
            return None
    
    def _setup_basic_connections(self):
        """Setup basic signal/slot connections"""
        try:
            if self.main_window:
                # Connect application signals to main window
                self.file_opened.connect(self.main_window.on_file_opened)
                self.file_closed.connect(self.main_window.on_file_closed)
                self.parsing_started.connect(self.main_window.on_parsing_started)
                self.parsing_finished.connect(self.main_window.on_parsing_finished)
                self.parsing_failed.connect(self.main_window.on_parsing_failed)
                
                # Update recent files
                recent_files = self.config_manager.config.recent_files
                if hasattr(self.main_window, 'update_recent_files'):
                    self.main_window.update_recent_files(recent_files)
                
                self.logger.debug("Basic connections setup complete")
        except Exception as e:
            self.logger.error(f"Basic connections setup failed: {e}")
    
    def open_file(self, file_path: str) -> bool:
        """
        SIMPLIFIED file opening - direct parsing, no threading
        Enhanced to get connections but with error handling
        """
        from pathlib import Path
        
        file_path = str(Path(file_path).resolve())
        print(f"🔧 Opening file: {file_path}")
        
        # Simple validation
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        # Close current file if open
        if self.current_file:
            self.close_file()
        
        # Emit parsing started
        self.parsing_started.emit(file_path)
        
        try:
            print("🔧 Starting parser...")
            # Direct parsing - no threading complexity
            packages, metadata = self.parser.parse_file(file_path)
            print(f"✅ Parsed {len(packages)} packages")
            
            # Store results
            self.current_file = file_path
            self.current_packages = packages
            self.current_metadata = metadata
            
            # Get parsed connections with error handling
            try:
                self.current_connections = self.parser.get_parsed_connections()
                print(f"🔗 Retrieved {len(self.current_connections)} connections")
            except Exception as e:
                print(f"⚠️ Connection retrieval failed: {e}")
                self.current_connections = []
            
            # Add to recent files
            try:
                self.config_manager.add_recent_file(file_path)
            except Exception as e:
                print(f"⚠️ Failed to add to recent files: {e}")
            
            # Emit signals
            self.file_opened.emit(file_path)
            self.parsing_finished.emit(packages, metadata)
            
            print("✅ File opened successfully")
            return True
            
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            import traceback
            traceback.print_exc()
            self.parsing_failed.emit(str(e))
            return False
    
    def close_file(self):
        """SIMPLIFIED close file"""
        if self.current_file:
            self.logger.info(f"Closing file: {self.current_file}")
            
            # Clear state
            self.current_file = None
            self.current_packages = []
            self.current_metadata = {}
            self.current_connections = []
            
            self.file_closed.emit()
    
    def get_parsed_connections(self) -> List[Connection]:
        """Get parsed connections for graphics scene"""
        return self.current_connections.copy()
    
    def get_connections_for_component(self, component_uuid: str) -> List[Connection]:
        """Get connections for specific component"""
        try:
            return [conn for conn in self.current_connections 
                    if conn.involves_component(component_uuid)]
        except Exception as e:
            self.logger.error(f"Get connections for component failed: {e}")
            return []
    
    def show(self):
        """Show main application window"""
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            self.logger.info("Main window displayed")
        else:
            print("❌ Cannot show main window - GUI not created")
    
    def quit(self):
        """SIMPLIFIED quit application"""
        self.logger.info("Application quit requested")
        
        # Save configuration
        try:
            self._save_configuration()
        except Exception as e:
            self.logger.error(f"Save configuration failed: {e}")
        
        # Close any open files
        self.close_file()
        
        # Close main window if it exists
        if self.main_window:
            self.main_window.close()
    
    def _save_configuration(self):
        """SIMPLIFIED save current application state"""
        try:
            # Save window geometry if main window exists
            if self.main_window:
                geometry = self.main_window.geometry()
                self.config_manager.update_config(
                    window_geometry={
                        'x': geometry.x(),
                        'y': geometry.y(),
                        'width': geometry.width(),
                        'height': geometry.height()
                    }
                )
        except Exception as e:
            self.logger.error(f"Save configuration failed: {e}")
    
    def _on_open_file_requested(self):
        """Handle open file request from main window"""
        # This is handled by the main window's file dialog
        pass
    
    # SIMPLIFIED properties
    @property
    def is_file_open(self) -> bool:
        """Check if a file is currently open"""
        return self.current_file is not None
    
    def get_current_packages(self) -> List[Package]:
        """Get currently loaded packages"""
        return self.current_packages.copy()
    
    def get_current_metadata(self) -> Dict[str, Any]:
        """Get current file metadata"""
        return self.current_metadata.copy()
    
    def get_application_info(self) -> Dict[str, Any]:
        """Get basic application information"""
        return {
            'version': AppConstants.APP_VERSION,
            'file_open': self.is_file_open,
            'current_file': self.current_file,
            'packages_loaded': len(self.current_packages),
            'connections_loaded': len(self.current_connections)
        }