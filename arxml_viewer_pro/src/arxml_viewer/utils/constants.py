# src/arxml_viewer/utils/constants.py
"""
Application Constants - Central definition of application constants
"""

from enum import Enum
from typing import Dict, Tuple

class AppConstants:
    """Application-wide constants"""
    
    # Application info
    APP_NAME = "ARXML Viewer Pro"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "ARXML Viewer Pro Team"
    ORGANIZATION = "ARXML Tools"
    
    # File extensions
    SUPPORTED_EXTENSIONS = ['.arxml', '.xml']
    
    # Performance limits
    MAX_FILE_SIZE_MB = 500
    MAX_COMPONENTS_WARNING = 1000
    CACHE_SIZE_LIMIT = 100
    
    # UI constants
    DEFAULT_WINDOW_SIZE = (1400, 900)
    MIN_WINDOW_SIZE = (800, 600)
    
    # Colors for component types (RGB tuples)
    COMPONENT_COLORS = {
        'APPLICATION': (52, 152, 219),      # Blue
        'COMPOSITION': (155, 89, 182),      # Purple
        'SERVICE': (230, 126, 34),          # Orange
        'SENSOR_ACTUATOR': (46, 125, 50),   # Green
        'COMPLEX_DEVICE_DRIVER': (211, 47, 47)  # Red
    }
    
    # Port colors
    PORT_COLORS = {
        'PROVIDED': (46, 125, 50),    # Green
        'REQUIRED': (211, 47, 47),    # Red
        'PROVIDED_REQUIRED': (255, 193, 7)  # Amber
    }

class UIConstants:
    """UI-specific constants"""
    
    # Splitter proportions (as percentages)
    TREE_PANEL_WIDTH = 25
    DIAGRAM_PANEL_WIDTH = 50
    PROPERTIES_PANEL_WIDTH = 25
    
    # Graphics constants
    COMPONENT_MIN_WIDTH = 120
    COMPONENT_MIN_HEIGHT = 80
    COMPONENT_PORT_SIZE = 8
    CONNECTION_LINE_WIDTH = 2
    
    # Zoom limits
    MIN_ZOOM = 0.1
    MAX_ZOOM = 5.0
    ZOOM_STEP = 0.1
    
    # Animation timing (milliseconds)
    SELECTION_ANIMATION_DURATION = 200
    HOVER_ANIMATION_DURATION = 150

class FileConstants:
    """File handling constants"""
    
    # Recent files
    MAX_RECENT_FILES = 10
    
    # Export formats
    EXPORT_FORMATS = {
        'PNG': 'Portable Network Graphics (*.png)',
        'SVG': 'Scalable Vector Graphics (*.svg)',
        'PDF': 'Portable Document Format (*.pdf)',
        'JSON': 'JSON Data Export (*.json)'
    }
    
    # File filters for dialogs
    ARXML_FILTER = "ARXML Files (*.arxml *.xml);;All Files (*.*)"