# src/arxml_viewer/gui/widgets/breadcrumb_widget.py
"""
Breadcrumb Navigation Widget - Shows navigation path for ARXML Viewer
Provides clickable breadcrumb navigation for hierarchical component navigation
"""

from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy, QToolTip, QScrollArea, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QFont, QFontMetrics, QPalette, QIcon, QPixmap, QPainter

from ...utils.logger import get_logger

class BreadcrumbItem:
    """Represents a single breadcrumb item"""
    
    def __init__(self, name: str, display_name: str = None, item_type: str = "component", 
                 item_uuid: str = None, tooltip: str = None):
        self.name = name
        self.display_name = display_name or name
        self.item_type = item_type  # 'package', 'component', 'composition'
        self.item_uuid = item_uuid
        self.tooltip = tooltip or f"{item_type.title()}: {name}"
        
    def __str__(self):
        return self.display_name
    
    def __repr__(self):
        return f"BreadcrumbItem({self.name}, {self.item_type})"

class BreadcrumbButton(QPushButton):
    """Custom button for breadcrumb items with hover effects"""
    
    item_clicked = pyqtSignal(object)  # BreadcrumbItem
    
    def __init__(self, breadcrumb_item: BreadcrumbItem, is_current: bool = False):
        super().__init__()
        
        self.breadcrumb_item = breadcrumb_item
        self.is_current = is_current
        
        # Set up button
        self.setText(breadcrumb_item.display_name)
        self.setToolTip(breadcrumb_item.tooltip)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        
        # Connect signal
        self.clicked.connect(lambda: self.item_clicked.emit(self.breadcrumb_item))
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply custom styling to breadcrumb button"""
        if self.is_current:
            # Current item - not clickable, different style
            self.setEnabled(False)
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #2c3e50;
                    font-weight: bold;
                    padding: 4px 8px;
                    text-align: left;
                }
            """)
        else:
            # Clickable breadcrumb item
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #3498db;
                    padding: 4px 8px;
                    text-align: left;
                    text-decoration: underline;
                }
                QPushButton:hover {
                    background-color: #e8f4fd;
                    color: #2980b9;
                    border-radius: 3px;
                }
                QPushButton:pressed {
                    background-color: #d6eaf8;
                    color: #1f618d;
                }
            """)
    
    def get_preferred_size(self):
        """Get preferred size for this button"""
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.text())
        return text_width + 16  # 8px padding on each side

class BreadcrumbSeparator(QLabel):
    """Separator between breadcrumb items"""
    
    def __init__(self):
        super().__init__("►")  # Arrow separator
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 10px;
                padding: 0 4px;
                background-color: transparent;
            }
        """)
        self.setFixedWidth(20)

