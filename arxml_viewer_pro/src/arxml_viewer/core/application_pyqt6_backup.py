# src/arxml_viewer/core/application.py
"""
Core Application Controller - Main application logic and coordination
"""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QProgressDialog
from PyQt6.QtCore import QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QCloseEvent

from ..parsers.arxml_parser import ARXMLParser, ARXMLParsingError
from ..models.package import Package
from ..config import ConfigManager
from ..utils.logger import get_logger
from ..utils.constants import AppConstants

class ParseWorker(QObject):
    """Worker thread for ARXML parsing"""
    
    finished = pyqtSignal(list, dict)  # packages, metadata
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.parser = ARXMLParser()
    
    def run(self):
        """Run parsing in background thread"""
        try:
            self.progress.emit("Loading ARXML file...")
            packages, metadata = self.parser.parse_file(self.file_path)
            self.finished.emit(packages, metadata)
        except ARXMLParsingError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")

class ARXMLViewerApplication(QObject):
    """
    Main application controller
    Coordinates between GUI, parsing, and business logic
    """
    
    # Signals
    file_opened = pyqtSignal(str)
    file_closed = pyqtSignal()
    parsing_started = pyqtSignal(str)
    parsing_finished = pyqtSignal(list, dict)
    parsing_failed = pyqtSignal(str)
    
    def __init__(self, config_manager: ConfigManager, show_splash: bool = True):
        super().__init__()
        
        self.logger = get_logger(__name__)
        self.config_manager = config_manager
        
        # Application state
        self.current_file: Optional[str] = None
        self.current_packages: List[Package] = []
        self.current_metadata: Dict[str, Any] = {}
        
        # Parsing
        self.parser = ARXMLParser()
        self.parse_thread: Optional[QThread] = None
        self.parse_worker: Optional[ParseWorker] = None
        
        # Main window will be created in Day 2
        self.main_window = None
        
        # Setup connections (will be enabled when GUI is ready)
        if show_splash:
            self._show_splash_screen()
    
    def _show_splash_screen(self):
        """Show application splash screen"""
        # TODO: Implement splash screen in Day 7
        pass
    
    def show(self):
        """Show main application window"""
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
        else:
            print("GUI not yet implemented - Day 2 task")
    
    def open_file(self, file_path: str) -> bool:
        """
        Open and parse ARXML file
        
        Args:
            file_path: Path to ARXML file
            
        Returns:
            True if file opening started successfully
        """
        file_path = str(Path(file_path).resolve())
        
        # Validate file
        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            return False
        
        # Check file size
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        if file_size_mb > self.config_manager.config.max_file_size_mb:
            print(f"Warning: Large file ({file_size_mb:.1f} MB)")
        
        # Close current file if open
        if self.current_file:
            self.close_file()
        
        # Start parsing
        self._start_parsing(file_path)
        return True
    
    def _start_parsing(self, file_path: str):
        """Start background parsing of ARXML file"""
        self.logger.info(f"Starting to parse file: {file_path}")
        
        # For Day 1, do synchronous parsing
        try:
            packages, metadata = self.parser.parse_file(file_path)
            self._on_parsing_finished(packages, metadata)
            self.current_file = file_path
        except Exception as e:
            self._on_parsing_error(str(e))
    
    def _on_parsing_finished(self, packages: List[Package], metadata: Dict[str, Any]):
        """Handle successful parsing completion"""
        self.logger.info(f"Parsing completed successfully: {len(packages)} packages")
        
        self.current_packages = packages
        self.current_metadata = metadata
        
        # Add to recent files
        if self.current_file:
            self.config_manager.add_recent_file(self.current_file)
        
        # Emit signals
        self.file_opened.emit(self.current_file)
        self.parsing_finished.emit(packages, metadata)
        
        print(f"✅ Successfully parsed {len(packages)} packages")
        for pkg in packages:
            components = pkg.get_all_components(recursive=True)
            print(f"   📦 {pkg.short_name}: {len(components)} components")
    
    def _on_parsing_error(self, error_message: str):
        """Handle parsing error"""
        self.logger.error(f"Parsing failed: {error_message}")
        
        self.current_file = None
        self.current_packages = []
        self.current_metadata = {}
        
        self.parsing_failed.emit(error_message)
        print(f"❌ Parsing failed: {error_message}")
    
    def close_file(self):
        """Close current file"""
        if self.current_file:
            self.logger.info(f"Closing file: {self.current_file}")
            
            self.current_file = None
            self.current_packages = []
            self.current_metadata = {}
            
            self.file_closed.emit()
    
    def quit(self):
        """Quit application"""
        self.logger.info("Application quit requested")
        
        # Save configuration
        self._save_configuration()
        
        # Close any open files
        self.close_file()
        
        # Close main window if it exists
        if self.main_window:
            self.main_window.close()
    
    def _save_configuration(self):
        """Save current application state to configuration"""
        # Save basic configuration for now
        pass
    
    @property
    def is_file_open(self) -> bool:
        """Check if a file is currently open"""
        return self.current_file is not None
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics for current file"""
        if self.parser:
            return self.parser.get_parsing_statistics()
        return {}