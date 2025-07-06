# src/arxml_viewer/gui/graphics/__init__.py - CORRECTED PyQt5 VERSION
"""
Graphics module initialization - CORRECTED for PyQt5 compatibility
Ensures proper import handling with correct PyQt5 classes
"""

# Import required Qt components with CORRECT PyQt5 class names
try:
    from PyQt5.QtWidgets import (
        QGraphicsPolygonItem,  # CORRECTED: This is the right class name
        QGraphicsEllipseItem, 
        QGraphicsRectItem,
        QGraphicsLineItem,
        QGraphicsPathItem,
        QGraphicsTextItem,
        QGraphicsItem
    )
    from PyQt5.QtCore import Qt, QPointF, QRectF
    from PyQt5.QtGui import QPolygonF, QPen, QBrush, QColor
    QT_GRAPHICS_AVAILABLE = True
    print("✅ Qt Graphics components imported successfully")
except ImportError as e:
    print(f"⚠️ Qt Graphics imports failed: {e}")
    QT_GRAPHICS_AVAILABLE = False
    
    # Create minimal fallbacks for missing Qt classes
    class QGraphicsPolygonItem:
        def __init__(self, *args, **kwargs):
            pass
    
    class QGraphicsEllipseItem:
        def __init__(self, *args, **kwargs):
            pass
    
    class QGraphicsRectItem:
        def __init__(self, *args, **kwargs):
            pass
    
    class QGraphicsLineItem:
        def __init__(self, *args, **kwargs):
            pass
    
    class QGraphicsPathItem:
        def __init__(self, *args, **kwargs):
            pass
    
    class QGraphicsTextItem:
        def __init__(self, *args, **kwargs):
            pass
    
    class QGraphicsItem:
        def __init__(self, *args, **kwargs):
            pass
    
    class QPolygonF:
        def __init__(self, *args, **kwargs):
            pass
    
    class QPointF:
        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y
    
    class QRectF:
        def __init__(self, x=0, y=0, w=0, h=0):
            pass

# Safe import handling for graphics components
try:
    from .graphics_scene import ComponentDiagramScene, ComponentGraphicsItem
    GRAPHICS_SCENE_AVAILABLE = True
    print("✅ Graphics scene components imported")
except ImportError as e:
    print(f"⚠️ Graphics scene import failed: {e}")
    GRAPHICS_SCENE_AVAILABLE = False
    
    # Create fallback classes
    class ComponentDiagramScene:
        def __init__(self, *args, **kwargs):
            self.components = {}
            self.connections = []
        
        def clear_scene(self):
            pass
        
        def load_packages(self, packages, connections=None):
            pass
        
        def addItem(self, item):
            pass
        
        def removeItem(self, item):
            pass
    
    class ComponentGraphicsItem:
        def __init__(self, component, *args, **kwargs):
            self.component = component

try:
    from .connection_graphics import ConnectionManager, ConnectionGraphicsItem
    CONNECTION_GRAPHICS_AVAILABLE = True
    print("✅ Connection graphics components imported")
except ImportError as e:
    print(f"⚠️ Connection graphics import failed: {e}")
    CONNECTION_GRAPHICS_AVAILABLE = False
    
    # Create fallback classes
    class ConnectionManager:
        def __init__(self, graphics_scene):
            self.graphics_scene = graphics_scene
            self.connection_items = []
        
        def add_connection(self, connection, start_port, end_port):
            # Create a simple fallback connection item
            connection_item = ConnectionGraphicsItem(connection, start_port, end_port)
            self.connection_items.append(connection_item)
            return connection_item
        
        def clear_all_connections(self):
            self.connection_items.clear()
        
        def get_connection_statistics(self):
            return {
                'total_connections': len(self.connection_items), 
                'by_type': {}, 
                'has_connections': len(self.connection_items) > 0
            }
        
        def highlight_connections_for_component(self, component_uuid, highlight=True):
            pass
        
        def get_connections_for_component(self, component_uuid):
            return []
        
        def get_connections_for_port(self, port_uuid):
            return []
    
    class ConnectionGraphicsItem:
        def __init__(self, connection, start_port, end_port):
            self.connection = connection
            self.start_port_item = start_port
            self.end_port_item = end_port
            self.is_selected_connection = False
            self.is_highlighted = False
        
        def set_selected(self, selected):
            self.is_selected_connection = selected
        
        def set_highlighted(self, highlighted):
            self.is_highlighted = highlighted
        
        def update_connection(self):
            pass

try:
    from .port_graphics import EnhancedPortGraphicsItem
    ENHANCED_PORTS_AVAILABLE = True
    print("✅ Enhanced port graphics components imported")
except ImportError as e:
    print(f"⚠️ Enhanced port graphics import failed: {e}")
    ENHANCED_PORTS_AVAILABLE = False
    
    # Create fallback class
    class EnhancedPortGraphicsItem:
        def __init__(self, port, parent=None):
            self.port = port
            self.parent_component = parent
        
        def get_port_center_scene_pos(self):
            return QPointF(0, 0)
        
        def highlight_port(self, highlight_type="selection"):
            pass
        
        def clear_highlight(self):
            pass

# Export all classes and availability flags
__all__ = [
    'ComponentDiagramScene', 'ComponentGraphicsItem',
    'ConnectionManager', 'ConnectionGraphicsItem', 
    'EnhancedPortGraphicsItem',
    'QGraphicsPolygonItem', 'QGraphicsEllipseItem', 'QGraphicsRectItem',  # Correct PyQt5 class names
    'QGraphicsLineItem', 'QGraphicsPathItem', 'QGraphicsTextItem', 'QGraphicsItem',
    'QPolygonF', 'QPointF', 'QRectF',
    'GRAPHICS_SCENE_AVAILABLE', 'CONNECTION_GRAPHICS_AVAILABLE', 'ENHANCED_PORTS_AVAILABLE',
    'QT_GRAPHICS_AVAILABLE'
]

print(f"🔧 Graphics module initialized - QT_GRAPHICS: {QT_GRAPHICS_AVAILABLE}, "
      f"SCENE: {GRAPHICS_SCENE_AVAILABLE}, CONNECTIONS: {CONNECTION_GRAPHICS_AVAILABLE}, "
      f"PORTS: {ENHANCED_PORTS_AVAILABLE}")