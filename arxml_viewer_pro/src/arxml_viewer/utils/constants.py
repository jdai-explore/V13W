# src/arxml_viewer/utils/constants.py - SIMPLIFIED VERSION
"""
Application Constants - SIMPLIFIED - Removed unused constants
FIXES APPLIED per guide:
- Remove layout algorithm constants - no complex layouts
- Remove export format constants - no export functionality
- Remove Day 5 connection and breadcrumb constants
- Keep only: App info, basic window sizes, basic component colors
- Simplify significantly - maybe 20 lines total per component
"""

from typing import Dict, Tuple

class AppConstants:
    """Application-wide constants - SIMPLIFIED"""
    
    # Application info - keep essential only
    APP_NAME = "ARXML Viewer Pro"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "ARXML Viewer Pro Team"
    ORGANIZATION = "ARXML Tools"
    
    # File extensions - keep essential only
    SUPPORTED_EXTENSIONS = ['.arxml', '.xml']
    
    # Basic performance limits
    MAX_FILE_SIZE_MB = 500
    MAX_COMPONENTS_WARNING = 1000
    
    # Basic UI constants
    DEFAULT_WINDOW_SIZE = (1400, 900)
    MIN_WINDOW_SIZE = (800, 600)
    
    # SIMPLIFIED colors for component types (RGB tuples)
    COMPONENT_COLORS = {
        'APPLICATION': (52, 152, 219),      # Blue
        'COMPOSITION': (155, 89, 182),      # Purple
        'SERVICE': (230, 126, 34),          # Orange
        'SENSOR_ACTUATOR': (46, 125, 50),   # Green
        'COMPLEX_DEVICE_DRIVER': (211, 47, 47)  # Red
    }
    
    # SIMPLIFIED port colors
    PORT_COLORS = {
        'PROVIDED': (46, 125, 50),    # Green
        'REQUIRED': (211, 47, 47),    # Red
        'PROVIDED_REQUIRED': (255, 193, 7)  # Amber
    }

class UIConstants:
    """UI-specific constants - SIMPLIFIED"""
    
    # Splitter proportions (as percentages) - keep basic only
    TREE_PANEL_WIDTH = 25
    DIAGRAM_PANEL_WIDTH = 50
    PROPERTIES_PANEL_WIDTH = 25
    
    # SIMPLIFIED graphics constants
    COMPONENT_MIN_WIDTH = 120
    COMPONENT_MIN_HEIGHT = 80
    COMPONENT_PORT_SIZE = 8
    CONNECTION_LINE_WIDTH = 2
    
    # Basic zoom limits
    MIN_ZOOM = 0.1
    MAX_ZOOM = 5.0
    ZOOM_STEP = 0.1

class FileConstants:
    """File handling constants - SIMPLIFIED"""
    
    # Recent files - keep basic only
    MAX_RECENT_FILES = 10
    
    # File filters for dialogs - SIMPLIFIED
    ARXML_FILTER = "ARXML Files (*.arxml *.xml);;All Files (*.*)"

# REMOVED CLASSES (as per guide requirements):
# - LayoutConstants (removed layout algorithm constants)
# - ExportConstants (removed export format constants) 
# - AnimationConstants (removed Day 5 animation constants)
# - BreadcrumbConstants (removed Day 5 breadcrumb constants)
# - ConnectionConstants (removed Day 5 connection constants)

# Export essential constants only
__all__ = ['AppConstants', 'UIConstants', 'FileConstants']