# src/arxml_viewer/gui/controllers/navigation_controller.py (ENHANCED VERSION)
"""
Navigation Controller for ARXML Viewer Pro - Enhanced with Day 5 Features
Handles navigation state management, composition drill-down, and breadcrumb navigation
Complete implementation with tree-diagram synchronization and connection awareness
"""
from typing import Optional, List, Dict, Any, Callable, Tuple
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget
import logging

from ...models.component import Component
from ...models.package import Package
from ...models.connection import Connection

logger = logging.getLogger(__name__)

class NavigationState:
    """Represents a navigation state for history management"""
    
    def __init__(self, 
                 context_type: str,
                 context_object: Any,
                 display_name: str,
                 breadcrumb_path: List[str] = None,
                 additional_data: Dict[str, Any] = None):
        self.context_type = context_type  # 'package', 'component', 'composition'
        self.context_object = context_object
        self.display_name = display_name
        self.breadcrumb_path = breadcrumb_path or []
        self.additional_data = additional_data or {}
        self.timestamp = None
        
    def __str__(self):
        return f"NavigationState({self.context_type}: {self.display_name})"

class NavigationController(QObject):
    """
    Enhanced navigation controller with Day 5 drill-down and connection features
    Provides comprehensive navigation state management and view synchronization
    """
    
    # All required signals for Day 5
    component_selected = pyqtSignal(object)
    package_changed = pyqtSignal(object)
    navigation_changed = pyqtSignal(object)
    component_selection_changed = pyqtSignal(object)
    navigation_requested = pyqtSignal(str, str)  # item_type, item_uuid
    focus_requested = pyqtSignal(str)  # item_uuid
    
    # Day 5 - Enhanced signals for drill-down and connections
    composition_drill_down_requested = pyqtSignal(object)  # Component
    composition_drill_up_requested = pyqtSignal()
    breadcrumb_updated = pyqtSignal(list)  # List of breadcrumb items
    connection_navigation_requested = pyqtSignal(object)  # Connection
    component_chain_requested = pyqtSignal(list)  # List of component UUIDs
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Navigation state
        self.current_component = None
        self.current_package = None
        self.current_composition = None  # Day 5 - Current composition context
        
        # Day 5 - Navigation history and breadcrumbs
        self.navigation_history: List[NavigationState] = []
        self.history_index = -1
        self.max_history_size = 50
        self.breadcrumb_path: List[Dict[str, str]] = []
        
        # View references
        self.tree_widget: Optional[QWidget] = None
        self.graphics_scene: Optional[QWidget] = None
        self.properties_panel: Optional[QWidget] = None
        
        # Day 5 - Enhanced mappings
        self.uuid_to_object_map: Dict[str, Any] = {}  # uuid -> object
        self.object_to_tree_item_map: Dict[str, Any] = {}  # uuid -> tree_item
        self.component_to_connections_map: Dict[str, List[Connection]] = {}
        
        # Day 5 - Navigation preferences
        self.auto_expand_compositions = True
        self.follow_connections = True
        self.highlight_related_components = True
        
        logger.info("Enhanced navigation controller initialized with Day 5 features")
    
    def set_tree_widget(self, tree_widget):
        """Set the tree widget reference"""
        self.tree_widget = tree_widget
        
        # Connect tree widget signals if available
        if hasattr(tree_widget, 'item_selected'):
            tree_widget.item_selected.connect(self._on_tree_item_selected)
        if hasattr(tree_widget, 'item_activated'):
            tree_widget.item_activated.connect(self._on_tree_item_activated)
            
        logger.debug("Enhanced tree widget connected")
    
    def set_graphics_scene(self, graphics_scene):
        """Set the graphics scene reference"""
        self.graphics_scene = graphics_scene
        
        # Connect graphics scene signals if available
        if hasattr(graphics_scene, 'component_selected'):
            graphics_scene.component_selected.connect(self._on_graphics_component_selected)
        if hasattr(graphics_scene, 'composition_drill_requested'):
            graphics_scene.composition_drill_requested.connect(self._on_composition_drill_requested)
        if hasattr(graphics_scene, 'connection_selected'):
            graphics_scene.connection_selected.connect(self._on_connection_selected)
            
        logger.debug("Enhanced graphics scene connected")
    
    def set_properties_panel(self, properties_panel):
        """Set the properties panel reference"""
        self.properties_panel = properties_panel
        logger.debug("Properties panel connected")
    
    def set_views(self, tree_widget=None, graphics_scene=None, properties_panel=None):
        """Set multiple view references at once"""
        if tree_widget:
            self.set_tree_widget(tree_widget)
        if graphics_scene:
            self.set_graphics_scene(graphics_scene)
        if properties_panel:
            self.set_properties_panel(properties_panel)
    
    # Day 5 - Enhanced navigation methods
    
    def select_component(self, component: Component, add_to_history: bool = True) -> None:
        """Select a component with enhanced Day 5 features"""
        logger.info(f"Selecting component: {component.short_name}")
        
        # Store previous state if adding to history
        if add_to_history and self.current_component != component:
            self._add_to_history()
        
        # Update current state
        previous_component = self.current_component
        self.current_component = component
        
        # Update mappings
        self.uuid_to_object_map[component.uuid] = component
        
        # Day 5 - Update breadcrumb path
        self._update_breadcrumb_for_component(component)
        
        # Synchronize views
        self._synchronize_tree_selection(component)
        self._synchronize_graphics_selection(component)
        
        # Day 5 - Highlight related elements
        if self.highlight_related_components:
            self._highlight_related_components(component)
        
        # Emit signals
        self.component_selected.emit(component)
        self.component_selection_changed.emit(component)
        self.navigation_changed.emit(component)
        
        logger.debug(f"Component selection completed: {component.short_name}")
    
    def navigate_to_package(self, package: Package, add_to_history: bool = True) -> None:
        """Navigate to a package with enhanced features"""
        logger.info(f"Navigating to package: {package.short_name}")
        
        if add_to_history and self.current_package != package:
            self._add_to_history()
        
        self.current_package = package
        self.uuid_to_object_map[package.uuid] = package
        
        # Update breadcrumb for package navigation
        self._update_breadcrumb_for_package(package)
        
        # Emit signals
        self.package_changed.emit(package)
        self.navigation_changed.emit(package)
    
    # Day 5 - Composition drill-down methods
    
    def drill_into_composition(self, composition: Component) -> bool:
        """Drill down into a composition component"""
        try:
            if not composition.is_composition:
                logger.warning(f"Component {composition.short_name} is not a composition")
                return False
            
            logger.info(f"Drilling into composition: {composition.short_name}")
            
            # Add current state to history
            self._add_to_history()
            
            # Update current composition context
            self.current_composition = composition
            self.current_component = None  # Clear component selection in composition context
            
            # Update breadcrumb path for composition
            self._add_breadcrumb_item({
                'type': 'composition',
                'uuid': composition.uuid,
                'name': composition.short_name,
                'display_name': f"📦 {composition.short_name}"
            })
            
            # Emit drill-down signal
            self.composition_drill_down_requested.emit(composition)
            
            # Update navigation state
            nav_state = NavigationState(
                context_type='composition',
                context_object=composition,
                display_name=composition.short_name,
                breadcrumb_path=self.get_breadcrumb_path_strings(),
                additional_data={'is_drill_down': True}
            )
            self._update_navigation_state(nav_state)
            
            return True
            
        except Exception as e:
            logger.error(f"Drill into composition failed: {e}")
            return False
    
    def drill_up_from_composition(self) -> bool:
        """Drill up from current composition"""
        try:
            if not self.current_composition:
                logger.warning("No current composition to drill up from")
                return False
            
            logger.info(f"Drilling up from composition: {self.current_composition.short_name}")
            
            # Remove composition from breadcrumb
            if self.breadcrumb_path:
                self.breadcrumb_path.pop()
            
            # Clear composition context
            previous_composition = self.current_composition
            self.current_composition = None
            
            # Navigate back in history
            if self.can_navigate_back():
                self.navigate_back()
            
            # Emit drill-up signal
            self.composition_drill_up_requested.emit()
            
            return True
            
        except Exception as e:
            logger.error(f"Drill up from composition failed: {e}")
            return False
    
    def is_in_composition_context(self) -> bool:
        """Check if currently in a composition drill-down context"""
        return self.current_composition is not None
    
    def get_current_composition(self) -> Optional[Component]:
        """Get current composition context"""
        return self.current_composition
    
    # Day 5 - Connection-aware navigation
    
    def navigate_along_connection(self, connection: Connection, from_component_uuid: str = None) -> bool:
        """Navigate along a connection to the connected component"""
        try:
            logger.info(f"Navigating along connection: {connection.short_name}")
            
            # Determine target component
            if from_component_uuid == connection.provider_endpoint.component_uuid:
                target_uuid = connection.requester_endpoint.component_uuid
            elif from_component_uuid == connection.requester_endpoint.component_uuid:
                target_uuid = connection.provider_endpoint.component_uuid
            else:
                # Default to requester if no from_component specified
                target_uuid = connection.requester_endpoint.component_uuid
            
            # Find target component
            target_component = self.uuid_to_object_map.get(target_uuid)
            if not target_component:
                logger.warning(f"Target component not found: {target_uuid}")
                return False
            
            # Navigate to target component
            self.select_component(target_component)
            
            # Emit connection navigation signal
            self.connection_navigation_requested.emit(connection)
            
            # Highlight connection path if graphics scene supports it
            if hasattr(self.graphics_scene, 'highlight_component_chain'):
                component_chain = [
                    connection.provider_endpoint.component_uuid,
                    connection.requester_endpoint.component_uuid
                ]
                self.component_chain_requested.emit(component_chain)
            
            return True
            
        except Exception as e:
            logger.error(f"Navigate along connection failed: {e}")
            return False
    
    def find_connection_path(self, start_component_uuid: str, end_component_uuid: str) -> List[str]:
        """Find connection path between two components"""
        try:
            if hasattr(self.graphics_scene, 'find_shortest_path'):
                return self.graphics_scene.find_shortest_path(start_component_uuid, end_component_uuid)
            return []
        except Exception as e:
            logger.error(f"Find connection path failed: {e}")
            return []
    
    def navigate_connection_path(self, component_path: List[str]) -> bool:
        """Navigate along a path of connected components"""
        try:
            if not component_path:
                return False
            
            logger.info(f"Navigating connection path with {len(component_path)} components")
            
            # Select the last component in the path
            last_component_uuid = component_path[-1]
            target_component = self.uuid_to_object_map.get(last_component_uuid)
            
            if target_component:
                self.select_component(target_component)
                
                # Highlight the entire path
                self.component_chain_requested.emit(component_path)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Navigate connection path failed: {e}")
            return False
    
    # Day 5 - Enhanced history management
    
    def _add_to_history(self):
        """Add current state to navigation history"""
        try:
            if self.current_component or self.current_package or self.current_composition:
                # Determine context
                if self.current_composition:
                    context_obj = self.current_composition
                    context_type = 'composition'
                    display_name = f"📦 {context_obj.short_name}"
                elif self.current_component:
                    context_obj = self.current_component
                    context_type = 'component'
                    display_name = context_obj.short_name
                elif self.current_package:
                    context_obj = self.current_package
                    context_type = 'package'
                    display_name = f"📁 {context_obj.short_name}"
                else:
                    return
                
                # Create navigation state
                nav_state = NavigationState(
                    context_type=context_type,
                    context_object=context_obj,
                    display_name=display_name,
                    breadcrumb_path=self.get_breadcrumb_path_strings(),
                    additional_data={
                        'component_uuid': self.current_component.uuid if self.current_component else None,
                        'package_uuid': self.current_package.uuid if self.current_package else None,
                        'composition_uuid': self.current_composition.uuid if self.current_composition else None
                    }
                )
                
                # Add to history
                # Remove any states after current index (for new branch)
                if self.history_index < len(self.navigation_history) - 1:
                    self.navigation_history = self.navigation_history[:self.history_index + 1]
                
                self.navigation_history.append(nav_state)
                self.history_index = len(self.navigation_history) - 1
                
                # Limit history size
                if len(self.navigation_history) > self.max_history_size:
                    self.navigation_history.pop(0)
                    self.history_index -= 1
                
                logger.debug(f"Added to history: {nav_state}")
                
        except Exception as e:
            logger.error(f"Add to history failed: {e}")
    
    def navigate_back(self) -> bool:
        """Navigate back in history"""
        try:
            if not self.can_navigate_back():
                return False
            
            self.history_index -= 1
            nav_state = self.navigation_history[self.history_index]
            
            logger.info(f"Navigating back to: {nav_state}")
            
            # Restore state
            self._restore_navigation_state(nav_state)
            
            return True
            
        except Exception as e:
            logger.error(f"Navigate back failed: {e}")
            return False
    
    def navigate_forward(self) -> bool:
        """Navigate forward in history"""
        try:
            if not self.can_navigate_forward():
                return False
            
            self.history_index += 1
            nav_state = self.navigation_history[self.history_index]
            
            logger.info(f"Navigating forward to: {nav_state}")
            
            # Restore state
            self._restore_navigation_state(nav_state)
            
            return True
            
        except Exception as e:
            logger.error(f"Navigate forward failed: {e}")
            return False
    
    def can_navigate_back(self) -> bool:
        """Check if back navigation is possible"""
        return self.history_index > 0
    
    def can_navigate_forward(self) -> bool:
        """Check if forward navigation is possible"""
        return self.history_index < len(self.navigation_history) - 1
    
    def _restore_navigation_state(self, nav_state: NavigationState):
        """Restore a navigation state"""
        try:
            # Restore context based on type
            if nav_state.context_type == 'component':
                self.current_component = nav_state.context_object
                self.current_package = None
                self.current_composition = None
            elif nav_state.context_type == 'package':
                self.current_package = nav_state.context_object
                self.current_component = None
                self.current_composition = None
            elif nav_state.context_type == 'composition':
                self.current_composition = nav_state.context_object
                self.current_component = None
                self.current_package = None
            
            # Restore breadcrumb path
            self._restore_breadcrumb_path(nav_state.breadcrumb_path)
            
            # Synchronize views
            if nav_state.context_object:
                if hasattr(nav_state.context_object, 'component_type'):  # Component
                    self._synchronize_views_for_component(nav_state.context_object, add_to_history=False)
                elif hasattr(nav_state.context_object, 'components'):  # Package
                    self._synchronize_views_for_package(nav_state.context_object, add_to_history=False)
            
            # Emit navigation changed
            self.navigation_changed.emit(nav_state.context_object)
            
        except Exception as e:
            logger.error(f"Restore navigation state failed: {e}")
    
    # Day 5 - Breadcrumb management
    
    def _update_breadcrumb_for_component(self, component: Component):
        """Update breadcrumb path for component selection"""
        try:
            # Build breadcrumb path
            path_items = []
            
            # Add package path if available
            if component.package_path:
                package_parts = component.package_path.split('/')
                for part in package_parts:
                    if part:
                        path_items.append({
                            'type': 'package',
                            'name': part,
                            'display_name': f"📁 {part}",
                            'uuid': None  # Package UUID not available here
                        })
            
            # Add current composition if in drill-down context
            if self.current_composition:
                path_items.append({
                    'type': 'composition',
                    'uuid': self.current_composition.uuid,
                    'name': self.current_composition.short_name,
                    'display_name': f"📦 {self.current_composition.short_name}"
                })
            
            # Add component
            path_items.append({
                'type': 'component',
                'uuid': component.uuid,
                'name': component.short_name,
                'display_name': component.short_name
            })
            
            self.breadcrumb_path = path_items
            self.breadcrumb_updated.emit(self.breadcrumb_path)
            
        except Exception as e:
            logger.error(f"Update breadcrumb for component failed: {e}")
    
    def _update_breadcrumb_for_package(self, package: Package):
        """Update breadcrumb path for package selection"""
        try:
            path_items = []
            
            # Build path from package hierarchy
            if package.full_path:
                package_parts = package.full_path.split('/')
                for part in package_parts:
                    if part:
                        path_items.append({
                            'type': 'package',
                            'name': part,
                            'display_name': f"📁 {part}",
                            'uuid': package.uuid if part == package.short_name else None
                        })
            else:
                path_items.append({
                    'type': 'package',
                    'uuid': package.uuid,
                    'name': package.short_name,
                    'display_name': f"📁 {package.short_name}"
                })
            
            self.breadcrumb_path = path_items
            self.breadcrumb_updated.emit(self.breadcrumb_path)
            
        except Exception as e:
            logger.error(f"Update breadcrumb for package failed: {e}")
    
    def _add_breadcrumb_item(self, item: Dict[str, str]):
        """Add item to breadcrumb path"""
        self.breadcrumb_path.append(item)
        self.breadcrumb_updated.emit(self.breadcrumb_path)
    
    def _restore_breadcrumb_path(self, path_strings: List[str]):
        """Restore breadcrumb path from strings"""
        try:
            # Convert strings back to breadcrumb items
            # This is a simplified restoration - in a full implementation,
            # you'd want to store more metadata
            path_items = []
            for path_str in path_strings:
                if path_str.startswith('📁'):
                    path_items.append({
                        'type': 'package',
                        'name': path_str[2:],  # Remove emoji
                        'display_name': path_str,
                        'uuid': None
                    })
                elif path_str.startswith('📦'):
                    path_items.append({
                        'type': 'composition',
                        'name': path_str[2:],  # Remove emoji
                        'display_name': path_str,
                        'uuid': None
                    })
                else:
                    path_items.append({
                        'type': 'component',
                        'name': path_str,
                        'display_name': path_str,
                        'uuid': None
                    })
            
            self.breadcrumb_path = path_items
            self.breadcrumb_updated.emit(self.breadcrumb_path)
            
        except Exception as e:
            logger.error(f"Restore breadcrumb path failed: {e}")
    
    def get_breadcrumb_path(self) -> List[Dict[str, str]]:
        """Get current breadcrumb path"""
        return self.breadcrumb_path.copy()
    
    def get_breadcrumb_path_strings(self) -> List[str]:
        """Get breadcrumb path as list of strings"""
        return [item['display_name'] for item in self.breadcrumb_path]
    
    def navigate_to_breadcrumb(self, breadcrumb_index: int) -> bool:
        """Navigate to a specific breadcrumb item"""
        try:
            if 0 <= breadcrumb_index < len(self.breadcrumb_path):
                target_item = self.breadcrumb_path[breadcrumb_index]
                
                # Navigate based on item type
                if target_item['type'] == 'component' and target_item['uuid']:
                    target_obj = self.uuid_to_object_map.get(target_item['uuid'])
                    if target_obj:
                        self.select_component(target_obj)
                        return True
                elif target_item['type'] == 'package' and target_item['uuid']:
                    target_obj = self.uuid_to_object_map.get(target_item['uuid'])
                    if target_obj:
                        self.navigate_to_package(target_obj)
                        return True
                elif target_item['type'] == 'composition' and target_item['uuid']:
                    target_obj = self.uuid_to_object_map.get(target_item['uuid'])
                    if target_obj:
                        self.drill_into_composition(target_obj)
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Navigate to breadcrumb failed: {e}")
            return False
    
    # Day 5 - Enhanced view synchronization
    
    def _synchronize_tree_selection(self, obj: Any):
        """Synchronize tree widget selection"""
        try:
            if self.tree_widget and hasattr(self.tree_widget, 'select_object_by_uuid'):
                if hasattr(obj, 'uuid'):
                    self.tree_widget.select_object_by_uuid(obj.uuid)
        except Exception as e:
            logger.error(f"Tree synchronization failed: {e}")
    
    def _synchronize_graphics_selection(self, obj: Any):
        """Synchronize graphics scene selection"""
        try:
            if self.graphics_scene and hasattr(self.graphics_scene, 'highlight_component'):
                if hasattr(obj, 'uuid'):
                    self.graphics_scene.highlight_component(obj.uuid)
        except Exception as e:
            logger.error(f"Graphics synchronization failed: {e}")
    
    def _synchronize_views_for_component(self, component: Component, add_to_history: bool = True):
        """Synchronize all views for component"""
        self._synchronize_tree_selection(component)
        self._synchronize_graphics_selection(component)
        
        if add_to_history:
            self.component_selected.emit(component)
    
    def _synchronize_views_for_package(self, package: Package, add_to_history: bool = True):
        """Synchronize all views for package"""
        self._synchronize_tree_selection(package)
        
        if add_to_history:
            self.package_changed.emit(package)
    
    def _highlight_related_components(self, component: Component):
        """Highlight components related to the selected component"""
        try:
            if not self.highlight_related_components:
                return
            
            # Get connections for this component
            connections = self.component_to_connections_map.get(component.uuid, [])
            
            if connections and hasattr(self.graphics_scene, 'highlight_connections_for_component'):
                self.graphics_scene.highlight_connections_for_component(component.uuid, True)
                
        except Exception as e:
            logger.error(f"Highlight related components failed: {e}")
    
    # Day 5 - Event handlers
    
    def _on_tree_item_selected(self, obj: Any):
        """Handle tree item selection"""
        try:
            if isinstance(obj, Component):
                self.select_component(obj)
            elif isinstance(obj, Package):
                self.navigate_to_package(obj)
        except Exception as e:
            logger.error(f"Tree item selection handling failed: {e}")
    
    def _on_tree_item_activated(self, obj: Any):
        """Handle tree item activation (double-click)"""
        try:
            if isinstance(obj, Component) and obj.is_composition:
                self.drill_into_composition(obj)
            elif isinstance(obj, Component):
                self.select_component(obj)
                self.focus_requested.emit(obj.uuid)
        except Exception as e:
            logger.error(f"Tree item activation handling failed: {e}")
    
    def _on_graphics_component_selected(self, component: Component):
        """Handle graphics scene component selection"""
        try:
            self.select_component(component)
        except Exception as e:
            logger.error(f"Graphics component selection handling failed: {e}")
    
    def _on_composition_drill_requested(self, component: Component):
        """Handle composition drill-down request from graphics scene"""
        try:
            self.drill_into_composition(component)
        except Exception as e:
            logger.error(f"Composition drill request handling failed: {e}")
    
    def _on_connection_selected(self, connection: Connection):
        """Handle connection selection from graphics scene"""
        try:
            self.connection_navigation_requested.emit(connection)
        except Exception as e:
            logger.error(f"Connection selection handling failed: {e}")
    
    # Day 5 - Enhanced utility methods
    
    def register_object(self, obj: Any):
        """Register object for navigation mapping"""
        try:
            if hasattr(obj, 'uuid'):
                self.uuid_to_object_map[obj.uuid] = obj
        except Exception as e:
            logger.error(f"Register object failed: {e}")
    
    def register_connection_mapping(self, component_uuid: str, connections: List[Connection]):
        """Register connection mapping for component"""
        self.component_to_connections_map[component_uuid] = connections
    
    def clear_mappings(self) -> None:
        """Clear all navigation mappings"""
        self.uuid_to_object_map.clear()
        self.object_to_tree_item_map.clear()
        self.component_to_connections_map.clear()
        self.navigation_history.clear()
        self.history_index = -1
        self.breadcrumb_path.clear()
        
        # Clear current state
        self.current_component = None
        self.current_package = None
        self.current_composition = None
    
    def get_current_component(self) -> Optional[Component]:
        """Get current component"""
        return self.current_component
    
    def get_current_package(self) -> Optional[Package]:
        """Get current package"""
        return self.current_package
    
    def get_navigation_info(self) -> Dict[str, Any]:
        """Get comprehensive navigation information"""
        return {
            'current_component': self.current_component.short_name if self.current_component else None,
            'current_package': self.current_package.short_name if self.current_package else None,
            'current_composition': self.current_composition.short_name if self.current_composition else None,
            'breadcrumb_path': self.get_breadcrumb_path_strings(),
            'history_size': len(self.navigation_history),
            'history_index': self.history_index,
            'can_navigate_back': self.can_navigate_back(),
            'can_navigate_forward': self.can_navigate_forward(),
            'is_in_composition': self.is_in_composition_context(),
            'registered_objects': len(self.uuid_to_object_map),
            'connection_mappings': len(self.component_to_connections_map)
        }
    
    def _update_navigation_state(self, nav_state: NavigationState):
        """Update internal navigation state"""
        # This method can be used for additional state management
        # if needed by the application
        pass