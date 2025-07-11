# src/arxml_viewer/gui/graphics/connection_graphics.py - SIMPLIFIED VERSION
"""
Connection Graphics - SIMPLIFIED connection visualization
MAJOR SIMPLIFICATION as per guide requirements:
- Remove ConnectionArrowHead class - simple lines only
- Remove ConnectionLabel class - no connection labels needed
- Remove animation systems and hover effects
- Remove complex routing algorithms
- Simplify ConnectionGraphicsItem to basic QGraphicsLineItem
- Remove ConnectionManager complexity - basic list of line items
- Remove validation, statistics, and metadata tracking
- Keep minimal: Simple lines between ports, basic selection
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen

from ...models.connection import Connection, ConnectionType
from ...utils.constants import AppConstants
from ...utils.logger import get_logger

class ConnectionGraphicsItem(QGraphicsLineItem):
    """
    SIMPLIFIED connection visualization - basic QGraphicsLineItem only
    Removed complex routing, arrows, labels, animations, hover effects
    """
    
    def __init__(self, connection: Connection, start_port_item, end_port_item, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        self.connection = connection
        self.start_port_item = start_port_item
        self.end_port_item = end_port_item
        
        # SIMPLIFIED visual properties
        self.line_width = 2
        self.is_selected_connection = False
        self.is_highlighted = False
        
        # Set BASIC line styling
        self._apply_basic_styling()
        
        # Make selectable
        self.setFlag(QGraphicsLineItem.ItemIsSelectable, True)
        self.setZValue(5)  # Above components but below ports
        
        # Create SIMPLE line between ports
        self._create_simple_line()
        
        # Set basic tooltip
        self.setToolTip(self._generate_simple_tooltip())
    
    def _apply_basic_styling(self):
        """Apply BASIC styling based on connection state and type"""
        try:
            # Choose color based on connection type
            if hasattr(self.connection, 'connection_type'):
                if self.connection.connection_type == ConnectionType.ASSEMBLY:
                    color = QColor(46, 125, 50)      # Green for assembly
                elif self.connection.connection_type == ConnectionType.DELEGATION:
                    color = QColor(255, 152, 0)      # Orange for delegation
                else:
                    color = QColor(96, 125, 139)     # Gray for others
            else:
                color = QColor(100, 149, 237)        # Default blue
            
            # Adjust for state
            width = self.line_width
            if self.is_selected_connection:
                color = QColor(255, 193, 7)          # Amber for selection
                width = 3
            elif self.is_highlighted:
                color = color.lighter(150)
            
            # Create BASIC pen
            pen = QPen(color, width)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            self.setPen(pen)
            
        except Exception as e:
            self.logger.error(f"Basic styling failed: {e}")
            # Fallback styling
            self.setPen(QPen(QColor(100, 149, 237), 2))
    
    def _create_simple_line(self):
        """Create SIMPLE line between ports"""
        try:
            start_pos = self._get_simple_port_position(self.start_port_item)
            end_pos = self._get_simple_port_position(self.end_port_item)
            
            if start_pos and end_pos:
                # Set line coordinates
                self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
            else:
                self.logger.warning("Could not get port positions for simple connection")
                # Fallback to origin line
                self.setLine(0, 0, 100, 0)
            
        except Exception as e:
            self.logger.error(f"Simple line creation failed: {e}")
            # Fallback to horizontal line
            self.setLine(0, 0, 100, 0)
    
    def _get_simple_port_position(self, port_item) -> Optional[QPointF]:
        """Get SIMPLE port position in scene coordinates"""
        try:
            if not port_item:
                return None
            
            # Try to get scene position
            if hasattr(port_item, 'scenePos'):
                scene_pos = port_item.scenePos()
                
                # Try to get center of port
                if hasattr(port_item, 'boundingRect'):
                    rect = port_item.boundingRect()
                    return scene_pos + rect.center()
                else:
                    return scene_pos
            
            # Fallback to origin
            return QPointF(0, 0)
            
        except Exception as e:
            self.logger.error(f"Simple port position failed: {e}")
            return QPointF(0, 0)
    
    def _generate_simple_tooltip(self) -> str:
        """Generate SIMPLE tooltip with basic connection info"""
        try:
            tooltip = f"Connection: {getattr(self.connection, 'short_name', 'Unknown')}"
            if hasattr(self.connection, 'connection_type'):
                tooltip += f"\nType: {self.connection.connection_type.value}"
            if hasattr(self.connection, 'uuid'):
                tooltip += f"\nUUID: {self.connection.uuid[:8]}..."
            return tooltip
        except Exception:
            return "Connection"
    
    def update_connection(self):
        """Update SIMPLE connection line"""
        try:
            self._create_simple_line()
            self._apply_basic_styling()
        except Exception as e:
            self.logger.error(f"Simple connection update failed: {e}")
    
    def set_selected(self, selected: bool):
        """Set SIMPLE connection selection state"""
        try:
            self.is_selected_connection = selected
            self._apply_basic_styling()
        except Exception as e:
            self.logger.error(f"Simple selection failed: {e}")
    
    def set_highlighted(self, highlighted: bool):
        """Set SIMPLE connection highlight state"""
        try:
            self.is_highlighted = highlighted
            self._apply_basic_styling()
        except Exception as e:
            self.logger.error(f"Simple highlighting failed: {e}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get SIMPLE connection information"""
        try:
            return {
                'name': getattr(self.connection, 'short_name', 'Unknown'),
                'type': getattr(self.connection, 'connection_type', 'Unknown'),
                'uuid': getattr(self.connection, 'uuid', 'Unknown'),
                'description': getattr(self.connection, 'desc', None)
            }
        except Exception as e:
            self.logger.error(f"Get connection info failed: {e}")
            return {'name': 'Unknown', 'type': 'Unknown', 'uuid': 'Unknown'}

