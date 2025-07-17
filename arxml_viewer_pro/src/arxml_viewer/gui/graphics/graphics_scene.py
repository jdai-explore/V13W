# src/arxml_viewer/gui/graphics/graphics_scene.py - FIXED VERSION FOR UNIQUE COMPONENTS
"""
Graphics Scene - FIXED to handle unique components correctly
FIXES APPLIED:
1. Enhanced deduplication logic based on UUIDs
2. Better component grouping and display
3. Improved component information display
4. Fixed component positioning to avoid overlaps
"""

import math
from typing import Dict, List, Optional, Any, Set
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
    """FIXED component graphics item with enhanced component info display"""
    
    def __init__(self, component: Component, parent=None):
        super().__init__(parent)
        
        self.component = component
        self.logger = get_logger(__name__)
        
        # State
        self.is_highlighted = False
        self.port_items: List[QGraphicsEllipseItem] = []
        
        # Set up component rectangle
        self._setup_component()
        
        # Create label with enhanced info
        self._create_enhanced_label()
        
        # Create ports
        self._create_ports()
        
        # Make item selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        # Set enhanced tooltip
        self.setToolTip(self._generate_enhanced_tooltip())
    
    def _setup_component(self):
        """Setup component rectangle with enhanced sizing"""
        try:
            # Enhanced sizing based on component type and content
            base_width = UIConstants.COMPONENT_MIN_WIDTH
            base_height = UIConstants.COMPONENT_MIN_HEIGHT
            
            # Adjust width for name length
            name_length = len(self.component.short_name or "Component")
            width = max(base_width, name_length * 10 + 60)
            
            # Adjust height for ports and type
            port_count = len(self.component.all_ports) if hasattr(self.component, 'all_ports') else 0
            height = max(base_height, port_count * 18 + 80)
            
            # Extra height for composition components
            if self.component.component_type == ComponentType.COMPOSITION:
                height += 20
            
            self.setRect(0, 0, width, height)
            
            # Apply styling
            self._apply_enhanced_styling()
            
        except Exception as e:
            self.logger.error(f"Component setup failed: {e}")
            self.setRect(0, 0, UIConstants.COMPONENT_MIN_WIDTH, UIConstants.COMPONENT_MIN_HEIGHT)
    
    def _apply_enhanced_styling(self):
        """Apply enhanced styling based on component type and state"""
        try:
            # Get color based on component type
            if hasattr(self.component, 'component_type'):
                component_type_name = self.component.component_type.name
                color_tuple = AppConstants.COMPONENT_COLORS.get(
                    component_type_name, 
                    AppConstants.COMPONENT_COLORS['APPLICATION']
                )
            else:
                color_tuple = AppConstants.COMPONENT_COLORS['APPLICATION']
            
            color = QColor(*color_tuple)
            
            # Apply highlighting if needed
            if self.is_highlighted:
                color = color.lighter(130)
                pen_width = 3
            else:
                pen_width = 2
            
            # Special styling for composition components
            if self.component.component_type == ComponentType.COMPOSITION:
                pen_width = 3
                # Use dashed line for compositions
                pen = QPen(color.darker(150), pen_width)
                pen.setStyle(Qt.DashLine)
                self.setPen(pen)
            else:
                self.setPen(QPen(color.darker(150), pen_width))
            
            self.setBrush(QBrush(color))
            self.setZValue(1)
            
        except Exception as e:
            self.logger.error(f"Enhanced styling failed: {e}")
            # Fallback styling
            self.setBrush(QBrush(QColor(100, 150, 200)))
            self.setPen(QPen(QColor(50, 75, 100), 2))
    
    def _create_enhanced_label(self):
        """Create enhanced component label with type information"""
        try:
            comp_rect = self.rect()
            
            # Main component name
            display_name = self.component.short_name or "Unnamed"
            
            # Add type indicator
            type_indicator = ""
            if hasattr(self.component, 'component_type'):
                if self.component.component_type == ComponentType.APPLICATION:
                    type_indicator = " [APP]"
                elif self.component.component_type == ComponentType.COMPOSITION:
                    type_indicator = " [COMP]"
                elif self.component.component_type == ComponentType.SERVICE:
                    type_indicator = " [SVC]"
                else:
                    type_indicator = f" [{self.component.component_type.name[:4]}]"
            
            full_display_name = display_name + type_indicator
            
            self.label = QGraphicsTextItem(full_display_name, self)
            
            # Position label in center of component
            label_rect = self.label.boundingRect()
            x = (comp_rect.width() - label_rect.width()) / 2
            y = (comp_rect.height() - label_rect.height()) / 2 - 15
            
            self.label.setPos(x, y)
            
            # Enhanced label styling
            font = QFont("Arial", 9)
            font.setWeight(QFont.Bold)
            self.label.setFont(font)
            self.label.setDefaultTextColor(QColor(255, 255, 255))
            
            # Add UUID info (first 8 characters)
            if hasattr(self.component, 'uuid') and self.component.uuid:
                uuid_short = self.component.uuid[:8]
                uuid_label = QGraphicsTextItem(f"UUID: {uuid_short}", self)
                uuid_font = QFont("Arial", 7)
                uuid_label.setFont(uuid_font)
                uuid_label.setDefaultTextColor(QColor(200, 200, 200))
                
                # Position below main label
                uuid_rect = uuid_label.boundingRect()
                uuid_x = (comp_rect.width() - uuid_rect.width()) / 2
                uuid_y = y + label_rect.height() + 2
                uuid_label.setPos(uuid_x, uuid_y)
            
        except Exception as e:
            self.logger.error(f"Enhanced label creation failed: {e}")
    
    def _create_ports(self):
        """Create port representations"""
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
            
            # Separate provided and required ports
            provided_ports = [p for p in ports if hasattr(p, 'is_provided') and p.is_provided]
            required_ports = [p for p in ports if hasattr(p, 'is_required') and p.is_required]
            
            # Position provided ports on right side
            self._position_ports(provided_ports, "right", comp_rect, port_size)
            
            # Position required ports on left side
            self._position_ports(required_ports, "left", comp_rect, port_size)
            
            print(f"✅ Created {len(self.port_items)} port items for {self.component.short_name}")
            
        except Exception as e:
            print(f"❌ Port creation failed: {e}")
            self.logger.error(f"Port creation failed: {e}")
    
    def _position_ports(self, ports: List[Port], side: str, comp_rect: QRectF, port_size: float):
        """Position ports on specified side"""
        try:
            if not ports:
                return
            
            port_spacing = comp_rect.height() / (len(ports) + 1)
            
            for i, port in enumerate(ports):
                # Calculate position
                if side == "right":
                    x = comp_rect.width() - port_size / 2
                else:  # left
                    x = -port_size / 2
                
                y = (i + 1) * port_spacing - port_size / 2
                
                # Create port item
                port_item = QGraphicsEllipseItem(-port_size/2, -port_size/2, port_size, port_size, self)
                port_item.setPos(x, y)
                
                # Set color based on port type
                if hasattr(port, 'is_provided') and port.is_provided:
                    color = QColor(*AppConstants.PORT_COLORS['PROVIDED'])
                else:
                    color = QColor(*AppConstants.PORT_COLORS['REQUIRED'])
                
                port_item.setBrush(QBrush(color))
                port_item.setPen(QPen(color.darker(150), 1))
                port_item.setZValue(10)
                
                # Store port reference
                port_item.port = port
                
                # Enhanced tooltip
                port_item.setToolTip(f"{port.short_name}\nType: {port.port_type.value}\nUUID: {port.uuid[:8] if port.uuid else 'N/A'}")
                
                self.port_items.append(port_item)
                
        except Exception as e:
            print(f"❌ Port positioning failed: {e}")
            self.logger.error(f"Port positioning failed: {e}")
    
    def _generate_enhanced_tooltip(self) -> str:
        """Generate enhanced tooltip with detailed component information"""
        try:
            tooltip = f"<b>{self.component.short_name}</b><br>"
            
            if hasattr(self.component, 'component_type'):
                tooltip += f"Type: {self.component.component_type.value}<br>"
            
            if hasattr(self.component, 'uuid'):
                tooltip += f"UUID: {self.component.uuid}<br>"
            
            if hasattr(self.component, 'package_path'):
                tooltip += f"Package: {self.component.package_path}<br>"
            
            if hasattr(self.component, 'all_ports'):
                tooltip += f"Ports: {len(self.component.all_ports)}<br>"
                
                provided_count = len([p for p in self.component.all_ports if hasattr(p, 'is_provided') and p.is_provided])
                required_count = len([p for p in self.component.all_ports if hasattr(p, 'is_required') and p.is_required])
                
                tooltip += f"  • Provided: {provided_count}<br>"
                tooltip += f"  • Required: {required_count}<br>"
            
            if hasattr(self.component, 'desc') and self.component.desc:
                tooltip += f"<br>Description:<br>{self.component.desc}"
            
            return tooltip
        except Exception as e:
            return f"Component: {getattr(self.component, 'short_name', 'Unknown')}"
    
    def highlight(self, highlight_type: str = "selection"):
        """Enhanced highlighting"""
        self.is_highlighted = True
        self._apply_enhanced_styling()
    
    def clear_highlight(self):
        """Clear highlighting"""
        self.is_highlighted = False
        self._apply_enhanced_styling()
    
    def get_port_items(self) -> List[QGraphicsEllipseItem]:
        """Get port graphics items"""
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
    FIXED Graphics Scene - prevents component duplication and shows correct information
    """
    
    # Signals
    component_selected = pyqtSignal(object)  # Component object
    component_double_clicked = pyqtSignal(object)  # Component object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        
        # Enhanced scene state
        self.components: Dict[str, ComponentGraphicsItem] = {}  # UUID -> graphics item
        self.connections: List[QGraphicsLineItem] = []
        self.component_positions: Dict[str, QPointF] = {}  # Track positions to avoid overlaps
        
        # Layout parameters
        self.grid_size = 20
        self.component_spacing = 200  # Increased spacing
        
        # Set scene properties
        self.setSceneRect(0, 0, 2000, 1500)
        self.setBackgroundBrush(QBrush(QColor(245, 245, 245)))
        
        # Connect signals
        self.selectionChanged.connect(self._on_selection_changed)
        
        print("✅ FIXED ComponentDiagramScene initialized")
    
    def load_packages(self, packages: List[Package], connections: List[Connection] = None):
        """Load and visualize packages - FIXED to prevent duplicates and show correct UUIDs"""
        print(f"🔧 FIXED graphics scene loading {len(packages)} packages")
        
        # Clear existing content
        self.clear_scene()
        
        # ENHANCED: Track components by UUID to prevent duplicates
        unique_components_by_uuid: Dict[str, Component] = {}
        component_count_by_package = {}
        
        # Collect all unique components
        for package in packages:
            try:
                package_components = []
                
                # Get direct components
                direct_components = package.components
                component_count_by_package[package.short_name] = len(direct_components)
                
                for comp in direct_components:
                    if hasattr(comp, 'uuid') and comp.uuid:
                        if comp.uuid not in unique_components_by_uuid:
                            unique_components_by_uuid[comp.uuid] = comp
                            package_components.append(comp)
                            print(f"✅ Added unique component: {comp.short_name} (UUID: {comp.uuid[:8]}...)")
                        else:
                            print(f"⚠️ Skipping duplicate component: {comp.short_name} (UUID: {comp.uuid[:8]}...)")
                    else:
                        print(f"⚠️ Component without UUID: {comp.short_name}")
                
                # Process sub-packages recursively
                self._collect_components_recursive(package.sub_packages, unique_components_by_uuid, 1)
                    
            except Exception as e:
                print(f"⚠️ Failed to process package {package.short_name}: {e}")
        
        # Convert to list
        all_unique_components = list(unique_components_by_uuid.values())
        
        print(f"📊 Component deduplication summary:")
        for pkg_name, count in component_count_by_package.items():
            print(f"  - {pkg_name}: {count} direct components")
        print(f"Total unique components: {len(all_unique_components)}")
        
        if not all_unique_components:
            print("⚠️ No components found to display")
            return
        
        # Create component graphics with enhanced info
        self._create_enhanced_component_graphics(all_unique_components)
        
        # Create connections
        if connections:
            print(f"🔗 Loading {len(connections)} connections")
            self._create_enhanced_connections(connections)
        else:
            print("⚠️ No connections provided")
        
        # Apply intelligent layout
        self._apply_intelligent_layout(all_unique_components)
        
        # Update scene rect
        self._update_scene_rect()
        
        print(f"✅ FIXED visualization complete: {len(all_unique_components)} unique components, "
              f"{len(self.connections)} connections")
    
    def _collect_components_recursive(self, sub_packages: List[Package], 
                                    unique_components: Dict[str, Component], level: int):
        """Recursively collect components from sub-packages"""
        for sub_pkg in sub_packages:
            try:
                print(f"{'  ' * level}📁 Processing sub-package: {sub_pkg.short_name}")
                
                for comp in sub_pkg.components:
                    if hasattr(comp, 'uuid') and comp.uuid:
                        if comp.uuid not in unique_components:
                            unique_components[comp.uuid] = comp
                            print(f"{'  ' * level}✅ Added unique component: {comp.short_name} (UUID: {comp.uuid[:8]}...)")
                        else:
                            print(f"{'  ' * level}⚠️ Skipping duplicate: {comp.short_name}")
                
                # Recurse into nested packages
                if sub_pkg.sub_packages:
                    self._collect_components_recursive(sub_pkg.sub_packages, unique_components, level + 1)
                    
            except Exception as e:
                print(f"{'  ' * level}❌ Failed to process sub-package: {e}")
    
    def _create_enhanced_component_graphics(self, components: List[Component]):
        """Create enhanced component graphics with better information display"""
        try:
            for component in components:
                try:
                    print(f"Creating enhanced component graphics: {component.short_name}")
                    
                    # Create enhanced ComponentGraphicsItem
                    comp_item = ComponentGraphicsItem(component)
                    
                    # Add to scene
                    self.addItem(comp_item)
                    
                    # Store reference by UUID
                    if hasattr(component, 'uuid') and component.uuid:
                        self.components[component.uuid] = comp_item
                    else:
                        # Fallback to name if no UUID
                        self.components[component.short_name] = comp_item
                    
                    print(f"✅ Created enhanced component graphics: {component.short_name}")
                    
                except Exception as e:
                    print(f"❌ Failed to create enhanced component {component.short_name}: {e}")
                    continue
            
            print(f"✅ Created {len(self.components)} enhanced component graphics")
            
        except Exception as e:
            print(f"❌ Enhanced component graphics creation failed: {e}")
            self.logger.error(f"Enhanced component graphics creation failed: {e}")
    
    def _create_enhanced_connections(self, connections: List[Connection]):
        """Create enhanced connections with better visualization"""
        try:
            connections_created = 0
            
            for connection in connections:
                try:
                    # Find start and end components by UUID
                    start_comp_uuid = None
                    end_comp_uuid = None
                    
                    if hasattr(connection, 'provider_endpoint') and hasattr(connection, 'requester_endpoint'):
                        start_comp_uuid = connection.provider_endpoint.component_uuid
                        end_comp_uuid = connection.requester_endpoint.component_uuid
                    
                    if start_comp_uuid and end_comp_uuid:
                        start_comp_item = self.components.get(start_comp_uuid)
                        end_comp_item = self.components.get(end_comp_uuid)
                        
                        if start_comp_item and end_comp_item:
                            # Create enhanced connection line
                            line_item = self._create_enhanced_connection_line(start_comp_item, end_comp_item, connection)
                            if line_item:
                                self.connections.append(line_item)
                                connections_created += 1
                        else:
                            print(f"⚠️ Could not find component items for connection: {connection.short_name}")
                            print(f"   Start UUID: {start_comp_uuid}")
                            print(f"   End UUID: {end_comp_uuid}")
                            print(f"   Available components: {list(self.components.keys())}")
                    
                except Exception as e:
                    print(f"❌ Failed to create enhanced connection {getattr(connection, 'short_name', 'Unknown')}: {e}")
                    continue
            
            print(f"🔗 Enhanced connection creation complete: {connections_created} lines created")
            
        except Exception as e:
            print(f"❌ Enhanced connection creation failed: {e}")
            self.logger.error(f"Enhanced connection creation failed: {e}")
    
    def _create_enhanced_connection_line(self, start_comp: ComponentGraphicsItem, 
                                       end_comp: ComponentGraphicsItem, connection: Connection) -> Optional[QGraphicsLineItem]:
        """Create an enhanced connection line between two components"""
        try:
            # Get component positions
            start_pos = start_comp.scenePos()
            end_pos = end_comp.scenePos()
            
            # Get component rectangles for better connection points
            start_rect = start_comp.rect()
            end_rect = end_comp.rect()
            
            # Calculate connection points (edges instead of centers)
            start_center = QPointF(
                start_pos.x() + start_rect.width() / 2,
                start_pos.y() + start_rect.height() / 2
            )
            end_center = QPointF(
                end_pos.x() + end_rect.width() / 2,
                end_pos.y() + end_rect.height() / 2
            )
            
            # Create enhanced line
            line = QGraphicsLineItem(start_center.x(), start_center.y(), end_center.x(), end_center.y())
            
            # Enhanced line styling based on connection type
            if hasattr(connection, 'connection_type'):
                if connection.connection_type == ConnectionType.ASSEMBLY:
                    color = QColor(46, 125, 50)      # Green for assembly
                    width = 2
                elif connection.connection_type == ConnectionType.DELEGATION:
                    color = QColor(255, 152, 0)      # Orange for delegation
                    width = 3
                else:
                    color = QColor(96, 125, 139)     # Gray for others
                    width = 2
            else:
                color = QColor(100, 149, 237)        # Default blue
                width = 2
            
            pen = QPen(color, width)
            pen.setCapStyle(Qt.RoundCap)
            line.setPen(pen)
            line.setZValue(5)
            
            # Store connection reference
            line.connection = connection
            
            # Enhanced tooltip
            tooltip = f"Connection: {getattr(connection, 'short_name', 'Unknown')}"
            if hasattr(connection, 'connection_type'):
                tooltip += f"\nType: {connection.connection_type.value}"
            if hasattr(connection, 'desc') and connection.desc:
                tooltip += f"\nDescription: {connection.desc}"
            line.setToolTip(tooltip)
            
            # Add to scene
            self.addItem(line)
            
            return line
            
        except Exception as e:
            print(f"❌ Enhanced connection line creation failed: {e}")
            return None
    
    def _apply_intelligent_layout(self, components: List[Component]):
        """Apply intelligent layout to avoid overlaps and group related components"""
        try:
            # Group components by type
            component_groups = {
                ComponentType.COMPOSITION: [],
                ComponentType.APPLICATION: [],
                ComponentType.SERVICE: [],
                ComponentType.SENSOR_ACTUATOR: [],
                ComponentType.COMPLEX_DEVICE_DRIVER: []
            }
            
            for component in components:
                comp_type = getattr(component, 'component_type', ComponentType.APPLICATION)
                component_groups[comp_type].append(component)
            
            # Layout parameters
            group_spacing_x = 300
            group_spacing_y = 250
            component_spacing = self.component_spacing
            
            current_x = 50
            max_y = 0
            
            # Layout each group
            for comp_type, group_components in component_groups.items():
                if not group_components:
                    continue
                
                print(f"📐 Laying out {len(group_components)} {comp_type.name} components")
                
                # Calculate grid for this group
                cols = max(1, math.ceil(math.sqrt(len(group_components))))
                
                group_start_y = 50
                group_max_y = group_start_y
                
                for i, component in enumerate(group_components):
                    if hasattr(component, 'uuid') and component.uuid in self.components:
                        row = i // cols
                        col = i % cols
                        
                        x = current_x + col * component_spacing
                        y = group_start_y + row * group_spacing_y
                        
                        comp_item = self.components[component.uuid]
                        comp_item.setPos(x, y)
                        
                        # Track position
                        self.component_positions[component.uuid] = QPointF(x, y)
                        
                        group_max_y = max(group_max_y, y + component_spacing)
                
                # Move to next group position
                current_x += (cols * component_spacing) + group_spacing_x
                max_y = max(max_y, group_max_y)
            
            # Update connections after positioning
            self._update_enhanced_connections()
            
            print(f"✅ Applied intelligent layout to {len(components)} components")
            
        except Exception as e:
            print(f"❌ Intelligent layout failed: {e}")
            self.logger.error(f"Intelligent layout failed: {e}")
    
    def _update_enhanced_connections(self):
        """Update enhanced connection lines after component movement"""
        try:
            for line_item in self.connections:
                if hasattr(line_item, 'connection'):
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
            print(f"❌ Enhanced connection update failed: {e}")
    
    def _update_scene_rect(self):
        """Update scene rectangle to fit all content"""
        try:
            if self.components:
                items_rect = self.itemsBoundingRect()
                
                # Add margins
                margin = 150
                expanded_rect = items_rect.adjusted(-margin, -margin, margin, margin)
                
                # Ensure minimum size
                min_width = 1200
                min_height = 900
                
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
        """Handle selection changes with enhanced component info"""
        try:
            selected_items = self.selectedItems()
            if selected_items:
                item = selected_items[0]
                if isinstance(item, ComponentGraphicsItem):
                    self.component_selected.emit(item.component)
                    print(f"🔧 Component selected: {item.component.short_name} (UUID: {item.component.uuid[:8]}...)")
        except Exception as e:
            print(f"❌ Enhanced selection handling failed: {e}")
    
    def highlight_component(self, component_uuid: str):
        """Enhanced component highlighting"""
        try:
            if component_uuid in self.components:
                comp_item = self.components[component_uuid]
                comp_item.highlight("focus")
        except Exception as e:
            self.logger.error(f"Component highlighting failed: {e}")
    
    def clear_scene(self):
        """Clear the scene"""
        try:
            # Clear tracking dictionaries
            self.components.clear()
            self.connections.clear()
            self.component_positions.clear()
            
            # Clear scene items
            self.clear()
            
            print("✅ Scene cleared")
            
        except Exception as e:
            self.logger.error(f"Scene clearing failed: {e}")
    
    def auto_arrange_layout(self):
        """Auto-arrange with intelligent grouping"""
        try:
            if not self.components:
                return
            
            # Get all component objects
            component_objects = []
            for comp_item in self.components.values():
                if hasattr(comp_item, 'component'):
                    component_objects.append(comp_item.component)
            
            # Apply intelligent layout
            self._apply_intelligent_layout(component_objects)
            
            print("✅ Enhanced auto-arrangement completed")
            
        except Exception as e:
            print(f"❌ Enhanced auto-arrangement failed: {e}")
            self.logger.error(f"Enhanced auto-arrangement failed: {e}")

# Export classes
__all__ = ['ComponentDiagramScene', 'ComponentGraphicsItem']