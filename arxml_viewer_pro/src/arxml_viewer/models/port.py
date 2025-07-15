# src/arxml_viewer/models/port.py - FIXED VERSION
"""
Port Models - AUTOSAR port and interface definitions
FIXED: Removed AutosarElement and Interface imports
Replaced Pydantic with dataclass, simplified port type validation
Removed complex Interface class - keep only interface_ref string
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
import uuid

class PortType(str, Enum):
    """SIMPLIFIED AUTOSAR port types"""
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
    """AUTOSAR interface types - simplified"""
    SENDER_RECEIVER = "SENDER-RECEIVER-INTERFACE"
    CLIENT_SERVER = "CLIENT-SERVER-INTERFACE"
    TRIGGER = "TRIGGER-INTERFACE"
    MODE_SWITCH = "MODE-SWITCH-INTERFACE"
    NV_DATA = "NV-DATA-INTERFACE"

@dataclass
class Port:
    """
    FIXED AUTOSAR Port definition - SIMPLIFIED
    Removed AutosarElement inheritance, using basic dataclass
    Replaced Pydantic with dataclass
    Removed Interface class - keep only interface_ref string
    Simplified PortType enum - just PROVIDED, REQUIRED, PROVIDED_REQUIRED
    Removed complex validation - basic type checking only
    """
    
    # Essential properties
    short_name: str
    port_type: PortType
    desc: Optional[str] = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Interface reference - simplified to string only
    interface_ref: Optional[str] = None  # Reference to interface (string path)
    
    # Component reference
    component_uuid: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure port_type is proper enum
        if isinstance(self.port_type, str):
            try:
                self.port_type = PortType(self.port_type)
            except ValueError:
                # Fallback to REQUIRED if unknown type
                self.port_type = PortType.REQUIRED
    
    @property
    def is_provided(self) -> bool:
        """Check if this is a provided port"""
        return self.port_type.is_provided()
    
    @property
    def is_required(self) -> bool:
        """Check if this is a required port"""
        return self.port_type.is_required()
    
    @property
    def is_bidirectional(self) -> bool:
        """Check if this is a bidirectional port"""
        return self.port_type == PortType.PROVIDED_REQUIRED
    
    def get_interface_name(self) -> Optional[str]:
        """Get interface name from reference"""
        if not self.interface_ref:
            return None
        
        # Extract interface name from path (simple implementation)
        if '/' in self.interface_ref:
            return self.interface_ref.split('/')[-1]
        return self.interface_ref
    
    def set_interface_reference(self, interface_ref: str) -> None:
        """Set interface reference"""
        self.interface_ref = interface_ref
    
    def get_port_info(self) -> Dict[str, Any]:
        """Get port information for display"""
        return {
            'name': self.short_name,
            'type': self.port_type.value,
            'uuid': self.uuid,
            'description': self.desc,
            'interface_ref': self.interface_ref,
            'interface_name': self.get_interface_name(),
            'component_uuid': self.component_uuid,
            'is_provided': self.is_provided,
            'is_required': self.is_required,
            'is_bidirectional': self.is_bidirectional
        }
    
    def matches_interface(self, interface_name: str) -> bool:
        """Check if port matches interface name"""
        if not self.interface_ref:
            return False
        
        port_interface_name = self.get_interface_name()
        if not port_interface_name:
            return False
        
        return port_interface_name.lower() == interface_name.lower()
    
    def can_connect_to(self, other_port: 'Port') -> bool:
        """
        Check if this port can connect to another port
        Basic rule: provided ports connect to required ports
        """
        if not isinstance(other_port, Port):
            return False
        
        # Basic connection rules
        if self.is_provided and other_port.is_required:
            return True
        elif self.is_required and other_port.is_provided:
            return True
        elif self.is_bidirectional or other_port.is_bidirectional:
            return True
        
        return False
    
    def __str__(self) -> str:
        return f"Port({self.short_name}, {self.port_type.value})"
    
    def __repr__(self) -> str:
        return (f"Port(uuid='{self.uuid}', short_name='{self.short_name}', "
                f"type='{self.port_type.value}', interface='{self.interface_ref}')")
    
    def __eq__(self, other) -> bool:
        """Check equality based on UUID"""
        if not isinstance(other, Port):
            return False
        return self.uuid == other.uuid
    
    def __hash__(self) -> int:
        """Hash based on UUID"""
        return hash(self.uuid)

# SIMPLIFIED Interface class for backward compatibility
@dataclass
class Port:
    """
    FIXED: Allow UUID to be provided, only generate if not set
    """
    # ... other fields ...
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Only generate UUID if not provided
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
            
        # Ensure port_type is proper enum
        if isinstance(self.port_type, str):
            try:
                self.port_type = PortType(self.port_type)
            except ValueError:
                self.port_type = PortType.REQUIRED
    
    def get_interface_info(self) -> Dict[str, Any]:
        """Get interface information"""
        return {
            'name': self.short_name,
            'type': self.interface_type.value,
            'uuid': self.uuid,
            'description': self.desc,
            'methods_count': len(self.methods),
            'data_elements_count': len(self.data_elements)
        }
    
    def __str__(self) -> str:
        return f"Interface({self.short_name}, {self.interface_type.value})"
    
    def __repr__(self) -> str:
        return (f"Interface(uuid='{self.uuid}', short_name='{self.short_name}', "
                f"type='{self.interface_type.value}')")

# Export all classes for backward compatibility
__all__ = ['Port', 'PortType', 'Interface', 'InterfaceType']