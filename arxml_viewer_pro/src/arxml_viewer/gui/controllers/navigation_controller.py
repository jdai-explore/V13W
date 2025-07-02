# src/arxml_viewer/gui/controllers/navigation_controller.py
"""
Navigation Controller - Coordinates tree-diagram navigation and selection
Manages synchronization between tree widget and graphics scene
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from ...models.component import Component
from ...models.port import Port
from ...models.package import Package
from ...utils.logger import get_logger

class NavigationController(QObject):
    """
    Controller for coordinating navigation between tree view and diagram
    Handles selection synchronization, focus management, and navigation history
    """
    
    # Signals
    component_selection_changed = pyqtSignal(object)  # Component or None
    package_selection_changed = pyqtSignal(object)    # Package or None
    port_selection_changed = pyqtSignal(object)       # Port or None
    navigation_requested = pyqtSignal(str, str)       # item_type, item_uuid
    focus_requested = pyqtSignal(str)                 # item_uuid
    
    def __init__(self, tree_widget=None, graphics_scene=None):
        super().__init__()
        
        self.logger = get_logger(__name__)
        
        # UI components
        self.tree_widget = tree_widget
        self.graphics_scene = graphics_scene
        
        # Navigation state
        self.current_selection: Optional[Any] = None
        self.current_selection_type: Optional[str] = None
        
        # Navigation history
        self.navigation_history: List[Dict[str, Any]] = []
        self.history_index: int = -1
        self.max_history_size: int = 100
        
        # Selection synchronization state
        self._updating_from_tree = False
        self._updating_from_scene = False
        
        # Item mapping
        self.tree_item_to_object: Dict[QTreeWidgetItem, Any] = {}
        self.object_to_tree_item: Dict[str, QTreeWidgetItem] = {}  # uuid -> tree_item
        
        # Setup connections
        self._setup_connections()
    
    def set_tree_widget(self, tree_widget: QTreeWidget):
        """Set the tree widget and connect signals"""
        if self.tree_widget:
            self._disconnect_tree_signals()
        
        self.tree_widget = tree_widget
        self._connect_tree_signals()
    
    def set_graphics_scene(self, graphics_scene):
        """Set the graphics scene and connect signals"""
        if self.graphics_scene:
            self._disconnect_scene_signals()
        
        self.graphics_scene = graphics_scene
        self._connect_scene_signals()
    
    def _setup_connections(self):
        """Setup signal connections"""
        self._connect_tree_signals()
        self._connect_scene_signals()
    
    def _connect_tree_signals(self):
        """Connect tree widget signals"""
        if self.tree_widget:
            self.tree_widget.itemSelectionChanged.connect(self._on_tree_selection_changed)
            self.tree_widget.itemDoubleClicked.connect(self._on_tree_item_double_clicked)
            self.tree_widget.itemExpanded.connect(self._on_tree_item_expanded)
            self.tree_widget.itemCollapsed.connect(self._on_tree_item_collapsed)
    
    def _disconnect_tree_signals(self):
        """Disconnect tree widget signals"""
        if self.tree_widget:
            self.tree_widget.itemSelectionChanged.disconnect()
            self.tree_widget.itemDoubleClicked.disconnect()
            self.tree_widget.itemExpanded.disconnect()
            self.tree_widget.itemCollapsed.disconnect()
    
    def _connect_scene_signals(self):
        """Connect graphics scene signals"""
        if self.graphics_scene:
            self.graphics_scene.component_selected.connect(self._on_scene_component_selected)
            self.graphics_scene.component_double_clicked.connect(self._on_scene_component_double_clicked)
    
    def _disconnect_scene_signals(self):
        """Disconnect graphics scene signals"""
        if self.graphics_scene:
            self.graphics_scene.component_selected.disconnect()
            self.graphics_scene.component_double_clicked.disconnect()
    
    def register_tree_item(self, tree_item: QTreeWidgetItem, obj: Any):
        """Register mapping between tree item and data object"""
        self.tree_item_to_object[tree_item] = obj
        
        # Store reverse mapping using object UUID
        if hasattr(obj, 'uuid'):
            self.object_to_tree_item[obj.uuid] = tree_item
    
    def clear_mappings(self):
        """Clear all tree item mappings"""
        self.tree_item_to_object.clear()
        self.object_to_tree_item.clear()
    
    def _on_tree_selection_changed(self):
        """Handle tree selection change"""
        if self._updating_from_scene:
            return
        
        self._updating_from_tree = True
        
        try:
            selected_items = self.tree_widget.selectedItems()
            
            if selected_items:
                selected_item = selected_items[0]
                obj = self.tree_item_to_object.get(selected_item)
                
                if obj:
                    self._select_object(obj, source='tree')
                    
                    # Highlight in graphics scene
                    if isinstance(obj, Component) and self.graphics_scene:
                        self.graphics_scene.highlight_component(obj.uuid)
            else:
                self._clear_selection(source='tree')
        
        finally:
            self._updating_from_tree = False
    
    def _on_tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item double click"""
        obj = self.tree_item_to_object.get(item)
        
        if obj:
            self.logger.debug(f"Tree item double-clicked: {getattr(obj, 'short_name', 'Unknown')}")
            
            if isinstance(obj, Component):
                if obj.is_composition:
                    # Navigate into composition (will be implemented in Day 6)
                    self.navigation_requested.emit('composition', obj.uuid)
                else:
                    # Focus on component in diagram
                    self.focus_requested.emit(obj.uuid)
            elif isinstance(obj, Package):
                # Expand/collapse package or navigate
                if item.isExpanded():
                    item.setExpanded(False)
                else:
                    item.setExpanded(True)
    
    def _on_tree_item_expanded(self, item: QTreeWidgetItem):
        """Handle tree item expansion"""
        obj = self.tree_item_to_object.get(item)
        if obj:
            self.logger.debug(f"Tree item expanded: {getattr(obj, 'short_name', 'Unknown')}")
    
    def _on_tree_item_collapsed(self, item: QTreeWidgetItem):
        """Handle tree item collapse"""
        obj = self.tree_item_to_object.get(item)
        if obj:
            self.logger.debug(f"Tree item collapsed: {getattr(obj, 'short_name', 'Unknown')}")
    
    def _on_scene_component_selected(self, component: Optional[Component]):
        """Handle component selection from graphics scene"""
        if self._updating_from_tree:
            return
        
        self._updating_from_scene = True
        
        try:
            if component:
                self._select_object(component, source='scene')
                
                # Update tree selection
                if component.uuid in self.object_to_tree_item:
                    tree_item = self.object_to_tree_item[component.uuid]
                    self.tree_widget.setCurrentItem(tree_item)
                    
                    # Ensure item is visible (expand parents if needed)
                    self._ensure_tree_item_visible(tree_item)
            else:
                self._clear_selection(source='scene')
        
        finally:
            self._updating_from_scene = False
    
    def _on_scene_component_double_clicked(self, component: Component):
        """Handle component double click from graphics scene"""
        self.logger.debug(f"Scene component double-clicked: {component.short_name}")
        
        if component.is_composition:
            # Navigate into composition
            self.navigation_requested.emit('composition', component.uuid)
        else:
            # Focus on component
            self.focus_requested.emit(component.uuid)
    
    def _select_object(self, obj: Any, source: str = 'unknown'):
        """Select an object and update state"""
        self.current_selection = obj
        
        if isinstance(obj, Component):
            self.current_selection_type = 'component'
            self.component_selection_changed.emit(obj)
        elif isinstance(obj, Port):
            self.current_selection_type = 'port'
            self.port_selection_changed.emit(obj)
        elif isinstance(obj, Package):
            self.current_selection_type = 'package'
            self.package_selection_changed.emit(obj)
        
        # Add to navigation history
        self._add_to_history(obj)
        
        self.logger.debug(f"Selected {self.current_selection_type}: {getattr(obj, 'short_name', 'Unknown')} (from {source})")
    
    def _clear_selection(self, source: str = 'unknown'):
        """Clear current selection"""
        self.current_selection = None
        self.current_selection_type = None
        
        # Emit clear signals
        self.component_selection_changed.emit(None)
        self.port_selection_changed.emit(None)
        self.package_selection_changed.emit(None)
        
        self.logger.debug(f"Selection cleared (from {source})")
    
    def _ensure_tree_item_visible(self, tree_item: QTreeWidgetItem):
        """Ensure tree item is visible by expanding parents"""
        parent = tree_item.parent()
        while parent:
            parent.setExpanded(True)
            parent = parent.parent()
        
        # Scroll to item
        self.tree_widget.scrollToItem(tree_item)
    
    def _add_to_history(self, obj: Any):
        """Add object to navigation history"""
        if not hasattr(obj, 'uuid'):
            return
        
        history_entry = {
            'uuid': obj.uuid,
            'type': type(obj).__name__.lower(),
            'name': getattr(obj, 'short_name', 'Unknown'),
            'timestamp': self._get_current_timestamp()
        }
        
        # Remove any existing entry for same object
        self.navigation_history = [h for h in self.navigation_history if h['uuid'] != obj.uuid]
        
        # Add to beginning of history
        self.navigation_history.insert(0, history_entry)
        
        # Limit history size
        if len(self.navigation_history) > self.max_history_size:
            self.navigation_history = self.navigation_history[:self.max_history_size]
        
        # Reset history index
        self.history_index = 0
    
    def navigate_back(self) -> bool:
        """Navigate to previous item in history"""
        if self.history_index < len(self.navigation_history) - 1:
            self.history_index += 1
            return self._navigate_to_history_item(self.history_index)
        return False
    
    def navigate_forward(self) -> bool:
        """Navigate to next item in history"""
        if self.history_index > 0:
            self.history_index -= 1
            return self._navigate_to_history_item(self.history_index)
        return False
    
    def _navigate_to_history_item(self, index: int) -> bool:
        """Navigate to specific history item"""
        if 0 <= index < len(self.navigation_history):
            history_entry = self.navigation_history[index]
            uuid = history_entry['uuid']
            
            # Find and select tree item
            if uuid in self.object_to_tree_item:
                tree_item = self.object_to_tree_item[uuid]
                obj = self.tree_item_to_object.get(tree_item)
                
                if obj:
                    # Update selection without adding to history
                    self._updating_from_tree = True
                    try:
                        self.tree_widget.setCurrentItem(tree_item)
                        self._ensure_tree_item_visible(tree_item)
                        self._select_object_without_history(obj)
                        return True
                    finally:
                        self._updating_from_tree = False
        
        return False
    
    def _select_object_without_history(self, obj: Any):
        """Select object without adding to history"""
        self.current_selection = obj
        
        if isinstance(obj, Component):
            self.current_selection_type = 'component'
            self.component_selection_changed.emit(obj)
            
            # Highlight in scene
            if self.graphics_scene:
                self.graphics_scene.highlight_component(obj.uuid)
        elif isinstance(obj, Port):
            self.current_selection_type = 'port'
            self.port_selection_changed.emit(obj)
        elif isinstance(obj, Package):
            self.current_selection_type = 'package'
            self.package_selection_changed.emit(obj)
    
    def get_navigation_history(self) -> List[Dict[str, Any]]:
        """Get navigation history"""
        return self.navigation_history.copy()
    
    def clear_navigation_history(self):
        """Clear navigation history"""
        self.navigation_history.clear()
        self.history_index = -1
    
    def can_navigate_back(self) -> bool:
        """Check if back navigation is possible"""
        return self.history_index < len(self.navigation_history) - 1
    
    def can_navigate_forward(self) -> bool:
        """Check if forward navigation is possible"""
        return self.history_index > 0
    
    def select_by_uuid(self, uuid: str) -> bool:
        """Select object by UUID"""
        if uuid in self.object_to_tree_item:
            tree_item = self.object_to_tree_item[uuid]
            obj = self.tree_item_to_object.get(tree_item)
            
            if obj:
                self.tree_widget.setCurrentItem(tree_item)
                self._ensure_tree_item_visible(tree_item)
                return True
        
        return False
    
    def expand_to_object(self, obj: Any) -> bool:
        """Expand tree to show specific object"""
        if hasattr(obj, 'uuid') and obj.uuid in self.object_to_tree_item:
            tree_item = self.object_to_tree_item[obj.uuid]
            self._ensure_tree_item_visible(tree_item)
            return True
        return False
    
    def get_current_selection(self) -> Optional[Any]:
        """Get currently selected object"""
        return self.current_selection
    
    def get_current_selection_type(self) -> Optional[str]:
        """Get type of currently selected object"""
        return self.current_selection_type
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.time()
    
    def get_breadcrumb_path(self) -> List[str]:
        """Get breadcrumb path for current selection"""
        if not self.current_selection:
            return []
        
        breadcrumbs = []
        
        if isinstance(self.current_selection, Component):
            # Add package path
            if self.current_selection.package_path:
                breadcrumbs.extend(self.current_selection.package_path.split('/'))
            
            # Add component name
            breadcrumbs.append(self.current_selection.short_name or 'Unknown Component')
        
        elif isinstance(self.current_selection, Package):
            # Add package path
            if self.current_selection.full_path:
                breadcrumbs.extend(self.current_selection.full_path.split('/'))
        
        elif isinstance(self.current_selection, Port):
            # Find parent component
            component = None
            if self.current_selection.component_uuid:
                for tree_item, obj in self.tree_item_to_object.items():
                    if isinstance(obj, Component) and obj.uuid == self.current_selection.component_uuid:
                        component = obj
                        break
            
            if component:
                if component.package_path:
                    breadcrumbs.extend(component.package_path.split('/'))
                breadcrumbs.append(component.short_name or 'Unknown Component')
            
            breadcrumbs.append(self.current_selection.short_name or 'Unknown Port')
        
        # Filter out empty strings
        return [b for b in breadcrumbs if b]