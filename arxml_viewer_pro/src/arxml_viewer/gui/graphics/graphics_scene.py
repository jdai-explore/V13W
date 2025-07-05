# src/arxml_viewer/gui/graphics/graphics_scene.py (ENHANCED VERSION)
"""
Graphics Scene - Enhanced with Day 5 Connection Visualization and Drill-Down
Integrates connection rendering, navigation, and composition drill-down
PRIORITY 1: CONNECTION VISUALIZATION - Complete Implementation
"""

import math
from typing import Dict, List, Optional, Tuple, Set, Any
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, 
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem,
    QMenu, QAction, QMessageBox, QGraphicsView
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QPainter, QTransform

from ...models.component import Component, ComponentType
from ...models.package import Package
from ...models.port import Port
from ...models.connection import Connection, ConnectionType
from ...utils.constants import AppConstants, UIConstants
from ...utils.logger import get_logger

# Import connection graphics components
try:
    from .connection_graphics import ConnectionGraphicsItem, ConnectionManager
    CONNECTION_GRAPHICS_AVAILABLE = True
    print("✅ Connection graphics available")
except ImportError:
    CONNECTION_GRAPHICS_AVAILABLE = False
    print("⚠️ Connection graphics not available - using fallback")

# Import enhanced port graphics
try:
    from .port_graphics import EnhancedPortGraphicsItem
    ENHANCED_PORTS_AVAILABLE = True
    print("✅ Enhanced port graphics available")
except ImportError:
    ENHANCED_PORTS_AVAILABLE = False
    print("⚠️ Enhanced port graphics not available - using fallback")

