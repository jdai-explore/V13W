# src/arxml_viewer/gui/graphics/graphics_scene_pyqt5.py
"""
Graphics Scene - PyQt5 Version for Component Visualization
Professional QGraphicsScene for AUTOSAR component visualization
"""

import math
from typing import Dict, List, Optional, Tuple
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, 
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import QColor, QPen, QBrush, QFont

from ...models.component import Component
from ...models.package import Package
from ...utils.constants import AppConstants, UIConstants
from ...utils.logger import get_logger

class ComponentGraphicsItem(QGraphicsRectItem):
    """Custom graphics item for component representation - PyQt5 version"""
    
    def __init__(self, component: Component, parent=None):
        super().__init__(parent)
        
        self.component = component
        self.logger = get_logger(__name__)
        
        # Set up component rectangle
        self.setRect(0, 0, UIConstants.COMPONENT_MIN_WIDTH, UIConstants.COMPONENT_MIN_HEIGHT)
        
        # Set colors based on component type
        self._setup_appearance()
        
        # Add component label
        self._create_label()
        
        # Add ports
        self._create_ports()
        
        # Make item selectable and movable (PyQt5 flags)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        # Set tooltip
        self.setToolTip(self._generate_tooltip())
    
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
        self.setOpacity(0.8)
    
    def _create_label(self):
        """Create component name label"""
        self.label = QGraphicsTextItem(self.component.short_name or "Unnamed", self)
        
        # Position label in center of component
        label_rect = self.label.boundingRect()
        comp_rect = self.rect()
        
        x = (comp_rect.width() - label_rect.width()) / 2
        y = (comp_rect.height() - label_rect.height()) / 2
        
        self.label.setPos(x, y)
        
        # Style the label (PyQt5 font weight)
        font = QFont("Arial", 9, QFont.Bold)
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
        
        if self.component.desc:
            tooltip += f"Description: {self.component.desc}<br>"
        
        return tooltip
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        super().mousePressEvent(event)
        # Emit selection signal (will be connected later)
        self.logger.debug(f"Component selected: {self.component.short_name}")

class PortGraphicsItem(QGraphicsEllipseItem):
    """Custom graphics item for port representation - PyQt5 version"""
    
    def __init__(self, port, parent=None):
        super().__init__(parent)
        
        self.port = port
        
        # Set port size
        size = UIConstants.COMPONENT_PORT_SIZE
        self.setRect(0, 0, size, size)
        
        # Set port color based on type
        self._setup_appearance()
        
        # Set tooltip
        self.setToolTip(self._generate_tooltip())
    
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
        
        if self.port.interface_ref:
            tooltip += f"Interface: {self.port.interface_ref}<br>"
        
        if self.port.desc:
            tooltip += f"Description: {self.port.desc}<br>"
        
        return tooltip

class ComponentDiagramScene(QGraphicsScene):
    """Custom graphics scene for component diagram visualization - PyQt5 version"""
    
    # Signals
    component_selected = pyqtSignal(object)  # Component object
    component_double_clicked = pyqtSignal(object)  # Component object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        
        # Scene state
        self.components: Dict[str, ComponentGraphicsItem] = {}
        self.connections: List[QGraphicsLineItem] = []
        
        # Layout parameters
        self.grid_size = 20
        self.component_spacing = 150
        
        # Set scene properties
        self.setSceneRect(0, 0, 2000, 1500)  # Large scene for components
        self.setBackgroundBrush(QBrush(QColor(45, 45, 45)))  # Dark background
        
        # Connect selection changes
        self.selectionChanged.connect(self._on_selection_changed)
    
    def load_packages(self, packages: List[Package]):
        """Load and visualize packages and components"""
        self.logger.info(f"Loading {len(packages)} packages for visualization")
        
        # Clear existing content
        self.clear()
        self.components.clear()
        self.connections.clear()
        
        # Collect all components from all packages
        all_components = []
        for package in packages:
            all_components.extend(package.get_all_components(recursive=True))
        
        if not all_components:
            self.logger.warning("No components found to visualize")
            return
        
        # Layout components in a grid
        self._layout_components_grid(all_components)
        
        # TODO: Add connections in later implementation
        
        self.logger.info(f"Visualization complete: {len(all_components)} components displayed")
    
    def _layout_components_grid(self, components: List[Component]):
        """Layout components in a grid pattern"""
        cols = math.ceil(math.sqrt(len(components)))
        
        for i, component in enumerate(components):
            row = i // cols
            col = i % cols
            
            # Calculate position
            x = col * (UIConstants.COMPONENT_MIN_WIDTH + self.component_spacing)
            y = row * (UIConstants.COMPONENT_MIN_HEIGHT + self.component_spacing)
            
            # Create graphics item
            comp_item = ComponentGraphicsItem(component)
            comp_item.setPos(x, y)
            
            # Add to scene
            self.addItem(comp_item)
            self.components[component.uuid] = comp_item
            
            # Connect double-click signal using lambda with default parameter
            # This is the PyQt5 way to handle the closure issue
            def make_double_click_handler(c):
                return lambda event: self._on_component_double_clicked(c)
            
            comp_item.mouseDoubleClickEvent = make_double_click_handler(component)
    
    def _layout_components_hierarchical(self, components: List[Component]):
        """Layout components in hierarchical arrangement (future implementation)"""
        # TODO: Implement hierarchical layout based on composition relationships
        pass
    
    def _on_selection_changed(self):
        """Handle selection changes in the scene"""
        selected_items = self.selectedItems()
        
        if selected_items:
            for item in selected_items:
                if isinstance(item, ComponentGraphicsItem):
                    self.component_selected.emit(item.component)
                    break
        else:
            self.component_selected.emit(None)
    
    def _on_component_double_clicked(self, component: Component):
        """Handle component double-click"""
        self.logger.info(f"Component double-clicked: {component.short_name}")
        self.component_double_clicked.emit(component)
    
    def highlight_component(self, component_uuid: str):
        """Highlight a specific component"""
        # Reset all highlights
        for comp_item in self.components.values():
            comp_item.setOpacity(0.8)
            comp_item.setPen(QPen(comp_item.brush().color().darker(150), 2))
        
        # Highlight selected component
        if component_uuid in self.components:
            comp_item = self.components[component_uuid]
            comp_item.setOpacity(1.0)
            comp_item.setPen(QPen(QColor(255, 255, 0), 3))  # Yellow highlight
    
    def fit_components_in_view(self):
        """Adjust scene rect to fit all components"""
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
    
    def clear_scene(self):
        """Clear all items from scene"""
        self.clear()
        self.components.clear()
        self.connections.clear()
        
        # Reset scene rect
        self.setSceneRect(0, 0, 2000, 1500)

