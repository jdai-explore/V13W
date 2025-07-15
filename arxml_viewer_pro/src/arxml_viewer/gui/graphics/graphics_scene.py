# src/arxml_viewer/gui/graphics/graphics_scene.py - FIXED VERSION
"""
Graphics Scene - FIXED to prevent component duplication
SIGNIFICANT SIMPLIFICATION as per guide requirements
"""

import math
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, 
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import QColor, QPen, QBrush, QFont

from ...models.component import Component, ComponentType
from ...models.package import Package
from ...models.port import Port
from ...models.connection import Connection, ConnectionType
from ...utils.constants import AppConstants, UIConstants
from ...utils.logger import get_logger

class ComponentGraphicsItem(QGraphicsRectItem):
    """
    SIMPLIFIED component graphics item - basic rectangle with text
    Removed Day 5 enhancements and complex functionality
    """
    
    def __init__(self, component: Component, parent=None):
        super().__init__(parent)
        
        self.component = component
        self.logger = get_logger(__name__)
        
        # SIMPLIFIED state - basic only
        self.is_highlighted = False
        self.port_items: List[QGraphicsEllipseItem] = []
        
        # Set up BASIC component rectangle
        self._setup_basic_component()
        
        # Create BASIC label
        self._create_basic_label()
        
        # Create BASIC ports
        self._create_basic_ports()
        
        # Make item selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        # Set basic tooltip
        self.setToolTip(self._generate_basic_tooltip())
    
    def _setup_basic_component(self):
        """Setup BASIC component rectangle with simple sizing"""
        try:
            # SIMPLIFIED sizing calculation
            min_width = UIConstants.COMPONENT_MIN_WIDTH
            min_height = UIConstants.COMPONENT_MIN_HEIGHT
            
            # Basic width based on name length
            name_length = len(self.component.short_name or "Component")
            width = max(min_width, name_length * 8 + 40)
            
            # Basic height based on port count
            port_count = len(self.component.all_ports) if hasattr(self.component, 'all_ports') else 0
            height = max(min_height, port_count * 15 + 60)
            
            self.setRect(0, 0, width, height)
            
            # Set BASIC appearance
            self._apply_basic_styling()
            
        except Exception as e:
            self.logger.error(f"Component setup failed: {e}")
            # Fallback to minimum size
            self.setRect(0, 0, UIConstants.COMPONENT_MIN_WIDTH, UIConstants.COMPONENT_MIN_HEIGHT)
    
    def _apply_basic_styling(self):
        """Apply BASIC styling based on component type"""
        try:
            # Get basic color for component type
            if hasattr(self.component, 'component_type'):
                component_type_name = self.component.component_type.name
                color_tuple = AppConstants.COMPONENT_COLORS.get(
                    component_type_name, 
                    AppConstants.COMPONENT_COLORS['APPLICATION']
                )
            else:
                color_tuple = AppConstants.COMPONENT_COLORS['APPLICATION']
            
            color = QColor(*color_tuple)
            
            # Apply basic highlighting if needed
            if self.is_highlighted:
                color = color.lighter(130)
                pen_width = 3
            else:
                pen_width = 2
            
            # Set basic brush and pen
            self.setBrush(QBrush(color))
            self.setPen(QPen(color.darker(150), pen_width))
            
            # Basic z-value
            self.setZValue(1)
            
        except Exception as e:
            self.logger.error(f"Basic styling failed: {e}")
            # Fallback styling
            self.setBrush(QBrush(QColor(100, 150, 200)))
            self.setPen(QPen(QColor(50, 75, 100), 2))
    
    def _create_basic_label(self):
        """Create BASIC component name label"""
        try:
            comp_rect = self.rect()
            
            # Basic component name
            display_name = self.component.short_name or "Unnamed"
            
            self.label = QGraphicsTextItem(display_name, self)
            
            # Position label in center of component
            label_rect = self.label.boundingRect()
            x = (comp_rect.width() - label_rect.width()) / 2
            y = (comp_rect.height() - label_rect.height()) / 2 - 10
            
            self.label.setPos(x, y)
            
            # Basic label styling
            font = QFont("Arial", 9)
            font.setWeight(QFont.Bold)
            self.label.setFont(font)
            self.label.setDefaultTextColor(QColor(255, 255, 255))
            
        except Exception as e:
            self.logger.error(f"Basic label creation failed: {e}")
    
    def _create_basic_ports(self):
        """Create BASIC port representations - simple ellipses"""
        try:
            self.port_items.clear()
            
            if not hasattr(self.component, 'all_ports'):
                return
            
            ports = self.component.all_ports
            total_ports = len(ports)
            
            if total_ports == 0:
                return
            
            comp_rect = self.rect()
            port_size = UIConstants.COMPONENT_PORT_SIZE
            
            # SIMPLE port positioning - distribute evenly on sides
            provided_ports = [p for p in ports if hasattr(p, 'is_provided') and p.is_provided]
            required_ports = [p for p in ports if hasattr(p, 'is_required') and p.is_required]
            
            # Position provided ports on right side
            self._position_basic_ports(provided_ports, "right", comp_rect, port_size)
            
            # Position required ports on left side
            self._position_basic_ports(required_ports, "left", comp_rect, port_size)
            
            print(f"✅ Created {len(self.port_items)} basic port items for {self.component.short_name}")
            
        except Exception as e:
            print(f"❌ Basic port creation failed: {e}")
            self.logger.error(f"Basic port creation failed: {e}")
    
    def _position_basic_ports(self, ports: List[Port], side: str, comp_rect: QRectF, port_size: float):
        """Position ports on specified side - BASIC implementation"""
        try:
            if not ports:
                return
            
            port_spacing = comp_rect.height() / (len(ports) + 1)
            
            for i, port in enumerate(ports):
                # Calculate basic position
                if side == "right":
                    x = comp_rect.width() - port_size / 2
                else:  # left
                    x = -port_size / 2
                
                y = (i + 1) * port_spacing - port_size / 2
                
                # Create BASIC port item - simple ellipse
                port_item = QGraphicsEllipseItem(-port_size/2, -port_size/2, port_size, port_size, self)
                port_item.setPos(x, y)
                
                # Set BASIC color based on port type
                if hasattr(port, 'is_provided') and port.is_provided:
                    color = QColor(*AppConstants.PORT_COLORS['PROVIDED'])
                else:
                    color = QColor(*AppConstants.PORT_COLORS['REQUIRED'])
                
                port_item.setBrush(QBrush(color))
                port_item.setPen(QPen(color.darker(150), 1))
                port_item.setZValue(10)
                
                # Store port reference for later use
                port_item.port = port
                
                # Basic tooltip
                port_item.setToolTip(f"{port.short_name}")
                
                self.port_items.append(port_item)
                
        except Exception as e:
            print(f"❌ Basic port positioning failed: {e}")
            self.logger.error(f"Basic port positioning failed: {e}")
    
    def _generate_basic_tooltip(self) -> str:
        """Generate BASIC tooltip"""
        try:
            tooltip = f"{self.component.short_name}\n"
            if hasattr(self.component, 'component_type'):
                tooltip += f"Type: {self.component.component_type.value}\n"
            if hasattr(self.component, 'all_ports'):
                tooltip += f"Ports: {len(self.component.all_ports)}\n"
            tooltip += f"UUID: {self.component.uuid}"
            return tooltip
        except Exception as e:
            return f"Component: {getattr(self.component, 'short_name', 'Unknown')}"
    
    def highlight(self, highlight_type: str = "selection"):
        """BASIC highlighting"""
        self.is_highlighted = True
        self._apply_basic_styling()
    
    def clear_highlight(self):
        """Clear BASIC highlighting"""
        self.is_highlighted = False
        self._apply_basic_styling()
    
    def get_port_items(self) -> List[QGraphicsEllipseItem]:
        """Get basic port graphics items"""
        return self.port_items
    
    def get_port_by_uuid(self, port_uuid: str):
        """Get port graphics item by UUID"""
        try:
            for port_item in self.port_items:
                if hasattr(port_item, 'port') and hasattr(port_item.port, 'uuid'):
                    if port_item.port.uuid == port_uuid:
                        return port_item
            return None
        except Exception as e:
            self.logger.error(f"Get port by UUID failed: {e}")
            return None

