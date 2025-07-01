"""
ARXML Viewer Pro - Professional AUTOSAR ARXML Viewer
Copyright (c) 2025 ARXML Viewer Pro Team
"""

__version__ = "1.0.0"
__author__ = "Jayadev Meka"
__email__ = "jd@miraiflow.tech"
__description__ = "Professional AUTOSAR ARXML file viewer for automotive engineers"

# Import main components for easy access (only Day 1 components)
try:
    from .parsers.arxml_parser import ARXMLParser
    from .models.component import Component, ComponentType
    from .models.port import Port, PortType
    from .models.connection import Connection
    from .models.package import Package
    from .config import ConfigManager
    
    __all__ = [
        "ARXMLParser", 
        "Component",
        "ComponentType",
        "Port",
        "PortType", 
        "Connection",
        "Package",
        "ConfigManager",
    ]
except ImportError:
    # GUI components not yet implemented - that's OK for Day 1
    __all__ = []