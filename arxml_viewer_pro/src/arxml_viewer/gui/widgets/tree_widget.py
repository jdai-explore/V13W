# src/arxml_viewer/gui/widgets/tree_widget.py
"""
Enhanced Tree Widget - Custom tree widget with advanced features
Provides hierarchical navigation with search, filtering, and context menus
"""

from typing import Dict, List, Optional, Set, Any
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QAction,
    QLineEdit, QVBoxLayout, QWidget, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QFrame, QToolButton, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QMimeData, QUrl
from PyQt5.QtGui import QIcon, QFont, QBrush, QColor, QDrag, QPainter

from ...models.component import Component, ComponentType
from ...models.port import Port, PortType
from ...models.package import Package
from ...utils.constants import AppConstants, UIConstants
from ...utils.logger import get_logger

class TreeItemType:
    """Tree item type constants"""
    PACKAGE = "package"
    COMPONENT = "component"
    PORT = "port"
    FOLDER = "folder"

class EnhancedTreeWidgetItem(QTreeWidgetItem):
    """Enhanced tree widget item with additional functionality"""
    
    def __init__(self, parent=None, item_type: str = TreeItemType.FOLDER):
        super().__init__(parent)
        
        self.item_type = item_type
        self.data_object: Optional[Any] = None
        self.is_filtered = False
        self.match_score = 0.0
        
        # Set default properties
        self.setFlags(self.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
        # Setup based on type
        self._setup_for_type()
    
    def _setup_for_type(self):
        """Setup item based on type"""
        if self.item_type == TreeItemType.PACKAGE:
            self.setFlags(self.flags() | Qt.ItemIsDropEnabled)
        elif self.item_type == TreeItemType.COMPONENT:
            self.setFlags(self.flags() | Qt.ItemIsDragEnabled)
        elif self.item_type == TreeItemType.PORT:
            self.setFlags(self.flags() | Qt.ItemIsDragEnabled)
    
    def set_data_object(self, obj: Any):
        """Set the data object this item represents"""
        self.data_object = obj
        
        if obj:
            # Update display text
            display_name = getattr(obj, 'short_name', 'Unknown')
            self.setText(0, display_name)
            
            # Set tooltip
            self.setToolTip(0, self._generate_tooltip())
            
            # Set icon based on object type
            self._set_icon_for_object()
    
    def _generate_tooltip(self) -> str:
        """Generate tooltip text for this item"""
        if not self.data_object:
            return ""
        
        obj = self.data_object
        tooltip_parts = []
        
        if isinstance(obj, Component):
            tooltip_parts.append(f"<b>{obj.short_name}</b>")
            tooltip_parts.append(f"Type: {obj.component_type.value}")
            tooltip_parts.append(f"Ports: {obj.port_count}")
            if obj.desc:
                tooltip_parts.append(f"Description: {obj.desc}")
        
        elif isinstance(obj, Port):
            tooltip_parts.append(f"<b>{obj.short_name}</b>")
            tooltip_parts.append(f"Type: {obj.port_type.value}")
            if obj.interface_ref:
                tooltip_parts.append(f"Interface: {obj.interface_ref}")
            if obj.desc:
                tooltip_parts.append(f"Description: {obj.desc}")
        
        elif isinstance(obj, Package):
            tooltip_parts.append(f"<b>{obj.short_name}</b>")
            tooltip_parts.append(f"Components: {len(obj.components)}")
            tooltip_parts.append(f"Sub-packages: {len(obj.sub_packages)}")
            if obj.desc:
                tooltip_parts.append(f"Description: {obj.desc}")
        
        return "<br>".join(tooltip_parts)
    
    def _set_icon_for_object(self):
        """Set icon based on object type"""
        # For now, use text indicators
        # Icons can be added later when icon resources are available
        if isinstance(self.data_object, Component):
            if self.data_object.component_type == ComponentType.APPLICATION:
                self.setText(0, f"📱 {self.data_object.short_name}")
            elif self.data_object.component_type == ComponentType.COMPOSITION:
                self.setText(0, f"📦 {self.data_object.short_name}")
            elif self.data_object.component_type == ComponentType.SERVICE:
                self.setText(0, f"🔧 {self.data_object.short_name}")
            else:
                self.setText(0, f"⚙️ {self.data_object.short_name}")
        
        elif isinstance(self.data_object, Port):
            if self.data_object.is_provided:
                self.setText(0, f"🟢 {self.data_object.short_name}")
            else:
                self.setText(0, f"🔴 {self.data_object.short_name}")
        
        elif isinstance(self.data_object, Package):
            self.setText(0, f"📁 {self.data_object.short_name}")
    
    def update_highlighting(self, search_terms: List[str]):
        """Update highlighting based on search terms"""
        if not search_terms or not self.data_object:
            self.setBackground(0, QBrush())
            return
        
        # Simple highlighting - check if any search term matches
        text_to_search = [
            getattr(self.data_object, 'short_name', ''),
            getattr(self.data_object, 'desc', ''),
        ]
        
        found_match = False
        for term in search_terms:
            for text in text_to_search:
                if term.lower() in text.lower():
                    found_match = True
                    break
            if found_match:
                break
        
        if found_match:
            # Highlight background
            self.setBackground(0, QBrush(QColor(255, 255, 0, 50)))  # Light yellow
        else:
            self.setBackground(0, QBrush())

class TreeSearchWidget(QWidget):
    """Search widget for tree filtering"""
    
    search_changed = pyqtSignal(str)
    filter_changed = pyqtSignal(str)
    clear_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup search widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Search row
        search_layout = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search components, ports, packages...")
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.returnPressed.connect(self._on_search_submitted)
        search_layout.addWidget(self.search_input)
        
        # Clear button
        self.clear_button = QPushButton("✕")
        self.clear_button.setMaximumWidth(30)
        self.clear_button.setToolTip("Clear search")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        search_layout.addWidget(self.clear_button)
        
        layout.addLayout(search_layout)
        
        # Filter row
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter:"))
        
        # Filter combobox
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Items",
            "Components Only",
            "Ports Only", 
            "Packages Only",
            "Application Components",
            "Composition Components",
            "Service Components"
        ])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Search timer for delayed search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._emit_search_changed)
        
        # Style the widget
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to search widget"""
        self.setStyleSheet("""
            TreeSearchWidget {
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QLineEdit {
                background-color: #505050;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 4px;
                color: white;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666;
                border-radius: 3px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QComboBox {
                background-color: #505050;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 2px 4px;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
    
    def _on_search_changed(self, text: str):
        """Handle search input change with delay"""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms delay
    
    def _emit_search_changed(self):
        """Emit search changed signal"""
        text = self.search_input.text().strip()
        self.search_changed.emit(text)
    
    def _on_search_submitted(self):
        """Handle search input submission (Enter key)"""
        self.search_timer.stop()
        self._emit_search_changed()
    
    def _on_filter_changed(self, filter_text: str):
        """Handle filter change"""
        self.filter_changed.emit(filter_text)
    
    def _on_clear_clicked(self):
        """Handle clear button click"""
        self.search_input.clear()
        self.filter_combo.setCurrentIndex(0)
        self.clear_requested.emit()
    
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_input.text().strip()
    
    def get_filter_text(self) -> str:
        """Get current filter text"""
        return self.filter_combo.currentText()
    
    def set_search_text(self, text: str):
        """Set search text"""
        self.search_input.setText(text)

class EnhancedTreeWidget(QTreeWidget):
    """
    Enhanced tree widget with search, filtering, and context menus
    Provides comprehensive navigation for ARXML components
    """
    
    # Signals
    item_selected = pyqtSignal(object)  # Selected data object
    item_activated = pyqtSignal(object)  # Activated data object (double-click)
    context_menu_requested = pyqtSignal(object, object)  # data object, QPoint
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        
        # Data
        self.packages: List[Package] = []
        self.all_items: List[EnhancedTreeWidgetItem] = []
        self.filtered_items: Set[EnhancedTreeWidgetItem] = set()
        
        # Search and filter state
        self.current_search_terms: List[str] = []
        self.current_filter: str = "All Items"
        
        # Setup UI
        self._setup_tree()
        self._setup_context_menu()
        
        # Connect signals
        self._connect_signals()
    
    def _setup_tree(self):
        """Setup tree widget properties"""
        # Header
        self.setHeaderLabels(["Components & Packages"])
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Behavior
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.setExpandsOnDoubleClick(False)  # Handle double-click manually
        self.setSortingEnabled(False)
        
        # Selection
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setSelectionBehavior(QTreeWidget.SelectRows)
        
        # Drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDrop)
        
        # Styling
        self._apply_tree_styling()
    
    def _apply_tree_styling(self):
        """Apply styling to tree widget"""
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555;
                selection-background-color: #4a90e2;
                selection-color: white;
                outline: none;
            }
            QTreeWidget::item {
                height: 24px;
                border: none;
                padding: 2px;
            }
            QTreeWidget::item:hover {
                background-color: #4a4a4a;
            }
            QTreeWidget::item:selected {
                background-color: #4a90e2;
            }
            QTreeWidget::item:selected:active {
                background-color: #4a90e2;
            }
            QTreeWidget::item:selected:!active {
                background-color: #666;
            }
        """)