# src/arxml_viewer/gui/main_window.py - MASSIVELY SIMPLIFIED VERSION
"""
Main Window - SIMPLIFIED VERSION - Basic 3-panel layout only
Removed all Day 5 complex features and deleted widget imports
MASSIVE SIMPLIFICATION: Basic functionality only
"""

import sys
from typing import Optional, List
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMenuBar, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QProgressBar, QLabel,
    QTreeWidget, QGraphicsView, QTextEdit, QPushButton,
    QTreeWidgetItem, QStackedWidget, QApplication, 
    QTabWidget, QFrame, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence, QFont, QPainter

from ..utils.constants import AppConstants, UIConstants
from ..utils.logger import get_logger

class MainWindow(QMainWindow):
    """
    SIMPLIFIED main window with basic three-panel layout:
    - Left: Basic component tree navigation 
    - Center: Component diagram visualization
    - Right: Properties panel
    
    REMOVED ALL DAY 5 FEATURES:
    - Breadcrumb navigation widgets
    - Export functionality 
    - Auto-layout algorithm integration
    - Enhanced layout management
    - Complex search widgets
    - Navigation history
    """
    
    # Basic signals only
    open_file_requested = pyqtSignal()
    close_file_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    
    def __init__(self, app_controller=None):
        super().__init__()
        
        self.logger = get_logger(__name__)
        self.app_controller = app_controller
        
        # Basic window state
        self.current_file: Optional[str] = None
        self.is_file_open: bool = False
        
        # Initialize UI components to None first
        self.tree_widget: Optional[QTreeWidget] = None
        self.graphics_scene = None
        self.graphics_view: Optional[QGraphicsView] = None
        self.properties_text: Optional[QTextEdit] = None
        self.properties_tabs: Optional[QTabWidget] = None
        self.main_splitter: Optional[QSplitter] = None
        self.graphics_stack: Optional[QStackedWidget] = None
        
        # Status bar components
        self.status_bar: Optional[QStatusBar] = None
        self.file_info_label: Optional[QLabel] = None
        self.progress_bar: Optional[QProgressBar] = None
        
        # Basic action references
        self.open_action: Optional[QAction] = None
        self.close_action: Optional[QAction] = None
        
        # Initialize UI in proper order
        try:
            self._setup_window()
            self._create_status_bar()
            self._create_menu_bar()
            self._create_tool_bar()
            self._create_central_widget()
            self._apply_basic_theme()
            self._show_welcome_message()
            
            self.logger.info("SIMPLIFIED MainWindow initialized successfully")
            
        except Exception as e:
            self.logger.error(f"MainWindow initialization failed: {e}")
            # Still try to show a basic window
            self.setWindowTitle("ARXML Viewer Pro - Initialization Error")
            self.resize(800, 600)
    
    def _setup_window(self):
        """Configure basic main window properties"""
        try:
            self.setWindowTitle(f"{AppConstants.APP_NAME} v{AppConstants.APP_VERSION}")
            self.setMinimumSize(*AppConstants.MIN_WINDOW_SIZE)
            self.resize(*AppConstants.DEFAULT_WINDOW_SIZE)
            
            # Center window on screen
            screen = QApplication.desktop().screenGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
        except Exception as e:
            self.logger.error(f"Window setup failed: {e}")
            # Fallback basic setup
            self.setWindowTitle("ARXML Viewer Pro")
            self.resize(1200, 800)
    
    def _create_status_bar(self):
        """Create basic status bar"""
        try:
            self.status_bar = self.statusBar()
            
            # File info label
            self.file_info_label = QLabel("No file open")
            self.status_bar.addWidget(self.file_info_label)
            
            # Progress bar (hidden by default)
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            self.progress_bar.setMaximumWidth(200)
            self.status_bar.addPermanentWidget(self.progress_bar)
            
            # Status message
            self.status_bar.showMessage("Ready")
            
        except Exception as e:
            self.logger.error(f"Status bar creation failed: {e}")
    
    def _create_menu_bar(self):
        """Create SIMPLIFIED menu bar - File menu only"""
        try:
            menubar = self.menuBar()
            
            # File Menu ONLY
            file_menu = menubar.addMenu("&File")
            
            # Open action
            self.open_action = QAction("&Open...", self)
            self.open_action.setShortcut(QKeySequence.Open)
            self.open_action.setStatusTip("Open ARXML file")
            self.open_action.triggered.connect(self.open_file_dialog)
            file_menu.addAction(self.open_action)
            
            file_menu.addSeparator()
            
            # Close action
            self.close_action = QAction("&Close", self)
            self.close_action.setShortcut(QKeySequence.Close)
            self.close_action.setStatusTip("Close current file")
            self.close_action.setEnabled(False)
            self.close_action.triggered.connect(self.close_file_requested.emit)
            file_menu.addAction(self.close_action)
            
            file_menu.addSeparator()
            
            # Exit action
            exit_action = QAction("E&xit", self)
            exit_action.setShortcut(QKeySequence.Quit)
            exit_action.setStatusTip("Exit application")
            exit_action.triggered.connect(self.exit_requested.emit)
            file_menu.addAction(exit_action)
            
        except Exception as e:
            self.logger.error(f"Menu bar creation failed: {e}")
    
    def _create_tool_bar(self):
        """Create SIMPLIFIED toolbar - Open and Close buttons only"""
        try:
            toolbar = self.addToolBar("Main")
            toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            
            # File operations only
            if self.open_action:
                toolbar.addAction(self.open_action)
            
            if self.close_action:
                toolbar.addAction(self.close_action)
            
        except Exception as e:
            self.logger.error(f"Toolbar creation failed: {e}")
    
    def _create_central_widget(self):
        """Create the SIMPLIFIED three-panel layout"""
        try:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Main horizontal splitter
            self.main_splitter = QSplitter(Qt.Horizontal)
            
            # Left panel: BASIC Tree navigation
            tree_panel = self._create_basic_tree_panel()
            self.main_splitter.addWidget(tree_panel)
            
            # Center panel: Graphics view
            graphics_panel = self._create_graphics_panel()
            self.main_splitter.addWidget(graphics_panel)
            
            # Right panel: BASIC Properties
            properties_panel = self._create_basic_properties_panel()
            self.main_splitter.addWidget(properties_panel)
            
            # Set splitter proportions
            total_width = AppConstants.DEFAULT_WINDOW_SIZE[0]
            tree_width = int(total_width * UIConstants.TREE_PANEL_WIDTH / 100)
            diagram_width = int(total_width * UIConstants.DIAGRAM_PANEL_WIDTH / 100)
            props_width = int(total_width * UIConstants.PROPERTIES_PANEL_WIDTH / 100)
            
            self.main_splitter.setSizes([tree_width, diagram_width, props_width])
            
            # Add splitter to layout
            main_layout.addWidget(self.main_splitter)
            
        except Exception as e:
            self.logger.error(f"Central widget creation failed: {e}")
    
    def _create_basic_tree_panel(self) -> QWidget:
        """Create SIMPLIFIED left tree navigation panel"""
        try:
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(5)
            
            # Panel title
            title_label = QLabel("Package Explorer")
            title_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(title_label)
            
            # BASIC tree widget - no complex enhanced version
            self.tree_widget = QTreeWidget()
            self.tree_widget.setHeaderLabels(["Components & Packages"])
            self.tree_widget.setAlternatingRowColors(True)
            layout.addWidget(self.tree_widget)
            
            return panel
            
        except Exception as e:
            self.logger.error(f"Tree panel creation failed: {e}")
            # Return minimal panel
            panel = QWidget()
            layout = QVBoxLayout(panel)
            error_label = QLabel("Tree panel failed to load")
            layout.addWidget(error_label)
            return panel
    
    def _create_graphics_panel(self) -> QWidget:
        """Create SIMPLIFIED center graphics visualization panel"""
        try:
            panel = QWidget()
            layout = QVBoxLayout(panel)
            
            # Panel title
            title_label = QLabel("Component Diagram")
            title_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(title_label)
            
            # Create BASIC graphics scene and view
            try:
                from .graphics.graphics_scene import ComponentDiagramScene
                self.graphics_scene = ComponentDiagramScene()
                self.graphics_view = QGraphicsView(self.graphics_scene)
                self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
                self.graphics_view.setRenderHint(QPainter.Antialiasing)
                
                # Connect basic scene signals if they exist
                if hasattr(self.graphics_scene, 'component_selected'):
                    self.graphics_scene.component_selected.connect(self._on_component_selected)
                
                print("✅ Graphics scene created successfully")
                
            except Exception as e:
                print(f"⚠️ Graphics scene creation failed: {e}")
                # Fallback to basic graphics view
                self.graphics_view = QGraphicsView()
                self.graphics_scene = None
            
            # Placeholder content
            placeholder_label = QLabel("Component visualization will appear here\n\nOpen an ARXML file to get started")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setStyleSheet("color: #666; font-size: 14px;")
            
            placeholder_widget = QWidget()
            placeholder_layout = QVBoxLayout(placeholder_widget)
            placeholder_layout.addWidget(placeholder_label)
            
            # Stack the placeholder and graphics view
            self.graphics_stack = QStackedWidget()
            self.graphics_stack.addWidget(placeholder_widget)  # Index 0: placeholder
            self.graphics_stack.addWidget(self.graphics_view)  # Index 1: graphics view
            
            layout.addWidget(self.graphics_stack)
            
            return panel
            
        except Exception as e:
            self.logger.error(f"Graphics panel creation failed: {e}")
            # Return minimal panel
            panel = QWidget()
            layout = QVBoxLayout(panel)
            error_label = QLabel("Graphics panel failed to load")
            layout.addWidget(error_label)
            return panel
    
    def _create_basic_properties_panel(self) -> QWidget:
        """Create SIMPLIFIED right properties panel"""
        try:
            panel = QWidget()
            layout = QVBoxLayout(panel)
            
            # Panel title
            title_label = QLabel("Properties")
            title_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(title_label)
            
            # BASIC properties display
            self.properties_text = QTextEdit()
            self.properties_text.setReadOnly(True)
            self.properties_text.setPlainText("Select a component to view its properties")
            layout.addWidget(self.properties_text)
            
            return panel
            
        except Exception as e:
            self.logger.error(f"Properties panel creation failed: {e}")
            # Return minimal panel
            panel = QWidget()
            layout = QVBoxLayout(panel)
            error_label = QLabel("Properties panel failed to load")
            layout.addWidget(error_label)
            return panel
    
    def _apply_basic_theme(self):
        """Apply SIMPLIFIED light theme styling"""
        try:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QMenuBar {
                    background-color: #ffffff;
                    color: #333333;
                    border-bottom: 1px solid #cccccc;
                    padding: 2px;
                }
                QToolBar {
                    background-color: #ffffff;
                    border-bottom: 1px solid #cccccc;
                    spacing: 3px;
                    color: #333333;
                    padding: 3px;
                }
                QStatusBar {
                    background-color: #ffffff;
                    color: #333333;
                    border-top: 1px solid #cccccc;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    selection-background-color: #e3f2fd;
                    padding: 4px;
                }
                QLabel {
                    color: #333333;
                }
                QTreeWidget {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    selection-background-color: #e3f2fd;
                    selection-color: #1976d2;
                }
                QGraphicsView {
                    background-color: #fafafa;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                }
            """)
        except Exception as e:
            self.logger.error(f"Theme application failed: {e}")
    
    def _show_welcome_message(self):
        """Show welcome message in status bar"""
        try:
            if self.status_bar:
                self.status_bar.showMessage(f"Welcome to {AppConstants.APP_NAME}! Open an ARXML file to get started.", 5000)
        except Exception as e:
            self.logger.error(f"Welcome message failed: {e}")
    
    # ==========================================
    # BASIC EVENT HANDLERS - SIMPLIFIED
    # ==========================================
    
    def on_parsing_started(self, file_path: str):
        """Handle parsing started event - SIMPLIFIED"""
        try:
            self.logger.info(f"Started parsing file: {file_path}")
            
            # Show progress bar
            if self.progress_bar:
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Update status
            if self.status_bar:
                self.status_bar.showMessage(f"Parsing {Path(file_path).name}...")
            
            # Clear previous content
            if self.tree_widget:
                self.tree_widget.clear()
            
            if self.properties_text:
                self.properties_text.setPlainText("Parsing file...")
            
            # Clear graphics scene
            if self.graphics_scene and hasattr(self.graphics_scene, 'clear_scene'):
                self.graphics_scene.clear_scene()
            
        except Exception as e:
            self.logger.error(f"Parsing started handler failed: {e}")
    
    def on_parsing_finished(self, packages, metadata):
        """Handle parsing finished event - SIMPLIFIED"""
        try:
            print(f"🔧 MainWindow: Parsing finished, {len(packages)} packages")
            
            if self.progress_bar:
                self.progress_bar.setVisible(False)
            
            # Load packages into BASIC tree widget
            if self.tree_widget and packages:
                try:
                    print("🔧 Loading packages into basic tree widget...")
                    self._load_packages_basic(packages)
                    print("✅ Basic tree widget loaded successfully")
                except Exception as e:
                    print(f"❌ Tree widget loading failed: {e}")
            
            # Load packages into graphics scene
            if self.graphics_scene and packages:
                try:
                    print("🔧 Loading packages into graphics scene...")
                    
                    # Get connections from app controller if available
                    connections = []
                    if self.app_controller and hasattr(self.app_controller, 'get_parsed_connections'):
                        try:
                            connections = self.app_controller.get_parsed_connections()
                            print(f"🔗 Retrieved {len(connections)} connections from app controller")
                        except Exception as e:
                            print(f"⚠️ Could not get connections: {e}")
                    
                    # Load with connections
                    self.graphics_scene.load_packages(packages, connections)
                    print("✅ Graphics scene loaded successfully")
                    
                    # Switch to graphics view
                    if self.graphics_stack:
                        self.graphics_stack.setCurrentIndex(1)
                        print("✅ Switched to graphics view")
                        
                except Exception as e:
                    print(f"❌ Graphics scene loading failed: {e}")
            
            # Show statistics
            stats = metadata.get('statistics', {})
            message = f"Loaded {stats.get('components_parsed', 0)} components in {stats.get('parse_time', 0):.2f}s"
            if self.status_bar:
                self.status_bar.showMessage(message, 3000)
            print(f"✅ {message}")
            
        except Exception as e:
            self.logger.error(f"Parsing finished handler failed: {e}")
            print(f"❌ Parsing finished handler failed: {e}")
    
    def on_parsing_failed(self, error_message: str):
        """Handle parsing failed event"""
        try:
            self.logger.error(f"Parsing failed: {error_message}")
            
            if self.progress_bar:
                self.progress_bar.setVisible(False)
            
            if self.status_bar:
                self.status_bar.showMessage(f"Parsing failed: {error_message}")
            
            QMessageBox.critical(self, "Parsing Failed", f"Failed to parse ARXML file:\n\n{error_message}")
            
        except Exception as e:
            self.logger.error(f"Parsing failed handler failed: {e}")
    
    def on_file_opened(self, file_path: str):
        """Handle file opened event - SIMPLIFIED"""
        try:
            self.current_file = file_path
            self.is_file_open = True
            
            # Update UI state
            if self.close_action:
                self.close_action.setEnabled(True)
            if self.file_info_label:
                self.file_info_label.setText(f"File: {Path(file_path).name}")
            self.setWindowTitle(f"{AppConstants.APP_NAME} - {Path(file_path).name}")
            
            # Switch to graphics view
            if self.graphics_stack:
                self.graphics_stack.setCurrentIndex(1)
            
            if self.status_bar:
                self.status_bar.showMessage(f"Opened: {Path(file_path).name}")
                
        except Exception as e:
            self.logger.error(f"File opened handler failed: {e}")
    
    def on_file_closed(self):
        """Handle file closed event - SIMPLIFIED"""
        try:
            self.current_file = None
            self.is_file_open = False
            
            # Update UI state
            if self.close_action:
                self.close_action.setEnabled(False)
            if self.file_info_label:
                self.file_info_label.setText("No file open")
            self.setWindowTitle(AppConstants.APP_NAME)
            
            # Switch to placeholder
            if self.graphics_stack:
                self.graphics_stack.setCurrentIndex(0)
            
            # Clear content
            if self.tree_widget:
                self.tree_widget.clear()
            if self.properties_text:
                self.properties_text.setPlainText("Select a component to view its properties")
            
            if self.graphics_scene and hasattr(self.graphics_scene, 'clear_scene'):
                self.graphics_scene.clear_scene()
            
            if self.status_bar:
                self.status_bar.showMessage("File closed")
                
        except Exception as e:
            self.logger.error(f"File closed handler failed: {e}")
    
    # ==========================================
    # BASIC UI EVENT HANDLERS
    # ==========================================
    
    def open_file_dialog(self):
        """Open file selection dialog"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open ARXML File",
                "",
                "ARXML Files (*.arxml *.xml);;All Files (*.*)"
            )
            
            if file_path:
                print(f"🔧 Selected file: {file_path}")
                if self.app_controller:
                    success = self.app_controller.open_file(file_path)
                    if not success:
                        QMessageBox.critical(self, "Error", f"Failed to open file: {file_path}")
                else:
                    print("❌ No app controller!")
        except Exception as e:
            self.logger.error(f"Open file dialog failed: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open file dialog: {e}")
    
    def _on_component_selected(self, component):
        """Handle component selection from graphics scene"""
        try:
            if component and self.properties_text:
                properties = f"Component: {component.short_name}\n"
                if hasattr(component, 'component_type'):
                    properties += f"Type: {component.component_type.value}\n"
                if hasattr(component, 'uuid'):
                    properties += f"UUID: {component.uuid}\n"
                if hasattr(component, 'port_count'):
                    properties += f"Ports: {component.port_count}\n"
                
                if hasattr(component, 'desc') and component.desc:
                    properties += f"\nDescription:\n{component.desc}\n"
                
                self.properties_text.setPlainText(properties)
        except Exception as e:
            self.logger.error(f"Component selection failed: {e}")
    
    def _load_packages_basic(self, packages):
        """Load packages into BASIC tree widget"""
        try:
            self.tree_widget.clear()
            
            for package in packages:
                # Create package item
                pkg_item = QTreeWidgetItem(self.tree_widget)
                pkg_item.setText(0, f"📁 {package.short_name}")
                
                # Add components
                for component in package.components:
                    comp_item = QTreeWidgetItem(pkg_item)
                    
                    # Component icon based on type
                    if hasattr(component, 'component_type'):
                        if component.component_type.name == 'APPLICATION':
                            icon = "📱"
                        elif component.component_type.name == 'COMPOSITION':
                            icon = "📦"
                        elif component.component_type.name == 'SERVICE':
                            icon = "🔧"
                        else:
                            icon = "⚙️"
                    else:
                        icon = "⚙️"
                    
                    comp_item.setText(0, f"{icon} {component.short_name}")
                    
                    # Add ports if they exist
                    if hasattr(component, 'all_ports'):
                        for port in component.all_ports:
                            port_item = QTreeWidgetItem(comp_item)
                            port_symbol = "🟢" if hasattr(port, 'is_provided') and port.is_provided else "🔴"
                            port_item.setText(0, f"{port_symbol} {port.short_name}")
                
                # Expand first level
                pkg_item.setExpanded(True)
            
            print(f"✅ Loaded {len(packages)} packages into basic tree")
            
        except Exception as e:
            print(f"❌ Basic tree loading failed: {e}")
    
    def update_recent_files(self, recent_files):
        """Update recent files (basic implementation)"""
        try:
            # Basic implementation - could be enhanced later
            pass
        except Exception as e:
            self.logger.error(f"Update recent files failed: {e}")
    
    # ==========================================
    # WINDOW LIFECYCLE
    # ==========================================
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            event.accept()
        except Exception as e:
            self.logger.error(f"Close event failed: {e}")
            event.accept()

# Export the MainWindow class
__all__ = ['MainWindow']