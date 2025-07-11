"""
ARXML Viewer Pro - Professional AUTOSAR ARXML Viewer
Copyright (c) 2025 ARXML Viewer Pro Team

FIXED VERSION: Removed imports to deleted modules
Only imports essential working components
"""

__version__ = "1.0.0"
__author__ = "Jayadev Meka"
__email__ = "jd@miraiflow.tech"
__description__ = "Professional AUTOSAR ARXML file viewer for automotive engineers"

# Import only essential components that exist and work
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
    
    print("✅ ARXML Viewer Pro core components loaded successfully")
    
except ImportError as e:
    # If core components fail to import, provide minimal fallback
    print(f"⚠️ Some core components failed to import: {e}")
    __all__ = []