class ComponentDiagramScene(QGraphicsScene):
    """
    FIXED Graphics Scene - prevent component duplication
    Basic functionality only: Load components, display as rectangles, simple connections as lines
    """
    
    # BASIC signals only
    component_selected = pyqtSignal(object)  # Component object
    component_double_clicked = pyqtSignal(object)  # Component object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        
        # SIMPLIFIED scene state
        self.components: Dict[str, ComponentGraphicsItem] = {}
        self.connections: List[QGraphicsLineItem] = []  # Simple line items only
        
        # BASIC layout parameters
        self.grid_size = 20
        self.component_spacing = 180
        
        # Set basic scene properties
        self.setSceneRect(0, 0, 2000, 1500)
        self.setBackgroundBrush(QBrush(QColor(245, 245, 245)))
        
        # Connect basic selection changes
        self.selectionChanged.connect(self._on_selection_changed)
        
        print("✅ FIXED ComponentDiagramScene initialized")
    
    def load_packages(self, packages: List[Package], connections: List[Connection] = None):
        """Load and visualize packages - FIXED to prevent duplicates"""
        print(f"🔧 FIXED graphics scene loading {len(packages)} packages")
        
        # Clear existing content
        self.clear_scene()
        
        # FIXED: Use a set to track unique components by UUID
        unique_components = {}
        component_count_by_package = {}
        
        for package in packages:
            try:
                # Get components WITHOUT recursion first
                direct_components = package.components
                component_count_by_package[package.short_name] = len(direct_components)
                
                # Add direct components
                for comp in direct_components:
                    if comp.uuid not in unique_components:
                        unique_components[comp.uuid] = comp
                        print(f"✅ Added component: {comp.short_name} (UUID: {comp.uuid[:8]}...)")
                    else:
                        print(f"⚠️ Skipping duplicate component: {comp.short_name} (UUID: {comp.uuid[:8]}...)")
                
                # Process sub-packages recursively
                def process_subpackages(sub_packages, level=1):
                    for sub_pkg in sub_packages:
                        print(f"{'  ' * level}📁 Processing sub-package: {sub_pkg.short_name}")
                        for comp in sub_pkg.components:
                            if comp.uuid not in unique_components:
                                unique_components[comp.uuid] = comp
                                print(f"{'  ' * level}✅ Added component: {comp.short_name} (UUID: {comp.uuid[:8]}...)")
                            else:
                                print(f"{'  ' * level}⚠️ Skipping duplicate: {comp.short_name}")
                        # Recurse
                        if sub_pkg.sub_packages:
                            process_subpackages(sub_pkg.sub_packages, level + 1)
                
                if package.sub_packages:
                    process_subpackages(package.sub_packages)
                    
            except Exception as e:
                print(f"⚠️ Failed to get components from package {package.short_name}: {e}")
        
        # Convert unique components to list
        all_components = list(unique_components.values())
        
        print(f"📊 Component deduplication summary:")
        for pkg_name, count in component_count_by_package.items():
            print(f"  - {pkg_name}: {count} direct components")
        print(f"Total unique components: {len(all_components)}")
        
        if not all_components:
            print("⚠️ No components found to display")
            return
        
        # Create component graphics
        self._create_basic_component_graphics(all_components)
        
        # Create connections
        if connections:
            print(f"🔗 Loading {len(connections)} connections as simple lines")
            self._create_simple_connections(connections)
        else:
            print("⚠️ No connections provided")
        
        # Apply layout
        self._apply_simple_grid_layout(all_components)
        
        # Update scene rect
        self._update_basic_scene_rect()
        
        print(f"✅ FIXED visualization complete: {len(all_components)} unique components, "
              f"{len(self.connections)} connections")
    
    def _create_basic_component_graphics(self, components: List[Component]):
        """Create BASIC component graphics - simple rectangles with text"""
        try:
            for component in components:
                try:
                    print(f"Creating BASIC component graphics: {component.short_name}")
                    
                    # Create BASIC ComponentGraphicsItem
                    comp_item = ComponentGraphicsItem(component)
                    
                    # Add to scene
                    self.addItem(comp_item)
                    
                    # Store reference
                    self.components[component.uuid] = comp_item
                    
                    print(f"✅ Created BASIC component graphics: {component.short_name}")
                    
                except Exception as e:
                    print(f"❌ Failed to create BASIC component {component.short_name}: {e}")
                    continue
            
            print(f"✅ Created {len(self.components)} BASIC component graphics")
            
        except Exception as e:
            print(f"❌ BASIC component graphics creation failed: {e}")
            self.logger.error(f"BASIC component graphics creation failed: {e}")
    
    def _create_simple_connections(self, connections: List[Connection]):
        """Create SIMPLE connections as basic lines"""
        try:
            connections_created = 0
            
            for connection in connections:
                try:
                    # Find start and end components
                    start_comp_uuid = None
                    end_comp_uuid = None
                    
                    if hasattr(connection, 'provider_endpoint') and hasattr(connection, 'requester_endpoint'):
                        start_comp_uuid = connection.provider_endpoint.component_uuid
                        end_comp_uuid = connection.requester_endpoint.component_uuid
                    
                    if start_comp_uuid and end_comp_uuid:
                        start_comp_item = self.components.get(start_comp_uuid)
                        end_comp_item = self.components.get(end_comp_uuid)
                        
                        if start_comp_item and end_comp_item:
                            # Create SIMPLE line connection
                            line_item = self._create_simple_line_connection(start_comp_item, end_comp_item, connection)
                            if line_item:
                                self.connections.append(line_item)
                                connections_created += 1
                        else:
                            print(f"⚠️ Could not find component items for connection: {connection.short_name}")
                    
                except Exception as e:
                    print(f"❌ Failed to create simple connection {getattr(connection, 'short_name', 'Unknown')}: {e}")
                    continue
            
            print(f"🔗 SIMPLE connection creation complete: {connections_created} lines created")
            
        except Exception as e:
            print(f"❌ SIMPLE connection creation failed: {e}")
            self.logger.error(f"SIMPLE connection creation failed: {e}")
    
    def _create_simple_line_connection(self, start_comp: ComponentGraphicsItem, end_comp: ComponentGraphicsItem, connection: Connection) -> Optional[QGraphicsLineItem]:
        """Create a SIMPLE line connection between two components"""
        try:
            # Get basic component positions
            start_pos = start_comp.scenePos()
            end_pos = end_comp.scenePos()
            
            # Get component rectangles for center points
            start_rect = start_comp.rect()
            end_rect = end_comp.rect()
            
            # Calculate center points
            start_center = QPointF(
                start_pos.x() + start_rect.width() / 2,
                start_pos.y() + start_rect.height() / 2
            )
            end_center = QPointF(
                end_pos.x() + end_rect.width() / 2,
                end_pos.y() + end_rect.height() / 2
            )
            
            # Create SIMPLE line
            line = QGraphicsLineItem(start_center.x(), start_center.y(), end_center.x(), end_center.y())
            
            # Set BASIC line styling
            if hasattr(connection, 'connection_type'):
                if connection.connection_type == ConnectionType.ASSEMBLY:
                    color = QColor(46, 125, 50)      # Green for assembly
                elif connection.connection_type == ConnectionType.DELEGATION:
                    color = QColor(255, 152, 0)      # Orange for delegation
                else:
                    color = QColor(96, 125, 139)     # Gray for others
            else:
                color = QColor(100, 149, 237)        # Default blue
            
            pen = QPen(color, 2)
            pen.setCapStyle(Qt.RoundCap)
            line.setPen(pen)
            line.setZValue(5)
            
            # Store connection reference
            line.connection = connection
            
            # Set basic tooltip
            line.setToolTip(f"Connection: {getattr(connection, 'short_name', 'Unknown')}")
            
            # Add to scene
            self.addItem(line)
            
            return line
            
        except Exception as e:
            print(f"❌ Simple line connection creation failed: {e}")
            return None
    
    def _apply_simple_grid_layout(self, components: List[Component]):
        """Apply SIMPLE grid layout - basic positioning only"""
        try:
            cols = max(1, math.ceil(math.sqrt(len(components))))
            spacing = self.component_spacing
            
            for i, component in enumerate(components):
                if component.uuid in self.components:
                    row = i // cols
                    col = i % cols
                    
                    x = col * spacing
                    y = row * spacing
                    
                    comp_item = self.components[component.uuid]
                    comp_item.setPos(x, y)
            
            # Update simple connections after positioning
            self._update_simple_connections()
            
            print(f"✅ Applied SIMPLE grid layout to {len(components)} components")
            
        except Exception as e:
            print(f"❌ Simple grid layout failed: {e}")
            self.logger.error(f"Simple grid layout failed: {e}")
    
    def _update_simple_connections(self):
        """Update SIMPLE line connections after component movement"""
        try:
            for line_item in self.connections:
                if hasattr(line_item, 'connection'):
                    # Find the connected components
                    connection = line_item.connection
                    if hasattr(connection, 'provider_endpoint') and hasattr(connection, 'requester_endpoint'):
                        start_comp_uuid = connection.provider_endpoint.component_uuid
                        end_comp_uuid = connection.requester_endpoint.component_uuid
                        
                        start_comp = self.components.get(start_comp_uuid)
                        end_comp = self.components.get(end_comp_uuid)
                        
                        if start_comp and end_comp:
                            # Update line position
                            start_pos = start_comp.scenePos()
                            end_pos = end_comp.scenePos()
                            
                            start_rect = start_comp.rect()
                            end_rect = end_comp.rect()
                            
                            start_center = QPointF(
                                start_pos.x() + start_rect.width() / 2,
                                start_pos.y() + start_rect.height() / 2
                            )
                            end_center = QPointF(
                                end_pos.x() + end_rect.width() / 2,
                                end_pos.y() + end_rect.height() / 2
                            )
                            
                            line_item.setLine(start_center.x(), start_center.y(), end_center.x(), end_center.y())
        
        except Exception as e:
            print(f"❌ Simple connection update failed: {e}")
    
    def _update_basic_scene_rect(self):
        """Update scene rectangle to fit all content - BASIC"""
        try:
            if self.components:
                items_rect = self.itemsBoundingRect()
                
                # Add basic margins
                margin = 100
                expanded_rect = items_rect.adjusted(-margin, -margin, margin, margin)
                
                # Ensure minimum size
                min_width = 1000
                min_height = 800
                
                final_rect = QRectF(
                    expanded_rect.x(),
                    expanded_rect.y(),
                    max(expanded_rect.width(), min_width),
                    max(expanded_rect.height(), min_height)
                )
                
                self.setSceneRect(final_rect)
                print(f"✅ Scene rect updated: {final_rect.width():.0f}x{final_rect.height():.0f}")
        except Exception as e:
            self.logger.error(f"Scene rect update failed: {e}")
    
    def _on_selection_changed(self):
        """Handle BASIC selection changes"""
        try:
            selected_items = self.selectedItems()
            if selected_items:
                item = selected_items[0]
                if isinstance(item, ComponentGraphicsItem):
                    self.component_selected.emit(item.component)
                    print(f"🔧 Component selected: {item.component.short_name}")
        except Exception as e:
            print(f"❌ Basic selection handling failed: {e}")
    
    def highlight_component(self, component_uuid: str):
        """BASIC component highlighting"""
        try:
            if component_uuid in self.components:
                comp_item = self.components[component_uuid]
                comp_item.highlight("focus")
        except Exception as e:
            self.logger.error(f"Component highlighting failed: {e}")
    
    def clear_scene(self):
        """Clear the scene - SIMPLIFIED"""
        try:
            # Clear components
            self.components.clear()
            self.connections.clear()
            
            # Clear scene items
            self.clear()
            
            print("✅ Scene cleared")
            
        except Exception as e:
            self.logger.error(f"Scene clearing failed: {e}")
    
    def auto_arrange_layout(self):
        """BASIC auto-arrange - simple grid layout only"""
        try:
            if not self.components:
                return
            
            # Get all components
            components = [comp_item.component for comp_item in self.components.values()]
            
            # Apply simple grid layout
            self._apply_simple_grid_layout(components)
            
            print("✅ BASIC auto-arrangement completed")
            
        except Exception as e:
            print(f"❌ BASIC auto-arrangement failed: {e}")
            self.logger.error(f"BASIC auto-arrangement failed: {e}")

# Export classes
__all__ = ['ComponentDiagramScene', 'ComponentGraphicsItem']