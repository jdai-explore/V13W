# src/arxml_viewer/gui/graphics/graphics_scene.py
"""
Graphics Scene - FIXED VERSION with Proper Component Graphics Items
All syntax and method errors resolved
"""

import math
from typing import Dict, List, Optional, Tuple, Set
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, 
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QPainter

from ...models.component import Component
from ...models.package import Package
from ...utils.constants import AppConstants, UIConstants
from ...utils.logger import get_logger

class ComponentGraphicsItem(QGraphicsRectItem):
    """Custom graphics item for component representation - FIXED VERSION"""
    
    def __init__(self, component: Component, parent=None):
        super().__init__(parent)
        
        self.component = component
        self.logger = get_logger(__name__)
        
        # Enhanced state tracking
        self.is_highlighted = False
        self.is_search_result = False
        self.search_relevance_score = 0.0
        self.original_opacity = 0.8
        
        # Set up component rectangle
        self.setRect(0, 0, UIConstants.COMPONENT_MIN_WIDTH, UIConstants.COMPONENT_MIN_HEIGHT)
        
        # Set colors based on component type
        self._setup_appearance()
        
        # Add component label
        self._create_label()
        
        # Add ports
        self._create_ports()
        
        # Make item selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        # Set tooltip
        self.setToolTip(self._generate_tooltip())
        
        # Enhanced interaction
        self.setAcceptHoverEvents(True)
    
    def _setup_appearance(self):
        """Setup component appearance based on type"""
        # Get color for component type
        color_tuple = AppConstants.COMPONENT_COLORS.get(
            self.component.component_type.name, 
            AppConstants.COMPONENT_COLORS['APPLICATION']
        )
        
        color = QColor(*color_tuple)
        
        # Set brush and pen
        self.setBrush(QBrush(color))
        self.setPen(QPen(color.darker(150), 2))
        
        # Set opacity for better visibility
        self.setOpacity(self.original_opacity)
    
    def _create_label(self):
        """Create component name label"""
        self.label = QGraphicsTextItem(self.component.short_name or "Unnamed", self)
        
        # Position label in center of component
        label_rect = self.label.boundingRect()
        comp_rect = self.rect()
        
        x = (comp_rect.width() - label_rect.width()) / 2
        y = (comp_rect.height() - label_rect.height()) / 2
        
        self.label.setPos(x, y)
        
        # Style the label
        font = QFont("Arial", 9)
        font.setWeight(QFont.Bold)
        self.label.setFont(font)
        self.label.setDefaultTextColor(QColor(255, 255, 255))
    
    def _create_ports(self):
        """Create port representations"""
        self.port_items = []
        
        # Calculate port positions
        total_ports = len(self.component.all_ports)
        if total_ports == 0:
            return
        
        port_size = UIConstants.COMPONENT_PORT_SIZE
        comp_rect = self.rect()
        
        # Distribute ports around the component perimeter
        for i, port in enumerate(self.component.all_ports):
            # For now, place ports on the left (required) and right (provided) sides
            if port.is_provided:
                # Right side
                x = comp_rect.width() - port_size / 2
                y = comp_rect.height() * (i + 1) / (total_ports + 1) - port_size / 2
            else:
                # Left side  
                x = -port_size / 2
                y = comp_rect.height() * (i + 1) / (total_ports + 1) - port_size / 2
            
            port_item = PortGraphicsItem(port, self)
            port_item.setPos(x, y)
            self.port_items.append(port_item)
    
    def _generate_tooltip(self) -> str:
        """Generate tooltip text for component"""
        tooltip = f"<b>{self.component.short_name}</b><br>"
        tooltip += f"Type: {self.component.component_type.value}<br>"
        tooltip += f"Package: {self.component.package_path or 'Unknown'}<br>"
        tooltip += f"Ports: {self.component.port_count}<br>"
        tooltip += f"UUID: {self.component.uuid}<br>"
        
        if self.component.desc:
            # Truncate long descriptions
            desc = self.component.desc
            if len(desc) > 100:
                desc = desc[:97] + "..."
            tooltip += f"Description: {desc}<br>"
        
        # Add search info if this is a search result
        if self.is_search_result:
            tooltip += f"<br><i>Search relevance: {self.search_relevance_score:.2f}</i>"
        
        return tooltip
    
    def highlight(self, highlight_type: str = "selection"):
        """Highlight component with different styles - FIXED METHOD"""
        self.is_highlighted = True
        
        if highlight_type == "selection":
            # Yellow border for selection
            self.setPen(QPen(QColor(255, 255, 0), 3))
            self.setOpacity(1.0)
        elif highlight_type == "search":
            # Blue border for search results
            self.setPen(QPen(QColor(100, 149, 237), 3))
            self.setOpacity(1.0)
            self.is_search_result = True
        elif highlight_type == "focus":
            # Bright border for focus
            self.setPen(QPen(QColor(255, 165, 0), 4))
            self.setOpacity(1.0)
        elif highlight_type == "navigation":
            # Green border for navigation
            self.setPen(QPen(QColor(0, 255, 0), 3))
            self.setOpacity(1.0)
    
    def clear_highlight(self):
        """Clear all highlighting - FIXED METHOD"""
        self.is_highlighted = False
        self.is_search_result = False
        
        # Restore original appearance
        self._setup_appearance()
    
    def set_search_relevance(self, score: float):
        """Set search relevance score"""
        self.search_relevance_score = score
        self.is_search_result = True
        
        # Adjust opacity based on relevance (higher score = more opaque)
        opacity = 0.5 + (score * 0.5)  # Range: 0.5 to 1.0
        self.setOpacity(opacity)
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        super().mousePressEvent(event)
        self.logger.debug(f"Component clicked: {self.component.short_name}")
    
    def hoverEnterEvent(self, event):
        """Handle hover enter"""
        if not self.is_highlighted:
            # Subtle highlight on hover
            current_pen = self.pen()
            current_pen.setWidth(3)
            self.setPen(current_pen)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        if not self.is_highlighted:
            # Restore normal pen width
            current_pen = self.pen()
            current_pen.setWidth(2)
            self.setPen(current_pen)
        super().hoverLeaveEvent(event)

