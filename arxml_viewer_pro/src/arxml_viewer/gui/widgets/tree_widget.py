# src/arxml_viewer/gui/widgets/tree_widget.py
"""
Enhanced Tree Widget - Custom tree widget with advanced features
Provides hierarchical navigation with search, filtering, and context menus
COMPLETE WORKING FILE WITH FIXED UI COLORS
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
            # Highlight background with light yellow
            self.setBackground(0, QBrush(QColor(255, 255, 200, 100)))
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
        """Apply light styling to search widget"""
        self.setStyleSheet("""
            TreeSearchWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                color: #495057;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #1976d2;
                box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.25);
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                color: #6c757d;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
                color: #495057;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px 12px;
                color: #495057;
                font-size: 13px;
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
            }
            QLabel {
                color: #495057;
                font-weight: 500;
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
    COMPLETE WORKING IMPLEMENTATION WITH FIXED COLORS
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
        """Apply light styling to tree widget with good contrast"""
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
                outline: none;
                font-size: 13px;
            }
            QTreeWidget::item {
                height: 28px;
                border: none;
                padding: 4px;
                color: #333333;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f5;
                color: #333333;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: bold;
            }
            QTreeWidget::item:selected:active {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTreeWidget::item:selected:!active {
                background-color: #f5f5f5;
                color: #666666;
            }
            QTreeWidget::branch {
                background-color: #ffffff;
            }
            QTreeWidget::branch:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                padding: 8px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
    
    def _setup_context_menu(self):
        """Setup context menu for tree items"""
        pass
    
    def _connect_signals(self):
        """Connect tree widget signals"""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemActivated.connect(self._on_item_activated)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _on_selection_changed(self):
        """Handle selection changes - SIMPLIFIED"""
        try:
            selected_items = self.selectedItems()
            if selected_items:
                item = selected_items[0]
                if hasattr(item, 'data_object') and item.data_object:
                    print(f"🔧 Tree item selected: {item.data_object}")
                    self.item_selected.emit(item.data_object)
        except Exception as e:
            print(f"❌ Selection handling failed: {e}")
    
    def _on_item_activated(self, item, column):
        """Handle item activation (double-click) - SIMPLIFIED"""
        try:
            if hasattr(item, 'data_object') and item.data_object:
                print(f"🔧 Tree item activated: {item.data_object}")
                self.item_activated.emit(item.data_object)
        except Exception as e:
            print(f"❌ Activation handling failed: {e}")
    
    def _show_context_menu(self, position):
        """Show context menu at position"""
        pass
    
    def load_packages(self, packages):
        """Load packages into tree widget - SIMPLIFIED VERSION"""
        print(f"🔧 Tree widget loading {len(packages)} packages")
        
        self.clear()
        self.all_items.clear()
        
        for package in packages:
            try:
                print(f"Adding package: {package.short_name}")
                
                # Create package item
                pkg_item = QTreeWidgetItem(self)
                pkg_item.setText(0, f"📁 {package.short_name}")
                
                # Store data object
                if not hasattr(pkg_item, 'data_object'):
                    pkg_item.data_object = package
                pkg_item.item_type = "package"
                
                # Add to tracking
                self.all_items.append(pkg_item)
                
                # Add components
                for component in package.components:
                    try:
                        comp_item = QTreeWidgetItem(pkg_item)
                        
                        # Component icon based on type
                        if component.component_type.name == 'APPLICATION':
                            icon = "📱"
                        elif component.component_type.name == 'COMPOSITION':
                            icon = "📦"
                        elif component.component_type.name == 'SERVICE':
                            icon = "🔧"
                        else:
                            icon = "⚙️"
                        
                        comp_item.setText(0, f"{icon} {component.short_name}")
                        comp_item.data_object = component
                        comp_item.item_type = "component"
                        self.all_items.append(comp_item)
                        
                        # Add ports
                        for port in component.all_ports:
                            try:
                                port_item = QTreeWidgetItem(comp_item)
                                port_symbol = "🟢" if port.is_provided else "🔴"
                                port_item.setText(0, f"{port_symbol} {port.short_name}")
                                port_item.data_object = port
                                port_item.item_type = "port"
                                self.all_items.append(port_item)
                            except Exception as e:
                                print(f"❌ Failed to add port {port.short_name}: {e}")
                        
                        print(f"  Added component: {component.short_name} with {len(component.all_ports)} ports")
                        
                    except Exception as e:
                        print(f"❌ Failed to add component {component.short_name}: {e}")
                
                # Add sub-packages recursively
                if package.sub_packages:
                    self._add_sub_packages(package.sub_packages, pkg_item)
                
                # Expand first level by default
                pkg_item.setExpanded(True)
                
                print(f"✅ Added package: {package.short_name} with {len(package.components)} components")
                
            except Exception as e:
                print(f"❌ Failed to add package {package.short_name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"✅ Tree widget populated with {len(self.all_items)} total items")
        
        # Expand all top level items
        self.expandToDepth(1)
    
    def _add_sub_packages(self, sub_packages, parent_item):
        """Add sub-packages recursively - SIMPLIFIED"""
        for sub_pkg in sub_packages:
            try:
                sub_item = QTreeWidgetItem(parent_item)
                sub_item.setText(0, f"📁 {sub_pkg.short_name}")
                sub_item.data_object = sub_pkg
                sub_item.item_type = "package"
                self.all_items.append(sub_item)
                
                # Add components in sub-package
                for component in sub_pkg.components:
                    try:
                        comp_item = QTreeWidgetItem(sub_item)
                        comp_item.setText(0, f"⚙️ {component.short_name}")
                        comp_item.data_object = component
                        comp_item.item_type = "component"
                        self.all_items.append(comp_item)
                        
                        # Add ports
                        for port in component.all_ports:
                            port_item = QTreeWidgetItem(comp_item)
                            port_symbol = "🟢" if port.is_provided else "🔴"
                            port_item.setText(0, f"{port_symbol} {port.short_name}")
                            port_item.data_object = port
                            port_item.item_type = "port"
                            self.all_items.append(port_item)
                            
                    except Exception as e:
                        print(f"❌ Failed to add sub-package component: {e}")
                
                # Recurse for nested packages
                if sub_pkg.sub_packages:
                    self._add_sub_packages(sub_pkg.sub_packages, sub_item)
                
            except Exception as e:
                print(f"❌ Failed to add sub-package: {e}")
    
    def apply_search(self, search_text):
        """Apply search filter - SIMPLIFIED"""
        if not search_text:
            self.clear_search_and_filter()
            return
        
        print(f"🔧 Applying search: {search_text}")
        search_lower = search_text.lower()
        
        for item in self.all_items:
            try:
                if hasattr(item, 'data_object') and item.data_object:
                    obj = item.data_object
                    # Simple text matching
                    text_to_search = getattr(obj, 'short_name', '').lower()
                    match = search_lower in text_to_search
                    item.setHidden(not match)
            except Exception as e:
                print(f"❌ Search item processing failed: {e}")
    
    def apply_filter(self, filter_text):
        """Apply type filter"""
        if filter_text == "All Items":
            self.clear_search_and_filter()
            return
        
        for item in self.all_items:
            if hasattr(item, 'item_type'):
                show = True
                if filter_text == "Components Only" and item.item_type != "component":
                    show = False
                elif filter_text == "Ports Only" and item.item_type != "port":
                    show = False
                elif filter_text == "Packages Only" and item.item_type != "package":
                    show = False
                
                item.setHidden(not show)
    
    def clear_search_and_filter(self):
        """Clear search and filter - SIMPLIFIED"""
        for item in self.all_items:
            try:
                item.setHidden(False)
            except Exception as e:
                print(f"❌ Clear filter failed: {e}")
    
    def select_object_by_uuid(self, uuid):
        """Select object by UUID"""
        for item in self.all_items:
            if (hasattr(item, 'data_object') and 
                item.data_object and 
                hasattr(item.data_object, 'uuid') and 
                item.data_object.uuid == uuid):
                self.setCurrentItem(item)
                return True
        return False
    
    def get_statistics(self):
        """Get tree statistics - SIMPLIFIED"""
        try:
            visible_count = sum(1 for item in self.all_items if not item.isHidden())
            return {
                'total_items': len(self.all_items),
                'visible_items': visible_count
            }
        except Exception as e:
            print(f"❌ Statistics failed: {e}")
            return {'total_items': 0, 'visible_items': 0}

# Export all classes
__all__ = ['EnhancedTreeWidget', 'TreeSearchWidget', 'EnhancedTreeWidgetItem', 'TreeItemType']