# src/arxml_viewer/gui/graphics/graphics_scene.py (UPDATED for Day 4)
"""
Graphics Scene - Enhanced for Day 4 with Advanced Port Interactions
Integrates enhanced port graphics, connection preview, and interface display
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
from ...models.port import Port
from ...utils.constants import AppConstants, UIConstants
from ...utils.logger import get_logger

# Import Day 4 enhancements
from .port_graphics import PortGraphicsItem
from .connection_preview import ConnectionPreviewManager

class ComponentGraphicsItem(QGraphicsRectItem):
    """Enhanced component graphics item with Day 4 port integration"""
    
    # Day 4 - Enhanced signals
    port_selected = pyqtSignal(object)  # Port object
    port_double_clicked = pyqtSignal(object)  # Port object
    port_context_menu_requested = pyqtSignal(object, object)  # Port, QPoint
    
    def __init__(self, component: Component, parent=None):
        super().__init__(parent)
        
        self.component = component
        self.logger = get_logger(__name__)
        
        # Enhanced state tracking
        self.is_highlighted = False
        self.is_search_result = False
        self.search_relevance_score = 0.0
        self.original_opacity = 0.8
        
        # Day 4 - Port items with enhanced graphics
        self.port_items: List[PortGraphicsItem] = []
        
        # Set up component rectangle
        self.setRect(0, 0, UIConstants.COMPONENT_MIN_WIDTH, UIConstants.COMPONENT_MIN_HEIGHT)
        
        # Set colors based on component type
        self._setup_appearance()
        
        # Add component label
        self._create_label()
        
        # Day 4 - Create enhanced ports
        self._create_enhanced_ports()
        
        # Make item selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        # Set tooltip
        self.setToolTip(self._generate_enhanced_tooltip())
        
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
    
    def _create_enhanced_ports(self):
        """Create enhanced port representations with Day 4 features"""
        try:
            self.port_items.clear()
            
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
        """Position ports on specified side of component"""
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
                port_item = PortGraphicsItem(port, self)
                port_item.setPos(x, y)
                
                # Connect port signals to component signals
                if hasattr(port_item, 'port_selected'):
                    port_item.port_selected.connect(self.port_selected.emit)
                
                self.port_items.append(port_item)
                
        except Exception as e:
            print(f"❌ Port positioning failed: {e}")
            self.logger.error(f"Port positioning failed: {e}")
    
    def _generate_enhanced_tooltip(self) -> str:
        """Generate enhanced tooltip with interface information"""
        try:
            tooltip = f"<b>{self.component.short_name}</b><br>"
            tooltip += f"Type: {self.component.component_type.value}<br>"
            tooltip += f"Package: {self.component.package_path or 'Unknown'}<br>"
            tooltip += f"Ports: {self.component.port_count}<br>"
            
            # Day 4 - Add interface information
            if self.component.all_ports:
                interfaces = set()
                for port in self.component.all_ports:
                    if port.interface_ref:
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
    
    def highlight(self, highlight_type: str = "selection"):
        """Highlight component with different styles"""
        try:
            self.is_highlighted = True
            
            if highlight_type == "selection":
                self.setPen(QPen(QColor(255, 255, 0), 3))
                self.setOpacity(1.0)
            elif highlight_type == "search":
                self.setPen(QPen(QColor(100, 149, 237), 3))
                self.setOpacity(1.0)
                self.is_search_result = True
            elif highlight_type == "focus":
                self.setPen(QPen(QColor(255, 165, 0), 4))
                self.setOpacity(1.0)
            elif highlight_type == "navigation":
                self.setPen(QPen(QColor(0, 255, 0), 3))
                self.setOpacity(1.0)
        except Exception as e:
            self.logger.error(f"Component highlighting failed: {e}")
    
    def clear_highlight(self):
        """Clear all highlighting"""
        try:
            self.is_highlighted = False
            self.is_search_result = False
            
            # Restore original appearance
            self._setup_appearance()
        except Exception as e:
            self.logger.error(f"Clear highlight failed: {e}")
    
    def get_port_items(self) -> List[PortGraphicsItem]:
        """Get all port graphics items - Day 4 Addition"""
        return self.port_items.copy()
    
    def get_port_by_uuid(self, port_uuid: str) -> Optional[PortGraphicsItem]:
        """Get port graphics item by UUID - Day 4 Addition"""
        try:
            for port_item in self.port_items:
                if port_item.port.uuid == port_uuid:
                    return port_item
            return None
        except Exception as e:
            self.logger.error(f"Get port by UUID failed: {e}")
            return None

class ComponentDiagramScene(QGraphicsScene):
    """
    Enhanced Graphics Scene with Day 4 port interaction and connection preview
    """
    
    # Enhanced signals for Day 4
    component_selected = pyqtSignal(object)  # Component object
    component_double_clicked = pyqtSignal(object)  # Component object
    port_selected = pyqtSignal(object)  # Port object - NEW
    port_double_clicked = pyqtSignal(object)  # Port object - NEW
    connection_preview_requested = pyqtSignal(object, object)  # source_port, target_port - NEW
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        
        # Scene state with enhanced components
        self.components: Dict[str, ComponentGraphicsItem] = {}
        self.connections: List[QGraphicsLineItem] = []
        
        # Day 4 - Enhanced state management
        self.current_selection: Optional[ComponentGraphicsItem] = None
        self.current_port_selection: Optional[PortGraphicsItem] = None
        self.search_results: Set[str] = set()
        self.highlighted_components: Set[str] = set()
        
        # Day 4 - Connection preview manager
        self.connection_preview_manager = ConnectionPreviewManager(self)
        self._setup_connection_preview()
        
        # Layout parameters
        self.grid_size = 20
        self.component_spacing = 150
        
        # Navigation integration
        self.navigation_controller = None
        self.auto_highlight_enabled = True
        
        # Set scene properties
        self.setSceneRect(0, 0, 2000, 1500)
        self.setBackgroundBrush(QBrush(QColor(245, 245, 245)))
        
        # Connect selection changes
        self.selectionChanged.connect(self._on_selection_changed)
    
    def _setup_connection_preview(self):
        """Setup connection preview system - Day 4"""
        try:
            # Connect preview manager signals
            self.connection_preview_manager.connection_preview_started.connect(
                self._on_connection_preview_started
            )
            self.connection_preview_manager.connection_preview_ended.connect(
                self._on_connection_preview_ended
            )
            self.connection_preview_manager.compatibility_checked.connect(
                self._on_compatibility_checked
            )
            
            print("✅ Connection preview system setup complete")
            
        except Exception as e:
            print(f"❌ Connection preview setup failed: {e}")
            self.logger.error(f"Connection preview setup failed: {e}")
    
    def set_navigation_controller(self, navigation_controller):
        """Set navigation controller for integration"""
        self.navigation_controller = navigation_controller
        self.logger.debug("Navigation controller connected to graphics scene")
    
    def load_packages(self, packages: List[Package]):
        """Load and visualize packages with Day 4 enhancements"""
        print(f"🔧 Enhanced graphics scene loading {len(packages)} packages")
        
        # Clear existing content
        self.clear()
        self.components.clear()
        self.connections.clear()
        self.search_results.clear()
        self.highlighted_components.clear()
        self.current_selection = None
        self.current_port_selection = None
        
        # Clear connection preview
        if self.connection_preview_manager:
            self.connection_preview_manager.clear_preview()
        
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
        
        # Enhanced grid layout
        cols = max(1, math.ceil(math.sqrt(len(all_components))))
        spacing = 180  # Increased spacing for better port visibility
        
        for i, component in enumerate(all_components):
            try:
                row = i // cols
                col = i % cols
                
                x = col * spacing
                y = row * spacing
                
                print(f"Creating enhanced component {component.short_name} at ({x}, {y})")
                
                # Create enhanced ComponentGraphicsItem
                comp_item = ComponentGraphicsItem(component)
                comp_item.setPos(x, y)
                
                # Connect enhanced signals
                comp_item.port_selected.connect(self._on_port_selected)
                comp_item.port_double_clicked.connect(self._on_port_double_clicked)
                
                # Add to scene
                self.addItem(comp_item)
                
                # Store reference
                self.components[component.uuid] = comp_item
                
                print(f"✅ Created enhanced component graphics: {component.short_name} "
                      f"with {len(comp_item.port_items)} ports")
                
            except Exception as e:
                print(f"❌ Failed to create enhanced component {component.short_name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"✅ Created {len(self.components)} enhanced component graphics")
        
        # Set scene rect with extra space for ports
        scene_width = cols * spacing + 200
        scene_height = math.ceil(len(all_components) / cols) * spacing + 200
        self.setSceneRect(0, 0, scene_width, scene_height)
        
        print(f"✅ Enhanced scene rect set to {scene_width}x{scene_height}")
        
        self.logger.info(f"Enhanced visualization complete: {len(all_components)} components with ports")
    
    # Day 4 - Enhanced event handlers
    
    def _on_port_selected(self, port):
        """Handle port selection - Day 4"""
        try:
            print(f"🔧 Port selected: {port.short_name}")
            
            # Clear previous port selection
            if self.current_port_selection:
                self.current_port_selection.clear_highlight()
            
            # Find port graphics item
            for comp_item in self.components.values():
                for port_item in comp_item.port_items:
                    if port_item.port.uuid == port.uuid:
                        self.current_port_selection = port_item
                        port_item.highlight_port("selection")
                        
                        # Start connection preview
                        self.connection_preview_manager.start_connection_preview(port_item)
                        break
            
            # Emit signal
            self.port_selected.emit(port)
            
        except Exception as e:
            print(f"❌ Port selection handling failed: {e}")
    
    def _on_port_double_clicked(self, port):
        """Handle port double-click - Day 4"""
        try:
            print(f"🔧 Port double-clicked: {port.short_name}")
            self.port_double_clicked.emit(port)
            
        except Exception as e:
            print(f"❌ Port double-click handling failed: {e}")
    
    def _on_connection_preview_started(self, source_port, target_port):
        """Handle connection preview start - Day 4"""
        try:
            print(f"🔗 Connection preview started from {source_port.port.short_name}")
        except Exception as e:
            print(f"❌ Connection preview start handling failed: {e}")
    
    def _on_connection_preview_ended(self):
        """Handle connection preview end - Day 4"""
        try:
            print("🔗 Connection preview ended")
        except Exception as e:
            print(f"❌ Connection preview end handling failed: {e}")
    
    def _on_compatibility_checked(self, port1, port2, compatible, reason):
        """Handle compatibility check result - Day 4"""
        try:
            if compatible:
                print(f"✅ Ports compatible: {port1.short_name} ↔ {port2.short_name}")
            else:
                print(f"❌ Ports incompatible: {port1.short_name} ↔ {port2.short_name} ({reason})")
        except Exception as e:
            print(f"❌ Compatibility check handling failed: {e}")