class PortGraphicsItem(QGraphicsEllipseItem):
    """Custom graphics item for port representation"""
    
    def __init__(self, port, parent=None):
        super().__init__(parent)
        
        self.port = port
        self.is_highlighted = False
        
        # Set port size
        size = UIConstants.COMPONENT_PORT_SIZE
        self.setRect(0, 0, size, size)
        
        # Set port color based on type
        self._setup_appearance()
        
        # Set tooltip
        self.setToolTip(self._generate_tooltip())
        
        # Enhanced interaction
        self.setAcceptHoverEvents(True)
    
    def _setup_appearance(self):
        """Setup port appearance based on type"""
        # Get color for port type
        if self.port.is_provided:
            color_tuple = AppConstants.PORT_COLORS['PROVIDED']
        elif self.port.is_required:
            color_tuple = AppConstants.PORT_COLORS['REQUIRED']
        else:
            color_tuple = AppConstants.PORT_COLORS['PROVIDED_REQUIRED']
        
        color = QColor(*color_tuple)
        
        # Set brush and pen
        self.setBrush(QBrush(color))
        self.setPen(QPen(color.darker(150), 1))
    
    def _generate_tooltip(self) -> str:
        """Generate tooltip text for port"""
        tooltip = f"<b>{self.port.short_name}</b><br>"
        tooltip += f"Type: {self.port.port_type.value}<br>"
        tooltip += f"UUID: {self.port.uuid}<br>"
        
        if self.port.interface_ref:
            tooltip += f"Interface: {self.port.interface_ref}<br>"
        
        if self.port.desc:
            desc = self.port.desc
            if len(desc) > 80:
                desc = desc[:77] + "..."
            tooltip += f"Description: {desc}<br>"
        
        # Add parent component info
        if hasattr(self.port, 'component_uuid') and self.port.component_uuid:
            tooltip += f"Component: {self.port.component_uuid[:8]}...<br>"
        
        return tooltip
    
    def highlight(self, highlight_type: str = "selection"):
        """Highlight port - FIXED METHOD"""
        self.is_highlighted = True
        
        if highlight_type == "selection":
            self.setPen(QPen(QColor(255, 255, 0), 2))
        elif highlight_type == "search":
            self.setPen(QPen(QColor(100, 149, 237), 2))
        elif highlight_type == "connection":
            self.setPen(QPen(QColor(255, 0, 255), 2))
    
    def clear_highlight(self):
        """Clear port highlighting - FIXED METHOD"""
        self.is_highlighted = False
        self._setup_appearance()
    
    def hoverEnterEvent(self, event):
        """Handle hover enter"""
        if not self.is_highlighted:
            current_pen = self.pen()
            current_pen.setWidth(2)
            self.setPen(current_pen)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        if not self.is_highlighted:
            current_pen = self.pen()
            current_pen.setWidth(1)
            self.setPen(current_pen)
        super().hoverLeaveEvent(event)

