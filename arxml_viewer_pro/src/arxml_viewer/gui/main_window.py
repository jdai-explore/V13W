# src/arxml_viewer/gui/main_window.py
"""
Main Window - PyQt5 Version with Day 3 Tree Navigation & Search Integration
Professional main window with enhanced three-panel layout for ARXML Viewer Pro
"""

import sys
from typing import Optional, List
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMenuBar, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QProgressBar, QLabel,
    QTreeWidget, QGraphicsView, QTextEdit, QPushButton,
    QTreeWidgetItem, QStackedWidget, QApplication, QDockWidget,
    QTabWidget, QFrame, QAction, QActionGroup, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence, QFont, QPainter

from .graphics.graphics_scene import ComponentDiagramScene
from .widgets.tree_widget import EnhancedTreeWidget, TreeSearchWidget
from .widgets.search_widget import AdvancedSearchWidget, CompactSearchWidget
from .controllers.navigation_controller import NavigationController
from .layout.layout_manager import LayoutManager
from ..services.search_engine import SearchEngine
from ..services.filter_manager import FilterManager
from ..utils.constants import AppConstants, UIConstants, FileConstants
from ..utils.logger import get_logger

class MainWindow(QMainWindow):
    """
    Professional main window with enhanced three-panel layout:
    - Left: Enhanced component tree navigation with search
    - Center: Component diagram visualization  
    - Right: Properties panel
    
    Day 3 additions:
    - Enhanced tree widget with search and filtering
    - Advanced search functionality
    - Navigation controller for tree-diagram sync
    - Layout manager for panel management
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
        
        # Day 3 - Core services
        self.search_engine = SearchEngine()
        self.filter_manager = FilterManager()
        
        # Day 3 - Controllers and managers
        self.navigation_controller = NavigationController()
        self.layout_manager = LayoutManager(self)
        
        # UI Components (will be created in _create_central_widget)
        self.enhanced_tree_widget: Optional[EnhancedTreeWidget] = None
        self.graphics_scene: Optional[ComponentDiagramScene] = None
        self.graphics_view: Optional[QGraphicsView] = None
        self.properties_text: Optional[QTextEdit] = None
        self.main_splitter: Optional[QSplitter] = None
        self.tree_panel: Optional[QWidget] = None
        self.graphics_panel: Optional[QWidget] = None
        self.properties_panel: Optional[QWidget] = None
        
        # Initialize UI
        self._setup_window()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_central_widget()
        self._setup_shortcuts()
        self._apply_theme()
        
        # Day 3 - Setup navigation and layout
        self._setup_navigation_controller()
        self._setup_layout_manager()
        
        # Show welcome message
        self._show_welcome_message()
        
        self.logger.info("MainWindow initialized successfully with Day 3 enhancements")
    
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
        
        # View Menu - Enhanced for Day 3
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
        
        view_menu.addSeparator()
        
        # Day 3 - Layout presets
        layout_submenu = view_menu.addMenu("&Layout")
        self._create_layout_menu(layout_submenu)
        
        # Day 3 - Search menu
        search_menu = menubar.addMenu("&Search")
        
        # Search actions
        find_action = QAction("&Find...", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.setStatusTip("Open search panel")
        find_action.triggered.connect(self._show_search_panel)
        search_menu.addAction(find_action)
        
        find_next_action = QAction("Find &Next", self)
        find_next_action.setShortcut(QKeySequence.FindNext)
        find_next_action.triggered.connect(self._find_next)
        search_menu.addAction(find_next_action)
        
        search_menu.addSeparator()
        
        clear_search_action = QAction("&Clear Search", self)
        clear_search_action.setShortcut(QKeySequence("Ctrl+Shift+F"))
        clear_search_action.triggered.connect(self._clear_search)
        search_menu.addAction(clear_search_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
    def _create_layout_menu(self, layout_menu):
        """Create layout presets menu"""
        # Create action group for exclusive selection
        self.layout_action_group = QActionGroup(self)
        
        # Get available layouts from layout manager
        layout_names = self.layout_manager.get_available_layouts()
        
        for layout_name in layout_names:
            action = QAction(layout_name, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, name=layout_name: self._apply_layout_preset(name))
            
            self.layout_action_group.addAction(action)
            layout_menu.addAction(action)
            
            # Check current layout
            if layout_name == self.layout_manager.get_current_layout_name():
                action.setChecked(True)
        
        layout_menu.addSeparator()
        
        # Save custom layout
        save_layout_action = QAction("Save Current Layout...", self)
        save_layout_action.triggered.connect(self._save_custom_layout)
        layout_menu.addAction(save_layout_action)
    
    def _create_tool_bar(self):
        """Create main toolbar with Day 3 enhancements"""
        toolbar = self.addToolBar("Main")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # File operations
        toolbar.addAction(self.open_action)
        toolbar.addSeparator()
        
        # Navigation buttons (enhanced for Day 3)
        self.back_action = QAction("Back", self)
        self.back_action.setEnabled(False)
        self.back_action.triggered.connect(self._navigate_back)
        toolbar.addAction(self.back_action)
        
        self.forward_action = QAction("Forward", self)
        self.forward_action.setEnabled(False)
        self.forward_action.triggered.connect(self._navigate_forward)
        toolbar.addAction(self.forward_action)
        
        toolbar.addSeparator()
        
        # Day 3 - Compact search widget in toolbar
        self.compact_search = CompactSearchWidget()
        self.compact_search.search_requested.connect(self._perform_quick_search)
        self.compact_search.advanced_search_requested.connect(self._show_advanced_search)
        toolbar.addWidget(self.compact_search)
        
        toolbar.addSeparator()
        
        # Zoom controls
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        toolbar.addWidget(self.zoom_label)
    
    def _create_status_bar(self):
        """Create status bar with Day 3 enhancements"""
        self.status_bar = self.statusBar()
        
        # File info label
        self.file_info_label = QLabel("No file open")
        self.status_bar.addWidget(self.file_info_label)
        
        # Day 3 - Search info label
        self.search_info_label = QLabel("")
        self.status_bar.addWidget(self.search_info_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Day 3 - Navigation info
        self.navigation_info_label = QLabel("")
        self.status_bar.addPermanentWidget(self.navigation_info_label)
        
        # Status message
        self.status_bar.showMessage("Ready")
    
    def _create_central_widget(self):
        """Create the enhanced three-panel layout with Day 3 features"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Enhanced Tree navigation with search
        self.tree_panel = self._create_enhanced_tree_panel()
        self.main_splitter.addWidget(self.tree_panel)
        
        # Center panel: Graphics view
        self.graphics_panel = self._create_graphics_panel()
        self.main_splitter.addWidget(self.graphics_panel)
        
        # Right panel: Enhanced Properties with tabs
        self.properties_panel = self._create_enhanced_properties_panel()
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
        
        # Day 3 - Create dockable advanced search widget
        self._create_search_dock()
    
    def _create_enhanced_tree_panel(self) -> QWidget:
        """Create the enhanced left tree navigation panel with Day 3 features"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Panel title with controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Package Explorer")
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Expand/collapse all buttons
        expand_all_btn = QPushButton("⊞")
        expand_all_btn.setMaximumWidth(25)
        expand_all_btn.setToolTip("Expand All")
        expand_all_btn.clicked.connect(self._expand_all_tree_items)
        header_layout.addWidget(expand_all_btn)
        
        collapse_all_btn = QPushButton("⊟")
        collapse_all_btn.setMaximumWidth(25)
        collapse_all_btn.setToolTip("Collapse All")
        collapse_all_btn.clicked.connect(self._collapse_all_tree_items)
        header_layout.addWidget(collapse_all_btn)
        
        layout.addLayout(header_layout)
        
        # Day 3 - Tree search widget
        self.tree_search_widget = TreeSearchWidget()
        self.tree_search_widget.search_changed.connect(self._on_tree_search_changed)
        self.tree_search_widget.filter_changed.connect(self._on_tree_filter_changed)
        self.tree_search_widget.clear_requested.connect(self._on_tree_search_cleared)
        layout.addWidget(self.tree_search_widget)
        
        # Day 3 - Enhanced tree widget
        self.enhanced_tree_widget = EnhancedTreeWidget()
        self.enhanced_tree_widget.item_selected.connect(self._on_tree_item_selected)
        self.enhanced_tree_widget.item_activated.connect(self._on_tree_item_activated)
        layout.addWidget(self.enhanced_tree_widget)
        
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
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        
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
    
    def _create_enhanced_properties_panel(self) -> QWidget:
        """Create the enhanced right properties panel with Day 3 features"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Panel title
        title_label = QLabel("Properties")
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        # Day 3 - Tabbed properties display
        self.properties_tabs = QTabWidget()
        
        # Properties tab
        self.properties_text = QTextEdit()
        self.properties_text.setReadOnly(True)
        self.properties_text.setPlainText("Select a component to view its properties")
        self.properties_tabs.addTab(self.properties_text, "Properties")
        
        # Search results tab (will be populated when search is performed)
        self.search_results_text = QTextEdit()
        self.search_results_text.setReadOnly(True)
        self.properties_tabs.addTab(self.search_results_text, "Search Results")
        
        # Statistics tab
        self.statistics_text = QTextEdit()
        self.statistics_text.setReadOnly(True)
        self.properties_tabs.addTab(self.statistics_text, "Statistics")
        
        layout.addWidget(self.properties_tabs)
        
        return panel
    
    def _create_search_dock(self):
        """Create dockable advanced search widget"""
        self.search_dock = QDockWidget("Advanced Search", self)
        self.search_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        
        # Create advanced search widget
        self.advanced_search_widget = AdvancedSearchWidget(self.search_engine)
        self.advanced_search_widget.search_started.connect(self._on_search_started)
        self.advanced_search_widget.search_completed.connect(self._on_search_completed)
        self.advanced_search_widget.result_selected.connect(self._on_search_result_selected)
        self.advanced_search_widget.result_activated.connect(self._on_search_result_activated)
        
        self.search_dock.setWidget(self.advanced_search_widget)
        
        # Initially hidden
        self.search_dock.setVisible(False)
        
        # Add to main window
        self.addDockWidget(Qt.BottomDockWidgetArea, self.search_dock)
    
    def _setup_navigation_controller(self):
        """Setup navigation controller with Day 3 components"""
        # Set up navigation controller with our widgets
        self.navigation_controller.set_tree_widget(self.enhanced_tree_widget)
        self.navigation_controller.set_graphics_scene(self.graphics_scene)
        
        # Connect navigation signals
        self.navigation_controller.component_selection_changed.connect(self._on_navigation_component_selected)
        self.navigation_controller.navigation_requested.connect(self._on_navigation_requested)
        self.navigation_controller.focus_requested.connect(self._on_focus_requested)
        
        self.logger.debug("Navigation controller setup complete")
    
    def _setup_layout_manager(self):
        """Setup layout manager with Day 3 components"""
        # Setup layout manager with our panels
        self.layout_manager.setup_ui_components(
            main_splitter=self.main_splitter,
            tree_panel=self.tree_panel,
            diagram_panel=self.graphics_panel,
            properties_panel=self.properties_panel
        )
        
        # Connect layout signals
        self.layout_manager.layout_changed.connect(self._on_layout_changed)
        self.layout_manager.panel_visibility_changed.connect(self._on_panel_visibility_changed)
        
        self.logger.debug("Layout manager setup complete")
    
    def _setup_shortcuts(self):
        """Setup additional keyboard shortcuts"""
        # F5 for refresh
        refresh_action = QAction(self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self._refresh_view)
        self.addAction(refresh_action)
        
        # Day 3 - Additional shortcuts
        # Ctrl+F for search
        search_action = QAction(self)
        search_action.setShortcut(QKeySequence("Ctrl+F"))
        search_action.triggered.connect(self._show_search_panel)
        self.addAction(search_action)
        
        # Ctrl+T for tree focus
        tree_focus_action = QAction(self)
        tree_focus_action.setShortcut(QKeySequence("Ctrl+T"))
        tree_focus_action.triggered.connect(self._focus_tree_panel)
        self.addAction(tree_focus_action)
        
        # Alt+Left/Right for navigation
        nav_back_action = QAction(self)
        nav_back_action.setShortcut(QKeySequence("Alt+Left"))
        nav_back_action.triggered.connect(self._navigate_back)
        self.addAction(nav_back_action)
        
        nav_forward_action = QAction(self)
        nav_forward_action.setShortcut(QKeySequence("Alt+Right"))
        nav_forward_action.triggered.connect(self._navigate_forward)
        self.addAction(nav_forward_action)
    
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
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #404040;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #505050;
                color: white;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: #4a90e2;
            }
            QTabBar::tab:hover {
                background-color: #5a5a5a;
            }
            QDockWidget {
                background-color: #404040;
                color: white;
                titlebar-close-icon: none;
                titlebar-normal-icon: none;
            }
            QDockWidget::title {
                background-color: #353535;
                color: white;
                padding: 5px;
                border: 1px solid #555;
            }
        """)
    
    def _show_welcome_message(self):
        """Show welcome message in status bar"""
        self.status_bar.showMessage(f"Welcome to {AppConstants.APP_NAME}! Open an ARXML file to get started.", 5000)
    
    # ===== Day 3 Event Handlers =====
    
    def _on_tree_search_changed(self, search_text: str):
        """Handle tree search text change"""
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.apply_search(search_text)
            
            # Update search info in status bar
            if search_text:
                self.search_info_label.setText(f"Tree search: '{search_text}'")
            else:
                self.search_info_label.setText("")
    
    def _on_tree_filter_changed(self, filter_text: str):
        """Handle tree filter change"""
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.apply_filter(filter_text)
    
    def _on_tree_search_cleared(self):
        """Handle tree search clear"""
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.clear_search_and_filter()
        self.search_info_label.setText("")
    
    def _on_tree_item_selected(self, obj):
        """Handle tree item selection"""
        # This is handled by navigation controller
        pass
    
    def _on_tree_item_activated(self, obj):
        """Handle tree item activation (double-click)"""
        # This is handled by navigation controller  
        pass
    
    def _on_navigation_component_selected(self, component):
        """Handle component selection from navigation controller"""
        if component:
            self._show_component_properties(component)
            self._update_navigation_info(component)
        else:
            self.properties_text.setPlainText("Select a component to view its properties")
            self.navigation_info_label.setText("")
    
    def _on_navigation_requested(self, item_type: str, item_uuid: str):
        """Handle navigation request"""
        self.logger.debug(f"Navigation requested: {item_type} {item_uuid}")
        # Will be implemented in Day 6 for composition navigation
    
    def _on_focus_requested(self, item_uuid: str):
        """Handle focus request"""
        if self.graphics_scene:
            self.graphics_scene.highlight_component(item_uuid)
            self._fit_to_window()
    
    def _perform_quick_search(self, query: str):
        """Perform quick search from toolbar"""
        if not query:
            return
            
        # Perform search using search engine
        try:
            results = self.search_engine.search(query, max_results=10)
            
            # Update search results tab
            results_text = f"Quick Search Results for '{query}':\n\n"
            
            if results:
                for i, result in enumerate(results, 1):
                    results_text += f"{i}. {result.item_name} ({result.item_type})\n"
                    results_text += f"   Match: {result.match_field}\n"
                    if result.parent_package:
                        results_text += f"   Package: {result.parent_package}\n"
                    results_text += f"   Score: {result.relevance_score:.2f}\n\n"
            else:
                results_text += "No results found."
            
            self.search_results_text.setPlainText(results_text)
            
            # Switch to search results tab
            self.properties_tabs.setCurrentIndex(1)
            
            # Highlight first result in tree if available
            if results:
                first_result = results[0]
                if self.enhanced_tree_widget:
                    self.enhanced_tree_widget.select_object_by_uuid(first_result.item_uuid)
            
            # Update status
            self.status_bar.showMessage(f"Found {len(results)} results for '{query}'", 3000)
            
        except Exception as e:
            self.logger.error(f"Quick search failed: {e}")
            self.status_bar.showMessage(f"Search failed: {e}", 5000)
    
    def _show_advanced_search(self):
        """Show advanced search panel"""
        self.search_dock.setVisible(True)
        self.search_dock.raise_()
        self.advanced_search_widget.focus_search_input()
    
    def _show_search_panel(self):
        """Show search panel (from menu/shortcut)"""
        self._show_advanced_search()
    
    def _find_next(self):
        """Find next search result"""
        # Will be implemented with search result navigation
        pass
    
    def _clear_search(self):
        """Clear all search"""
        self.compact_search.clear_search()
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.clear_search_and_filter()
        self.search_info_label.setText("")
        self.search_results_text.clear()
    
    def _on_search_started(self, query: str):
        """Handle search started"""
        self.status_bar.showMessage(f"Searching for '{query}'...")
    
    def _on_search_completed(self, results):
        """Handle search completed"""
        count = len(results)
        self.status_bar.showMessage(f"Search completed: {count} results found", 3000)
        
        # Update search results in properties panel
        self._update_search_results_display(results)
    
    def _on_search_result_selected(self, result):
        """Handle search result selection"""
        # Highlight in tree
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.select_object_by_uuid(result.item_uuid)
    
    def _on_search_result_activated(self, result):
        """Handle search result activation (double-click)"""
        # Focus in diagram
        self._on_focus_requested(result.item_uuid)
    
    def _update_search_results_display(self, results):
        """Update search results display in properties panel"""
        if not results:
            self.search_results_text.setPlainText("No search results.")
            return
        
        results_text = f"Search Results ({len(results)}):\n\n"
        
        for i, result in enumerate(results, 1):
            results_text += f"{i}. {result.item_name}\n"
            results_text += f"   Type: {result.item_type}\n"
            results_text += f"   Match Field: {result.match_field}\n"
            results_text += f"   Relevance: {result.relevance_score:.2f}\n"
            
            if result.parent_package:
                results_text += f"   Package: {result.parent_package}\n"
            
            if result.match_text and len(result.match_text) < 100:
                results_text += f"   Text: {result.match_text}\n"
            
            results_text += "\n"
        
        self.search_results_text.setPlainText(results_text)
    
    def _navigate_back(self):
        """Navigate back in history"""
        if self.navigation_controller.navigate_back():
            self.back_action.setEnabled(self.navigation_controller.can_navigate_back())
            self.forward_action.setEnabled(self.navigation_controller.can_navigate_forward())
    
    def _navigate_forward(self):
        """Navigate forward in history"""
        if self.navigation_controller.navigate_forward():
            self.back_action.setEnabled(self.navigation_controller.can_navigate_back())
            self.forward_action.setEnabled(self.navigation_controller.can_navigate_forward())
    
    def _update_navigation_info(self, obj):
        """Update navigation info in status bar"""
        if obj:
            breadcrumbs = self.navigation_controller.get_breadcrumb_path()
            if breadcrumbs:
                path_text = " > ".join(breadcrumbs[-3:])  # Show last 3 levels
                self.navigation_info_label.setText(path_text)
        
        # Update navigation buttons
        self.back_action.setEnabled(self.navigation_controller.can_navigate_back())
        self.forward_action.setEnabled(self.navigation_controller.can_navigate_forward())
    
    def _apply_layout_preset(self, layout_name: str):
        """Apply layout preset"""
        self.layout_manager.apply_layout(layout_name)
    
    def _save_custom_layout(self):
        """Save current layout as custom"""
        name, ok = QInputDialog.getText(self, "Save Layout", "Enter layout name:")
        if ok and name:
            self.layout_manager.save_current_as_custom_layout(name, f"Custom layout: {name}")
    
    def _on_layout_changed(self, layout_name: str):
        """Handle layout change"""
        self.logger.debug(f"Layout changed to: {layout_name}")
        
        # Update menu checkmarks
        for action in self.layout_action_group.actions():
            action.setChecked(action.text() == layout_name)
    
    def _on_panel_visibility_changed(self, panel_name: str, visible: bool):
        """Handle panel visibility change"""
        if panel_name == 'tree':
            self.toggle_tree_action.setChecked(visible)
        elif panel_name == 'properties':
            self.toggle_properties_action.setChecked(visible)
    
    def _expand_all_tree_items(self):
        """Expand all tree items"""
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.expandAll()
    
    def _collapse_all_tree_items(self):
        """Collapse all tree items"""
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.collapseAll()
    
    def _focus_tree_panel(self):
        """Focus tree panel"""
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.setFocus()
    
    # ===== Existing Event Handlers (Updated for Day 3) =====
    
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
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.clear()
        self.properties_text.setPlainText("Select a component to view its properties")
        self.search_results_text.clear()
        self.statistics_text.clear()
        
        if hasattr(self, 'graphics_scene'):
            self.graphics_scene.clear_scene()
        
        # Clear search and navigation
        self._clear_search()
        self.navigation_controller.clear_mappings()
        
        self.status_bar.showMessage("File closed")
    
    def on_parsing_started(self, file_path: str):
        """Handle parsing started event"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_bar.showMessage(f"Parsing {Path(file_path).name}...")
    
    def on_parsing_finished(self, packages, metadata):
        """Handle parsing finished event - Enhanced for Day 3"""
        self.progress_bar.setVisible(False)
        
        # Day 3 - Build search index
        try:
            self.search_engine.build_index(packages)
            self.logger.debug("Search index built successfully")
        except Exception as e:
            self.logger.error(f"Failed to build search index: {e}")
        
        # Update enhanced tree widget
        if self.enhanced_tree_widget:
            self.enhanced_tree_widget.load_packages(packages)
        
        # Setup navigation controller mappings
        self._setup_tree_navigation_mappings()
        
        # Load packages into graphics scene
        if hasattr(self, 'graphics_scene'):
            self.graphics_scene.load_packages(packages)
            self.graphics_scene.fit_components_in_view()
        
        # Update statistics tab
        self._update_statistics_display(packages, metadata)
        
        # Show statistics
        stats = metadata.get('statistics', {})
        message = f"Loaded {stats.get('components_parsed', 0)} components in {stats.get('parse_time', 0):.2f}s"
        self.status_bar.showMessage(message, 3000)
    
    def _setup_tree_navigation_mappings(self):
        """Setup navigation mappings between tree items and objects"""
        if not self.enhanced_tree_widget:
            return
        
        # Clear existing mappings
        self.navigation_controller.clear_mappings()
        
        # Register all tree items with navigation controller
        def register_tree_items(item, parent_count=0):
            if hasattr(item, 'data_object') and item.data_object:
                self.navigation_controller.register_tree_item(item, item.data_object)
            
            # Register children recursively
            for i in range(item.childCount()):
                child = item.child(i)
                register_tree_items(child, parent_count + 1)
        
        # Register all top-level items and their children
        for i in range(self.enhanced_tree_widget.topLevelItemCount()):
            top_item = self.enhanced_tree_widget.topLevelItem(i)
            register_tree_items(top_item)
        
        self.logger.debug("Tree navigation mappings setup complete")
    
    def _update_statistics_display(self, packages, metadata):
        """Update statistics display"""
        stats_text = "File Statistics:\n\n"
        
        # File info
        if self.current_file:
            file_path = Path(self.current_file)
            stats_text += f"File: {file_path.name}\n"
            stats_text += f"Size: {file_path.stat().st_size / 1024:.1f} KB\n\n"
        
        # Parsing stats
        parse_stats = metadata.get('statistics', {})
        stats_text += f"Parse Time: {parse_stats.get('parse_time', 0):.2f} seconds\n"
        stats_text += f"Components: {parse_stats.get('components_parsed', 0)}\n"
        stats_text += f"Ports: {parse_stats.get('ports_parsed', 0)}\n"
        stats_text += f"Packages: {parse_stats.get('packages_parsed', 0)}\n\n"
        
        # Component breakdown
        component_counts = {}
        total_ports = 0
        
        for package in packages:
            for component in package.get_all_components(recursive=True):
                comp_type = component.component_type.name
                component_counts[comp_type] = component_counts.get(comp_type, 0) + 1
                total_ports += component.port_count
        
        if component_counts:
            stats_text += "Component Types:\n"
            for comp_type, count in sorted(component_counts.items()):
                stats_text += f"  {comp_type}: {count}\n"
            stats_text += f"\nTotal Ports: {total_ports}\n"
        
        # Tree statistics
        if self.enhanced_tree_widget:
            tree_stats = self.enhanced_tree_widget.get_statistics()
            stats_text += f"\nTree View:\n"
            stats_text += f"  Total Items: {tree_stats.get('total_items', 0)}\n"
            stats_text += f"  Visible Items: {tree_stats.get('visible_items', 0)}\n"
        
        # Search engine statistics
        search_stats = self.search_engine.get_statistics()
        stats_text += f"\nSearch Index:\n"
        stats_text += f"  Indexed Words: {search_stats.get('indexed_words', 0)}\n"
        stats_text += f"  Search History: {search_stats.get('search_history_size', 0)}\n"
        
        self.statistics_text.setPlainText(stats_text)
    
    def on_parsing_failed(self, error_message: str):
        """Handle parsing failed event"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Parsing failed")
        
        QMessageBox.critical(
            self,
            "Parsing Error",
            f"Failed to parse ARXML file:\n\n{error_message}"
        )
    
    def update_recent_files(self, recent_files: List[str]):
        """Update recent files menu"""
        self._update_recent_files_menu(recent_files)
    
    def _update_recent_files_menu(self, recent_files: List[str]):
        """Update the recent files submenu"""
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
        # This is now handled by navigation controller
        pass
    
    def _on_component_double_clicked(self, component):
        """Handle component double-click from graphics scene"""
        # This is now handled by navigation controller
        pass
    
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
        
        # Switch to properties tab
        self.properties_tabs.setCurrentIndex(0)
    
    # View control methods (Enhanced for Day 3)
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
        self.layout_manager.toggle_panel_visibility('tree')
    
    def _toggle_properties_panel(self):
        """Toggle properties panel visibility"""
        self.layout_manager.toggle_panel_visibility('properties')
    
    def _refresh_view(self):
        """Refresh the current view"""
        if self.is_file_open:
            self.status_bar.showMessage("Refreshing view...", 1000)
            
            # Refresh search index
            if hasattr(self, 'packages') and self.packages:
                self.search_engine.build_index(self.packages)
    
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
            <p><b>Features:</b></p>
            <ul>
            <li>Enhanced tree navigation with search</li>
            <li>Advanced search and filtering</li>
            <li>Component visualization</li>
            <li>Navigation history</li>
            <li>Customizable layouts</li>
            </ul>
            """
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save layout state
        self.layout_manager.save_state_on_exit()
        
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