class ConnectionManager:
    """
    SIMPLIFIED connection manager - basic list of line items only
    Removed complex validation, statistics, metadata tracking
    """
    
    def __init__(self, graphics_scene):
        self.graphics_scene = graphics_scene
        self.logger = get_logger(__name__)
        
        # SIMPLIFIED state - basic list only
        self.connection_items: List[ConnectionGraphicsItem] = []
        
        print("✅ SIMPLIFIED ConnectionManager initialized")
    
    def add_connection(self, connection: Connection, start_port_item, end_port_item) -> Optional[ConnectionGraphicsItem]:
        """Add a SIMPLE connection to the scene"""
        try:
            if not connection or not start_port_item or not end_port_item:
                self.logger.warning("Invalid connection parameters")
                return None
            
            # Create SIMPLE connection graphics item
            connection_item = ConnectionGraphicsItem(connection, start_port_item, end_port_item)
            
            # Add to scene
            if self.graphics_scene:
                self.graphics_scene.addItem(connection_item)
            
            # Store in SIMPLE list
            self.connection_items.append(connection_item)
            
            self.logger.debug(f"Added simple connection: {getattr(connection, 'short_name', 'Unknown')}")
            return connection_item
            
        except Exception as e:
            self.logger.error(f"Failed to add simple connection: {e}")
            return None
    
    def remove_connection(self, connection_item: ConnectionGraphicsItem):
        """Remove a SIMPLE connection from the scene"""
        try:
            if connection_item not in self.connection_items:
                return
            
            # Remove from scene
            if self.graphics_scene:
                self.graphics_scene.removeItem(connection_item)
            
            # Remove from SIMPLE list
            self.connection_items.remove(connection_item)
            
            self.logger.debug(f"Removed simple connection")
            
        except Exception as e:
            self.logger.error(f"Failed to remove simple connection: {e}")
    
    def clear_all_connections(self):
        """Clear all SIMPLE connections from the scene"""
        try:
            # Remove all connection items
            for connection_item in self.connection_items[:]:  # Copy list to avoid modification issues
                self.remove_connection(connection_item)
            
            # Clear SIMPLE list
            self.connection_items.clear()
            
            self.logger.debug("Cleared all simple connections")
            
        except Exception as e:
            self.logger.error(f"Failed to clear simple connections: {e}")
    
    def update_all_connections(self):
        """Update all SIMPLE connection lines"""
        try:
            updated_count = 0
            for connection_item in self.connection_items:
                try:
                    connection_item.update_connection()
                    updated_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to update simple connection: {e}")
            
            self.logger.debug(f"Updated {updated_count} simple connections")
            
        except Exception as e:
            self.logger.error(f"Simple connection update failed: {e}")
    
    def get_connections_for_component(self, component_uuid: str) -> List[ConnectionGraphicsItem]:
        """Get SIMPLE connections involving a specific component"""
        result = []
        try:
            for connection_item in self.connection_items:
                if hasattr(connection_item, 'connection') and hasattr(connection_item.connection, 'involves_component'):
                    if connection_item.connection.involves_component(component_uuid):
                        result.append(connection_item)
        except Exception as e:
            self.logger.error(f"Failed to get simple connections for component: {e}")
        
        return result
    
    def get_connections_for_port(self, port_uuid: str) -> List[ConnectionGraphicsItem]:
        """Get SIMPLE connections involving a specific port"""
        result = []
        try:
            for connection_item in self.connection_items:
                if hasattr(connection_item, 'connection') and hasattr(connection_item.connection, 'involves_port'):
                    if connection_item.connection.involves_port(port_uuid):
                        result.append(connection_item)
        except Exception as e:
            self.logger.error(f"Failed to get simple connections for port: {e}")
        
        return result
    
    def highlight_connections_for_component(self, component_uuid: str, highlight: bool = True):
        """Highlight SIMPLE connections for a component"""
        try:
            connections = self.get_connections_for_component(component_uuid)
            for connection_item in connections:
                connection_item.set_highlighted(highlight)
        except Exception as e:
            self.logger.error(f"Failed to highlight simple connections: {e}")
    
    def select_connection_by_uuid(self, connection_uuid: str) -> bool:
        """Select SIMPLE connection by UUID"""
        try:
            for connection_item in self.connection_items:
                # Clear other selections
                connection_item.set_selected(False)
                
                # Select target connection if UUID matches
                if (hasattr(connection_item, 'connection') and 
                    hasattr(connection_item.connection, 'uuid') and
                    connection_item.connection.uuid == connection_uuid):
                    connection_item.set_selected(True)
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to select simple connection: {e}")
            return False
    
    def get_connection_by_uuid(self, connection_uuid: str) -> Optional[ConnectionGraphicsItem]:
        """Get SIMPLE connection graphics item by UUID"""
        try:
            for connection_item in self.connection_items:
                if (hasattr(connection_item, 'connection') and 
                    hasattr(connection_item.connection, 'uuid') and
                    connection_item.connection.uuid == connection_uuid):
                    return connection_item
            return None
        except Exception as e:
            self.logger.error(f"Failed to get simple connection by UUID: {e}")
            return None
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        """Get SIMPLE statistics about connections"""
        try:
            total_connections = len(self.connection_items)
            
            # Count by type - simplified
            type_counts = {}
            for connection_item in self.connection_items:
                try:
                    if hasattr(connection_item, 'connection') and hasattr(connection_item.connection, 'connection_type'):
                        conn_type = connection_item.connection.connection_type.value
                        type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
                except Exception:
                    pass
            
            # Count by state - simplified
            selected_count = sum(1 for item in self.connection_items 
                               if hasattr(item, 'is_selected_connection') and item.is_selected_connection)
            highlighted_count = sum(1 for item in self.connection_items 
                                  if hasattr(item, 'is_highlighted') and item.is_highlighted)
            
            return {
                'total_connections': total_connections,
                'by_type': type_counts,
                'selected_count': selected_count,
                'highlighted_count': highlighted_count,
                'has_connections': total_connections > 0
            }
        except Exception as e:
            self.logger.error(f"Failed to get simple connection statistics: {e}")
            return {'total_connections': 0, 'by_type': {}, 'has_connections': False}
    
    def validate_connections(self) -> Dict[str, Any]:
        """SIMPLE validation of connections"""
        try:
            valid_connections = 0
            issues = []
            
            for connection_item in self.connection_items:
                try:
                    # Basic validation - check if line has valid coordinates
                    line = connection_item.line()
                    if line.length() > 0:
                        valid_connections += 1
                    else:
                        issues.append("Connection has zero length")
                        
                except Exception as e:
                    issues.append(f"Connection validation failed: {e}")
            
            return {
                'total_connections': len(self.connection_items),
                'valid_connections': valid_connections,
                'issues': issues,
                'is_valid': len(issues) == 0
            }
            
        except Exception as e:
            self.logger.error(f"Simple connection validation failed: {e}")
            return {
                'total_connections': 0,
                'valid_connections': 0,
                'issues': [f"Validation error: {e}"],
                'is_valid': False
            }

# SIMPLIFIED utility functions
def create_simple_connection_line(start_point: QPointF, end_point: QPointF, 
                                color: QColor = None, width: int = 2) -> QGraphicsLineItem:
    """Create a SIMPLE connection line (utility function)"""
    line = QGraphicsLineItem(start_point.x(), start_point.y(), end_point.x(), end_point.y())
    
    if color is None:
        color = QColor(100, 149, 237)  # Default blue
    
    pen = QPen(color, width)
    pen.setCapStyle(Qt.RoundCap)
    line.setPen(pen)
    line.setZValue(5)
    
    return line

def calculate_simple_connection_route(start_point: QPointF, end_point: QPointF) -> List[QPointF]:
    """Calculate SIMPLE connection route - direct line only"""
    return [start_point, end_point]

# Export SIMPLIFIED classes
__all__ = [
    'ConnectionGraphicsItem', 
    'ConnectionManager',
    'create_simple_connection_line',
    'calculate_simple_connection_route'
]