class ComponentDiagramScene(QGraphicsScene):
    """
    FIXED Graphics Scene for component diagram visualization
    Uses proper ComponentGraphicsItem objects with all required methods
    """
    
    # Signals
    component_selected = pyqtSignal(object)  # Component object
    component_double_clicked = pyqtSignal(object)  # Component object
    
    # Enhanced signals
    component_focused = pyqtSignal(str)  # component_uuid
    port_selected = pyqtSignal(object)  # Port object
    selection_cleared = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        
        # Scene state - FIXED to use ComponentGraphicsItem
        self.components: Dict[str, ComponentGraphicsItem] = {}
        self.connections: List[QGraphicsLineItem] = []
        
        # Enhanced state management
        self.current_selection: Optional[ComponentGraphicsItem] = None
        self.search_results: Set[str] = set()  # Set of component UUIDs
        self.highlighted_components: Set[str] = set()
        
        # Layout parameters
        self.grid_size = 20
        self.component_spacing = 150
        
        # Navigation integration
        self.navigation_controller = None
        self.auto_highlight_enabled = True
        
        # Set scene properties
        self.setSceneRect(0, 0, 2000, 1500)  # Large scene for components
        self.setBackgroundBrush(QBrush(QColor(245, 245, 245)))  # Light gray background
        
        # Connect selection changes
        self.selectionChanged.connect(self._on_selection_changed)
    
    def set_navigation_controller(self, navigation_controller):
        """Set navigation controller for integration"""
        self.navigation_controller = navigation_controller
        self.logger.debug("Navigation controller connected to graphics scene")
    
    def load_packages(self, packages: List[Package]):
        """Load and visualize packages - FIXED VERSION using ComponentGraphicsItem"""
        print(f"🔧 Graphics scene loading {len(packages)} packages")
        
        # Clear existing content
        self.clear()
        self.components.clear()
        self.connections.clear()
        self.search_results.clear()
        self.highlighted_components.clear()
        self.current_selection = None
        
        # Get all components
        all_components = []
        for package in packages:
            components = package.get_all_components(recursive=True)
            all_components.extend(components)
            print(f"Package {package.short_name}: {len(components)} components")
        
        print(f"Total components to display: {len(all_components)}")
        
        if not all_components:
            print("⚠️  No components found to display")
            return
        
        # Simple grid layout
        cols = max(1, math.ceil(math.sqrt(len(all_components))))
        spacing = 150
        
        for i, component in enumerate(all_components):
            try:
                row = i // cols
                col = i % cols
                
                x = col * spacing
                y = row * spacing
                
                print(f"Creating component {component.short_name} at ({x}, {y})")
                
                # Create ComponentGraphicsItem - FIXED
                comp_item = ComponentGraphicsItem(component)
                comp_item.setPos(x, y)
                
                # Add to scene
                self.addItem(comp_item)
                
                # Store reference - FIXED to use ComponentGraphicsItem
                self.components[component.uuid] = comp_item
                
                print(f"✅ Created component graphics item: {component.short_name}")
                
            except Exception as e:
                print(f"❌ Failed to create component {component.short_name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"✅ Created {len(self.components)} component graphics")
        
        # Set scene rect
        scene_width = cols * spacing + 100
        scene_height = math.ceil(len(all_components) / cols) * spacing + 100
        self.setSceneRect(0, 0, scene_width, scene_height)
        
        print(f"✅ Scene rect set to {scene_width}x{scene_height}")
        
        # Setup enhanced interactions
        self._setup_component_interactions()
        
        self.logger.info(f"Visualization complete: {len(all_components)} components displayed")
    
    def _setup_component_interactions(self):
        """Setup enhanced component interactions"""
        print("🔧 Setting up component interactions...")
        # Component interactions are handled by mousePressEvent
        pass
    
    def _handle_component_selection(self, comp_item: ComponentGraphicsItem):
        """Handle component selection with navigation integration - FIXED"""
        try:
            # Clear previous selection
            if self.current_selection and self.current_selection != comp_item:
                self.current_selection.clear_highlight()
            
            # Set new selection
            self.current_selection = comp_item
            comp_item.highlight("selection")
            
            # Get component from graphics item
            component = comp_item.component
            if component:
                # Emit selection signal
                self.component_selected.emit(component)
                self.logger.debug(f"Component selected: {component.short_name}")
            
        except Exception as e:
            print(f"❌ Component selection handling failed: {e}")
    
    def _handle_component_double_click(self, comp_item: ComponentGraphicsItem):
        """Handle component double-click with navigation integration - FIXED"""
        try:
            component = comp_item.component
            if component:
                self.component_double_clicked.emit(component)
                
                # Focus on component
                self.focus_on_component(component.uuid)
                
                self.logger.debug(f"Component double-clicked: {component.short_name}")
                
        except Exception as e:
            print(f"❌ Component double-click handling failed: {e}")
    
    def _on_selection_changed(self):
        """Handle selection changes in the scene - FIXED"""
        try:
            selected_items = self.selectedItems()
            
            if selected_items:
                for item in selected_items:
                    if isinstance(item, ComponentGraphicsItem):
                        # Don't re-trigger if already selected
                        if self.current_selection != item:
                            self._handle_component_selection(item)
                        break
            else:
                # Clear selection
                if self.current_selection:
                    self.current_selection.clear_highlight()
                    self.current_selection = None
                
                self.component_selected.emit(None)
                self.selection_cleared.emit()
                
        except Exception as e:
            print(f"❌ Selection change handling failed: {e}")
    
    def highlight_component(self, component_uuid: str, highlight_type: str = "selection"):
        """Highlight a specific component - FIXED"""
        try:
            # Clear previous highlights of this type
            if highlight_type == "selection":
                self._clear_all_highlights()
            
            # Highlight specified component
            if component_uuid in self.components:
                comp_item = self.components[component_uuid]
                comp_item.highlight(highlight_type)
                
                if highlight_type == "selection":
                    self.current_selection = comp_item
                    # Select the item in the scene
                    self.clearSelection()
                    comp_item.setSelected(True)
                
                self.highlighted_components.add(component_uuid)
                
                component = comp_item.component
                if component:
                    self.logger.debug(f"Component highlighted: {component.short_name} ({highlight_type})")
                    
        except Exception as e:
            print(f"❌ Component highlighting failed: {e}")
    
    def focus_on_component(self, component_uuid: str):
        """Focus and center view on specific component - FIXED"""
        try:
            if component_uuid in self.components:
                comp_item = self.components[component_uuid]
                
                # Highlight with focus style
                comp_item.highlight("focus")
                
                # Center view on component
                comp_rect = comp_item.sceneBoundingRect()
                self.setSceneRect(comp_rect.adjusted(-200, -200, 200, 200))
                
                # Emit focus signal
                self.component_focused.emit(component_uuid)
                
                # Clear focus highlight after a delay
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(2000, lambda: self._clear_focus_highlight(component_uuid))
                
                component = comp_item.component
                if component:
                    self.logger.debug(f"Focused on component: {component.short_name}")
                    
        except Exception as e:
            print(f"❌ Component focus failed: {e}")
    
    def _clear_focus_highlight(self, component_uuid: str):
        """Clear focus highlight after delay - FIXED"""
        try:
            if component_uuid in self.components:
                comp_item = self.components[component_uuid]
                if comp_item != self.current_selection:
                    comp_item.clear_highlight()
                else:
                    comp_item.highlight("selection")  # Restore selection highlight
        except Exception as e:
            print(f"❌ Clear focus highlight failed: {e}")
    
    def _clear_all_highlights(self):
        """Clear all component highlights except search results - FIXED"""
        try:
            for comp_item in self.components.values():
                component = comp_item.component
                if component and component.uuid not in self.search_results:
                    comp_item.clear_highlight()
            
            self.highlighted_components.clear()
            self.current_selection = None
            
        except Exception as e:
            print(f"❌ Clear highlights failed: {e}")
    
    def mousePressEvent(self, event):
        """Handle mouse press events for component selection - FIXED"""
        try:
            # Check if we have any views
            if not self.views():
                super().mousePressEvent(event)
                return
            
            # Get item at click position
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            
            if item:
                print(f"🔧 Item clicked: {type(item).__name__}")
                
                # Check if it's a ComponentGraphicsItem - FIXED
                if isinstance(item, ComponentGraphicsItem):
                    print(f"✅ Component clicked: {item.component.short_name}")
                    self._handle_component_selection(item)
                elif hasattr(item, 'parentItem') and isinstance(item.parentItem(), ComponentGraphicsItem):
                    # Clicked on a child item (like port or label) - select parent component
                    parent_item = item.parentItem()
                    print(f"✅ Component clicked via child: {parent_item.component.short_name}")
                    self._handle_component_selection(parent_item)
            else:
                # Clicked on empty space - clear selection
                if self.current_selection:
                    self.current_selection.clear_highlight()
                    self.current_selection = None
                self.clearSelection()
                self.component_selected.emit(None)
            
        except Exception as e:
            print(f"❌ Mouse press handling failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Call parent implementation
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle mouse double-click events - FIXED"""
        try:
            if not self.views():
                super().mouseDoubleClickEvent(event)
                return
            
            # Get item at click position
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            
            if item and isinstance(item, ComponentGraphicsItem):
                print(f"🔧 Component double-clicked: {item.component.short_name}")
                self._handle_component_double_click(item)
            
        except Exception as e:
            print(f"❌ Double-click handling failed: {e}")
        
        super().mouseDoubleClickEvent(event)
    
    def fit_components_in_view(self):
        """Adjust scene rect to fit all components - FIXED"""
        try:
            if self.components:
                # Calculate bounding rect of all components
                min_x = min_y = float('inf')
                max_x = max_y = float('-inf')
                
                for comp_item in self.components.values():
                    rect = comp_item.sceneBoundingRect()
                    min_x = min(min_x, rect.left())
                    min_y = min(min_y, rect.top())
                    max_x = max(max_x, rect.right())
                    max_y = max(max_y, rect.bottom())
                
                # Add some padding
                padding = 50
                self.setSceneRect(
                    min_x - padding,
                    min_y - padding, 
                    max_x - min_x + 2 * padding,
                    max_y - min_y + 2 * padding
                )
                
        except Exception as e:
            print(f"❌ Fit to view failed: {e}")
    
    def clear_scene(self):
        """Clear all items from scene - FIXED"""
        try:
            self.clear()
            self.components.clear()
            self.connections.clear()
            self.search_results.clear()
            self.highlighted_components.clear()
            self.current_selection = None
            
            # Reset scene rect
            self.setSceneRect(0, 0, 2000, 1500)
            print("✅ Scene cleared")
            
        except Exception as e:
            print(f"❌ Scene clear failed: {e}")
    
    def get_visible_components(self) -> List:
        """Get list of currently visible components - FIXED"""
        try:
            visible_components = []
            scene_rect = self.sceneRect()
            
            for comp_item in self.components.values():
                if comp_item.isVisible() and scene_rect.intersects(comp_item.sceneBoundingRect()):
                    component = comp_item.component
                    if component:
                        visible_components.append(component)
            
            return visible_components
            
        except Exception as e:
            print(f"❌ Get visible components failed: {e}")
            return []
    
    def get_scene_statistics(self) -> Dict[str, int]:
        """Get scene statistics - FIXED"""
        try:
            return {
                'total_components': len(self.components),
                'search_results': len(self.search_results),
                'highlighted_components': len(self.highlighted_components),
                'visible_components': len(self.get_visible_components()),
                'selected_components': 1 if self.current_selection else 0
            }
        except Exception as e:
            print(f"❌ Get statistics failed: {e}")
            return {'total_components': 0, 'search_results': 0, 'highlighted_components': 0, 'visible_components': 0, 'selected_components': 0}