# src/arxml_viewer/models/port.py
"""
Port Models - AUTOSAR port and interface definitions
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from .autosar import AutosarElement

class PortType(str, Enum):
    """AUTOSAR port types"""
    PROVIDED = "P-PORT-PROTOTYPE"
    REQUIRED = "R-PORT-PROTOTYPE"
    PROVIDED_REQUIRED = "PR-PORT-PROTOTYPE"
    
    def is_provided(self) -> bool:
        """Check if port provides interfaces"""
        return self in [PortType.PROVIDED, PortType.PROVIDED_REQUIRED]
    
    def is_required(self) -> bool:
        """Check if port requires interfaces"""
        return self in [PortType.REQUIRED, PortType.PROVIDED_REQUIRED]

class InterfaceType(str, Enum):
    """AUTOSAR interface types"""
    SENDER_RECEIVER = "SENDER-RECEIVER-INTERFACE"
    CLIENT_SERVER = "CLIENT-SERVER-INTERFACE"
    TRIGGER = "TRIGGER-INTERFACE"
    MODE_SWITCH = "MODE-SWITCH-INTERFACE"
    NV_DATA = "NV-DATA-INTERFACE"

class Interface(AutosarElement):
    """AUTOSAR Interface definition"""
    interface_type: InterfaceType
    methods: List[str] = Field(default_factory=list)
    data_elements: List[str] = Field(default_factory=list)
    
class Port(AutosarElement):
    """AUTOSAR Port definition"""
    port_type: PortType
    interface_ref: Optional[str] = None  # Reference to interface
    interface: Optional[Interface] = None  # Resolved interface
    
    # Component reference
    component_uuid: Optional[str] = None
    
    # Rendering properties
    position: Optional[tuple] = None  # Relative position on component
    
    @validator('port_type')
    def validate_port_type(cls, v):
        """Validate port type"""
        if isinstance(v, str):
            return PortType(v)
        return v
    
    @property
    def is_provided(self) -> bool:
        """Check if this is a provided port"""
        return self.port_type.is_provided()
    
    @property
    def is_required(self) -> bool:
        """Check if this is a required port"""
        return self.port_type.is_required()
    
    def __str__(self) -> str:
        return f"Port({self.short_name}, {self.port_type.value})"