class ComponentGraphicsItem(QGraphicsRectItem):
    """Enhanced component graphics item with Day 5 connection integration"""
    
    # Enhanced signals for Day 5
    port_selected = pyqtSignal(object)  # Port object
    port_double_clicked = pyqtSignal(object)  # Port object
    port_context_menu_requested = pyqtSignal(object, object)  # Port, QPoint
    composition_drill_requested = pyqtSignal(object)  # Component object
    
    def __init__(self, component: Component, parent=None):
        super().__init__(parent)
        
        self.component = component
        self.logger = get_logger(__name__)
        
        # Enhanced state tracking for Day 5
        self.is_highlighted = False
        self.is_search_result = False
        self.is_connection_highlighted = False
        self.search_relevance_score = 0.0
        self.original_opacity = 0.8
        
        # Day 5 - Port items with enhanced graphics
        self.port_items: List = []  # Contains EnhancedPortGraphicsItem or fallback
        self.enhanced_port_items: List = []  # For backward compatibility
        
        # Day 5 - Connection tracking
        self.connected_ports: Dict[str, List[str]] = {}  # port_uuid -> [connection_uuids]
        self.connection_items: List = []  # Connected connection graphics items
        
        # Set up component rectangle with enhanced sizing
        self._calculate_component_size()
        
        # Set colors based on component type
        self._setup_appearance()
        
        # Add component label
        self._create_enhanced_label()
        
        # Day 5 - Create enhanced ports with connection support
        self._create_enhanced_ports()
        
        # Make item selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Set tooltip
        self.setToolTip(self._generate_enhanced_tooltip())
        
        # Enhanced interaction
        self.setAcceptHoverEvents(True)
        
        # Day 5 - Composition drill-down support
        if self.component.is_composition:
            self.setCursor(Qt.PointingHandCursor)
    
    def _calculate_component_size(self):
        """Calculate component size based on content - Enhanced for Day 5"""
        try:
            # Base dimensions
            min_width = UIConstants.COMPONENT_MIN_WIDTH
            min_height = UIConstants.COMPONENT_MIN_HEIGHT
            
            # Calculate width based on name length
            name_length = len(self.component.short_name or "Component")
            text_width = max(min_width, name_length * 8 + 40)  # Rough estimate
            
            # Calculate height based on port count with better spacing
            port_count = self.component.port_count
            if port_count > 0:
                ports_per_side = max(
                    len(self.component.provided_ports),
                    len(self.component.required_ports)
                )
                port_height = ports_per_side * (UIConstants.COMPONENT_PORT_SIZE + 8) + 20
                height = max(min_height, port_height)
            else:
                height = min_height
            
            # Composition components get extra space for drill-down indicator
            if self.component.is_composition:
                height += 20
                text_width += 30  # Space for composition icon
            
            self.setRect(0, 0, text_width, height)
            
        except Exception as e:
            self.logger.error(f"Component size calculation failed: {e}")
            # Fallback to minimum size
            self.setRect(0, 0, min_width, min_height)
    
    def _setup_appearance(self):
        """Setup component appearance based on type - Enhanced for Day 5"""
        # Get color for component type
        color_tuple = AppConstants.COMPONENT_COLORS.get(
            self.component.component_type.name, 
            AppConstants.COMPONENT_COLORS['APPLICATION']
        )
        
        color = QColor(*color_tuple)
        
        # Enhanced appearance for different states
        if self.is_connection_highlighted:
            # Special highlighting for connection-related components
            color = color.lighter(120)
            pen_width = 3
            pen_color = QColor(255, 215, 0)  # Gold
        elif self.is_highlighted:
            color = color.lighter(130)
            pen_width = 3
            pen_color = color.darker(150)
        else:
            pen_width = 2
            pen_color = color.darker(150)
        
        # Set brush and pen
        self.setBrush(QBrush(color))
        self.setPen(QPen(pen_color, pen_width))
        
        # Set opacity for better visibility
        self.setOpacity(self.original_opacity)
        
        # Enhanced z-value for composition components
        if self.component.is_composition:
            self.setZValue(2)  # Slightly higher than regular components
        else:
            self.setZValue(1)
    
    def _create_enhanced_label(self):
        """Create enhanced component name label with composition indicator"""
        comp_rect = self.rect()
        
        # Component name
        display_name = self.component.short_name or "Unnamed"
        
        # Add composition indicator
        if self.component.is_composition:
            display_name = f"📦 {display_name}"
        
        self.label = QGraphicsTextItem(display_name, self)
        
        # Position label in center of component
        label_rect = self.label.boundingRect()
        
        x = (comp_rect.width() - label_rect.width()) / 2
        y = (comp_rect.height() - label_rect.height()) / 2
        
        # Adjust for ports if present
        if self.component.port_count > 0:
            y = y - 10  # Move up slightly to make room for ports
        
        self.label.setPos(x, y)
        
        # Style the label
        font = QFont("Arial", 9)
        font.setWeight(QFont.Bold)
        self.label.setFont(font)
        self.label.setDefaultTextColor(QColor(255, 255, 255))
        
        # Add composition drill-down hint
        if self.component.is_composition:
            hint_text = "(Double-click to drill down)"
            self.drill_hint = QGraphicsTextItem(hint_text, self)
            hint_font = QFont("Arial", 7)
            hint_font.setItalic(True)
            self.drill_hint.setFont(hint_font)
            self.drill_hint.setDefaultTextColor(QColor(200, 200, 200))
            
            hint_rect = self.drill_hint.boundingRect()
            hint_x = (comp_rect.width() - hint_rect.width()) / 2
            hint_y = y + label_rect.height() + 5
            self.drill_hint.setPos(hint_x, hint_y)
    
    def _create_enhanced_ports(self):
        """Create enhanced port representations with Day 5 connection support"""
        try:
            self.port_items.clear()
            self.enhanced_port_items.clear()
            
            total_ports = len(self.component.all_ports)
            if total_ports == 0:
                return
            
            comp_rect = self.rect()
            
            # Group ports by type for better layout
            provided_ports = [p for p in self.component.all_ports if p.is_provided]
            required_ports = [p for p in self.component.all_ports if p.is_required]
            
            # Position provided ports on right side
            self._position_ports_on_side(provided_ports, "right", comp_rect)
            
            # Position required ports on left side
            self._position_ports_on_side(required_ports, "left", comp_rect)
            
            print(f"✅ Created {len(self.port_items)} enhanced port items for {self.component.short_name}")
            
        except Exception as e:
            print(f"❌ Enhanced port creation failed: {e}")
            self.logger.error(f"Enhanced port creation failed: {e}")
    
    def _position_ports_on_side(self, ports: List[Port], side: str, comp_rect: QRectF):
        """Position ports on specified side of component - Enhanced for Day 5"""
        try:
            if not ports:
                return
            
            port_size = UIConstants.COMPONENT_PORT_SIZE
            port_spacing = max(port_size * 1.5, comp_rect.height() / (len(ports) + 1))
            
            for i, port in enumerate(ports):
                # Calculate position
                if side == "right":
                    x = comp_rect.width() - port_size / 2
                elif side == "left":
                    x = -port_size / 2
                else:  # top or bottom
                    x = comp_rect.width() * (i + 1) / (len(ports) + 1) - port_size / 2
                
                if side in ["left", "right"]:
                    y = comp_rect.height() * (i + 1) / (len(ports) + 1) - port_size / 2
                else:
                    y = comp_rect.height() - port_size / 2 if side == "bottom" else -port_size / 2
                
                # Create enhanced port item
                if ENHANCED_PORTS_AVAILABLE:
                    # Use enhanced port graphics with Day 5 features
                    port_item = EnhancedPortGraphicsItem(port, self)
                    port_item.setPos(x, y)
                    
                    # Connect enhanced signals
                    try:
                        port_item.port_selected.connect(self.port_selected.emit)
                        port_item.port_double_clicked.connect(self.port_double_clicked.emit)
                        port_item.port_context_menu_requested.connect(self.port_context_menu_requested.emit)
                    except Exception as e:
                        print(f"⚠️ Signal connection failed: {e}")
                    
                    self.enhanced_port_items.append(port_item)
                else:
                    # Use basic port graphics as fallback
                    port_item = self._create_basic_port_item(port, x, y)
                
                self.port_items.append(port_item)
                
        except Exception as e:
            print(f"❌ Port positioning failed: {e}")
            self.logger.error(f"Port positioning failed: {e}")
    
    def _create_basic_port_item(self, port: Port, x: float, y: float):
        """Create basic port item as fallback"""
        try:
            port_size = UIConstants.COMPONENT_PORT_SIZE
            port_item = QGraphicsEllipseItem(-port_size/2, -port_size/2, port_size, port_size, self)
            port_item.setPos(x, y)
            
            # Set color based on port type
            if port.is_provided:
                color = QColor(*AppConstants.PORT_COLORS['PROVIDED'])
            else:
                color = QColor(*AppConstants.PORT_COLORS['REQUIRED'])
            
            port_item.setBrush(QBrush(color))
            port_item.setPen(QPen(color.darker(150), 1))
            port_item.setZValue(10)
            
            # Add port reference for later use
            port_item.port = port
            
            # Basic tooltip
            port_item.setToolTip(f"{port.short_name} ({port.port_type.value})")
            
            return port_item
            
        except Exception as e:
            self.logger.error(f"Basic port creation failed: {e}")
            return None
    
    def _generate_enhanced_tooltip(self) -> str:
        """Generate enhanced tooltip with connection information"""
        try:
            tooltip = f"<b>{self.component.short_name}</b><br>"
            tooltip += f"Type: {self.component.component_type.value}<br>"
            tooltip += f"Package: {self.component.package_path or 'Unknown'}<br>"
            tooltip += f"Ports: {self.component.port_count}<br>"
            
            # Day 5 - Add connection information
            if self.connected_ports:
                total_connections = sum(len(conns) for conns in self.connected_ports.values())
                tooltip += f"Connections: {total_connections}<br>"
            
            # Day 5 - Add composition information
            if self.component.is_composition:
                tooltip += f"<br><b>📦 Composition Component</b><br>"
                tooltip += f"Sub-components: {len(self.component.components)}<br>"
                tooltip += f"Internal connections: {len(self.component.connections)}<br>"
                tooltip += f"<i>Double-click to drill down</i><br>"
            
            # Add interface information
            if self.component.all_ports:
                interfaces = set()
                for port in self.component.all_ports:
                    if hasattr(port, 'interface_ref') and port.interface_ref:
                        interfaces.add(port.interface_ref)
                
                if interfaces:
                    tooltip += f"Interfaces: {len(interfaces)}<br>"
                    if len(interfaces) <= 3:
                        tooltip += f"  • {', '.join(interfaces)}<br>"
            
            tooltip += f"UUID: {self.component.uuid}<br>"
            
            if self.component.desc:
                desc = self.component.desc
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                tooltip += f"Description: {desc}<br>"
            
            # Add search info if this is a search result
            if self.is_search_result:
                tooltip += f"<br><i>Search relevance: {self.search_relevance_score:.2f}</i>"
            
            return tooltip
            
        except Exception as e:
            print(f"❌ Enhanced tooltip generation failed: {e}")
            return f"Component: {self.component.short_name}"
    
    # Day 5 - Enhanced interaction methods
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click for composition drill-down"""
        try:
            if self.component.is_composition and event.button() == Qt.LeftButton:
                print(f"🔧 Composition drill-down requested: {self.component.short_name}")
                self.composition_drill_requested.emit(self.component)
            else:
                super().mouseDoubleClickEvent(event)
        except Exception as e:
            self.logger.error(f"Double-click handling failed: {e}")
    
    def contextMenuEvent(self, event):
        """Enhanced context menu with Day 5 features"""
        try:
            menu = QMenu()
            
            # Component info
            info_action = QAction(f"📋 {self.component.short_name} Details", None)
            info_action.triggered.connect(self._show_component_details)
            menu.addAction(info_action)
            
            menu.addSeparator()
            
            # Day 5 - Connection actions
            if self.connected_ports:
                highlight_connections_action = QAction("🔗 Highlight Connections", None)
                highlight_connections_action.triggered.connect(self._highlight_connections)
                menu.addAction(highlight_connections_action)
                
                show_connections_action = QAction("📋 Show Connection Details", None)
                show_connections_action.triggered.connect(self._show_connection_details)
                menu.addAction(show_connections_action)
                
                menu.addSeparator()
            
            # Day 5 - Composition actions
            if self.component.is_composition:
                drill_down_action = QAction("📦 Drill Down into Composition", None)
                drill_down_action.triggered.connect(lambda: self.composition_drill_requested.emit(self.component))
                menu.addAction(drill_down_action)
                
                menu.addSeparator()
            
            # Standard actions
            copy_name_action = QAction("📋 Copy Name", None)
            copy_name_action.triggered.connect(lambda: self._copy_to_clipboard(self.component.short_name))
            menu.addAction(copy_name_action)
            
            copy_uuid_action = QAction("🔑 Copy UUID", None)
            copy_uuid_action.triggered.connect(lambda: self._copy_to_clipboard(self.component.uuid))
            menu.addAction(copy_uuid_action)
            
            menu.exec_(event.screenPos())
            
        except Exception as e:
            self.logger.error(f"Context menu failed: {e}")
    
    def _show_component_details(self):
        """Show detailed component information"""
        try:
            details = f"Component: {self.component.short_name}\n"
            details += f"Type: {self.component.component_type.value}\n"
            details += f"Package: {self.component.package_path}\n"
            details += f"Ports: {self.component.port_count}\n"
            details += f"UUID: {self.component.uuid}\n"
            
            if self.component.is_composition:
                details += f"\nComposition Details:\n"
                details += f"Sub-components: {len(self.component.components)}\n"
                details += f"Internal connections: {len(self.component.connections)}\n"
            
            if self.connected_ports:
                total_connections = sum(len(conns) for conns in self.connected_ports.values())
                details += f"\nConnections: {total_connections}\n"
            
            if self.component.desc:
                details += f"\nDescription:\n{self.component.desc}\n"
            
            QMessageBox.information(None, "Component Details", details)
            
        except Exception as e:
            self.logger.error(f"Show component details failed: {e}")
    
    def _highlight_connections(self):
        """Highlight all connections for this component"""
        try:
            if self.scene():
                # This will be handled by the scene's connection manager
                scene = self.scene()
                if hasattr(scene, 'connection_manager'):
                    scene.connection_manager.highlight_connections_for_component(
                        self.component.uuid, True
                    )
                print(f"🔗 Highlighted connections for {self.component.short_name}")
        except Exception as e:
            self.logger.error(f"Highlight connections failed: {e}")
    
    def _show_connection_details(self):
        """Show detailed connection information"""
        try:
            if not self.connected_ports:
                QMessageBox.information(None, "Connection Details", 
                                      f"No connections found for {self.component.short_name}")
                return
            
            details = f"Connections for {self.component.short_name}:\n\n"
            
            for port_uuid, connection_uuids in self.connected_ports.items():
                port_name = "Unknown Port"
                for port in self.component.all_ports:
                    if port.uuid == port_uuid:
                        port_name = port.short_name
                        break
                
                details += f"Port '{port_name}':\n"
                details += f"  Connections: {len(connection_uuids)}\n"
                for conn_uuid in connection_uuids[:3]:  # Show first 3
                    details += f"    • {conn_uuid[:8]}...\n"
                if len(connection_uuids) > 3:
                    details += f"    • ... and {len(connection_uuids) - 3} more\n"
                details += "\n"
            
            QMessageBox.information(None, "Connection Details", details)
            
        except Exception as e:
            self.logger.error(f"Show connection details failed: {e}")
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        try:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
        except Exception as e:
            self.logger.error(f"Copy to clipboard failed: {e}")
    
    # Day 5 - Connection management methods
    
    def add_connection(self, port_uuid: str, connection_uuid: str):
        """Add connection reference to port"""
        try:
            if port_uuid not in self.connected_ports:
                self.connected_ports[port_uuid] = []
            
            if connection_uuid not in self.connected_ports[port_uuid]:
                self.connected_ports[port_uuid].append(connection_uuid)
                
            # Update tooltip
            self.setToolTip(self._generate_enhanced_tooltip())
            
        except Exception as e:
            self.logger.error(f"Add connection failed: {e}")
    
    def remove_connection(self, port_uuid: str, connection_uuid: str):
        """Remove connection reference from port"""
        try:
            if port_uuid in self.connected_ports:
                if connection_uuid in self.connected_ports[port_uuid]:
                    self.connected_ports[port_uuid].remove(connection_uuid)
                
                # Clean up empty port entries
                if not self.connected_ports[port_uuid]:
                    del self.connected_ports[port_uuid]
                
                # Update tooltip
                self.setToolTip(self._generate_enhanced_tooltip())
                
        except Exception as e:
            self.logger.error(f"Remove connection failed: {e}")
    
    def highlight_for_connection(self, highlight: bool):
        """Highlight component for connection visualization"""
        try:
            self.is_connection_highlighted = highlight
            self._setup_appearance()
        except Exception as e:
            self.logger.error(f"Connection highlighting failed: {e}")
    
    def get_port_items(self) -> List:
        """Get all port graphics items"""
        return self.enhanced_port_items if self.enhanced_port_items else self.port_items
    
    def get_port_by_uuid(self, port_uuid: str):
        """Get port graphics item by UUID"""
        try:
            for port_item in self.get_port_items():
                if hasattr(port_item, 'port') and port_item.port.uuid == port_uuid:
                    return port_item
            return None
        except Exception as e:
            self.logger.error(f"Get port by UUID failed: {e}")
            return None
    
    def itemChange(self, change, value):
        """Handle item changes - update connections when moved"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Notify scene to update connections
            if self.scene() and hasattr(self.scene(), 'update_connections_for_component'):
                self.scene().update_connections_for_component(self.component.uuid)
        
        return super().itemChange(change, value)