class BreadcrumbWidget(QWidget):
    """
    Main breadcrumb navigation widget
    Shows clickable navigation path with separators
    """
    
    # Signals
    breadcrumb_clicked = pyqtSignal(object)  # BreadcrumbItem
    navigation_requested = pyqtSignal(str, str)  # item_type, item_uuid
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        
        # Navigation state
        self.breadcrumb_items: List[BreadcrumbItem] = []
        self.max_visible_items = 6  # Maximum breadcrumb items to show
        
        # UI components
        self.buttons: List[BreadcrumbButton] = []
        self.separators: List[BreadcrumbSeparator] = []
        
        # Setup UI
        self._setup_ui()
        self._apply_widget_styling()
        
        # Add default "Root" item
        self.set_root_item("System", "System Root", "system")
    
    def _setup_ui(self):
        """Setup the breadcrumb widget UI"""
        # Main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(8, 4, 8, 4)
        self.main_layout.setSpacing(0)
        
        # Scroll area for long breadcrumbs
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_area.setMaximumHeight(32)
        
        # Content widget for scroll area
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_layout.addStretch()  # Push items to the left
        
        self.scroll_area.setWidget(self.content_widget)
        
        # Add scroll area to main layout
        self.main_layout.addWidget(self.scroll_area)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(40)
    
    def _apply_widget_styling(self):
        """Apply styling to the widget"""
        self.setStyleSheet("""
            BreadcrumbWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
    
    def set_root_item(self, name: str, display_name: str = None, item_type: str = "system"):
        """Set the root breadcrumb item"""
        root_item = BreadcrumbItem(
            name=name,
            display_name=display_name or name,
            item_type=item_type,
            tooltip=f"Navigate to {display_name or name}"
        )
        self.breadcrumb_items = [root_item]
        self._rebuild_breadcrumbs()
    
    def navigate_to(self, breadcrumb_item: BreadcrumbItem):
        """Navigate to a specific breadcrumb item"""
        try:
            # Find the item in current breadcrumbs
            if breadcrumb_item in self.breadcrumb_items:
                # Remove all items after the clicked one
                item_index = self.breadcrumb_items.index(breadcrumb_item)
                self.breadcrumb_items = self.breadcrumb_items[:item_index + 1]
                
                # Rebuild UI
                self._rebuild_breadcrumbs()
                
                # Emit signals
                self.breadcrumb_clicked.emit(breadcrumb_item)
                if breadcrumb_item.item_uuid:
                    self.navigation_requested.emit(breadcrumb_item.item_type, breadcrumb_item.item_uuid)
                
                self.logger.debug(f"Navigated to: {breadcrumb_item.name}")
            
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
    
    def add_breadcrumb(self, name: str, display_name: str = None, item_type: str = "component",
                      item_uuid: str = None, tooltip: str = None):
        """Add a new breadcrumb item to the path"""
        try:
            breadcrumb_item = BreadcrumbItem(
                name=name,
                display_name=display_name or name,
                item_type=item_type,
                item_uuid=item_uuid,
                tooltip=tooltip
            )
            
            # Don't add duplicates
            if self.breadcrumb_items and self.breadcrumb_items[-1].name == name:
                return
            
            self.breadcrumb_items.append(breadcrumb_item)
            
            # Limit the number of visible items
            if len(self.breadcrumb_items) > self.max_visible_items:
                # Keep root and recent items
                self.breadcrumb_items = [self.breadcrumb_items[0]] + self.breadcrumb_items[-(self.max_visible_items-1):]
            
            self._rebuild_breadcrumbs()
            self.logger.debug(f"Added breadcrumb: {name}")
            
        except Exception as e:
            self.logger.error(f"Failed to add breadcrumb: {e}")
    
    def set_breadcrumb_path(self, path_items: List[Dict[str, Any]]):
        """Set complete breadcrumb path from list of items"""
        try:
            self.breadcrumb_items = []
            
            for item_data in path_items:
                breadcrumb_item = BreadcrumbItem(
                    name=item_data.get('name', 'Unknown'),
                    display_name=item_data.get('display_name'),
                    item_type=item_data.get('item_type', 'component'),
                    item_uuid=item_data.get('item_uuid'),
                    tooltip=item_data.get('tooltip')
                )
                self.breadcrumb_items.append(breadcrumb_item)
            
            self._rebuild_breadcrumbs()
            self.logger.debug(f"Set breadcrumb path with {len(path_items)} items")
            
        except Exception as e:
            self.logger.error(f"Failed to set breadcrumb path: {e}")
    
    def _rebuild_breadcrumbs(self):
        """Rebuild the breadcrumb UI"""
        try:
            # Clear existing widgets
            self._clear_breadcrumbs()
            
            if not self.breadcrumb_items:
                return
            
            # Create breadcrumb buttons and separators
            for i, item in enumerate(self.breadcrumb_items):
                # Create button
                is_current = (i == len(self.breadcrumb_items) - 1)
                button = BreadcrumbButton(item, is_current)
                button.item_clicked.connect(self.navigate_to)
                
                self.buttons.append(button)
                self.content_layout.addWidget(button)
                
                # Add separator (except for last item)
                if i < len(self.breadcrumb_items) - 1:
                    separator = BreadcrumbSeparator()
                    self.separators.append(separator)
                    self.content_layout.addWidget(separator)
            
            # Add stretch to push items to the left
            self.content_layout.addStretch()
            
            # Scroll to the end to show current item
            QTimer.singleShot(50, self._scroll_to_end)
            
        except Exception as e:
            self.logger.error(f"Failed to rebuild breadcrumbs: {e}")
    
    def _clear_breadcrumbs(self):
        """Clear all breadcrumb widgets"""
        try:
            # Remove all buttons
            for button in self.buttons:
                self.content_layout.removeWidget(button)
                button.deleteLater()
            self.buttons.clear()
            
            # Remove all separators
            for separator in self.separators:
                self.content_layout.removeWidget(separator)
                separator.deleteLater()
            self.separators.clear()
            
        except Exception as e:
            self.logger.error(f"Failed to clear breadcrumbs: {e}")
    
    def _scroll_to_end(self):
        """Scroll to show the rightmost (current) breadcrumb"""
        try:
            scrollbar = self.scroll_area.horizontalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            self.logger.error(f"Failed to scroll to end: {e}")
    
    def get_current_item(self) -> Optional[BreadcrumbItem]:
        """Get the current (last) breadcrumb item"""
        return self.breadcrumb_items[-1] if self.breadcrumb_items else None
    
    def get_breadcrumb_path(self) -> List[str]:
        """Get breadcrumb path as list of names"""
        return [item.name for item in self.breadcrumb_items]
    
    def get_breadcrumb_path_display(self) -> List[str]:
        """Get breadcrumb path as list of display names"""
        return [item.display_name for item in self.breadcrumb_items]
    
    def clear_breadcrumbs(self):
        """Clear all breadcrumbs except root"""
        try:
            if self.breadcrumb_items:
                # Keep only the root item
                self.breadcrumb_items = self.breadcrumb_items[:1]
                self._rebuild_breadcrumbs()
                self.logger.debug("Cleared breadcrumbs to root")
        except Exception as e:
            self.logger.error(f"Failed to clear breadcrumbs: {e}")
    
    def go_back(self):
        """Navigate back one level"""
        try:
            if len(self.breadcrumb_items) > 1:
                # Remove last item
                removed_item = self.breadcrumb_items.pop()
                self._rebuild_breadcrumbs()
                
                # Emit navigation to previous item
                if self.breadcrumb_items:
                    current_item = self.breadcrumb_items[-1]
                    self.breadcrumb_clicked.emit(current_item)
                    if current_item.item_uuid:
                        self.navigation_requested.emit(current_item.item_type, current_item.item_uuid)
                
                self.logger.debug(f"Navigated back from: {removed_item.name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to go back: {e}")
            return False
    
    def can_go_back(self) -> bool:
        """Check if can navigate back"""
        return len(self.breadcrumb_items) > 1
    
    def set_max_visible_items(self, max_items: int):
        """Set maximum number of visible breadcrumb items"""
        self.max_visible_items = max(2, max_items)  # Minimum 2 items
        
        # Rebuild if we have too many items
        if len(self.breadcrumb_items) > self.max_visible_items:
            self.breadcrumb_items = [self.breadcrumb_items[0]] + self.breadcrumb_items[-(self.max_visible_items-1):]
            self._rebuild_breadcrumbs()
    
    def get_breadcrumb_info(self) -> Dict[str, Any]:
        """Get information about current breadcrumb state"""
        return {
            'total_items': len(self.breadcrumb_items),
            'current_item': self.get_current_item().name if self.breadcrumb_items else None,
            'can_go_back': self.can_go_back(),
            'path': self.get_breadcrumb_path(),
            'path_display': self.get_breadcrumb_path_display()
        }
    
    def update_current_item_tooltip(self, tooltip: str):
        """Update tooltip of current breadcrumb item"""
        try:
            if self.breadcrumb_items and self.buttons:
                current_button = self.buttons[-1]
                current_button.setToolTip(tooltip)
                self.breadcrumb_items[-1].tooltip = tooltip
        except Exception as e:
            self.logger.error(f"Failed to update tooltip: {e}")

class CompactBreadcrumbWidget(BreadcrumbWidget):
    """Compact version of breadcrumb widget for toolbars"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Override styling for compact version
        self.setFixedHeight(28)
        self.max_visible_items = 4
        
        # Compact styling
        self.setStyleSheet("""
            CompactBreadcrumbWidget {
                background-color: transparent;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
    
    def _setup_ui(self):
        """Setup compact UI"""
        super()._setup_ui()
        
        # Adjust layout for compact version
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.scroll_area.setMaximumHeight(24)

# Utility functions
def create_breadcrumb_from_navigation_path(navigation_path: List[Dict[str, Any]]) -> List[BreadcrumbItem]:
    """Create breadcrumb items from navigation path"""
    breadcrumbs = []
    
    for item_data in navigation_path:
        breadcrumb = BreadcrumbItem(
            name=item_data.get('name', 'Unknown'),
            display_name=item_data.get('display_name'),
            item_type=item_data.get('type', 'component'),
            item_uuid=item_data.get('uuid'),
            tooltip=item_data.get('description')
        )
        breadcrumbs.append(breadcrumb)
    
    return breadcrumbs

def format_breadcrumb_path(breadcrumb_items: List[BreadcrumbItem], separator: str = " > ") -> str:
    """Format breadcrumb path as string"""
    return separator.join(item.display_name for item in breadcrumb_items)