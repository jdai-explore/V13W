# src/arxml_viewer/gui/graphics/connection_graphics.py (ENHANCED FOR DAY 5)
"""
Connection Graphics - Enhanced connection visualization with proper rendering
Draws connections between ports with arrows, labels, and routing
PRIORITY 1: CONNECTION VISUALIZATION - Complete Implementation
"""

import math
from typing import Optional, Tuple, List, Dict, Any
from PyQt5.QtWidgets import (
    QGraphicsPathItem, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsItem, QGraphicsEllipseItem, QGraphicsScene
)
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer
from PyQt5.QtGui import (
    QColor, QPen, QBrush, QPainterPath, QFont, QPainter,
    QLinearGradient, QPolygonF, QPainterPathStroker
)

from ...models.connection import Connection, ConnectionType
from ...utils.constants import AppConstants
from ...utils.logger import get_logger

class ConnectionGraphicsItem(QGraphicsPathItem):
    """
    Enhanced connection visualization between two ports
    Supports different connection types with appropriate styling
    PRIORITY 1: CONNECTION VISUALIZATION - Complete Implementation
    """
    
    def __init__(self, connection: Connection, start_port_item, end_port_item, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        self.connection = connection
        self.start_port_item = start_port_item
        self.end_port_item = end_port_item
        
        # Visual properties based on connection type
        self.line_width = 2
        self.arrow_size = 12
        self.selected_line_width = 3
        
        # Colors based on connection type
        if connection.connection_type == ConnectionType.ASSEMBLY:
            self.connection_color = QColor(46, 125, 50)      # Green for assembly
            self.line_style = Qt.SolidLine
        elif connection.connection_type == ConnectionType.DELEGATION:
            self.connection_color = QColor(255, 152, 0)      # Orange for delegation
            self.line_style = Qt.DashLine
        else:
            self.connection_color = QColor(96, 125, 139)     # Gray for others
            self.line_style = Qt.SolidLine
        
        self.selected_color = QColor(255, 193, 7)            # Amber for selection
        self.hover_color = self.connection_color.lighter(130)
        
        # State
        self.is_selected_connection = False
        self.is_hovering = False
        self.is_highlighted = False
        
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
        if connection.short_name and connection.short_name.strip():
            self.connection_label = ConnectionLabel(connection.short_name, self)
        
        # Animation timer for selection feedback
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_selection)
        self.animation_phase = 0.0
    
    def _create_connection_path(self):
        """Create the connection path between ports with intelligent routing"""
        try:
            start_pos = self._get_port_scene_position(self.start_port_item)
            end_pos = self._get_port_scene_position(self.end_port_item)
            
            if not start_pos or not end_pos:
                self.logger.warning("Could not get port positions for connection")
                return
            
            # Choose path type based on connection type and port positions
            if self.connection.connection_type == ConnectionType.ASSEMBLY:
                # Direct connection with slight curve for aesthetics
                path = self._create_curved_path(start_pos, end_pos)
            elif self.connection.connection_type == ConnectionType.DELEGATION:
                # More structured path for delegation
                path = self._create_orthogonal_path(start_pos, end_pos)
            else:
                # Straight line for other types
                path = self._create_straight_path(start_pos, end_pos)
            
            self.setPath(path)
            
            # Update arrow head position
            if hasattr(self, 'arrow_head') and self.arrow_head:
                self.arrow_head.update_position()
            
            # Update label position
            if self.connection_label:
                self.connection_label.update_position()
            
        except Exception as e:
            self.logger.error(f"Failed to create connection path: {e}")
            # Fallback to simple line
            self._create_fallback_path()
    
    def _create_straight_path(self, start_pos: QPointF, end_pos: QPointF) -> QPainterPath:
        """Create straight line path"""
        path = QPainterPath()
        path.moveTo(start_pos)
        path.lineTo(end_pos)
        return path
    
    def _create_curved_path(self, start_pos: QPointF, end_pos: QPointF) -> QPainterPath:
        """Create curved path for better aesthetics"""
        path = QPainterPath()
        path.moveTo(start_pos)
        
        # Calculate control points for smooth curve
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 50:  # Very close ports - use straight line
            path.lineTo(end_pos)
        else:
            # Add curve based on distance and direction
            curve_strength = min(distance * 0.3, 100)  # Max curve of 100 pixels
            
            # Perpendicular offset for curve
            perp_x = -dy / distance * curve_strength * 0.3
            perp_y = dx / distance * curve_strength * 0.3
            
            # Control point at midpoint with perpendicular offset
            mid_x = (start_pos.x() + end_pos.x()) / 2 + perp_x
            mid_y = (start_pos.y() + end_pos.y()) / 2 + perp_y
            
            control_point = QPointF(mid_x, mid_y)
            path.quadTo(control_point, end_pos)
        
        return path
    
    def _create_orthogonal_path(self, start_pos: QPointF, end_pos: QPointF) -> QPainterPath:
        """Create orthogonal (L-shaped) path for delegation connections"""
        path = QPainterPath()
        path.moveTo(start_pos)
        
        # Calculate intermediate points for L-shape
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        
        # Choose horizontal-first or vertical-first based on greater distance
        if abs(dx) > abs(dy):
            # Horizontal first
            intermediate = QPointF(start_pos.x() + dx * 0.7, start_pos.y())
            path.lineTo(intermediate)
            path.lineTo(QPointF(intermediate.x(), end_pos.y()))
            path.lineTo(end_pos)
        else:
            # Vertical first
            intermediate = QPointF(start_pos.x(), start_pos.y() + dy * 0.7)
            path.lineTo(intermediate)
            path.lineTo(QPointF(end_pos.x(), intermediate.y()))
            path.lineTo(end_pos)
        
        return path
    
    def _create_fallback_path(self):
        """Create simple fallback path when position detection fails"""
        try:
            path = QPainterPath()
            path.moveTo(0, 0)
            path.lineTo(100, 0)  # Simple horizontal line
            self.setPath(path)
        except Exception:
            pass
    
    def _get_port_scene_position(self, port_item) -> Optional[QPointF]:
        """Get port position in scene coordinates with enhanced detection"""
        try:
            if not port_item:
                return None
            
            # Try enhanced port graphics method first
            if hasattr(port_item, 'get_port_center_scene_pos'):
                return port_item.get_port_center_scene_pos()
            
            # Try standard scene position with center offset
            if hasattr(port_item, 'scenePos') and hasattr(port_item, 'boundingRect'):
                scene_pos = port_item.scenePos()
                rect = port_item.boundingRect()
                return scene_pos + rect.center()
            
            # Try simple scene position
            if hasattr(port_item, 'scenePos'):
                return port_item.scenePos()
            
            # Fallback to origin
            return QPointF(0, 0)
            
        except Exception as e:
            self.logger.error(f"Failed to get port position: {e}")
            return QPointF(0, 0)
    
    def _apply_styling(self):
        """Apply visual styling based on connection state and type"""
        try:
            # Choose color based on state
            if self.is_selected_connection:
                color = self.selected_color
                width = self.selected_line_width
            elif self.is_hovering:
                color = self.hover_color
                width = self.line_width
            elif self.is_highlighted:
                color = self.connection_color.lighter(150)
                width = self.line_width
            else:
                color = self.connection_color
                width = self.line_width
            
            # Create pen with appropriate style
            pen = QPen(color, width)
            pen.setStyle(self.line_style)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            
            # Add subtle gradient for better visibility
            if not self.is_selected_connection:
                pen.setColor(color)
            
            self.setPen(pen)
            
            # No brush for path items (lines only)
            self.setBrush(QBrush(Qt.NoBrush))
            
        except Exception as e:
            self.logger.error(f"Failed to apply styling: {e}")
    
    def update_connection(self):
        """Update connection path and styling"""
        self._create_connection_path()
        self._apply_styling()
        
        # Update arrow head
        if hasattr(self, 'arrow_head') and self.arrow_head:
            self.arrow_head.update_position()
        
        # Update label position
        if self.connection_label:
            self.connection_label.update_position()
    
    def set_selected(self, selected: bool):
        """Set connection selection state with animation"""
        self.is_selected_connection = selected
        self._apply_styling()
        
        if hasattr(self, 'arrow_head') and self.arrow_head:
            self.arrow_head.set_selected(selected)
        
        # Start selection animation
        if selected:
            self.animation_timer.start(100)  # 100ms intervals
        else:
            self.animation_timer.stop()
            self.animation_phase = 0.0
    
    def set_highlighted(self, highlighted: bool):
        """Set connection highlight state"""
        self.is_highlighted = highlighted
        self._apply_styling()
    
    def _animate_selection(self):
        """Animate selected connection for better visibility"""
        try:
            self.animation_phase += 0.2
            if self.animation_phase >= 2 * math.pi:
                self.animation_phase = 0.0
            
            # Subtle pulsing effect by varying line width
            if self.is_selected_connection:
                pulse_width = self.selected_line_width + math.sin(self.animation_phase) * 0.5
                pen = self.pen()
                pen.setWidth(max(1, int(pulse_width)))
                self.setPen(pen)
        except Exception:
            pass  # Animation errors are not critical
    
    def hoverEnterEvent(self, event):
        """Handle hover enter with visual feedback"""
        self.is_hovering = True
        self._apply_styling()
        
        # Show enhanced tooltip
        tooltip = self._generate_enhanced_tooltip()
        self.setToolTip(tooltip)
        
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
            # Clear other selections in scene
            if self.scene():
                for item in self.scene().selectedItems():
                    if item != self and hasattr(item, 'set_selected'):
                        item.set_selected(False)
                self.setSelected(True)
        super().mousePressEvent(event)
    
    def _generate_enhanced_tooltip(self) -> str:
        """Generate enhanced tooltip with connection details"""
        try:
            tooltip_parts = [
                f"<b>🔗 {self.connection.short_name}</b>",
                f"Type: {self.connection.connection_type.value}",
                f"UUID: {self.connection.uuid[:8]}...",
            ]
            
            if self.connection.desc:
                desc = self.connection.desc
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                tooltip_parts.append(f"Description: {desc}")
            
            # Add endpoint information
            tooltip_parts.append("Endpoints:")
            tooltip_parts.append(f"  Provider: {self.connection.provider_endpoint.component_uuid[:8]}...")
            tooltip_parts.append(f"  Requester: {self.connection.requester_endpoint.component_uuid[:8]}...")
            
            return "<br>".join(tooltip_parts)
        except Exception:
            return f"Connection: {self.connection.short_name or 'Unknown'}"
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for display"""
        return {
            'name': self.connection.short_name or 'Unnamed Connection',
            'type': self.connection.connection_type.value,
            'uuid': self.connection.uuid,
            'description': self.connection.desc,
            'provider_component': self.connection.provider_endpoint.component_uuid,
            'provider_port': self.connection.provider_endpoint.port_uuid,
            'requester_component': self.connection.requester_endpoint.component_uuid,
            'requester_port': self.connection.requester_endpoint.port_uuid
        }

class ConnectionArrowHead(QGraphicsPolygonF):
    """Enhanced arrow head for connection end with proper scaling"""
    
    def __init__(self, connection_item: ConnectionGraphicsItem):
        super().__init__(connection_item)
        
        self.connection_item = connection_item
        self.arrow_size = connection_item.arrow_size
        
        self.setZValue(6)  # Above connection line
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)
        
        self.update_position()
    
    def update_position(self):
        """Update arrow head position and direction based on connection path"""
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
            if length > 20:
                end_point = path.pointAtPercent(1.0)
                direction_point = path.pointAtPercent(0.95)
            else:
                end_point = path.pointAtPercent(1.0)
                direction_point = path.pointAtPercent(0.5)
            
            # Calculate angle
            dx = end_point.x() - direction_point.x()
            dy = end_point.y() - direction_point.y()
            
            if abs(dx) < 0.1 and abs(dy) < 0.1:
                return  # Too close to calculate direction
            
            angle = math.atan2(dy, dx)
            
            # Create arrow polygon
            arrow_points = self._create_arrow_polygon(end_point, angle)
            self.setPolygon(arrow_points)
            
            # Apply styling
            self._apply_arrow_styling()
            
        except Exception as e:
            self.connection_item.logger.error(f"Failed to update arrow position: {e}")
    
    def _create_arrow_polygon(self, tip_point: QPointF, angle: float) -> QPolygonF:
        """Create arrow head polygon with proper proportions"""
        # Arrow dimensions
        arrow_length = self.arrow_size
        arrow_width = self.arrow_size * 0.6
        
        # Calculate arrow points
        back_angle1 = angle + math.pi - 0.4  # 23 degrees
        back_angle2 = angle + math.pi + 0.4  # 23 degrees
        
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
    
    def _apply_arrow_styling(self):
        """Apply styling to arrow head"""
        try:
            color = self.connection_item.pen().color()
            self.setBrush(QBrush(color))
            self.setPen(QPen(color.darker(120), 1))
        except Exception:
            pass
    
    def set_selected(self, selected: bool):
        """Update arrow styling for selection"""
        try:
            self._apply_arrow_styling()
        except Exception:
            pass

class ConnectionLabel(QGraphicsTextItem):
    """Enhanced label for connection with better positioning"""
    
    def __init__(self, text: str, connection_item: ConnectionGraphicsItem):
        super().__init__(text, connection_item)
        
        self.connection_item = connection_item
        
        # Setup font and appearance
        font = QFont("Arial", 8)
        self.setFont(font)
        self.setDefaultTextColor(QColor(50, 50, 50))
        
        # Background for better readability
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        self.setZValue(7)  # Above everything
        
        # Add background rectangle for better visibility
        self._setup_background()
        
        self.update_position()
    
    def _setup_background(self):
        """Setup background rectangle for label"""
        try:
            # Create a subtle background
            self.setStyleSheet("""
                QGraphicsTextItem {
                    background-color: rgba(255, 255, 255, 200);
                    border: 1px solid rgba(0, 0, 0, 100);
                    border-radius: 3px;
                    padding: 2px;
                }
            """)
        except Exception:
            pass
    
    def update_position(self):
        """Position label at connection midpoint with smart offset"""
        try:
            path = self.connection_item.path()
            if path.isEmpty():
                return
            
            # Get midpoint of connection
            mid_point = path.pointAtPercent(0.5)
            
            # Calculate smart offset based on connection direction
            if path.length() > 20:
                before_mid = path.pointAtPercent(0.4)
                after_mid = path.pointAtPercent(0.6)
                
                # Calculate perpendicular offset
                dx = after_mid.x() - before_mid.x()
                dy = after_mid.y() - before_mid.y()
                length = math.sqrt(dx * dx + dy * dy)
                
                if length > 0:
                    # Perpendicular vector
                    perp_x = -dy / length * 15  # 15 pixel offset
                    perp_y = dx / length * 15
                    
                    # Offset the label
                    label_rect = self.boundingRect()
                    offset_x = perp_x - label_rect.width() / 2
                    offset_y = perp_y - label_rect.height() / 2
                    
                    self.setPos(mid_point.x() + offset_x, mid_point.y() + offset_y)
                else:
                    # Fallback to simple offset
                    self._simple_position_offset(mid_point)
            else:
                self._simple_position_offset(mid_point)
            
        except Exception as e:
            self.connection_item.logger.error(f"Failed to update label position: {e}")
    
    def _simple_position_offset(self, mid_point: QPointF):
        """Simple label positioning as fallback"""
        try:
            label_rect = self.boundingRect()
            offset_x = -label_rect.width() / 2
            offset_y = -label_rect.height() - 8
            self.setPos(mid_point.x() + offset_x, mid_point.y() + offset_y)
        except Exception:
            self.setPos(mid_point)

class ConnectionManager:
    """Enhanced manager for multiple connections in a scene"""
    
    def __init__(self, graphics_scene):
        self.graphics_scene = graphics_scene
        self.logger = get_logger(__name__)
        self.connection_items: List[ConnectionGraphicsItem] = []
        self.connection_map: Dict[str, ConnectionGraphicsItem] = {}  # uuid -> item
        
        # Performance optimization
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._batch_update_connections)
        self.pending_updates = set()
    
    def add_connection(self, connection: Connection, start_port_item, end_port_item) -> Optional[ConnectionGraphicsItem]:
        """Add a connection to the scene with validation"""
        try:
            if not connection or not start_port_item or not end_port_item:
                self.logger.warning("Invalid connection parameters")
                return None
            
            # Check if connection already exists
            if connection.uuid in self.connection_map:
                self.logger.warning(f"Connection {connection.uuid} already exists")
                return self.connection_map[connection.uuid]
            
            # Create connection graphics item
            connection_item = ConnectionGraphicsItem(connection, start_port_item, end_port_item)
            
            # Add to scene
            self.graphics_scene.addItem(connection_item)
            
            # Store references
            self.connection_items.append(connection_item)
            self.connection_map[connection.uuid] = connection_item
            
            self.logger.debug(f"Added connection: {connection.short_name} ({connection.connection_type.value})")
            return connection_item
            
        except Exception as e:
            self.logger.error(f"Failed to add connection: {e}")
            return None
    
    def remove_connection(self, connection_item: ConnectionGraphicsItem):
        """Remove a connection from the scene"""
        try:
            if connection_item not in self.connection_items:
                return
            
            # Remove from scene
            self.graphics_scene.removeItem(connection_item)
            
            # Remove from tracking
            self.connection_items.remove(connection_item)
            
            # Remove from map
            connection_uuid = connection_item.connection.uuid
            if connection_uuid in self.connection_map:
                del self.connection_map[connection_uuid]
            
            self.logger.debug(f"Removed connection: {connection_item.connection.short_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to remove connection: {e}")
    
    def remove_connection_by_uuid(self, connection_uuid: str):
        """Remove connection by UUID"""
        if connection_uuid in self.connection_map:
            self.remove_connection(self.connection_map[connection_uuid])
    
    def clear_all_connections(self):
        """Clear all connections from the scene"""
        try:
            # Stop any pending updates
            self.update_timer.stop()
            self.pending_updates.clear()
            
            # Remove all connection items
            for connection_item in self.connection_items[:]:  # Copy list to avoid modification issues
                self.remove_connection(connection_item)
            
            # Clear collections
            self.connection_items.clear()
            self.connection_map.clear()
            
            self.logger.debug("Cleared all connections")
            
        except Exception as e:
            self.logger.error(f"Failed to clear connections: {e}")
    
    def update_all_connections(self):
        """Update all connection paths and positions with batching"""
        try:
            if not self.connection_items:
                return
            
            # Add all connections to pending updates
            self.pending_updates.update(self.connection_items)
            
            # Start batch update timer
            self.update_timer.start(50)  # 50ms delay for batching
            
        except Exception as e:
            self.logger.error(f"Failed to schedule connection updates: {e}")
    
    def _batch_update_connections(self):
        """Batch update connections for better performance"""
        try:
            updated_count = 0
            for connection_item in list(self.pending_updates):
                try:
                    connection_item.update_connection()
                    updated_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to update connection: {e}")
            
            self.pending_updates.clear()
            self.logger.debug(f"Batch updated {updated_count} connections")
            
        except Exception as e:
            self.logger.error(f"Batch update failed: {e}")
    
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
                connection_item.set_highlighted(highlight)
        except Exception as e:
            self.logger.error(f"Failed to highlight connections: {e}")
    
    def select_connection_by_uuid(self, connection_uuid: str) -> bool:
        """Select connection by UUID"""
        try:
            if connection_uuid in self.connection_map:
                # Clear other selections
                for connection_item in self.connection_items:
                    connection_item.set_selected(False)
                
                # Select target connection
                self.connection_map[connection_uuid].set_selected(True)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to select connection: {e}")
            return False
    
    def get_connection_by_uuid(self, connection_uuid: str) -> Optional[ConnectionGraphicsItem]:
        """Get connection graphics item by UUID"""
        return self.connection_map.get(connection_uuid)
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        """Get statistics about connections"""
        try:
            total_connections = len(self.connection_items)
            
            # Count by type
            type_counts = {}
            for connection_item in self.connection_items:
                conn_type = connection_item.connection.connection_type.value
                type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
            
            # Count by state
            selected_count = sum(1 for item in self.connection_items if item.is_selected_connection)
            highlighted_count = sum(1 for item in self.connection_items if item.is_highlighted)
            
            return {
                'total_connections': total_connections,
                'by_type': type_counts,
                'selected_count': selected_count,
                'highlighted_count': highlighted_count,
                'has_connections': total_connections > 0
            }
        except Exception as e:
            self.logger.error(f"Failed to get connection statistics: {e}")
            return {'total_connections': 0, 'by_type': {}, 'has_connections': False}
    
    def find_connections_between_ports(self, port1_uuid: str, port2_uuid: str) -> List[ConnectionGraphicsItem]:
        """Find connections between two specific ports"""
        result = []
        try:
            for connection_item in self.connection_items:
                connection = connection_item.connection
                if ((connection.provider_endpoint.port_uuid == port1_uuid and 
                     connection.requester_endpoint.port_uuid == port2_uuid) or
                    (connection.provider_endpoint.port_uuid == port2_uuid and 
                     connection.requester_endpoint.port_uuid == port1_uuid)):
                    result.append(connection_item)
        except Exception as e:
            self.logger.error(f"Failed to find connections between ports: {e}")
        
        return result
    
    def validate_connections(self) -> Dict[str, Any]:
        """Validate all connections and return issues"""
        issues = []
        valid_connections = 0
        
        try:
            for connection_item in self.connection_items:
                try:
                    # Check if start and end ports still exist
                    start_pos = connection_item._get_port_scene_position(connection_item.start_port_item)
                    end_pos = connection_item._get_port_scene_position(connection_item.end_port_item)
                    
                    if not start_pos or not end_pos:
                        issues.append(f"Connection {connection_item.connection.short_name} has invalid port positions")
                    else:
                        valid_connections += 1
                        
                except Exception as e:
                    issues.append(f"Connection {connection_item.connection.short_name} validation failed: {e}")
            
            return {
                'total_connections': len(self.connection_items),
                'valid_connections': valid_connections,
                'issues': issues,
                'is_valid': len(issues) == 0
            }
            
        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            return {
                'total_connections': 0,
                'valid_connections': 0,
                'issues': [f"Validation error: {e}"],
                'is_valid': False
            }

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
    """Calculate connection route avoiding obstacles (enhanced implementation)"""
    try:
        # Simple obstacle avoidance implementation
        if not avoid_rects:
            return [start_point, end_point]
        
        # Check if direct line intersects any obstacles
        direct_intersects = False
        for rect in avoid_rects:
            if rect.contains(start_point) or rect.contains(end_point):
                continue  # Skip if points are inside rectangles
            
            # Simple line-rectangle intersection check
            if _line_intersects_rect(start_point, end_point, rect):
                direct_intersects = True
                break
        
        if not direct_intersects:
            return [start_point, end_point]
        
        # Route around obstacles (simplified)
        mid_x = (start_point.x() + end_point.x()) / 2
        mid_y = (start_point.y() + end_point.y()) / 2
        
        # Find a safe intermediate point
        offset = 50  # Offset distance
        if start_point.x() < end_point.x():
            safe_point = QPointF(mid_x, start_point.y() - offset)
        else:
            safe_point = QPointF(mid_x, start_point.y() + offset)
        
        return [start_point, safe_point, QPointF(safe_point.x(), end_point.y()), end_point]
        
    except Exception:
        # Fallback to direct route
        return [start_point, end_point]

def _line_intersects_rect(start: QPointF, end: QPointF, rect: QRectF) -> bool:
    """Simple line-rectangle intersection test"""
    try:
        # Very simplified - just check if line passes through rect center area
        center = rect.center()
        expanded_rect = QRectF(
            rect.x() - rect.width() * 0.1,
            rect.y() - rect.height() * 0.1,
            rect.width() * 1.2,
            rect.height() * 1.2
        )
        
        # Check if line segment passes near the rectangle
        # This is a simplified approximation
        line_center = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)
        return expanded_rect.contains(line_center)
        
    except Exception:
        return False