# Additional PyQt5 specific graphics utilities

class ConnectionGraphicsItem(QGraphicsLineItem):
    """Custom graphics item for connection visualization - PyQt5 version"""
    
    def __init__(self, connection, start_point: QPointF, end_point: QPointF, parent=None):
        super().__init__(parent)
        
        self.connection = connection
        
        # Set line
        self.setLine(start_point.x(), start_point.y(), end_point.x(), end_point.y())
        
        # Style the connection
        pen = QPen(QColor(100, 100, 100), 2)
        pen.setStyle(Qt.SolidLine)
        self.setPen(pen)
        
        # Make selectable
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        # Set tooltip
        self.setToolTip(f"Connection: {connection.short_name or 'Unnamed'}")
    
    def paint(self, painter, option, widget=None):
        """Custom paint method for arrow heads"""
        super().paint(painter, option, widget)
        
        # TODO: Add arrow head drawing for connection direction
        pass

class LayoutManager:
    """Layout manager for component positioning - PyQt5 compatible"""
    
    @staticmethod
    def grid_layout(components: List[Component], spacing: int = 150) -> Dict[str, Tuple[float, float]]:
        """Calculate grid layout positions for components"""
        positions = {}
        cols = math.ceil(math.sqrt(len(components)))
        
        for i, component in enumerate(components):
            row = i // cols
            col = i % cols
            
            x = col * (UIConstants.COMPONENT_MIN_WIDTH + spacing)
            y = row * (UIConstants.COMPONENT_MIN_HEIGHT + spacing)
            
            positions[component.uuid] = (x, y)
        
        return positions
    
    @staticmethod
    def hierarchical_layout(components: List[Component], spacing: int = 200) -> Dict[str, Tuple[float, float]]:
        """Calculate hierarchical layout positions (future implementation)"""
        # Placeholder for hierarchical layout algorithm
        return LayoutManager.grid_layout(components, spacing)

class SceneManager:
    """Scene management utilities for PyQt5"""
    
    def __init__(self, scene: ComponentDiagramScene):
        self.scene = scene
        self.logger = get_logger(__name__)
    
    def export_scene_to_image(self, file_path: str, format: str = "PNG"):
        """Export scene to image file"""
        try:
            from PyQt5.QtGui import QPixmap, QPainter
            
            # Get scene rect
            rect = self.scene.sceneRect()
            
            # Create pixmap
            pixmap = QPixmap(int(rect.width()), int(rect.height()))
            pixmap.fill(QColor(45, 45, 45))  # Dark background
            
            # Render scene to pixmap
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            self.scene.render(painter)
            painter.end()
            
            # Save to file
            pixmap.save(file_path, format)
            self.logger.info(f"Scene exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export scene: {e}")
            return False
    
    def print_scene(self, printer):
        """Print scene to printer (PyQt5 compatible)"""
        try:
            from PyQt5.QtGui import QPainter
            
            painter = QPainter(printer)
            painter.setRenderHint(QPainter.Antialiasing)
            self.scene.render(painter)
            painter.end()
            
            self.logger.info("Scene printed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to print scene: {e}")
            return False