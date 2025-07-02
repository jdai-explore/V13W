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
        Open and parse ARXML file
        
        Args:
            file_path: Path to ARXML file
            
        Returns:
            True if file opening started successfully
        """
        file_path = str(Path(file_path).resolve())
        
        # Validate file
        if not Path(file_path).exists():
            error_msg = f"Error: File not found: {file_path}"
            self.logger.error(error_msg)
            if self.main_window:
                QMessageBox.critical(self.main_window, "File Error", error_msg)
            return False
        
        # Check file size
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        if file_size_mb > self.config_manager.config.max_file_size_mb:
            self.logger.warning(f"Large file ({file_size_mb:.1f} MB)")
        
        # Close current file if open
        if self.current_file:
            self.close_file()
        
        # Start parsing
        self._start_parsing(file_path)
        return True
    
    def _start_parsing(self, file_path: str):
        """Start background parsing of ARXML file"""
        self.logger.info(f"Starting to parse file: {file_path}")
        self.parsing_started.emit(file_path)
        
        # For now, do synchronous parsing (async parsing in later versions)
        try:
            packages, metadata = self.parser.parse_file(file_path)
            self._on_parsing_finished(packages, metadata)
            self.current_file = file_path
        except Exception as e:
            self._on_parsing_error(str(e))
    
    def _on_parsing_finished(self, packages: List[Package], metadata: Dict[str, Any]):
        """Handle successful parsing completion - Enhanced for Day 3"""
        self.logger.info(f"Parsing completed successfully: {len(packages)} packages")
        
        self.current_packages = packages
        self.current_metadata = metadata
        
        # Day 3 - Build search index
        try:
            self.search_engine.build_index(packages)
            self.search_index_ready = True
            
            # Emit search index built signal with statistics
            search_stats = self.search_engine.get_statistics()
            self.search_index_built.emit(search_stats)
            
            self.logger.info(f"Search index built: {search_stats.get('indexed_words', 0)} words indexed")
            
        except Exception as e:
            self.logger.error(f"Failed to build search index: {e}")
            self.search_index_ready = False
        
        # Add to recent files
        if self.current_file:
            self.config_manager.add_recent_file(self.current_file)
            
            # Update recent files in main window
            if self.main_window:
                recent_files = self.config_manager.config.recent_files
                self.main_window.update_recent_files(recent_files)
        
        # Emit signals
        self.file_opened.emit(self.current_file)
        self.parsing_finished.emit(packages, metadata)
        
        self.logger.info(f"Successfully parsed {len(packages)} packages")
        for pkg in packages:
            components = pkg.get_all_components(recursive=True)
            self.logger.debug(f"Package {pkg.short_name}: {len(components)} components")
    
    def _on_parsing_error(self, error_message: str):
        """Handle parsing error"""
        self.logger.error(f"Parsing failed: {error_message}")
        
        self.current_file = None
        self.current_packages = []
        self.current_metadata = {}
        self.search_index_ready = False
        
        self.parsing_failed.emit(error_message)
    
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
    
    def _load_service_states(self):
        """Load Day 3 service states from configuration"""
        try:
            config = self.config_manager.config
            
            # Load search history
            if hasattr(config, 'search_history') and config.search_history:
                self.search_engine.search_history = config.search_history
            
            # Load saved filters
            if hasattr(config, 'saved_filters') and config.saved_filters:
                self.filter_manager.import_filters_from_json(config.saved_filters)
            
            self.logger.debug("Service states loaded")
            
        except Exception as e:
            self.logger.warning(f"Failed to load service states: {e}")
    
    # ===== Day 3 Service Methods =====
    
    def perform_search(self, query: str, scope: SearchScope = SearchScope.ALL, 
                      mode: SearchMode = SearchMode.CONTAINS, max_results: int = 50) -> List:
        """
        Perform search using search engine
        
        Args:
            query: Search query string
            scope: Search scope
            mode: Search mode
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        if not self.search_index_ready:
            self.logger.warning("Search index not ready")
            return []
        
        try:
            results = self.search_engine.search(
                query=query,
                scope=scope,
                mode=mode,
                max_results=max_results
            )
            
            self.last_search_results = results
            self.logger.debug(f"Search performed: '{query}' -> {len(results)} results")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def apply_filter(self, filter_name: str) -> int:
        """
        Apply a filter and return number of results
        
        Args:
            filter_name: Name of filter to apply
            
        Returns:
            Number of items after filtering
        """
        if not self.current_packages:
            return 0
        
        try:
            # Apply quick filter
            self.filter_manager.apply_quick_filter(filter_name)
            
            # Get all components for filtering
            all_components = []
            for package in self.current_packages:
                all_components.extend(package.get_all_components(recursive=True))
            
            # Apply filter
            filtered_components = self.filter_manager.filter_components(all_components)
            
            # Track active filter
            if filter_name not in self.active_filters:
                self.active_filters.append(filter_name)
            
            # Emit signal
            self.filter_applied.emit(filter_name, len(filtered_components))
            
            self.logger.debug(f"Filter applied: {filter_name} -> {len(filtered_components)} results")
            
            return len(filtered_components)
            
        except Exception as e:
            self.logger.error(f"Filter application failed: {e}")
            return 0
    
    def clear_filters(self):
        """Clear all active filters"""
        try:
            self.filter_manager.clear_filters()
            self.active_filters.clear()
            
            self.logger.debug("All filters cleared")
            
        except Exception as e:
            self.logger.error(f"Failed to clear filters: {e}")
    
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
    
    def get_component_by_uuid(self, uuid: str):
        """Get component by UUID from current packages"""
        for package in self.current_packages:
            for component in package.get_all_components(recursive=True):
                if component.uuid == uuid:
                    return component
        return None
    
    def get_port_by_uuid(self, uuid: str):
        """Get port by UUID from current packages"""
        for package in self.current_packages:
            for component in package.get_all_components(recursive=True):
                for port in component.all_ports:
                    if port.uuid == uuid:
                        return port
        return None
    
    def get_package_by_uuid(self, uuid: str):
        """Get package by UUID from current packages"""
        def search_package(pkg):
            if pkg.uuid == uuid:
                return pkg
            for sub_pkg in pkg.sub_packages:
                result = search_package(sub_pkg)
                if result:
                    return result
            return None
        
        for package in self.current_packages:
            result = search_package(package)
            if result:
                return result
        return None
    
    def get_application_statistics(self) -> Dict[str, Any]:
        """Get comprehensive application statistics"""
        stats = {
            'file_info': {
                'current_file': self.current_file,
                'file_open': self.is_file_open,
                'packages_loaded': len(self.current_packages)
            },
            'parsing_stats': self.current_metadata.get('statistics', {}),
            'search_stats': self.search_engine.get_statistics() if self.search_engine else {},
            'filter_stats': {
                'active_filters': len(self.active_filters),
                'saved_filters': len(self.filter_manager.saved_filter_sets) if self.filter_manager else 0
            }
        }
        
        # Add component statistics
        if self.current_packages:
            all_components = []
            total_ports = 0
            
            for package in self.current_packages:
                components = package.get_all_components(recursive=True)
                all_components.extend(components)
                total_ports += sum(comp.port_count for comp in components)
            
            # Count by type
            component_types = {}
            for comp in all_components:
                comp_type = comp.component_type.name
                component_types[comp_type] = component_types.get(comp_type, 0) + 1
            
            stats['component_stats'] = {
                'total_components': len(all_components),
                'total_ports': total_ports,
                'component_types': component_types,
                'average_ports_per_component': total_ports / len(all_components) if all_components else 0
            }
        
        return stats
    
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
    
    # ===== Public API Methods =====
    
    def search_components(self, query: str, **kwargs) -> List:
        """Public API for component search"""
        return self.perform_search(query, scope=SearchScope.COMPONENTS, **kwargs)
    
    def search_ports(self, query: str, **kwargs) -> List:
        """Public API for port search"""
        return self.perform_search(query, scope=SearchScope.PORTS, **kwargs)
    
    def search_packages(self, query: str, **kwargs) -> List:
        """Public API for package search"""
        return self.perform_search(query, scope=SearchScope.PACKAGES, **kwargs)
    
    def filter_by_component_type(self, component_type: str) -> int:
        """Filter by component type"""
        filter_map = {
            'application': 'application',
            'composition': 'composition', 
            'service': 'service'
        }
        
        filter_key = filter_map.get(component_type.lower())
        if filter_key:
            return self.apply_filter(filter_key)
        else:
            self.logger.warning(f"Unknown component type filter: {component_type}")
            return 0
    
    def get_search_suggestions(self, partial_query: str, max_suggestions: int = 10) -> List[str]:
        """Get search suggestions"""
        if self.search_engine and self.search_index_ready:
            return self.search_engine.get_search_suggestions(partial_query, max_suggestions)
        return []
    
    def export_search_results(self, file_path: str, format: str = "json") -> bool:
        """Export last search results to file"""
        if not self.last_search_results:
            return False
        
        try:
            if format.lower() == "json":
                import json
                
                export_data = []
                for result in self.last_search_results:
                    export_data.append({
                        'item_name': result.item_name,
                        'item_type': result.item_type,
                        'match_field': result.match_field,
                        'relevance_score': result.relevance_score,
                        'parent_package': result.parent_package,
                        'item_uuid': result.item_uuid
                    })
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2)
                
                self.logger.info(f"Search results exported to {file_path}")
                return True
            
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to export search results: {e}")
            return False
    
    @property
    def is_file_open(self) -> bool:
        """Check if a file is currently open"""
        return self.current_file is not None
    
    @property
    def is_search_ready(self) -> bool:
        """Check if search functionality is ready"""
        return self.search_index_ready
    
    @property
    def has_active_filters(self) -> bool:
        """Check if there are active filters"""
        return len(self.active_filters) > 0
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics for current file"""
        if self.parser:
            return self.parser.get_parsing_statistics()
        return {}
    
    def get_current_packages(self) -> List[Package]:
        """Get currently loaded packages"""
        return self.current_packages.copy()
    
    def get_current_metadata(self) -> Dict[str, Any]:
        """Get current file metadata"""
        return self.current_metadata.copy()
    
    # ===== Initialization Enhancement =====
    
    def initialize_services(self):
        """Initialize Day 3 services with saved states"""
        self._load_service_states()
        
        # Additional service initialization can be added here
        self.logger.debug("Day 3 services initialized")
    
    def __del__(self):
        """Cleanup when application is destroyed"""
        try:
            # Save states before destruction
            self._save_service_states()
        except:
            pass