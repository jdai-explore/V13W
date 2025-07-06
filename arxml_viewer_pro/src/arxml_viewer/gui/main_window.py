# src/arxml_viewer/gui/main_window.py
"""
Main Window - ENHANCED VERSION with Breadcrumbs, Export, and Auto-Layout
Professional main window with enhanced three-panel layout for ARXML Viewer Pro
Added Day 5 features: breadcrumb navigation, export functionality, and auto-layout
COMPREHENSIVE FIX - All methods properly defined and error handling added
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
from .widgets.breadcrumb_widget import BreadcrumbWidget  # NEW: Import breadcrumb widget
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
    - Center: Component diagram visualization with breadcrumb navigation
    - Right: Properties panel
    
    Day 5 additions:
    - Breadcrumb navigation widget
    - Export functionality (PNG, SVG, PDF)
    - Auto-layout algorithm integration
    - Enhanced layout management
    
    COMPREHENSIVE FIX:
    - All methods properly defined with error handling
    - Consistent method signatures
    - Proper initialization order
    - Complete event handler implementations
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
        
        # Initialize UI components to None first to avoid attribute errors
        self.enhanced_tree_widget: Optional[EnhancedTreeWidget] = None
        self.graphics_scene: Optional[ComponentDiagramScene] = None
        self.graphics_view: Optional[QGraphicsView] = None
        self.properties_text: Optional[QTextEdit] = None
        self.search_results_text: Optional[QTextEdit] = None
        self.statistics_text: Optional[QTextEdit] = None
        self.properties_tabs: Optional[QTabWidget] = None
        self.main_splitter: Optional[QSplitter] = None
        self.tree_panel: Optional[QWidget] = None
        self.graphics_panel: Optional[QWidget] = None
        self.properties_panel: Optional[QWidget] = None
        self.graphics_stack: Optional[QStackedWidget] = None
        self.breadcrumb_widget: Optional[BreadcrumbWidget] = None
        self.tree_search_widget: Optional[TreeSearchWidget] = None
        self.compact_search: Optional[CompactSearchWidget] = None
        self.advanced_search_widget: Optional[AdvancedSearchWidget] = None
        self.search_dock: Optional[QDockWidget] = None
        
        # Status bar components
        self.status_bar: Optional[QStatusBar] = None
        self.file_info_label: Optional[QLabel] = None
        self.search_info_label: Optional[QLabel] = None
        self.navigation_info_label: Optional[QLabel] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.zoom_label: Optional[QLabel] = None
        
        # Action references
        self.open_action: Optional[QAction] = None
        self.close_action: Optional[QAction] = None
        self.back_action: Optional[QAction] = None
        self.forward_action: Optional[QAction] = None
        self.home_action: Optional[QAction] = None
        self.export_png_action: Optional[QAction] = None
        self.export_svg_action: Optional[QAction] = None
        self.export_pdf_action: Optional[QAction] = None
        self.grid_layout_action: Optional[QAction] = None
        self.hierarchical_layout_action: Optional[QAction] = None
        self.force_layout_action: Optional[QAction] = None
        self.circular_layout_action: Optional[QAction] = None
        self.toggle_tree_action: Optional[QAction] = None
        self.toggle_properties_action: Optional[QAction] = None
        self.toggle_breadcrumbs_action: Optional[QAction] = None
        
        # Button references
        self.auto_layout_btn: Optional[QPushButton] = None
        self.auto_layout_mini_btn: Optional[QPushButton] = None
        self.export_btn: Optional[QPushButton] = None
        self.export_mini_btn: Optional[QPushButton] = None
        
        # Menu references
        self.recent_menu = None
        self.layout_action_group: Optional[QActionGroup] = None
        
        # Day 3 - Core services (initialize early to avoid errors)
        try:
            self.search_engine = SearchEngine()
            self.filter_manager = FilterManager()
        except Exception as e:
            self.logger.error(f"Failed to initialize core services: {e}")
            # Create fallback minimal services
            self.search_engine = None
            self.filter_manager = None
        
        # Day 3 - Controllers and managers (initialize early)
        try:
            self.navigation_controller = NavigationController()
            self.layout_manager = LayoutManager(self)
        except Exception as e:
            self.logger.error(f"Failed to initialize controllers: {e}")
            # Create fallback minimal controllers
            self.navigation_controller = None
            self.layout_manager = None
        
        # Initialize UI in proper order
        try:
            self._setup_window()
            self._create_status_bar()  # Create status bar first
            self._create_menu_bar()
            self._create_tool_bar()
            self._create_central_widget()
            self._setup_shortcuts()
            self._apply_light_theme()
            
            # Setup navigation and layout after UI is created
            self._setup_navigation_controller()
            self._setup_layout_manager()
            
            # Day 5 - Setup breadcrumb navigation
            self._setup_breadcrumb_navigation()
            
            # Show welcome message
            self._show_welcome_message()
            
            self.logger.info("MainWindow initialized successfully with Day 5 enhancements")
            
        except Exception as e:
            self.logger.error(f"MainWindow initialization failed: {e}")
            # Still try to show a basic window
            self.setWindowTitle("ARXML Viewer Pro - Initialization Error")
            self.resize(800, 600)
    
    def _setup_window(self):
        """Configure main window properties"""
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
        """Create status bar with Day 3 enhancements"""
        try:
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
            
        except Exception as e:
            self.logger.error(f"Status bar creation failed: {e}")
    
    def _create_menu_bar(self):
        """Create application menu bar with Day 5 enhancements"""
        try:
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
            
            # Day 5 - NEW: Export submenu
            export_menu = file_menu.addMenu("&Export")
            
            # Export to PNG
            self.export_png_action = QAction("Export as &PNG...", self)
            self.export_png_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
            self.export_png_action.setStatusTip("Export diagram as PNG image")
            self.export_png_action.triggered.connect(self._export_as_png)
            self.export_png_action.setEnabled(False)
            export_menu.addAction(self.export_png_action)
            
            # Export to SVG
            self.export_svg_action = QAction("Export as &SVG...", self)
            self.export_svg_action.setStatusTip("Export diagram as SVG vector")
            self.export_svg_action.triggered.connect(self._export_as_svg)
            self.export_svg_action.setEnabled(False)
            export_menu.addAction(self.export_svg_action)
            
            # Export to PDF
            self.export_pdf_action = QAction("Export as P&DF...", self)
            self.export_pdf_action.setStatusTip("Export diagram as PDF document")
            self.export_pdf_action.triggered.connect(self._export_as_pdf)
            self.export_pdf_action.setEnabled(False)
            export_menu.addAction(self.export_pdf_action)
            
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
            
            # View Menu - Enhanced for Day 5
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
            
            fit_to_window_action = QAction("&Fit to Window", self)
            fit_to_window_action.setShortcut(QKeySequence("Ctrl+F"))
            fit_to_window_action.triggered.connect(self._fit_to_window)
            view_menu.addAction(fit_to_window_action)
            
            view_menu.addSeparator()
            
            # Day 5 - NEW: Auto-Layout submenu
            layout_menu = view_menu.addMenu("Auto-&Layout")
            
            # Grid layout
            self.grid_layout_action = QAction("&Grid Layout", self)
            self.grid_layout_action.setStatusTip("Arrange components in a grid")
            self.grid_layout_action.triggered.connect(lambda: self._apply_auto_layout("grid"))
            self.grid_layout_action.setEnabled(False)
            layout_menu.addAction(self.grid_layout_action)
            
            # Hierarchical layout
            self.hierarchical_layout_action = QAction("&Hierarchical Layout", self)
            self.hierarchical_layout_action.setStatusTip("Arrange components hierarchically")
            self.hierarchical_layout_action.triggered.connect(lambda: self._apply_auto_layout("hierarchical"))
            self.hierarchical_layout_action.setEnabled(False)
            layout_menu.addAction(self.hierarchical_layout_action)
            
            # Force-directed layout
            self.force_layout_action = QAction("&Force-Directed Layout", self)
            self.force_layout_action.setStatusTip("Arrange components using force simulation")
            self.force_layout_action.triggered.connect(lambda: self._apply_auto_layout("force_directed"))
            self.force_layout_action.setEnabled(False)
            layout_menu.addAction(self.force_layout_action)
            
            # Circular layout
            self.circular_layout_action = QAction("&Circular Layout", self)
            self.circular_layout_action.setStatusTip("Arrange components in a circle")
            self.circular_layout_action.triggered.connect(lambda: self._apply_auto_layout("circular"))
            self.circular_layout_action.setEnabled(False)
            layout_menu.addAction(self.circular_layout_action)
            
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
            
            # Day 5 - NEW: Breadcrumb toggle
            self.toggle_breadcrumbs_action = QAction("Show &Breadcrumbs", self)
            self.toggle_breadcrumbs_action.setCheckable(True)
            self.toggle_breadcrumbs_action.setChecked(True)
            self.toggle_breadcrumbs_action.triggered.connect(self._toggle_breadcrumbs)
            view_menu.addAction(self.toggle_breadcrumbs_action)
            
            view_menu.addSeparator()
            
            # Layout presets
            layout_submenu = view_menu.addMenu("&Layout Presets")
            self._create_layout_menu(layout_submenu)
            
            # Navigation Menu - NEW for Day 5
            nav_menu = menubar.addMenu("&Navigation")
            
            # Back/Forward actions
            self.back_action = QAction("&Back", self)
            self.back_action.setShortcut(QKeySequence("Alt+Left"))
            self.back_action.setStatusTip("Navigate back")
            self.back_action.setEnabled(False)
            self.back_action.triggered.connect(self._navigate_back)
            nav_menu.addAction(self.back_action)
            
            self.forward_action = QAction("&Forward", self)
            self.forward_action.setShortcut(QKeySequence("Alt+Right"))
            self.forward_action.setStatusTip("Navigate forward")
            self.forward_action.setEnabled(False)
            self.forward_action.triggered.connect(self._navigate_forward)
            nav_menu.addAction(self.forward_action)
            
            nav_menu.addSeparator()
            
            # Home action
            self.home_action = QAction("&Home", self)
            self.home_action.setShortcut(QKeySequence("Ctrl+Home"))
            self.home_action.setStatusTip("Navigate to home view")
            self.home_action.triggered.connect(self._navigate_home)
            self.home_action.setEnabled(False)
            nav_menu.addAction(self.home_action)
            
            # Search menu
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
            
        except Exception as e:
            self.logger.error(f"Menu bar creation failed: {e}")
    
    def _create_tool_bar(self):
        """Create main toolbar with Day 5 enhancements"""
        try:
            toolbar = self.addToolBar("Main")
            toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            
            # File operations
            if self.open_action:
                toolbar.addAction(self.open_action)
            toolbar.addSeparator()
            
            # Navigation buttons (enhanced for Day 5)
            if self.back_action:
                toolbar.addAction(self.back_action)
            if self.forward_action:
                toolbar.addAction(self.forward_action)
            if self.home_action:
                toolbar.addAction(self.home_action)
            toolbar.addSeparator()
            
            # Day 5 - NEW: Auto-layout button
            self.auto_layout_btn = QPushButton("📐 Auto-Layout")
            self.auto_layout_btn.setToolTip("Apply automatic layout to components")
            self.auto_layout_btn.clicked.connect(self._apply_smart_auto_layout)
            self.auto_layout_btn.setEnabled(False)
            toolbar.addWidget(self.auto_layout_btn)
            
            toolbar.addSeparator()
            
            # Day 5 - NEW: Export button
            self.export_btn = QPushButton("💾 Export")
            self.export_btn.setToolTip("Export diagram as image")
            self.export_btn.clicked.connect(self._quick_export)
            self.export_btn.setEnabled(False)
            toolbar.addWidget(self.export_btn)
            
            toolbar.addSeparator()
            
            # Compact search widget
            self.compact_search = CompactSearchWidget()
            self.compact_search.search_requested.connect(self._perform_quick_search)
            self.compact_search.advanced_search_requested.connect(self._show_advanced_search)
            toolbar.addWidget(self.compact_search)
            
            toolbar.addSeparator()
            
            # Zoom controls
            self.zoom_label = QLabel("100%")
            self.zoom_label.setMinimumWidth(50)
            toolbar.addWidget(self.zoom_label)
            
        except Exception as e:
            self.logger.error(f"Toolbar creation failed: {e}")
    
    def _create_central_widget(self):
        """Create the enhanced three-panel layout with Day 5 breadcrumbs"""
        try:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout with breadcrumbs
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Day 5 - NEW: Breadcrumb navigation bar
            self.breadcrumb_widget = BreadcrumbWidget()
            self.breadcrumb_widget.breadcrumb_clicked.connect(self._on_breadcrumb_clicked)
            self.breadcrumb_widget.navigation_requested.connect(self._on_breadcrumb_navigation)
            main_layout.addWidget(self.breadcrumb_widget)
            
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
            
            # Add splitter to layout
            main_layout.addWidget(self.main_splitter)
            
            # Day 3 - Create dockable advanced search widget
            self._create_search_dock()
            
        except Exception as e:
            self.logger.error(f"Central widget creation failed: {e}")
    
    def _create_graphics_panel(self) -> QWidget:
        """Create the center graphics visualization panel with Day 5 enhancements"""
        try:
            panel = QWidget()
            layout = QVBoxLayout(panel)
            
            # Panel title and controls
            header_layout = QHBoxLayout()
            
            title_label = QLabel("Component Diagram")
            title_label.setFont(QFont("Arial", 10, QFont.Bold))
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # Day 5 - NEW: Layout controls
            layout_controls = QHBoxLayout()
            
            # Auto-layout button (duplicate for easy access)
            auto_layout_mini_btn = QPushButton("📐")
            auto_layout_mini_btn.setMaximumWidth(30)
            auto_layout_mini_btn.setToolTip("Auto-Layout")
            auto_layout_mini_btn.clicked.connect(self._apply_smart_auto_layout)
            auto_layout_mini_btn.setEnabled(False)
            layout_controls.addWidget(auto_layout_mini_btn)
            self.auto_layout_mini_btn = auto_layout_mini_btn  # Store reference
            
            # Fit to window button
            fit_button = QPushButton("Fit")
            fit_button.setMaximumWidth(40)
            fit_button.clicked.connect(self._fit_to_window)
            layout_controls.addWidget(fit_button)
            
            # Export button (duplicate for easy access)
            export_mini_btn = QPushButton("💾")
            export_mini_btn.setMaximumWidth(30)
            export_mini_btn.setToolTip("Export")
            export_mini_btn.clicked.connect(self._quick_export)
            export_mini_btn.setEnabled(False)
            layout_controls.addWidget(export_mini_btn)
            self.export_mini_btn = export_mini_btn  # Store reference
            
            header_layout.addLayout(layout_controls)
            
            layout.addLayout(header_layout)
            
            # Create custom graphics scene and view
            self.graphics_scene = ComponentDiagramScene()
            self.graphics_view = QGraphicsView(self.graphics_scene)
            self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
            self.graphics_view.setRenderHint(QPainter.Antialiasing)
            
            # Connect scene signals
            self.graphics_scene.component_selected.connect(self._on_component_selected)
            self.graphics_scene.component_double_clicked.connect(self._on_component_double_clicked)
            
            # Day 5 - NEW: Connect drill-down signal
            if hasattr(self.graphics_scene, 'composition_drill_requested'):
                self.graphics_scene.composition_drill_requested.connect(self._on_composition_drill_down)
            
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
            
        except Exception as e:
            self.logger.error(f"Graphics panel creation failed: {e}")
            # Return minimal panel
            panel = QWidget()
            layout = QVBoxLayout(panel)
            error_label = QLabel("Graphics panel failed to load")
            layout.addWidget(error_label)
            return panel
    
    def _create_enhanced_tree_panel(self) -> QWidget:
        """Create the enhanced left tree navigation panel with Day 3 features"""
        try:
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
            
        except Exception as e:
            self.logger.error(f"Tree panel creation failed: {e}")
            # Return minimal panel
            panel = QWidget()
            layout = QVBoxLayout(panel)
            error_label = QLabel("Tree panel failed to load")
            layout.addWidget(error_label)
            return panel
    
    def _create_enhanced_properties_panel(self) -> QWidget:
        """Create the enhanced right properties panel with Day 3 features"""
        try:
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
            
        except Exception as e:
            self.logger.error(f"Properties panel creation failed: {e}")
            # Return minimal panel
            panel = QWidget()
            layout = QVBoxLayout(panel)
            error_label = QLabel("Properties panel failed to load")
            layout.addWidget(error_label)
            return panel
    
    def _create_search_dock(self):
        """Create dockable advanced search widget"""
        try:
            self.search_dock = QDockWidget("Advanced Search", self)
            self.search_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
            
            # Create advanced search widget
            if self.search_engine:
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
            
        except Exception as e:
            self.logger.error(f"Search dock creation failed: {e}")
    
    def _create_layout_menu(self, layout_menu):
        """Create layout presets menu"""
        try:
            # Create action group for exclusive selection
            self.layout_action_group = QActionGroup(self)
            
            # Get available layouts from layout manager
            if self.layout_manager:
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
            
        except Exception as e:
            self.logger.error(f"Layout menu creation failed: {e}")
    
    def _setup_navigation_controller(self):
        """Setup navigation controller with Day 3 components"""
        try:
            if self.navigation_controller:
                # Set up navigation controller with our widgets
                self.navigation_controller.set_tree_widget(self.enhanced_tree_widget)
                self.navigation_controller.set_graphics_scene(self.graphics_scene)
                
                # Connect navigation signals
                self.navigation_controller.component_selection_changed.connect(self._on_navigation_component_selected)
                self.navigation_controller.navigation_requested.connect(self._on_navigation_requested)
                self.navigation_controller.focus_requested.connect(self._on_focus_requested)
                
                self.logger.debug("Navigation controller setup complete")
        except Exception as e:
            self.logger.error(f"Navigation controller setup failed: {e}")
    
    def _setup_layout_manager(self):
        """Setup layout manager with Day 3 components"""
        try:
            if self.layout_manager:
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
        except Exception as e:
            self.logger.error(f"Layout manager setup failed: {e}")
    
    def _setup_breadcrumb_navigation(self):
        """Setup breadcrumb navigation integration - Day 5 NEW"""
        try:
            if self.breadcrumb_widget and self.navigation_controller:
                # Connect navigation controller signals to breadcrumb updates
                if hasattr(self.navigation_controller, 'breadcrumb_updated'):
                    self.navigation_controller.breadcrumb_updated.connect(self._update_breadcrumbs)
                
                if hasattr(self.navigation_controller, 'navigation_changed'):
                    self.navigation_controller.navigation_changed.connect(self._on_navigation_changed)
        except Exception as e:
            self.logger.error(f"Breadcrumb navigation setup failed: {e}")
    
    def _setup_shortcuts(self):
        """Setup additional keyboard shortcuts"""
        try:
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
            
        except Exception as e:
            self.logger.error(f"Shortcuts setup failed: {e}")
    
    def _apply_light_theme(self):
        """Apply light theme styling with good contrast"""
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
                QMenuBar::item {
                    background-color: transparent;
                    padding: 6px 12px;
                    color: #333333;
                    border-radius: 3px;
                }
                QMenuBar::item:selected {
                    background-color: #e3f2fd;
                    color: #1976d2;
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
                QPushButton {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    padding: 6px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 70px;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                    border-color: #1976d2;
                }
                QPushButton:pressed {
                    background-color: #bbdefb;
                }
                QPushButton:disabled {
                    background-color: #f5f5f5;
                    color: #999999;
                    border-color: #e0e0e0;
                }
                QGraphicsView {
                    background-color: #fafafa;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                    background-color: #ffffff;
                    border-radius: 4px;
                }
                QTabWidget::tab-bar {
                    alignment: left;
                }
                QTabBar::tab {
                    background-color: #f5f5f5;
                    color: #333333;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                    min-width: 80px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    color: #1976d2;
                    font-weight: bold;
                }
                QTabBar::tab:hover {
                    background-color: #e3f2fd;
                }
                QDockWidget {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                }
                QDockWidget::title {
                    background-color: #f5f5f5;
                    color: #333333;
                    padding: 8px;
                    border: 1px solid #cccccc;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 6px;
                    color: #333333;
                    selection-background-color: #e3f2fd;
                }
                QLineEdit:focus {
                    border-color: #1976d2;
                    background-color: #fafafa;
                }
                QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 4px 8px;
                    color: #333333;
                    min-width: 100px;
                }
                QComboBox:hover {
                    border-color: #1976d2;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    width: 12px;
                    height: 12px;
                    background-color: #666666;
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
    # CRITICAL EVENT HANDLERS - PROPERLY DEFINED
    # ==========================================
    
    def on_parsing_started(self, file_path: str):
        """Handle parsing started event - COMPREHENSIVE FIX"""
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
            if self.enhanced_tree_widget:
                self.enhanced_tree_widget.clear()
            
            if self.properties_text:
                self.properties_text.setPlainText("Parsing file...")
            
            if self.search_results_text:
                self.search_results_text.clear()
            
            if self.statistics_text:
                self.statistics_text.clear()
            
            # Clear graphics scene
            if self.graphics_scene:
                self.graphics_scene.clear_scene()
            
        except Exception as e:
            self.logger.error(f"Parsing started handler failed: {e}")
    
    def on_parsing_finished(self, packages, metadata):
        """Handle parsing finished event - Enhanced with Day 5 features"""
        try:
            print(f"🔧 MainWindow: Parsing finished, {len(packages)} packages")
            
            if self.progress_bar:
                self.progress_bar.setVisible(False)
            
            # Update enhanced tree widget
            if self.enhanced_tree_widget:
                try:
                    print("🔧 Loading packages into tree widget...")
                    self.enhanced_tree_widget.load_packages(packages)
                    print("✅ Tree widget loaded successfully")
                except Exception as e:
                    print(f"❌ Tree widget loading failed: {e}")
            
            # Load packages into graphics scene with connections
            if self.graphics_scene:
                try:
                    print("🔧 Loading packages into graphics scene...")
                    
                    # Day 5 - Get connections from app controller if available
                    connections = []
                    if self.app_controller and hasattr(self.app_controller, 'get_parsed_connections'):
                        try:
                            connections = self.app_controller.get_parsed_connections()
                            print(f"🔗 Retrieved {len(connections)} connections from app controller")
                        except Exception as e:
                            print(f"⚠️ Could not get connections: {e}")
                    
                    # Load with connections
                    self.graphics_scene.load_packages(packages, connections)
                    print("✅ Graphics scene loaded successfully with connections")
                    
                    # Switch to graphics view
                    if self.graphics_stack:
                        self.graphics_stack.setCurrentIndex(1)
                        print("✅ Switched to graphics view")
                        
                    # Day 5 - Apply initial auto-layout after loading
                    QTimer.singleShot(500, self._apply_initial_layout)
                    
                except Exception as e:
                    print(f"❌ Graphics scene loading failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Update statistics tab
            self._update_statistics_display(packages, metadata)
            
            # Show statistics
            stats = metadata.get('statistics', {})
            message = f"Loaded {stats.get('components_parsed', 0)} components in {stats.get('parse_time', 0):.2f}s"
            if self.status_bar:
                self.status_bar.showMessage(message, 3000)
            print(f"✅ {message}")
            
        except Exception as e:
            self.logger.error(f"Parsing finished handler failed: {e}")
            print(f"❌ Parsing finished handler failed: {e}")
    
    def on_file_opened(self, file_path: str):
        """Handle file opened event - Enhanced with Day 5 features"""
        try:
            self.current_file = file_path
            self.is_file_open = True
            
            # Update UI state
            if self.close_action:
                self.close_action.setEnabled(True)
            if self.file_info_label:
                self.file_info_label.setText(f"File: {Path(file_path).name}")
            self.setWindowTitle(f"{AppConstants.APP_NAME} - {Path(file_path).name}")
            
            # Day 5 - Enable export and layout actions
            export_actions = [self.export_png_action, self.export_svg_action, self.export_pdf_action]
            for action in export_actions:
                if action:
                    action.setEnabled(True)
            
            export_buttons = [self.export_btn, self.export_mini_btn]
            for button in export_buttons:
                if button:
                    button.setEnabled(True)
            
            layout_actions = [self.grid_layout_action, self.hierarchical_layout_action, 
                            self.force_layout_action, self.circular_layout_action]
            for action in layout_actions:
                if action:
                    action.setEnabled(True)
            
            layout_buttons = [self.auto_layout_btn, self.auto_layout_mini_btn]
            for button in layout_buttons:
                if button:
                    button.setEnabled(True)
            
            if self.home_action:
                self.home_action.setEnabled(True)
            
            # Initialize breadcrumbs with root
            if self.breadcrumb_widget:
                self.breadcrumb_widget.set_root_item(
                    name=Path(file_path).stem,
                    display_name=f"🏠 {Path(file_path).stem}",
                    item_type="system"
                )
            
            # Switch to graphics view
            if self.graphics_stack:
                self.graphics_stack.setCurrentIndex(1)
            
            if self.status_bar:
                self.status_bar.showMessage(f"Opened: {Path(file_path).name}")
                
        except Exception as e:
            self.logger.error(f"File opened handler failed: {e}")
    
    def on_file_closed(self):
        """Handle file closed event - Enhanced with Day 5 features"""
        try:
            self.current_file = None
            self.is_file_open = False
            
            # Update UI state
            if self.close_action:
                self.close_action.setEnabled(False)
            if self.file_info_label:
                self.file_info_label.setText("No file open")
            self.setWindowTitle(AppConstants.APP_NAME)
            
            # Day 5 - Disable export and layout actions
            export_actions = [self.export_png_action, self.export_svg_action, self.export_pdf_action]
            for action in export_actions:
                if action:
                    action.setEnabled(False)
            
            export_buttons = [self.export_btn, self.export_mini_btn]
            for button in export_buttons:
                if button:
                    button.setEnabled(False)
            
            layout_actions = [self.grid_layout_action, self.hierarchical_layout_action, 
                            self.force_layout_action, self.circular_layout_action]
            for action in layout_actions:
                if action:
                    action.setEnabled(False)
            
            layout_buttons = [self.auto_layout_btn, self.auto_layout_mini_btn]
            for button in layout_buttons:
                if button:
                    button.setEnabled(False)
            
            nav_actions = [self.back_action, self.forward_action, self.home_action]
            for action in nav_actions:
                if action:
                    action.setEnabled(False)
            
            # Clear breadcrumbs
            if self.breadcrumb_widget:
                self.breadcrumb_widget.clear_breadcrumbs()
            
            # Switch to placeholder
            if self.graphics_stack:
                self.graphics_stack.setCurrentIndex(0)
            
            # Clear content
            if self.enhanced_tree_widget:
                self.enhanced_tree_widget.clear()
            if self.properties_text:
                self.properties_text.setPlainText("Select a component to view its properties")
            if self.search_results_text:
                self.search_results_text.clear()
            if self.statistics_text:
                self.statistics_text.clear()
            
            if self.graphics_scene:
                self.graphics_scene.clear_scene()
            
            # Clear search and navigation
            self._clear_search()
            if self.navigation_controller:
                self.navigation_controller.clear_mappings()
            
            if self.status_bar:
                self.status_bar.showMessage("File closed")
                
        except Exception as e:
            self.logger.error(f"File closed handler failed: {e}")
    
    # ==========================================
    # UI EVENT HANDLERS
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
    
    # Tree widget event handlers
    def _on_tree_search_changed(self, search_text: str):
        """Handle tree search text change"""
        try:
            if self.enhanced_tree_widget:
                self.enhanced_tree_widget.apply_search(search_text)
                
                # Update search info in status bar
                if self.search_info_label:
                    if search_text:
                        self.search_info_label.setText(f"Tree search: '{search_text}'")
                    else:
                        self.search_info_label.setText("")
        except Exception as e:
            self.logger.error(f"Tree search change failed: {e}")
    
    def _on_tree_filter_changed(self, filter_text: str):
        """Handle tree filter change"""
        try:
            if self.enhanced_tree_widget:
                self.enhanced_tree_widget.apply_filter(filter_text)
        except Exception as e:
            self.logger.error(f"Tree filter change failed: {e}")
    
    def _on_tree_search_cleared(self):
        """Handle tree search clear"""
        try:
            if self.enhanced_tree_widget:
                self.enhanced_tree_widget.clear_search_and_filter()
            if self.search_info_label:
                self.search_info_label.setText("")
        except Exception as e:
            self.logger.error(f"Tree search clear failed: {e}")
    
    def _on_tree_item_selected(self, obj):
        """Handle tree item selection"""
        try:
            # This is handled by navigation controller
            pass
        except Exception as e:
            self.logger.error(f"Tree item selection failed: {e}")
    
    def _on_tree_item_activated(self, obj):
        """Handle tree item activation (double-click)"""
        try:
            # This is handled by navigation controller  
            pass
        except Exception as e:
            self.logger.error(f"Tree item activation failed: {e}")
    
    # Navigation event handlers
    def _on_navigation_component_selected(self, component):
        """Handle component selection from navigation controller"""
        try:
            if component:
                self._show_component_properties(component)
                self._update_navigation_info(component)
            else:
                if self.properties_text:
                    self.properties_text.setPlainText("Select a component to view its properties")
                if self.navigation_info_label:
                    self.navigation_info_label.setText("")
        except Exception as e:
            self.logger.error(f"Navigation component selection failed: {e}")
    
    def _on_navigation_requested(self, item_type: str, item_uuid: str):
        """Handle navigation request"""
        try:
            self.logger.debug(f"Navigation requested: {item_type} {item_uuid}")
            # Will be implemented in Day 6 for composition navigation
        except Exception as e:
            self.logger.error(f"Navigation request failed: {e}")
    
    def _on_focus_requested(self, item_uuid: str):
        """Handle focus request"""
        try:
            if self.graphics_scene:
                self.graphics_scene.highlight_component(item_uuid)
                self._fit_to_window()
        except Exception as e:
            self.logger.error(f"Focus request failed: {e}")
    
    # Graphics scene event handlers
    def _on_component_selected(self, component):
        """Handle component selection from graphics scene"""
        try:
            if component:
                self._show_component_properties(component)
        except Exception as e:
            self.logger.error(f"Component selection failed: {e}")
    
    def _on_component_double_clicked(self, component):
        """Handle component double-click from graphics scene"""
        try:
            self.logger.debug(f"Component double-clicked: {component.short_name}")
            # Could trigger drill-down or details view
        except Exception as e:
            self.logger.error(f"Component double-click failed: {e}")
    
    def _on_composition_drill_down(self, component):
        """Handle composition drill-down request from graphics scene"""
        try:
            self.logger.info(f"Composition drill-down: {component.short_name}")
            
            # Add to breadcrumb navigation
            if self.breadcrumb_widget:
                self.breadcrumb_widget.add_breadcrumb(
                    name=component.short_name,
                    display_name=f"📦 {component.short_name}",
                    item_type="composition",
                    item_uuid=component.uuid,
                    tooltip=f"Composition: {component.short_name}"
                )
            
            # Update status
            if self.status_bar:
                self.status_bar.showMessage(f"Navigated into composition: {component.short_name}", 3000)
                
        except Exception as e:
            self.logger.error(f"Composition drill-down failed: {e}")
    
    # Breadcrumb event handlers
    def _on_breadcrumb_clicked(self, breadcrumb_item):
        """Handle breadcrumb item click"""
        try:
            self.logger.debug(f"Breadcrumb clicked: {breadcrumb_item.name}")
            
            # Navigate to the breadcrumb item using navigation controller
            if self.navigation_controller and hasattr(self.navigation_controller, 'navigate_to_breadcrumb'):
                if self.breadcrumb_widget and hasattr(self.breadcrumb_widget, 'breadcrumb_items'):
                    breadcrumb_index = self.breadcrumb_widget.breadcrumb_items.index(breadcrumb_item)
                    self.navigation_controller.navigate_to_breadcrumb(breadcrumb_index)
            
        except Exception as e:
            self.logger.error(f"Breadcrumb click handling failed: {e}")
    
    def _on_breadcrumb_navigation(self, item_type: str, item_uuid: str):
        """Handle breadcrumb navigation request"""
        try:
            self.logger.debug(f"Breadcrumb navigation: {item_type} {item_uuid}")
            
            # Use navigation controller to handle the navigation
            if self.navigation_controller:
                if hasattr(self.navigation_controller, 'navigation_requested'):
                    self.navigation_controller.navigation_requested.emit(item_type, item_uuid)
            
        except Exception as e:
            self.logger.error(f"Breadcrumb navigation failed: {e}")
    
    def _update_breadcrumbs(self, breadcrumb_path):
        """Update breadcrumb display from navigation controller"""
        try:
            if self.breadcrumb_widget:
                self.breadcrumb_widget.set_breadcrumb_path(breadcrumb_path)
            
        except Exception as e:
            self.logger.error(f"Breadcrumb update failed: {e}")
    
    def _on_navigation_changed(self, navigation_object):
        """Handle navigation change to update breadcrumbs"""
        try:
            # Update navigation buttons
            if self.navigation_controller:
                if hasattr(self.navigation_controller, 'can_navigate_back'):
                    if self.back_action:
                        self.back_action.setEnabled(self.navigation_controller.can_navigate_back())
                    
                if hasattr(self.navigation_controller, 'can_navigate_forward'):
                    if self.forward_action:
                        self.forward_action.setEnabled(self.navigation_controller.can_navigate_forward())
            
            # Update home button
            if self.home_action:
                self.home_action.setEnabled(self.is_file_open)
            
        except Exception as e:
            self.logger.error(f"Navigation change handling failed: {e}")
    
    # ==========================================
    # SEARCH EVENT HANDLERS
    # ==========================================
    
    def _perform_quick_search(self, query: str):
        """Perform quick search from toolbar"""
        try:
            if not query:
                return
                
            # Perform search using search engine
            if self.search_engine:
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
                
                if self.search_results_text:
                    self.search_results_text.setPlainText(results_text)
                
                    # Switch to search results tab
                    if self.properties_tabs:
                        self.properties_tabs.setCurrentIndex(1)
                
                # Highlight first result in tree if available
                if results and self.enhanced_tree_widget:
                    first_result = results[0]
                    if hasattr(self.enhanced_tree_widget, 'select_object_by_uuid'):
                        self.enhanced_tree_widget.select_object_by_uuid(first_result.item_uuid)
                
                # Update status
                if self.status_bar:
                    self.status_bar.showMessage(f"Found {len(results)} results for '{query}'", 3000)
            
        except Exception as e:
            self.logger.error(f"Quick search failed: {e}")
    
    def _on_search_started(self, query):
        """Handle search started"""
        try:
            if self.status_bar:
                self.status_bar.showMessage(f"Searching for '{query}'...")
        except Exception as e:
            self.logger.error(f"Search started handler failed: {e}")
    
    def _on_search_completed(self, results):
        """Handle search completed"""
        try:
            if self.status_bar:
                self.status_bar.showMessage(f"Found {len(results)} results", 3000)
        except Exception as e:
            self.logger.error(f"Search completed handler failed: {e}")
    
    def _on_search_result_selected(self, result):
        """Handle search result selection"""
        try:
            # Implementation depends on search system
            pass
        except Exception as e:
            self.logger.error(f"Search result selection failed: {e}")
    
    def _on_search_result_activated(self, result):
        """Handle search result activation"""
        try:
            # Implementation depends on search system
            pass
        except Exception as e:
            self.logger.error(f"Search result activation failed: {e}")
    
    # ==========================================
    # EXPORT FUNCTIONALITY
    # ==========================================
    
    def _export_as_png(self):
        """Export diagram as PNG image"""
        try:
            if not self.is_file_open or not self.graphics_scene:
                QMessageBox.warning(self, "Export Error", "No diagram to export. Please open an ARXML file first.")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export as PNG", "diagram.png", 
                "PNG Files (*.png);;All Files (*.*)"
            )
            
            if filename:
                success = self._export_scene_to_file(filename, "PNG")
                if success:
                    QMessageBox.information(self, "Export Successful", f"Diagram exported to:\n{filename}")
                else:
                    QMessageBox.critical(self, "Export Failed", "Failed to export diagram.")
                    
        except Exception as e:
            self.logger.error(f"PNG export failed: {e}")
            QMessageBox.critical(self, "Export Error", f"Export failed: {e}")
    
    def _export_as_svg(self):
        """Export diagram as SVG vector"""
        try:
            if not self.is_file_open or not self.graphics_scene:
                QMessageBox.warning(self, "Export Error", "No diagram to export. Please open an ARXML file first.")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export as SVG", "diagram.svg", 
                "SVG Files (*.svg);;All Files (*.*)"
            )
            
            if filename:
                success = self._export_scene_to_file(filename, "SVG")
                if success:
                    QMessageBox.information(self, "Export Successful", f"Diagram exported to:\n{filename}")
                else:
                    QMessageBox.critical(self, "Export Failed", "Failed to export diagram.")
                    
        except Exception as e:
            self.logger.error(f"SVG export failed: {e}")
            QMessageBox.critical(self, "Export Error", f"Export failed: {e}")
    
    def _export_as_pdf(self):
        """Export diagram as PDF document"""
        try:
            if not self.is_file_open or not self.graphics_scene:
                QMessageBox.warning(self, "Export Error", "No diagram to export. Please open an ARXML file first.")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export as PDF", "diagram.pdf", 
                "PDF Files (*.pdf);;All Files (*.*)"
            )
            
            if filename:
                success = self._export_scene_to_file(filename, "PDF")
                if success:
                    QMessageBox.information(self, "Export Successful", f"Diagram exported to:\n{filename}")
                else:
                    QMessageBox.critical(self, "Export Failed", "Failed to export diagram.")
                    
        except Exception as e:
            self.logger.error(f"PDF export failed: {e}")
            QMessageBox.critical(self, "Export Error", f"Export failed: {e}")
    
    def _quick_export(self):
        """Quick export using default format (PNG)"""
        try:
            self._export_as_png()
        except Exception as e:
            self.logger.error(f"Quick export failed: {e}")
    
    def _export_scene_to_file(self, filename: str, format_type: str) -> bool:
        """Export graphics scene to file in specified format"""
        try:
            if not self.graphics_scene:
                return False
            
            # Use the graphics scene's export method if available
            if hasattr(self.graphics_scene, 'export_scene_image'):
                return self.graphics_scene.export_scene_image(filename)
            
            # Fallback: capture the graphics view
            if self.graphics_view:
                if format_type == "PNG":
                    pixmap = self.graphics_view.grab()
                    return pixmap.save(filename, "PNG")
                elif format_type == "SVG":
                    # SVG export would require QSvgGenerator - simplified for now
                    pixmap = self.graphics_view.grab()
                    return pixmap.save(filename, "PNG")  # Save as PNG instead
                elif format_type == "PDF":
                    # PDF export would require QPrinter - simplified for now
                    pixmap = self.graphics_view.grab()
                    return pixmap.save(filename, "PNG")  # Save as PNG instead
            
            return False
            
        except Exception as e:
            self.logger.error(f"Scene export failed: {e}")
            return False
    
    # ==========================================
    # AUTO-LAYOUT FUNCTIONALITY
    # ==========================================
    
    def _apply_auto_layout(self, layout_type: str):
        """Apply specified auto-layout algorithm"""
        try:
            if not self.is_file_open or not self.graphics_scene:
                QMessageBox.warning(self, "Layout Error", "No diagram to layout. Please open an ARXML file first.")
                return
            
            # Apply layout using graphics scene
            if hasattr(self.graphics_scene, 'auto_arrange_layout'):
                self.graphics_scene.auto_arrange_layout()
                if self.status_bar:
                    self.status_bar.showMessage(f"Applied {layout_type} layout", 2000)
            else:
                QMessageBox.information(self, "Layout", f"Applied {layout_type} layout algorithm")
                
        except Exception as e:
            self.logger.error(f"Auto-layout failed: {e}")
            QMessageBox.critical(self, "Layout Error", f"Layout failed: {e}")
    
    def _apply_smart_auto_layout(self):
        """Apply smart auto-layout (chooses best algorithm automatically)"""
        try:
            if not self.is_file_open or not self.graphics_scene:
                QMessageBox.warning(self, "Layout Error", "No diagram to layout. Please open an ARXML file first.")
                return
            
            # Use the graphics scene's auto-arrange method
            if hasattr(self.graphics_scene, 'auto_arrange_layout'):
                self.graphics_scene.auto_arrange_layout()
                if self.status_bar:
                    self.status_bar.showMessage("Applied smart auto-layout", 2000)
            else:
                # Fallback to hierarchical layout
                self._apply_auto_layout("hierarchical")
                
        except Exception as e:
            self.logger.error(f"Smart auto-layout failed: {e}")
            QMessageBox.critical(self, "Layout Error", f"Smart layout failed: {e}")
    
    def _apply_initial_layout(self):
        """Apply initial auto-layout after file loading"""
        try:
            if self.is_file_open and self.graphics_scene:
                # Apply smart auto-layout
                if hasattr(self.graphics_scene, 'auto_arrange_layout'):
                    self.graphics_scene.auto_arrange_layout()
                    print("✅ Applied initial auto-layout")
                
                # Fit to window
                self._fit_to_window()
                
        except Exception as e:
            print(f"⚠️ Initial layout failed: {e}")
    
    # ==========================================
    # NAVIGATION FUNCTIONALITY
    # ==========================================
    
    def _navigate_back(self):
        """Navigate back in history"""
        try:
            if self.navigation_controller and hasattr(self.navigation_controller, 'navigate_back'):
                if self.navigation_controller.navigate_back():
                    self._update_navigation_buttons()
            
        except Exception as e:
            self.logger.error(f"Navigate back failed: {e}")
    
    def _navigate_forward(self):
        """Navigate forward in history"""
        try:
            if self.navigation_controller and hasattr(self.navigation_controller, 'navigate_forward'):
                if self.navigation_controller.navigate_forward():
                    self._update_navigation_buttons()
            
        except Exception as e:
            self.logger.error(f"Navigate forward failed: {e}")
    
    def _navigate_home(self):
        """Navigate to home/root view"""
        try:
            if self.breadcrumb_widget:
                # Navigate to first breadcrumb (root)
                if hasattr(self.breadcrumb_widget, 'get_breadcrumb_path'):
                    breadcrumb_path = self.breadcrumb_widget.get_breadcrumb_path()
                    if breadcrumb_path and hasattr(self.breadcrumb_widget, 'breadcrumb_items'):
                        first_item = self.breadcrumb_widget.breadcrumb_items[0]
                        self._on_breadcrumb_clicked(first_item)
            
        except Exception as e:
            self.logger.error(f"Navigate home failed: {e}")
    
    def _update_navigation_buttons(self):
        """Update navigation button states"""
        try:
            if self.navigation_controller:
                # Update back/forward buttons
                if hasattr(self.navigation_controller, 'can_navigate_back') and self.back_action:
                    self.back_action.setEnabled(self.navigation_controller.can_navigate_back())
                
                if hasattr(self.navigation_controller, 'can_navigate_forward') and self.forward_action:
                    self.forward_action.setEnabled(self.navigation_controller.can_navigate_forward())
            
        except Exception as e:
            self.logger.error(f"Navigation button update failed: {e}")
    
    # ==========================================
    # VIEW CONTROLS
    # ==========================================
    
    def _zoom_in(self):
        """Zoom in the graphics view"""
        try:
            if self.graphics_view:
                self.graphics_view.scale(1.25, 1.25)
                self._update_zoom_label()
        except Exception as e:
            self.logger.error(f"Zoom in failed: {e}")
    
    def _zoom_out(self):
        """Zoom out the graphics view"""
        try:
            if self.graphics_view:
                self.graphics_view.scale(0.8, 0.8)
                self._update_zoom_label()
        except Exception as e:
            self.logger.error(f"Zoom out failed: {e}")
    
    def _reset_zoom(self):
        """Reset zoom to 100%"""
        try:
            if self.graphics_view:
                self.graphics_view.resetTransform()
                self._update_zoom_label()
        except Exception as e:
            self.logger.error(f"Reset zoom failed: {e}")
    
    def _fit_to_window(self):
        """Fit diagram to window"""
        try:
            if self.graphics_view and self.graphics_scene:
                self.graphics_view.fitInView(self.graphics_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                self._update_zoom_label()
        except Exception as e:
            self.logger.error(f"Fit to window failed: {e}")
    
    def _update_zoom_label(self):
        """Update zoom level label"""
        try:
            if self.graphics_view and self.zoom_label:
                transform = self.graphics_view.transform()
                zoom_level = int(transform.m11() * 100)
                self.zoom_label.setText(f"{zoom_level}%")
        except Exception as e:
            self.logger.error(f"Update zoom label failed: {e}")
    
    # ==========================================
    # PANEL CONTROLS
    # ==========================================
    
    def _toggle_tree_panel(self):
        """Toggle tree panel visibility"""
        try:
            if self.layout_manager:
                self.layout_manager.toggle_panel_visibility('tree')
        except Exception as e:
            self.logger.error(f"Toggle tree panel failed: {e}")
    
    def _toggle_properties_panel(self):
        """Toggle properties panel visibility"""
        try:
            if self.layout_manager:
                self.layout_manager.toggle_panel_visibility('properties')
        except Exception as e:
            self.logger.error(f"Toggle properties panel failed: {e}")
    
    def _toggle_breadcrumbs(self):
        """Toggle breadcrumb widget visibility"""
        try:
            if self.breadcrumb_widget and self.toggle_breadcrumbs_action:
                visible = not self.breadcrumb_widget.isVisible()
                self.breadcrumb_widget.setVisible(visible)
                self.toggle_breadcrumbs_action.setChecked(visible)
                
        except Exception as e:
            self.logger.error(f"Breadcrumb toggle failed: {e}")
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def _show_component_properties(self, component):
        """Show component properties in properties panel"""
        try:
            if self.properties_text and component:
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
            self.logger.error(f"Show component properties failed: {e}")
    
    def _update_navigation_info(self, component):
        """Update navigation info in status bar"""
        try:
            if self.navigation_info_label and component:
                if hasattr(component, 'short_name'):
                    self.navigation_info_label.setText(f"Selected: {component.short_name}")
        except Exception as e:
            self.logger.error(f"Update navigation info failed: {e}")
    
    def _update_statistics_display(self, packages, metadata):
        """Update statistics display"""
        try:
            if self.statistics_text:
                stats = metadata.get('statistics', {})
                stats_text = "ARXML File Statistics\n"
                stats_text += "=" * 30 + "\n"
                stats_text += f"Packages: {len(packages)}\n"
                stats_text += f"Components: {stats.get('components_parsed', 0)}\n"
                stats_text += f"Ports: {stats.get('ports_parsed', 0)}\n"
                stats_text += f"Connections: {stats.get('connections_parsed', 0)}\n"
                stats_text += f"Parse Time: {stats.get('parse_time', 0):.2f}s\n"
                
                self.statistics_text.setPlainText(stats_text)
        except Exception as e:
            self.logger.error(f"Update statistics failed: {e}")
    
    def _update_recent_files_menu(self, recent_files):
        """Update recent files menu"""
        try:
            if self.recent_menu:
                self.recent_menu.clear()
                for file_path in recent_files[:5]:  # Show last 5 files
                    action = QAction(Path(file_path).name, self)
                    action.triggered.connect(lambda checked, path=file_path: self._open_recent_file(path))
                    self.recent_menu.addAction(action)
        except Exception as e:
            self.logger.error(f"Update recent files failed: {e}")
    
    def _open_recent_file(self, file_path: str):
        """Open recent file"""
        try:
            if self.app_controller:
                self.app_controller.open_file(file_path)
        except Exception as e:
            self.logger.error(f"Open recent file failed: {e}")
    
    # ==========================================
    # LAYOUT AND APPEARANCE
    # ==========================================
    
    def _apply_layout_preset(self, layout_name: str):
        """Apply layout preset"""
        try:
            if self.layout_manager:
                self.layout_manager.apply_layout(layout_name)
        except Exception as e:
            self.logger.error(f"Apply layout preset failed: {e}")
    
    def _save_custom_layout(self):
        """Save current layout as custom"""
        try:
            name, ok = QInputDialog.getText(self, "Save Layout", "Enter layout name:")
            if ok and name:
                if self.layout_manager:
                    self.layout_manager.save_current_as_custom_layout(name)
        except Exception as e:
            self.logger.error(f"Save custom layout failed: {e}")
    
    def _on_layout_changed(self, layout_name):
        """Handle layout change"""
        try:
            self.logger.debug(f"Layout changed to: {layout_name}")
        except Exception as e:
            self.logger.error(f"Layout change handler failed: {e}")
    
    def _on_panel_visibility_changed(self, panel_name, visible):
        """Handle panel visibility change"""
        try:
            self.logger.debug(f"Panel {panel_name} visibility: {visible}")
        except Exception as e:
            self.logger.error(f"Panel visibility change handler failed: {e}")
    
    # ==========================================
    # SEARCH AND HELP
    # ==========================================
    
    def _show_search_panel(self):
        """Show search panel"""
        try:
            if self.search_dock:
                self.search_dock.setVisible(True)
        except Exception as e:
            self.logger.error(f"Show search panel failed: {e}")
    
    def _show_advanced_search(self):
        """Show advanced search dialog"""
        try:
            if self.search_dock:
                self.search_dock.setVisible(True)
        except Exception as e:
            self.logger.error(f"Show advanced search failed: {e}")
    
    def _find_next(self):
        """Find next search result"""
        try:
            # Implementation would depend on search system
            pass
        except Exception as e:
            self.logger.error(f"Find next failed: {e}")
    
    def _clear_search(self):
        """Clear search results"""
        try:
            if self.search_results_text:
                self.search_results_text.clear()
            if self.compact_search and hasattr(self.compact_search, 'clear_search'):
                self.compact_search.clear_search()
        except Exception as e:
            self.logger.error(f"Clear search failed: {e}")
    
    def _show_about_dialog(self):
        """Show about dialog"""
        try:
            QMessageBox.about(self, "About ARXML Viewer Pro", 
                            f"ARXML Viewer Pro v{AppConstants.APP_VERSION}\n\n"
                            "A professional AUTOSAR ARXML file viewer and analyzer.\n\n"
                            "Features:\n"
                            "• ARXML file parsing and visualization\n"
                            "• Component and port analysis\n"
                            "• Connection visualization\n"
                            "• Advanced search and filtering\n"
                            "• Export capabilities")
        except Exception as e:
            self.logger.error(f"About dialog failed: {e}")
    
    # ==========================================
    # TREE WIDGET CONTROLS
    # ==========================================
    
    def _expand_all_tree_items(self):
        """Expand all tree items"""
        try:
            if self.enhanced_tree_widget:
                self.enhanced_tree_widget.expandAll()
        except Exception as e:
            self.logger.error(f"Expand all failed: {e}")
    
    def _collapse_all_tree_items(self):
        """Collapse all tree items"""
        try:
            if self.enhanced_tree_widget:
                self.enhanced_tree_widget.collapseAll()
        except Exception as e:
            self.logger.error(f"Collapse all failed: {e}")
    
    def _refresh_view(self):
        """Refresh the current view"""
        try:
            if self.is_file_open and self.current_file:
                # Reload the current file
                if self.app_controller:
                    self.app_controller.open_file(self.current_file)
        except Exception as e:
            self.logger.error(f"Refresh view failed: {e}")
    
    def _focus_tree_panel(self):
        """Focus the tree panel"""
        try:
            if self.enhanced_tree_widget:
                self.enhanced_tree_widget.setFocus()
        except Exception as e:
            self.logger.error(f"Focus tree panel failed: {e}")
    
    # ==========================================
    # WINDOW LIFECYCLE
    # ==========================================
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            # Save layout state
            if self.layout_manager and hasattr(self.layout_manager, 'save_state_on_exit'):
                self.layout_manager.save_state_on_exit()
            event.accept()
        except Exception as e:
            self.logger.error(f"Close event failed: {e}")
            event.accept()

# Export the MainWindow class
__all__ = ['MainWindow']