# src/arxml_viewer/gui/graphics/connection_graphics_fallback.py
"""
Connection Graphics Fallback - Simple implementation for testing
Provides basic connection graphics functionality when full implementation fails
"""

from typing import List, Dict, Any, Optional
from PyQt5.QtCore import QObject

class ConnectionGraphicsItem:
    """Fallback connection graphics item"""
    
    def __init__(self, connection, start_port_item, end_port_item, parent=None):
        self.connection = connection
        self.start_port_item = start_port_item
        self.end_port_item = end_port_item
        self.is_selected_connection = False
        self.is_highlighted = False
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected_connection = selected
    
    def set_highlighted(self, highlighted: bool):
        """Set highlight state"""
        self.is_highlighted = highlighted
    
    def update_connection(self):
        """Update connection display"""
        pass
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            'name': self.connection.short_name or 'Unnamed Connection',
            'type': self.connection.connection_type.value,
            'uuid': self.connection.uuid,
        }

class ConnectionManager(QObject):
    """Fallback connection manager"""
    
    def __init__(self, graphics_scene):
        super().__init__()
        self.graphics_scene = graphics_scene
        self.connection_items: List[ConnectionGraphicsItem] = []
        self.connection_map: Dict[str, ConnectionGraphicsItem] = {}
    
    def add_connection(self, connection, start_port_item, end_port_item) -> Optional[ConnectionGraphicsItem]:
        """Add a connection (fallback implementation)"""
        try:
            connection_item = ConnectionGraphicsItem(connection, start_port_item, end_port_item)
            self.connection_items.append(connection_item)
            self.connection_map[connection.uuid] = connection_item
            return connection_item
        except Exception:
            return None
    
    def remove_connection(self, connection_item: ConnectionGraphicsItem):
        """Remove a connection"""
        try:
            if connection_item in self.connection_items:
                self.connection_items.remove(connection_item)
            
            connection_uuid = connection_item.connection.uuid
            if connection_uuid in self.connection_map:
                del self.connection_map[connection_uuid]
        except Exception:
            pass
    
    def clear_all_connections(self):
        """Clear all connections"""
        self.connection_items.clear()
        self.connection_map.clear()
    
    def update_all_connections(self):
        """Update all connections"""
        for item in self.connection_items:
            item.update_connection()
    
    def get_connections_for_component(self, component_uuid: str) -> List[ConnectionGraphicsItem]:
        """Get connections for component"""
        result = []
        for item in self.connection_items:
            if item.connection.involves_component(component_uuid):
                result.append(item)
        return result
    
    def get_connections_for_port(self, port_uuid: str) -> List[ConnectionGraphicsItem]:
        """Get connections for port"""
        result = []
        for item in self.connection_items:
            if item.connection.involves_port(port_uuid):
                result.append(item)
        return result
    
    def highlight_connections_for_component(self, component_uuid: str, highlight: bool = True):
        """Highlight connections for component"""
        connections = self.get_connections_for_component(component_uuid)
        for item in connections:
            item.set_highlighted(highlight)
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        """Get connection statistics"""
        total_connections = len(self.connection_items)
        type_counts = {}
        
        for item in self.connection_items:
            conn_type = item.connection.connection_type.value
            type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
        
        return {
            'total_connections': total_connections,
            'by_type': type_counts,
            'selected_count': sum(1 for item in self.connection_items if item.is_selected_connection),
            'highlighted_count': sum(1 for item in self.connection_items if item.is_highlighted),
            'has_connections': total_connections > 0
        }