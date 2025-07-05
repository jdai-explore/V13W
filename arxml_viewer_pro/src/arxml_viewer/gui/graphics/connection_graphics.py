# src/arxml_viewer/gui/graphics/connection_graphics.py
"""
Connection Graphics - Simple connection visualization for ARXML Viewer
Draws lines between connected ports with arrows and labels
"""

import math
from typing import Optional, Tuple, List
from PyQt5.QtWidgets import (
    QGraphicsPathItem, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsItem, QGraphicsEllipseItem
)
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import (
    QColor, QPen, QBrush, QPainterPath, QFont, QPainter,
    QLinearGradient, QPolygonF
)

from ...models.connection import Connection, ConnectionType
from ...utils.constants import AppConstants
from ...utils.logger import get_logger

class ConnectionGraphicsItem(QGraphicsPathItem):
    """
    Simple connection visualization between two ports
    Draws a line with arrow head and optional label
    """
    
    def __init__(self, connection: Connection, start_port_item, end_port_item, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        self.connection = connection
        self.start_port_item = start_port_item
        self.end_port_item = end_port_item
        
        # Visual properties
        self.line_width = 2
        self.arrow_size = 12
        self.connection_color = QColor(100, 149, 237)  # Cornflower blue
        self.selected_color = QColor(255, 165, 0)      # Orange
        self.hover_color = QColor(30, 144, 255)        # Dodger blue
        
        # State
        self.is_selected_connection = False
        self.is_hovering = False
        
        # Setup graphics
        self.setZValue(5)  # Above components but below ports
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Create the connection path
        self._create_connection_path()
        self._apply_styling()
        
        # Create arrow head
        self.arrow_head = ConnectionArrowHead(self)
        
        # Create optional label
        self.connection_label = None
        if connection.short_name:
            self.connection_label = ConnectionLabel(connection.short_name, self)
    
    def _create_connection_path(self):
        """Create the connection path between ports"""
        try:
            start_pos = self._get_port_scene_position(self.start_port_item)
            end_pos = self._get_port_scene_position(self.end_port_item)
            
            if not start_pos or not end_pos:
                self.logger.warning("Could not get port positions for connection")
                return
            
            # Create path based on connection type
            path = QPainterPath()
            
            if self.connection.connection_type == ConnectionType.ASSEMBLY:
                # Direct connection - straight line with slight curve
                path = self._create_curved_path(start_pos, end_pos)
            elif self.connection.connection_type == ConnectionType.DELEGATION:
                # Delegation - dashed line
                path = self._create_straight_path(start_pos, end_pos)
            else:
                # Default - straight line
                path = self._create_straight_path(start_pos, end_pos)
            
            self.setPath(path)
            
        except Exception as e:
            self.logger.error(f"Failed to create connection path: {e}")
    
    def _create_straight_path(self, start_pos: QPointF, end_pos: QPointF) -> QPainterPath:
        """Create straight line path"""
        path = QPainterPath()
        path.moveTo(start_pos)
        path.lineTo(end_pos)
        return path
    
    def _create_curved_path(self, start_pos: QPointF, end_pos: QPointF) -> QPainterPath:
        """Create slightly curved path for better aesthetics"""
        path = QPainterPath()
        path.moveTo(start_pos)
        
        # Calculate control points for smooth curve
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        
        # Add slight curve based on distance and direction
        mid_x = start_pos.x() + dx * 0.5
        mid_y = start_pos.y() + dy * 0.5
        
        # Offset perpendicular to line for curve
        curve_offset = min(abs(dx), abs(dy)) * 0.1
        if abs(dx) > abs(dy):
            mid_y += curve_offset if dy > 0 else -curve_offset
        else:
            mid_x += curve_offset if dx > 0 else -curve_offset
        
        control_point = QPointF(mid_x, mid_y)
        path.quadTo(control_point, end_pos)
        
        return path
    
    def _get_port_scene_position(self, port_item) -> Optional[QPointF]:
        """Get port position in scene coordinates"""
        try:
            if hasattr(port_item, 'get_port_center_scene_pos'):
                return port_item.get_port_center_scene_pos()
            elif hasattr(port_item, 'scenePos'):
                # For basic port items, use center of bounding rect
                scene_pos = port_item.scenePos()
                rect = port_item.boundingRect()
                return scene_pos + rect.center()
            else:
                self.logger.warning("Port item has no position method")
                return None
        except Exception as e:
            self.logger.error(f"Failed to get port position: {e}")
            return None
    
    def _apply_styling(self):
        """Apply visual styling to connection"""
        try:
            # Choose color based on state
            if self.is_selected_connection:
                color = self.selected_color
                width = self.line_width + 1
            elif self.is_hovering:
                color = self.hover_color
                width = self.line_width
            else:
                color = self.connection_color
                width = self.line_width
            
            # Create pen with appropriate style
            pen = QPen(color, width)
            
            # Different line styles for different connection types
            if self.connection.connection_type == ConnectionType.DELEGATION:
                pen.setStyle(Qt.DashLine)
            elif self.connection.connection_type == ConnectionType.PASS_THROUGH:
                pen.setStyle(Qt.DotLine)
            else:
                pen.setStyle(Qt.SolidLine)
            
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            
            self.setPen(pen)
            
        except Exception as e:
            self.logger.error(f"Failed to apply styling: {e}")
    
    def update_connection(self):
        """Update connection path and styling"""
        self._create_connection_path()
        self._apply_styling()
        
        # Update arrow head
        if hasattr(self, 'arrow_head'):
            self.arrow_head.update_position()
        
        # Update label position
        if self.connection_label:
            self.connection_label.update_position()
    
    def set_selected(self, selected: bool):
        """Set connection selection state"""
        self.is_selected_connection = selected
        self._apply_styling()
        
        if hasattr(self, 'arrow_head'):
            self.arrow_head.set_selected(selected)
    
    def hoverEnterEvent(self, event):
        """Handle hover enter"""
        self.is_hovering = True
        self._apply_styling()
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        self.is_hovering = False
        self._apply_styling()
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        if event.button() == Qt.LeftButton:
            self.set_selected(True)
            # Emit selection signal if needed
            if self.scene():
                self.scene().clearSelection()
                self.setSelected(True)
        super().mousePressEvent(event)
    
    def get_connection_info(self) -> dict:
        """Get connection information for display"""
        return {
            'name': self.connection.short_name or 'Unnamed Connection',
            'type': self.connection.connection_type.value,
            'uuid': self.connection.uuid,
            'provider': self.connection.provider_endpoint.component_uuid[:8],
            'requester': self.connection.requester_endpoint.component_uuid[:8]
        }

class ConnectionArrowHead(QGraphicsPolygonItem):
    """Arrow head for connection end"""
    
    def __init__(self, connection_item: ConnectionGraphicsItem):
        super().__init__(connection_item)
        
        self.connection_item = connection_item
        self.arrow_size = connection_item.arrow_size
        
        self.setZValue(6)  # Above connection line
        self.update_position()
    
    def update_position(self):
        """Update arrow head position and direction"""
        try:
            # Get connection path
            path = self.connection_item.path()
            if path.isEmpty():
                return
            
            # Get end point and direction
            length = path.length()
            if length < 1:
                return
            
            # Get point near end for direction calculation
            end_point = path.pointAtPercent(1.0)
            direction_point = path.pointAtPercent(0.95) if length > 20 else path.pointAtPercent(0.5)
            
            # Calculate angle
            dx = end_point.x() - direction_point.x()
            dy = end_point.y() - direction_point.y()
            
            if dx == 0 and dy == 0:
                return
            
            angle = math.atan2(dy, dx)
            
            # Create arrow polygon
            arrow_points = self._create_arrow_polygon(end_point, angle)
            self.setPolygon(arrow_points)
            
            # Apply styling
            color = self.connection_item.pen().color()
            self.setBrush(QBrush(color))
            self.setPen(QPen(color.darker(120), 1))
            
        except Exception as e:
            self.connection_item.logger.error(f"Failed to update arrow position: {e}")
    
    def _create_arrow_polygon(self, tip_point: QPointF, angle: float) -> QPolygonF:
        """Create arrow head polygon"""
        # Arrow dimensions
        arrow_length = self.arrow_size
        arrow_width = self.arrow_size * 0.6
        
        # Calculate arrow points
        back_angle1 = angle + math.pi - 0.4
        back_angle2 = angle + math.pi + 0.4
        
        point1 = QPointF(
            tip_point.x() + arrow_length * math.cos(back_angle1),
            tip_point.y() + arrow_length * math.sin(back_angle1)
        )
        
        point2 = QPointF(
            tip_point.x() + arrow_length * math.cos(back_angle2),
            tip_point.y() + arrow_length * math.sin(back_angle2)
        )
        
        # Create polygon
        arrow_polygon = QPolygonF([tip_point, point1, point2])
        return arrow_polygon
    
    def set_selected(self, selected: bool):
        """Update arrow styling for selection"""
        color = self.connection_item.pen().color()
        if selected:
            color = color.lighter(150)
        
        self.setBrush(QBrush(color))
        self.setPen(QPen(color.darker(120), 1))

class ConnectionLabel(QGraphicsTextItem):
    """Optional label for connection"""
    
    def __init__(self, text: str, connection_item: ConnectionGraphicsItem):
        super().__init__(text, connection_item)
        
        self.connection_item = connection_item
        
        # Setup font and appearance
        font = QFont("Arial", 8)
        self.setFont(font)
        self.setDefaultTextColor(QColor(60, 60, 60))
        
        # Background for better readability
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        self.setZValue(7)  # Above everything
        
        self.update_position()
    
    def update_position(self):
        """Position label at connection midpoint"""
        try:
            path = self.connection_item.path()
            if path.isEmpty():
                return
            
            # Get midpoint of connection
            mid_point = path.pointAtPercent(0.5)
            
            # Offset label slightly above the line
            label_rect = self.boundingRect()
            offset_x = -label_rect.width() / 2
            offset_y = -label_rect.height() - 5
            
            self.setPos(mid_point.x() + offset_x, mid_point.y() + offset_y)
            
        except Exception as e:
            self.connection_item.logger.error(f"Failed to update label position: {e}")

class ConnectionManager:
    """Manages multiple connections in a scene"""
    
    def __init__(self, graphics_scene):
        self.graphics_scene = graphics_scene
        self.logger = get_logger(__name__)
        self.connection_items: List[ConnectionGraphicsItem] = []
    
    def add_connection(self, connection: Connection, start_port_item, end_port_item):
        """Add a connection to the scene"""
        try:
            connection_item = ConnectionGraphicsItem(connection, start_port_item, end_port_item)
            self.graphics_scene.addItem(connection_item)
            self.connection_items.append(connection_item)
            
            self.logger.debug(f"Added connection: {connection.short_name}")
            return connection_item
            
        except Exception as e:
            self.logger.error(f"Failed to add connection: {e}")
            return None
    
    def remove_connection(self, connection_item: ConnectionGraphicsItem):
        """Remove a connection from the scene"""
        try:
            if connection_item in self.connection_items:
                self.graphics_scene.removeItem(connection_item)
                self.connection_items.remove(connection_item)
                self.logger.debug("Removed connection")
        except Exception as e:
            self.logger.error(f"Failed to remove connection: {e}")
    
    def clear_all_connections(self):
        """Clear all connections from the scene"""
        try:
            for connection_item in self.connection_items[:]:  # Copy list to avoid modification issues
                self.remove_connection(connection_item)
            self.connection_items.clear()
            self.logger.debug("Cleared all connections")
        except Exception as e:
            self.logger.error(f"Failed to clear connections: {e}")
    
    def update_all_connections(self):
        """Update all connection paths and positions"""
        try:
            for connection_item in self.connection_items:
                connection_item.update_connection()
            self.logger.debug("Updated all connections")
        except Exception as e:
            self.logger.error(f"Failed to update connections: {e}")
    
    def get_connections_for_component(self, component_uuid: str) -> List[ConnectionGraphicsItem]:
        """Get all connections involving a specific component"""
        result = []
        try:
            for connection_item in self.connection_items:
                if connection_item.connection.involves_component(component_uuid):
                    result.append(connection_item)
        except Exception as e:
            self.logger.error(f"Failed to get connections for component: {e}")
        
        return result
    
    def get_connections_for_port(self, port_uuid: str) -> List[ConnectionGraphicsItem]:
        """Get all connections involving a specific port"""
        result = []
        try:
            for connection_item in self.connection_items:
                if connection_item.connection.involves_port(port_uuid):
                    result.append(connection_item)
        except Exception as e:
            self.logger.error(f"Failed to get connections for port: {e}")
        
        return result
    
    def highlight_connections_for_component(self, component_uuid: str, highlight: bool = True):
        """Highlight all connections for a component"""
        try:
            connections = self.get_connections_for_component(component_uuid)
            for connection_item in connections:
                connection_item.set_selected(highlight)
        except Exception as e:
            self.logger.error(f"Failed to highlight connections: {e}")
    
    def get_connection_statistics(self) -> dict:
        """Get statistics about connections"""
        try:
            total_connections = len(self.connection_items)
            
            # Count by type
            type_counts = {}
            for connection_item in self.connection_items:
                conn_type = connection_item.connection.connection_type.value
                type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
            
            return {
                'total_connections': total_connections,
                'by_type': type_counts,
                'has_connections': total_connections > 0
            }
        except Exception as e:
            self.logger.error(f"Failed to get connection statistics: {e}")
            return {'total_connections': 0, 'by_type': {}, 'has_connections': False}

# Utility functions for external use
def create_simple_connection_line(start_point: QPointF, end_point: QPointF, 
                                color: QColor = None, width: int = 2) -> QGraphicsLineItem:
    """Create a simple connection line (utility function)"""
    line = QGraphicsLineItem(start_point.x(), start_point.y(), end_point.x(), end_point.y())
    
    if color is None:
        color = QColor(100, 149, 237)  # Default blue
    
    pen = QPen(color, width)
    pen.setCapStyle(Qt.RoundCap)
    line.setPen(pen)
    line.setZValue(5)
    
    return line

def calculate_connection_route(start_point: QPointF, end_point: QPointF, 
                             avoid_rects: List[QRectF] = None) -> List[QPointF]:
    """Calculate connection route avoiding obstacles (simple implementation)"""
    # For now, return simple direct route
    # Can be enhanced later with pathfinding algorithms
    if avoid_rects:
        # Simple obstacle avoidance - go around the middle
        mid_x = (start_point.x() + end_point.x()) / 2
        mid_y = (start_point.y() + end_point.y()) / 2
        
        # Check if direct line intersects any obstacles
        # If so, route around them (simplified logic)
        return [start_point, QPointF(mid_x, start_point.y()), 
                QPointF(mid_x, end_point.y()), end_point]
    else:
        return [start_point, end_point]