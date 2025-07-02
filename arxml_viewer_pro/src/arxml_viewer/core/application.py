# src/arxml_viewer/core/application.py
"""
Core Application Controller - Main application logic and coordination
Enhanced with Day 3 search engine, filter manager, and navigation integration
"""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QProgressDialog
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QCloseEvent

from ..parsers.arxml_parser import ARXMLParser, ARXMLParsingError
from ..models.package import Package
from ..config import ConfigManager
from ..utils.logger import get_logger
from ..utils.constants import AppConstants

# Day 3 - Import new services
from ..services.search_engine import SearchEngine, SearchScope, SearchMode
from ..services.filter_manager import FilterManager

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
    Enhanced with Day 3 search, filtering, and navigation capabilities
    """
    
    # Signals
    file_opened = pyqtSignal(str)
    file_closed = pyqtSignal()
    parsing_started = pyqtSignal(str)
    parsing_finished = pyqtSignal(list, dict)
    parsing_failed = pyqtSignal(str)
    
    # Day 3 - Enhanced signals
    search_index_built = pyqtSignal(dict)  # search statistics
    filter_applied = pyqtSignal(str, int)  # filter_name, result_count
    navigation_state_changed = pyqtSignal(dict)  # navigation state
    
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
        
        # Day 3 - Core services initialization
        self.search_engine = SearchEngine()
        self.filter_manager = FilterManager()
        
        # Day 3 - Service state
        self.search_index_ready = False
        self.active_filters: List[str] = []
        self.last_search_results = []
        
        # Create the main window
        self.main_window = self._create_main_window()
        
        # Setup connections
        self._setup_connections()
        
        # Day 3 - Setup service connections
        self._setup_service_connections()
        
        if show_splash:
            self._show_splash_screen()
    
    def _create_main_window(self):
        """Create and configure the main window"""
        try:
            from ..gui.main_window import MainWindow
            main_window = MainWindow(app_controller=self)
            
            # Connect main window signals
            main_window.open_file_requested.connect(self._on_open_file_requested)
            main_window.close_file_requested.connect(self.close_file)
            main_window.exit_requested.connect(self.quit)
            
            # Day 3 - Connect services to main window
            self._connect_services_to_main_window(main_window)
            
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
    
    def _connect_services_to_main_window(self, main_window):
        """Connect Day 3 services to main window"""
        try:
            # Connect search engine to main window's search widget
            if hasattr(main_window, 'search_engine'):
                main_window.search_engine = self.search_engine
            
            # Connect filter manager to main window
            if hasattr(main_window, 'filter_manager'):
                main_window.filter_manager = self.filter_manager
            
            # Connect navigation controller to graphics scene
            if hasattr(main_window, 'navigation_controller') and hasattr(main_window, 'graphics_scene'):
                main_window.graphics_scene.set_navigation_controller(main_window.navigation_controller)
            
            self.logger.debug("Services connected to main window successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to connect some services to main window: {e}")
    
    def _setup_connections(self):
        """Setup signal/slot connections"""
        if self.main_window:
            # Connect application signals to main window
            self.file_opened.connect(self.main_window.on_file_opened)
            self.file_closed.connect(self.main_window.on_file_closed)
            self.parsing_started.connect(self.main_window.on_parsing_started)
            self.parsing_finished.connect(self.main_window.on_parsing_finished)
            self.parsing_failed.connect(self.main_window.on_parsing_failed)
            
            # Update recent files
            recent_files = self.config_manager.config.recent_files
            self.main_window.update_recent_files(recent_files)
    
    def _setup_service_connections(self):
        """Setup Day 3 service connections"""
        # Connect service signals to application
        self.search_index_built.connect(self._on_search_index_built)
        self.filter_applied.connect(self._on_filter_applied)
        self.navigation_state_changed.connect(self._on_navigation_state_changed)
    
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
            self.logger.info("Main window displayed")
        else:
            print("❌ Cannot show main window - GUI not created")
    
    def _on_open_file_requested(self):
        """Handle open file request from main window"""
        # Get file path from main window's file dialog
        # This is handled by the main window's open_file_dialog method
        pass
    
    def open_file(self, file_path: str) -> bool:
        """
        Open and parse ARXML file - SIMPLIFIED VERSION
        
        Args:
            file_path: Path to ARXML file
            
        Returns:
            True if file opening started successfully
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
        
        try:
            print("🔧 Starting parser...")
            packages, metadata = self.parser.parse_file(file_path)
            print(f"✅ Parsed {len(packages)} packages")
            
            # Store results
            self.current_file = file_path
            self.current_packages = packages
            self.current_metadata = metadata
            
            # Build search index
            try:
                self.search_engine.build_index(packages)
                self.search_index_ready = True
                print("✅ Search index built")
            except Exception as e:
                print(f"⚠️ Search index build failed: {e}")
                self.search_index_ready = False
            
            # Notify UI
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
        """Close current file - Enhanced for Day 3"""
        if self.current_file:
            self.logger.info(f"Closing file: {self.current_file}")
            
            # Day 3 - Clear search and filter state
            self._clear_search_state()
            self._clear_filter_state()
            
            self.current_file = None
            self.current_packages = []
            self.current_metadata = {}
            self.search_index_ready = False
            
            self.file_closed.emit()
    
    def quit(self):
        """Quit application"""
        self.logger.info("Application quit requested")
        
        # Save configuration
        self._save_configuration()
        
        # Day 3 - Save service states
        self._save_service_states()
        
        # Close any open files
        self.close_file()
        
        # Close main window if it exists
        if self.main_window:
            self.main_window.close()
    
    def _save_configuration(self):
        """Save current application state to configuration"""
        # Save window geometry and state if main window exists
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
    
    def _save_service_states(self):
        """Save Day 3 service states"""
        try:
            # Save search history
            if self.search_engine:
                search_history = self.search_engine.search_history
                self.config_manager.update_config(search_history=search_history[:10])  # Save last 10
            
            # Save active filters
            if self.active_filters:
                self.config_manager.update_config(active_filters=self.active_filters)
            
            # Save filter manager state
            if self.filter_manager:
                filter_exports = self.filter_manager.export_filters_to_json()
                self.config_manager.update_config(saved_filters=filter_exports)
            
            self.logger.debug("Service states saved")
            
        except Exception as e:
            self.logger.warning(f"Failed to save service states: {e}")
    
    def _clear_search_state(self):
        """Clear search-related state"""
        self.last_search_results = []
        self.search_index_ready = False
        
        # Clear search engine state
        if self.search_engine:
            self.search_engine.index.clear()
    
    def _clear_filter_state(self):
        """Clear filter-related state"""
        self.active_filters.clear()
        
        # Clear filter manager state
        if self.filter_manager:
            self.filter_manager.clear_filters()
    
    # ===== Service Event Handlers =====
    
    def _on_search_index_built(self, search_stats: Dict[str, Any]):
        """Handle search index built"""
        self.logger.info(f"Search index built: {search_stats}")
        
        # Update main window if available
        if self.main_window and hasattr(self.main_window, '_update_search_status'):
            self.main_window._update_search_status("Search index ready")
    
    def _on_filter_applied(self, filter_name: str, result_count: int):
        """Handle filter applied"""
        self.logger.debug(f"Filter '{filter_name}' applied: {result_count} results")
        
        # Update main window status if available
        if self.main_window:
            message = f"Filter '{filter_name}' applied: {result_count} items"
            self.main_window.status_bar.showMessage(message, 3000)
    
    def _on_navigation_state_changed(self, nav_state: Dict[str, Any]):
        """Handle navigation state change"""
        self.logger.debug(f"Navigation state changed: {nav_state}")
    
    @property
    def is_file_open(self) -> bool:
        """Check if a file is currently open"""
        return self.current_file is not None
    
    @property
    def is_search_ready(self) -> bool:
        """Check if search functionality is ready"""
        return self.search_index_ready
    
    def get_current_packages(self) -> List[Package]:
        """Get currently loaded packages"""
        return self.current_packages.copy()
    
    def get_current_metadata(self) -> Dict[str, Any]:
        """Get current file metadata"""
        return self.current_metadata.copy()