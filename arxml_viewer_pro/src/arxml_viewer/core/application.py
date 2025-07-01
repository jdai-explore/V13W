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

from ..gui.main_window import MainWindow
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
        
        # Create main window
        self.main_window = MainWindow(self)
        
        # Setup connections
        self._setup_connections()
        
        # Apply saved configuration
        self._apply_configuration()
        
        # Show splash screen if requested
        if show_splash:
            self._show_splash_screen()
    
    def _setup_connections(self):
        """Setup signal connections"""
        # File operations
        self.file_opened.connect(self.main_window.on_file_opened)
        self.file_closed.connect(self.main_window.on_file_closed)
        
        # Parsing signals
        self.parsing_started.connect(self.main_window.on_parsing_started)
        self.parsing_finished.connect(self.main_window.on_parsing_finished)
        self.parsing_failed.connect(self.main_window.on_parsing_failed)
        
        # Main window signals
        self.main_window.open_file_requested.connect(self.open_file_dialog)
        self.main_window.close_file_requested.connect(self.close_file)
        self.main_window.exit_requested.connect(self.quit)
    
    def _apply_configuration(self):
        """Apply saved configuration to application"""
        config = self.config_manager.config
        
        # Window geometry
        if config.window_geometry:
            self.main_window.restoreGeometry(
                bytes(config.window_geometry.get('geometry', b''))
            )
        
        # Theme
        self.main_window.set_theme(config.theme)
        
        # Recent files
        self.main_window.update_recent_files(config.recent_files)
    
    def _show_splash_screen(self):
        """Show application splash screen"""
        # TODO: Implement splash screen in Day 7
        pass
    
    def show(self):
        """Show main application window"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
    
    def open_file_dialog(self):
        """Open file selection dialog"""
        self.main_window.open_file_dialog()
    
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
            self.show_error(f"File not found: {file_path}")
            return False
        
        # Check file size
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        if file_size_mb > self.config_manager.config.max_file_size_mb:
            reply = QMessageBox.question(
                self.main_window,
                "Large File Warning",
                f"File size ({file_size_mb:.1f} MB) exceeds recommended limit "
                f"({self.config_manager.config.max_file_size_mb} MB).\n\n"
                "Opening large files may impact performance. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False
        
        # Close current file if open
        if self.current_file:
            self.close_file()
        
        # Start parsing in background thread
        self._start_parsing(file_path)
        return True
    
    def _start_parsing(self, file_path: str):
        """Start background parsing of ARXML file"""
        self.logger.info(f"Starting to parse file: {file_path}")
        
        # Create worker thread
        self.parse_thread = QThread()
        self.parse_worker = ParseWorker(file_path)
        self.parse_worker.moveToThread(self.parse_thread)
        
        # Connect signals
        self.parse_thread.started.connect(self.parse_worker.run)
        self.parse_worker.finished.connect(self._on_parsing_finished)
        self.parse_worker.error.connect(self._on_parsing_error)
        self.parse_worker.progress.connect(self._on_parsing_progress)
        
        # Cleanup when done
        self.parse_worker.finished.connect(self.parse_thread.quit)
        self.parse_worker.error.connect(self.parse_thread.quit)
        self.parse_thread.finished.connect(self.parse_thread.deleteLater)
        
        # Start parsing
        self.current_file = file_path
        self.parsing_started.emit(file_path)
        self.parse_thread.start()
    
    def _on_parsing_finished(self, packages: List[Package], metadata: Dict[str, Any]):
        """Handle successful parsing completion"""
        self.logger.info(f"Parsing completed successfully: {len(packages)} packages")
        
        self.current_packages = packages
        self.current_metadata = metadata
        
        # Add to recent files
        if self.current_file:
            self.config_manager.add_recent_file(self.current_file)
            self.main_window.update_recent_files(self.config_manager.config.recent_files)
        
        # Emit signals
        self.file_opened.emit(self.current_file)
        self.parsing_finished.emit(packages, metadata)
    
    def _on_parsing_error(self, error_message: str):
        """Handle parsing error"""
        self.logger.error(f"Parsing failed: {error_message}")
        
        self.current_file = None
        self.current_packages = []
        self.current_metadata = {}
        
        self.parsing_failed.emit(error_message)
        self.show_error(f"Failed to parse ARXML file:\n\n{error_message}")
    
    def _on_parsing_progress(self, message: str):
        """Handle parsing progress updates"""
        self.logger.debug(f"Parsing progress: {message}")
        # TODO: Update progress dialog in main window
    
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
        
        # Cleanup parsing thread
        if self.parse_thread and self.parse_thread.isRunning():
            self.parse_thread.quit()
            self.parse_thread.wait(3000)  # Wait max 3 seconds
        
        # Close main window
        self.main_window.close()
    
    def _save_configuration(self):
        """Save current application state to configuration"""
        # Save window geometry
        geometry = self.main_window.saveGeometry()
        self.config_manager.update_config(
            window_geometry={'geometry': geometry.data()}
        )
    
    def show_error(self, message: str, title: str = "Error"):
        """Show error message dialog"""
        QMessageBox.critical(self.main_window, title, message)
    
    def show_warning(self, message: str, title: str = "Warning"):
        """Show warning message dialog"""
        QMessageBox.warning(self.main_window, title, message)
    
    def show_info(self, message: str, title: str = "Information"):
        """Show information message dialog"""
        QMessageBox.information(self.main_window, title, message)
    
    @property
    def is_file_open(self) -> bool:
        """Check if a file is currently open"""
        return self.current_file is not None
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics for current file"""
        if self.parser:
            return self.parser.get_parsing_statistics()
        return {}