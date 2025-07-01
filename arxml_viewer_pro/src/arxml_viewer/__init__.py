"""
ARXML Viewer Pro - Professional AUTOSAR ARXML Viewer
Copyright (c) 2025 ARXML Viewer Pro Team
"""

__version__ = "1.0.0"
__author__ = "Jayadev Meka"
__email__ = "jd@miraiflow.tech"
__description__ = "Professional AUTOSAR ARXML file viewer for automotive engineers"

# Import main components for easy access
from .core.application import ARXMLViewerApplication
from .parsers.arxml_parser import ARXMLParser
from .models.component import Component, ComponentType
from .models.port import Port, PortType
from .models.connection import Connection
from .models.package import Package

__all__ = [
    "ARXMLViewerApplication",
    "ARXMLParser", 
    "Component",
    "ComponentType",
    "Port",
    "PortType", 
    "Connection",
    "Package",
]