class ComponentDiagramScene(QGraphicsScene):
    """
    Enhanced Graphics Scene with Day 5 connection visualization and drill-down
    Complete implementation with connection rendering and navigation
    """
    
    # Enhanced signals for Day 5
    component_selected = pyqtSignal(object)  # Component object
    component_double_clicked = pyqtSignal(object)  # Component object
    port_selected = pyqtSignal(object)  # Port object
    port_double_clicked = pyqtSignal(object)  # Port object
    composition_drill_requested = pyqtSignal(object)  # Component object
    connection_selected = pyqtSignal(object)  # Connection object
    connection_double_clicked = pyqtSignal(object)  # Connection object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        
        # Scene state with enhanced components and connections
        self.components: Dict[str, ComponentGraphicsItem] = {}
        self.connections: List = []  # Will contain ConnectionGraphicsItem objects
        
        # Day 5 - Connection management
        if CONNECTION_GRAPHICS_AVAILABLE:
            self.connection_manager = ConnectionManager(self)
            print("✅ Connection manager initialized")
        else:
            self.connection_manager = None
            print("⚠️ Connection manager not available")
        
        # Day 5 - Enhanced state management
        self.current_selection: Optional[ComponentGraphicsItem] = None
        self.current_port_selection = None
        self.current_connection_selection = None
        self.search_results: Set[str] = set()
        self.highlighted_components: Set[str] = set()
        
        # Day 5 - Navigation and drill-down state
        self.navigation_history: List[Dict[str, Any]] = []
        self.current_composition: Optional[Component] = None
        self.breadcrumb_path: List[str] = []
        
        # Layout parameters
        self.grid_size = 20
        self.component_spacing = 180  # Increased for better connection visibility
        
        # Navigation integration
        self.navigation_controller = None
        self.auto_highlight_enabled = True
        
        # Set scene properties
        self.setSceneRect(0, 0, 2000, 1500)
        self.setBackgroundBrush(QBrush(QColor(245, 245, 245)))
        
        # Connect selection changes
        self.selectionChanged.connect(self._on_selection_changed)
        
        # Day 5 - Auto-update timer for connections
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._update_all_connections)
    
    def set_navigation_controller(self, navigation_controller):
        """Set navigation controller for integration"""
        self.navigation_controller = navigation_controller
        self.logger.debug("Navigation controller connected to graphics scene")
    
    def load_packages(self, packages: List[Package], connections: List[Connection] = None):
        """Load and visualize packages with Day 5 connection support"""
        print(f"🔧 Enhanced graphics scene loading {len(packages)} packages")
        
        # Clear existing content
        self.clear_scene()
        
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
        
        # Create component graphics with enhanced features
        self._create_component_graphics(all_components)
        
        # Day 5 - Load and render connections
        if connections:
            print(f"🔗 Loading {len(connections)} connections")
            self._load_connections(connections)
        else:
            print("⚠️ No connections provided")
        
        # Apply intelligent layout
        self._apply_intelligent_layout(all_components, connections or [])
        
        # Update scene rect with extra space for connections
        self._update_scene_rect()
        
        print(f"✅ Enhanced visualization complete: {len(all_components)} components, "
              f"{len(connections or [])} connections")
        
        self.logger.info(f"Enhanced visualization complete: {len(all_components)} components with connections")
    
    def _create_component_graphics(self, components: List[Component]):
        """Create enhanced component graphics with Day 5 features"""
        try:
            for component in components:
                try:
                    print(f"Creating enhanced component graphics: {component.short_name}")
                    
                    # Create enhanced ComponentGraphicsItem
                    comp_item = ComponentGraphicsItem(component)
                    
                    # Connect enhanced signals
                    comp_item.port_selected.connect(self._on_port_selected)
                    comp_item.port_double_clicked.connect(self._on_port_double_clicked)
                    comp_item.composition_drill_requested.connect(self._on_composition_drill_requested)
                    
                    # Add to scene
                    self.addItem(comp_item)
                    
                    # Store reference
                    self.components[component.uuid] = comp_item
                    
                    port_count = len(comp_item.get_port_items())
                    print(f"✅ Created enhanced component graphics: {component.short_name} "
                          f"with {port_count} ports")
                    
                except Exception as e:
                    print(f"❌ Failed to create enhanced component {component.short_name}: {e}")
                    continue
            
            print(f"✅ Created {len(self.components)} enhanced component graphics")
            
        except Exception as e:
            print(f"❌ Component graphics creation failed: {e}")
            self.logger.error(f"Component graphics creation failed: {e}")
    
    def _load_connections(self, connections: List[Connection]):
        """Load and render connections with Day 5 visualization"""
        try:
            if not self.connection_manager:
                print("⚠️ Connection manager not available - skipping connection rendering")
                return
            
            connections_created = 0
            connections_failed = 0
            
            for connection in connections:
                try:
                    # Find start and end port items
                    start_port_item = self._find_port_item(
                        connection.provider_endpoint.component_uuid,
                        connection.provider_endpoint.port_uuid
                    )
                    
                    end_port_item = self._find_port_item(
                        connection.requester_endpoint.component_uuid,
                        connection.requester_endpoint.port_uuid
                    )
                    
                    if start_port_item and end_port_item:
                        # Create connection graphics
                        connection_item = self.connection_manager.add_connection(
                            connection, start_port_item, end_port_item
                        )
                        
                        if connection_item:
                            # Connect signals
                            # connection_item.connection_selected.connect(self.connection_selected.emit)
                            # connection_item.connection_double_clicked.connect(self.connection_double_clicked.emit)
                            
                            # Update component connection tracking
                            self._update_component_connections(connection)
                            
                            connections_created += 1
                        else:
                            connections_failed += 1
                    else:
                        print(f"⚠️ Could not find port items for connection: {connection.short_name}")
                        connections_failed += 1
                        
                except Exception as e:
                    print(f"❌ Failed to create connection {connection.short_name}: {e}")
                    connections_failed += 1
                    continue
            
            print(f"🔗 Connection loading complete: {connections_created} created, {connections_failed} failed")
            
        except Exception as e:
            print(f"❌ Connection loading failed: {e}")
            self.logger.error(f"Connection loading failed: {e}")
    
    def _find_port_item(self, component_uuid: str, port_uuid: str):
        """Find port graphics item by component and port UUID"""
        try:
            if component_uuid in self.components:
                comp_item = self.components[component_uuid]
                return comp_item.get_port_by_uuid(port_uuid)
            return None
        except Exception as e:
            self.logger.error(f"Find port item failed: {e}")
            return None
    
    def _update_component_connections(self, connection: Connection):
        """Update component connection tracking"""
        try:
            # Update provider component
            provider_comp_uuid = connection.provider_endpoint.component_uuid
            provider_port_uuid = connection.provider_endpoint.port_uuid
            
            if provider_comp_uuid in self.components:
                comp_item = self.components[provider_comp_uuid]
                comp_item.add_connection(provider_port_uuid, connection.uuid)
            
            # Update requester component
            requester_comp_uuid = connection.requester_endpoint.component_uuid
            requester_port_uuid = connection.requester_endpoint.port_uuid
            
            if requester_comp_uuid in self.components:
                comp_item = self.components[requester_comp_uuid]
                comp_item.add_connection(requester_port_uuid, connection.uuid)
                
        except Exception as e:
            self.logger.error(f"Update component connections failed: {e}")
    
    def _apply_intelligent_layout(self, components: List[Component], connections: List[Connection]):
        """Apply intelligent layout considering connections"""
        try:
            # Use layout algorithms from utils
            from ...utils.layout_algorithms import LayoutEngine, LayoutType, detect_best_layout
            
            # Detect best layout type
            layout_type = detect_best_layout(components, connections)
            print(f"🔧 Applying {layout_type.value} layout")
            
            # Create layout engine
            layout_engine = LayoutEngine()
            
            # Apply layout
            positions = layout_engine.apply_layout(components, connections, layout_type)
            
            # Position components
            positioned_count = 0
            for component in components:
                if component.uuid in positions and component.uuid in self.components:
                    pos = positions[component.uuid]
                    comp_item = self.components[component.uuid]
                    comp_item.setPos(pos.x, pos.y)
                    positioned_count += 1
            
            print(f"✅ Positioned {positioned_count} components using {layout_type.value} layout")
            
        except Exception as e:
            print(f"⚠️ Intelligent layout failed, using fallback: {e}")
            self._apply_fallback_layout(components)
    
    def _apply_fallback_layout(self, components: List[Component]):
        """Apply simple fallback layout"""
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
            
            print(f"✅ Applied fallback grid layout")
            
        except Exception as e:
            print(f"❌ Fallback layout failed: {e}")
    
    def _update_scene_rect(self):
        """Update scene rectangle to fit all content with margins"""
        try:
            if self.components:
                items_rect = self.itemsBoundingRect()
                
                # Add margins for connections and navigation
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
    
    # Day 5 - Enhanced event handlers
    
    def _on_port_selected(self, port):
        """Handle port selection with connection highlighting"""
        try:
            print(f"🔧 Port selected: {port.short_name}")
            
            # Clear previous port selection
            if self.current_port_selection:
                if hasattr(self.current_port_selection, 'clear_highlight'):
                    self.current_port_selection.clear_highlight()
            
            # Find and highlight port graphics item
            for comp_item in self.components.values():
                for port_item in comp_item.get_port_items():
                    if hasattr(port_item, 'port') and port_item.port.uuid == port.uuid:
                        self.current_port_selection = port_item
                        if hasattr(port_item, 'highlight_port'):
                            port_item.highlight_port("selection")
                        break
            
            # Highlight related connections
            if self.connection_manager:
                self._highlight_port_connections(port.uuid)
            
            # Emit signal
            self.port_selected.emit(port)
            
        except Exception as e:
            print(f"❌ Port selection handling failed: {e}")
    
    def _on_port_double_clicked(self, port):
        """Handle port double-click with enhanced actions"""
        try:
            print(f"🔧 Port double-clicked: {port.short_name}")
            
            # Show port details or start connection preview
            if hasattr(self.current_port_selection, 'show_port_details'):
                self.current_port_selection.show_port_details()
            
            self.port_double_clicked.emit(port)
            
        except Exception as e:
            print(f"❌ Port double-click handling failed: {e}")
    
    def _on_composition_drill_requested(self, component):
        """Handle composition drill-down request"""
        try:
            print(f"📦 Composition drill-down requested: {component.short_name}")
            
            # Save current state to navigation history
            current_state = {
                'components': list(self.components.keys()),
                'connections': [item.connection.uuid for item in self.connection_manager.connection_items] if self.connection_manager else [],
                'scene_rect': self.sceneRect(),
                'composition_name': component.short_name
            }
            self.navigation_history.append(current_state)
            
            # Set current composition
            self.current_composition = component
            self.breadcrumb_path.append(component.short_name)
            
            # Load composition internal structure
            self._load_composition_internals(component)
            
            # Emit signal for UI updates
            self.composition_drill_requested.emit(component)
            
        except Exception as e:
            print(f"❌ Composition drill-down failed: {e}")
            self.logger.error(f"Composition drill-down failed: {e}")
    
    def _load_composition_internals(self, composition: Component):
        """Load composition internal structure"""
        try:
            print(f"📦 Loading internals for composition: {composition.short_name}")
            
            # Clear current scene
            self.clear_scene()
            
            # Load sub-components
            if composition.components:
                print(f"Loading {len(composition.components)} sub-components")
                self._create_component_graphics(composition.components)
                
                # Load internal connections
                internal_connections = []
                # Here you would get internal connections from the composition
                # For now, we'll use the connections already stored in the component
                if hasattr(composition, 'internal_connections'):
                    internal_connections = composition.internal_connections
                
                if internal_connections:
                    self._load_connections(internal_connections)
                
                # Apply layout for internal structure
                self._apply_intelligent_layout(composition.components, internal_connections)
                
                # Update scene rect
                self._update_scene_rect()
                
                print(f"✅ Loaded composition internals: {len(composition.components)} components")
            else:
                print("⚠️ Composition has no sub-components")
                
        except Exception as e:
            print(f"❌ Loading composition internals failed: {e}")
            self.logger.error(f"Loading composition internals failed: {e}")
    
    def navigate_back(self) -> bool:
        """Navigate back from composition drill-down"""
        try:
            if not self.navigation_history:
                print("⚠️ No navigation history available")
                return False
            
            # Get previous state
            previous_state = self.navigation_history.pop()
            
            # Update breadcrumb path
            if self.breadcrumb_path:
                self.breadcrumb_path.pop()
            
            print(f"🔙 Navigating back to: {previous_state.get('composition_name', 'Root')}")
            
            # Restore previous state
            # This would require reloading the previous components and connections
            # For now, we'll emit a signal to let the main application handle it
            
            # Clear current composition
            self.current_composition = None
            
            return True
            
        except Exception as e:
            print(f"❌ Navigate back failed: {e}")
            self.logger.error(f"Navigate back failed: {e}")
            return False
    
    def can_navigate_back(self) -> bool:
        """Check if back navigation is possible"""
        return len(self.navigation_history) > 0
    
    def get_breadcrumb_path(self) -> List[str]:
        """Get current breadcrumb path"""
        return self.breadcrumb_path.copy()
    
    def _highlight_port_connections(self, port_uuid: str):
        """Highlight connections related to a specific port"""
        try:
            if self.connection_manager:
                connections = self.connection_manager.get_connections_for_port(port_uuid)
                
                # Clear previous highlights
                for connection_item in self.connection_manager.connection_items:
                    connection_item.set_highlighted(False)
                
                # Highlight related connections
                for connection_item in connections:
                    connection_item.set_highlighted(True)
                
                print(f"🔗 Highlighted {len(connections)} connections for port")
                
        except Exception as e:
            self.logger.error(f"Highlight port connections failed: {e}")
    
    def _on_selection_changed(self):
        """Handle selection changes"""
        try:
            selected_items = self.selectedItems()
            if selected_items:
                item = selected_items[0]
                if isinstance(item, ComponentGraphicsItem):
                    self.current_selection = item
                    self.component_selected.emit(item.component)
                    
                    # Highlight component connections
                    if self.connection_manager:
                        self.connection_manager.highlight_connections_for_component(
                            item.component.uuid, True
                        )
        except Exception as e:
            print(f"❌ Selection handling failed: {e}")
    
    # Day 5 - Connection management methods
    
    def update_connections_for_component(self, component_uuid: str):
        """Update connections when component is moved"""
        try:
            if self.connection_manager:
                # Get connections for this component
                connections = self.connection_manager.get_connections_for_component(component_uuid)
                
                # Update each connection
                for connection_item in connections:
                    connection_item.update_connection()
                
        except Exception as e:
            self.logger.error(f"Update connections for component failed: {e}")
    
    def _update_all_connections(self):
        """Update all connections (called by timer)"""
        try:
            if self.connection_manager:
                self.connection_manager.update_all_connections()
        except Exception as e:
            self.logger.error(f"Update all connections failed: {e}")
    
    def highlight_component(self, component_uuid: str):
        """Highlight component by UUID"""
        try:
            if component_uuid in self.components:
                comp_item = self.components[component_uuid]
                comp_item.highlight("focus")
                
                # Also highlight its connections
                if self.connection_manager:
                    self.connection_manager.highlight_connections_for_component(component_uuid, True)
        except Exception as e:
            self.logger.error(f"Component highlighting failed: {e}")
    
    def clear_all_highlights(self):
        """Clear all highlights in the scene"""
        try:
            # Clear component highlights
            for comp_item in self.components.values():
                comp_item.clear_highlight()
                comp_item.highlight_for_connection(False)
            
            # Clear connection highlights
            if self.connection_manager:
                for connection_item in self.connection_manager.connection_items:
                    connection_item.set_highlighted(False)
            
            # Clear port highlights
            for comp_item in self.components.values():
                for port_item in comp_item.get_port_items():
                    if hasattr(port_item, 'clear_highlight'):
                        port_item.clear_highlight()
                        
        except Exception as e:
            self.logger.error(f"Clear highlights failed: {e}")
    
    def fit_components_in_view(self):
        """Fit all components in view"""
        try:
            if self.components:
                items_rect = self.itemsBoundingRect()
                self.setSceneRect(items_rect)
        except Exception as e:
            self.logger.error(f"Fit components failed: {e}")
    
    def clear_scene(self):
        """Clear the scene safely"""
        try:
            # Clear connection manager
            if self.connection_manager:
                self.connection_manager.clear_all_connections()
            
            # Clear components
            self.components.clear()
            self.connections.clear()
            
            # Clear selection state
            self.current_selection = None
            self.current_port_selection = None
            self.current_connection_selection = None
            
            # Clear scene items
            self.clear()
            
        except Exception as e:
            self.logger.error(f"Scene clearing failed: {e}")
    
    # Day 5 - Export and utilities
    
    def export_scene_image(self, file_path: str, width: int = 1920, height: int = 1080):
        """Export scene as image"""
        try:
            from PyQt5.QtGui import QPixmap, QPainter
            from PyQt5.QtCore import QRectF
            
            # Create pixmap
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.white)
            
            # Create painter
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Render scene
            source_rect = self.itemsBoundingRect()
            target_rect = QRectF(0, 0, width, height)
            self.render(painter, target_rect, source_rect)
            
            # Save image
            pixmap.save(file_path)
            painter.end()
            
            print(f"✅ Scene exported to: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Scene export failed: {e}")
            self.logger.error(f"Scene export failed: {e}")
            return False
    
    def get_scene_statistics(self) -> Dict[str, Any]:
        """Get scene statistics"""
        try:
            connection_stats = {}
            if self.connection_manager:
                connection_stats = self.connection_manager.get_connection_statistics()
            
            return {
                'components': len(self.components),
                'connections': connection_stats.get('total_connections', 0),
                'scene_rect': {
                    'width': self.sceneRect().width(),
                    'height': self.sceneRect().height()
                },
                'navigation': {
                    'history_depth': len(self.navigation_history),
                    'current_composition': self.current_composition.short_name if self.current_composition else None,
                    'breadcrumb_path': self.breadcrumb_path
                },
                'connection_details': connection_stats
            }
        except Exception as e:
            self.logger.error(f"Get scene statistics failed: {e}")
            return {}
    
    # Day 5 - Advanced features
    
    def find_shortest_path(self, start_component_uuid: str, end_component_uuid: str) -> List[str]:
        """Find shortest connection path between two components"""
        try:
            if not self.connection_manager:
                return []
            
            # Build connection graph
            graph = {}
            for connection_item in self.connection_manager.connection_items:
                connection = connection_item.connection
                provider_uuid = connection.provider_endpoint.component_uuid
                requester_uuid = connection.requester_endpoint.component_uuid
                
                if provider_uuid not in graph:
                    graph[provider_uuid] = []
                if requester_uuid not in graph:
                    graph[requester_uuid] = []
                
                graph[provider_uuid].append(requester_uuid)
                graph[requester_uuid].append(provider_uuid)  # Bidirectional
            
            # Simple BFS to find shortest path
            from collections import deque
            
            if start_component_uuid not in graph or end_component_uuid not in graph:
                return []
            
            queue = deque([(start_component_uuid, [start_component_uuid])])
            visited = {start_component_uuid}
            
            while queue:
                current, path = queue.popleft()
                
                if current == end_component_uuid:
                    return path
                
                for neighbor in graph.get(current, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
            
            return []  # No path found
            
        except Exception as e:
            self.logger.error(f"Find shortest path failed: {e}")
            return []
    
    def highlight_component_chain(self, component_uuids: List[str]):
        """Highlight a chain of components and their connections"""
        try:
            # Clear previous highlights
            self.clear_all_highlights()
            
            # Highlight components
            for comp_uuid in component_uuids:
                if comp_uuid in self.components:
                    self.components[comp_uuid].highlight_for_connection(True)
            
            # Highlight connections between adjacent components
            if self.connection_manager:
                for i in range(len(component_uuids) - 1):
                    comp1_uuid = component_uuids[i]
                    comp2_uuid = component_uuids[i + 1]
                    
                    # Find connections between these components
                    for connection_item in self.connection_manager.connection_items:
                        connection = connection_item.connection
                        provider_uuid = connection.provider_endpoint.component_uuid
                        requester_uuid = connection.requester_endpoint.component_uuid
                        
                        if ((provider_uuid == comp1_uuid and requester_uuid == comp2_uuid) or
                            (provider_uuid == comp2_uuid and requester_uuid == comp1_uuid)):
                            connection_item.set_highlighted(True)
            
            print(f"🔗 Highlighted component chain with {len(component_uuids)} components")
            
        except Exception as e:
            self.logger.error(f"Highlight component chain failed: {e}")
    
    def auto_arrange_layout(self):
        """Auto-arrange components using intelligent layout"""
        try:
            if not self.components:
                return
            
            # Get all components
            components = [comp_item.component for comp_item in self.components.values()]
            
            # Get all connections
            connections = []
            if self.connection_manager:
                connections = [item.connection for item in self.connection_manager.connection_items]
            
            # Apply intelligent layout
            self._apply_intelligent_layout(components, connections)
            
            # Update all connections
            if self.connection_manager:
                self.connection_manager.update_all_connections()
            
            print("✅ Auto-arrangement completed")
            
        except Exception as e:
            print(f"❌ Auto-arrangement failed: {e}")
            self.logger.error(f"Auto-arrangement failed: {e}")