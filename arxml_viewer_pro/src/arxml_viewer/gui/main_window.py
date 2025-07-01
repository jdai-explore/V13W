# src/arxml_viewer/gui/main_window_pyqt5.py
"""
Main Window - PyQt5 Version
Copy this content to src/arxml_viewer/gui/main_window.py
"""

import sys
from typing import Optional, List
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMenuBar, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QProgressBar, QLabel,
    QTreeWidget, QGraphicsView, QTextEdit, QPushButton,
    QTreeWidgetItem, QStackedWidget, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence, QFont

from .graphics.graphics_scene_pyqt5 import ComponentDiagramScene
from ..utils.constants import AppConstants, UIConstants, FileConstants
from ..utils.logger import get_logger

class MainWindow(QMainWindow):
    """
    Professional main window with three-panel layout:
    - Left: Component tree navigation
    - Center: Component diagram visualization  
    - Right: Properties panel
    """
    
    # Signals
    open_file_requested = pyqtSignal()
    close_file_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    
    def __init__(self, app_controller=None):
        super().__init__()
        
        self.logger = get_logger(__name__)
        self.app_controller = app_controller
        
        # Window state
        self.current_file: Optional[str] = None
        self.is_file_open: bool = False
        
        # Initialize UI
        self._setup_window()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_central_widget()
        self._setup_shortcuts()
        self._apply_theme()
        
        # Show welcome message
        self._show_welcome_message()
        
        self.logger.info("MainWindow initialized successfully")
    
    def _setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle(f"{AppConstants.APP_NAME} v{AppConstants.APP_VERSION}")
        self.setMinimumSize(*AppConstants.MIN_WINDOW_SIZE)
        self.resize(*AppConstants.DEFAULT_WINDOW_SIZE)
        
        # Center window on screen
        screen = QApplication.desktop().screenGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        # Open action
        from PyQt5.QtWidgets import QAction
        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.setStatusTip("Open ARXML file")
        self.open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(self.open_action)
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Files")
        self._update_recent_files_menu([])
        
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
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        # Zoom actions
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("&Reset Zoom", self)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom_action.triggered.connect(self._reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        view_menu.addSeparator()
        
        # Panel toggles
        self.toggle_tree_action = QAction("Show &Tree Panel", self)
        self.toggle_tree_action.setCheckable(True)
        self.toggle_tree_action.setChecked(True)
        self.toggle_tree_action.triggered.connect(self._toggle_tree_panel)
        view_menu.addAction(self.toggle_tree_action)
        
        self.toggle_properties_action = QAction("Show &Properties Panel", self)
        self.toggle_properties_action.setCheckable(True)
        self.toggle_properties_action.setChecked(True)
        self.toggle_properties_action.triggered.connect(self._toggle_properties_panel)
        view_menu.addAction(self.toggle_properties_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        """Create main toolbar"""
        from PyQt5.QtWidgets import QAction
        toolbar = self.addToolBar("Main")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Open button
        toolbar.addAction(self.open_action)
        toolbar.addSeparator()
        
        # Navigation buttons (will be enabled when file is open)
        self.back_action = QAction("Back", self)
        self.back_action.setEnabled(False)
        toolbar.addAction(self.back_action)
        
        self.forward_action = QAction("Forward", self)
        self.forward_action.setEnabled(False)
        toolbar.addAction(self.forward_action)
        
        toolbar.addSeparator()
        
        # Zoom controls
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        toolbar.addWidget(self.zoom_label)
    
    def _create_status_bar(self):
        """Create status bar with information panels"""
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
    
    def _create_central_widget(self):
        """Create the main three-panel layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Tree navigation
        self.tree_panel = self._create_tree_panel()
        self.main_splitter.addWidget(self.tree_panel)
        
        # Center panel: Graphics view
        self.graphics_panel = self._create_graphics_panel()
        self.main_splitter.addWidget(self.graphics_panel)
        
        # Right panel: Properties
        self.properties_panel = self._create_properties_panel()
        self.main_splitter.addWidget(self.properties_panel)
        
        # Set splitter proportions
        total_width = AppConstants.DEFAULT_WINDOW_SIZE[0]
        tree_width = int(total_width * UIConstants.TREE_PANEL_WIDTH / 100)
        diagram_width = int(total_width * UIConstants.DIAGRAM_PANEL_WIDTH / 100)
        props_width = int(total_width * UIConstants.PROPERTIES_PANEL_WIDTH / 100)
        
        self.main_splitter.setSizes([tree_width, diagram_width, props_width])
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.main_splitter)
    
    def _create_tree_panel(self) -> QWidget:
        """Create the left tree navigation panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Panel title
        title_label = QLabel("Package Explorer")
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        # Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Components")
        self.tree_widget.setAlternatingRowColors(True)
        layout.addWidget(self.tree_widget)
        
        return panel
    
    def _create_graphics_panel(self) -> QWidget:
        """Create the center graphics visualization panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Panel title and controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Component Diagram")
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Fit to window button
        fit_button = QPushButton("Fit to Window")
        fit_button.clicked.connect(self._fit_to_window)
        header_layout.addWidget(fit_button)
        
        layout.addLayout(header_layout)
        
        # Create custom graphics scene and view
        self.graphics_scene = ComponentDiagramScene()
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.graphics_view.setRenderHint(self.graphics_view.Antialiasing)
        
        # Connect scene signals
        self.graphics_scene.component_selected.connect(self._on_component_selected)
        self.graphics_scene.component_double_clicked.connect(self._on_component_double_clicked)
        
        # Placeholder content
        placeholder_label = QLabel("Component visualization will appear here\n\nOpen an ARXML file to get started")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("color: #666; font-size: 14px;")
        
        placeholder_layout = QVBoxLayout()
        placeholder_layout.addWidget(placeholder_label)
        placeholder_widget = QWidget()
        placeholder_widget.setLayout(placeholder_layout)
        
        # Stack the placeholder and graphics view
        self.graphics_stack = QStackedWidget()
        self.graphics_stack.addWidget(placeholder_widget)  # Index 0: placeholder
        self.graphics_stack.addWidget(self.graphics_view)  # Index 1: graphics view
        
        layout.addWidget(self.graphics_stack)
        
        return panel
    
    def _create_properties_panel(self) -> QWidget:
        """Create the right properties panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Panel title
        title_label = QLabel("Properties")
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        # Properties display
        self.properties_text = QTextEdit()
        self.properties_text.setReadOnly(True)
        self.properties_text.setPlainText("Select a component to view its properties")
        layout.addWidget(self.properties_text)
        
        return panel
    
    def _setup_shortcuts(self):
        """Setup additional keyboard shortcuts"""
        from PyQt5.QtWidgets import QAction
        # F5 for refresh
        refresh_action = QAction(self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self._refresh_view)
        self.addAction(refresh_action)
    
    def _apply_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #353535;
                color: #ffffff;
                border: none;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #4a4a4a;
            }
            QToolBar {
                background-color: #353535;
                border: none;
                spacing: 2px;
            }
            QStatusBar {
                background-color: #353535;
                color: #ffffff;
                border-top: 1px solid #555;
            }
            QTreeWidget {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555;
                selection-background-color: #4a90e2;
            }
            QTextEdit {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666;
                padding: 4px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QGraphicsView {
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
        """)
    
    def _show_welcome_message(self):
        """Show welcome message in status bar"""
        self.status_bar.showMessage(f"Welcome to {AppConstants.APP_NAME}! Open an ARXML file to get started.", 5000)
    
    # Event handlers and methods
    def open_file_dialog(self):
        """Open file selection dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open ARXML File",
            "",
            FileConstants.ARXML_FILTER
        )
        
        if file_path:
            self.open_file_requested.emit()
    
    def on_file_opened(self, file_path: str):
        """Handle file opened event"""
        self.current_file = file_path
        self.is_file_open = True
        
        # Update UI state
        self.close_action.setEnabled(True)
        self.file_info_label.setText(f"File: {Path(file_path).name}")
        self.setWindowTitle(f"{AppConstants.APP_NAME} - {Path(file_path).name}")
        
        # Switch to graphics view
        self.graphics_stack.setCurrentIndex(1)
        
        self.status_bar.showMessage(f"Opened: {Path(file_path).name}")
    
    def on_file_closed(self):
        """Handle file closed event"""
        self.current_file = None
        self.is_file_open = False
        
        # Update UI state
        self.close_action.setEnabled(False)
        self.file_info_label.setText("No file open")
        self.setWindowTitle(AppConstants.APP_NAME)
        
        # Switch to placeholder
        self.graphics_stack.setCurrentIndex(0)
        
        # Clear content
        self.tree_widget.clear()
        self.properties_text.setPlainText("Select a component to view its properties")
        if hasattr(self, 'graphics_scene'):
            self.graphics_scene.clear_scene()
        
        self.status_bar.showMessage("File closed")
    
    def on_parsing_started(self, file_path: str):
        """Handle parsing started event"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_bar.showMessage(f"Parsing {Path(file_path).name}...")
    
    def on_parsing_finished(self, packages, metadata):
        """Handle parsing finished event"""
        self.progress_bar.setVisible(False)
        
        # Update tree widget with packages
        self._populate_tree_widget(packages)
        
        # Load packages into graphics scene
        if hasattr(self, 'graphics_scene'):
            self.graphics_scene.load_packages(packages)
            self.graphics_scene.fit_components_in_view()
        
        # Show statistics
        stats = metadata.get('statistics', {})
        message = f"Loaded {stats.get('components_parsed', 0)} components in {stats.get('parse_time', 0):.2f}s"
        self.status_bar.showMessage(message, 3000)
    
    def on_parsing_failed(self, error_message: str):
        """Handle parsing failed event"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Parsing failed")
        
        QMessageBox.critical(
            self,
            "Parsing Error",
            f"Failed to parse ARXML file:\n\n{error_message}"
        )
    
    def _populate_tree_widget(self, packages):
        """Populate tree widget with package and component data"""
        self.tree_widget.clear()
        
        for package in packages:
            self._add_package_to_tree(package, self.tree_widget)
        
        self.tree_widget.expandAll()
    
    def _add_package_to_tree(self, package, parent):
        """Recursively add package and its contents to tree"""
        # Create package item
        package_item = QTreeWidgetItem(parent, [package.short_name or "Unnamed Package"])
        package_item.setToolTip(0, package.full_path or "")
        
        # Add components
        for component in package.components:
            comp_item = QTreeWidgetItem(package_item, [f"{component.short_name} ({component.component_type.value})"])
            comp_item.setToolTip(0, f"Type: {component.component_type.value}\nPorts: {component.port_count}")
        
        # Add sub-packages
        for sub_package in package.sub_packages:
            self._add_package_to_tree(sub_package, package_item)
    
    def update_recent_files(self, recent_files: List[str]):
        """Update recent files menu"""
        self._update_recent_files_menu(recent_files)
    
    def _update_recent_files_menu(self, recent_files: List[str]):
        """Update the recent files submenu"""
        from PyQt5.QtWidgets import QAction
        self.recent_menu.clear()
        
        if recent_files:
            for file_path in recent_files:
                action = QAction(Path(file_path).name, self)
                action.setToolTip(file_path)
                action.triggered.connect(lambda checked, path=file_path: self._open_recent_file(path))
                self.recent_menu.addAction(action)
        else:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
    
    def _open_recent_file(self, file_path: str):
        """Open a recent file"""
        if self.app_controller:
            self.app_controller.open_file(file_path)
    
    def set_theme(self, theme: str):
        """Set application theme"""
        if theme == "dark":
            self._apply_theme()
    
    def _on_component_selected(self, component):
        """Handle component selection from graphics scene"""
        if component:
            # Update properties panel
            self._show_component_properties(component)
            self.logger.debug(f"Component selected: {component.short_name}")
        else:
            self.properties_text.setPlainText("Select a component to view its properties")
    
    def _on_component_double_clicked(self, component):
        """Handle component double-click from graphics scene"""
        self.logger.info(f"Component double-clicked: {component.short_name}")
        
        if component.is_composition:
            self.status_bar.showMessage(f"Composition navigation: {component.short_name} (Coming in Day 6)", 2000)
        else:
            self.status_bar.showMessage(f"Component details: {component.short_name}", 2000)
    
    def _show_component_properties(self, component):
        """Display component properties in the properties panel"""
        properties_text = f"Component: {component.short_name}\n"
        properties_text += f"Type: {component.component_type.value}\n"
        properties_text += f"Package: {component.package_path or 'Unknown'}\n"
        properties_text += f"UUID: {component.uuid}\n\n"
        
        if component.desc:
            properties_text += f"Description:\n{component.desc}\n\n"
        
        # Port information
        properties_text += f"Ports ({component.port_count}):\n"
        
        if component.provided_ports:
            properties_text += "\nProvided Ports:\n"
            for port in component.provided_ports:
                properties_text += f"  • {port.short_name} ({port.port_type.value})\n"
                if port.interface_ref:
                    properties_text += f"    Interface: {port.interface_ref}\n"
        
        if component.required_ports:
            properties_text += "\nRequired Ports:\n"
            for port in component.required_ports:
                properties_text += f"  • {port.short_name} ({port.port_type.value})\n"
                if port.interface_ref:
                    properties_text += f"    Interface: {port.interface_ref}\n"
        
        # Composition information
        if component.is_composition:
            properties_text += f"\nComposition Details:\n"
            properties_text += f"Sub-components: {len(component.components)}\n"
            properties_text += f"Connections: {len(component.connections)}\n"
        
        self.properties_text.setPlainText(properties_text)
    
    # View control methods
    def _zoom_in(self):
        """Zoom in the graphics view"""
        if hasattr(self, 'graphics_view'):
            self.graphics_view.scale(1.2, 1.2)
            self._update_zoom_label()
    
    def _zoom_out(self):
        """Zoom out the graphics view"""
        if hasattr(self, 'graphics_view'):
            self.graphics_view.scale(0.8, 0.8)
            self._update_zoom_label()
    
    def _reset_zoom(self):
        """Reset zoom to 100%"""
        if hasattr(self, 'graphics_view'):
            self.graphics_view.resetTransform()
            self._update_zoom_label()
    
    def _fit_to_window(self):
        """Fit diagram content to window"""
        if hasattr(self, 'graphics_scene') and hasattr(self, 'graphics_view'):
            self.graphics_scene.fit_components_in_view()
            self.graphics_view.fitInView(self.graphics_scene.sceneRect(), Qt.KeepAspectRatio)
            self._update_zoom_label()
    
    def _update_zoom_label(self):
        """Update zoom percentage label"""
        if hasattr(self, 'graphics_view'):
            transform = self.graphics_view.transform()
            zoom = transform.m11() * 100
            self.zoom_label.setText(f"{zoom:.0f}%")
    
    def _toggle_tree_panel(self):
        """Toggle tree panel visibility"""
        if self.tree_panel.isVisible():
            self.tree_panel.hide()
            self.toggle_tree_action.setText("Show &Tree Panel")
        else:
            self.tree_panel.show()
            self.toggle_tree_action.setText("Hide &Tree Panel")
    
    def _toggle_properties_panel(self):
        """Toggle properties panel visibility"""
        if self.properties_panel.isVisible():
            self.properties_panel.hide()
            self.toggle_properties_action.setText("Show &Properties Panel")
        else:
            self.properties_panel.show()
            self.toggle_properties_action.setText("Hide &Properties Panel")
    
    def _refresh_view(self):
        """Refresh the current view"""
        if self.is_file_open:
            self.status_bar.showMessage("Refreshing view...", 1000)
    
    def _show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            f"About {AppConstants.APP_NAME}",
            f"""
            <h3>{AppConstants.APP_NAME} v{AppConstants.APP_VERSION}</h3>
            <p>Professional AUTOSAR ARXML file viewer for automotive engineers</p>
            <p>Built with Python and PyQt5</p>
            <p><b>Author:</b> {AppConstants.APP_AUTHOR}</p>
            <p><b>Organization:</b> {AppConstants.ORGANIZATION}</p>
            """
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_file_open:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.exit_requested.emit()
                event.accept()
            else:
                event.ignore()
        else:
            self.exit_requested.emit()
            event.accept()