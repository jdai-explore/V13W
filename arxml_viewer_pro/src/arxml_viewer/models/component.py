# src/arxml_viewer/models/component.py - FIXED VERSION
"""
Component Models - FIXED VERSION with complete dataclass definition
FIXES APPLIED:
- Complete dataclass definition with all required fields
- Proper UUID field initialization  
- Fixed __post_init__ method
- Corrected field defaults and types
"""

from typing import Optional, List
from enum import Enum
from dataclasses import dataclass, field
import uuid

# Forward reference to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port import Port
    from .connection import Connection

class ComponentType(str, Enum):
    """AUTOSAR component types"""
    APPLICATION = "APPLICATION-SW-COMPONENT-TYPE"
    COMPOSITION = "COMPOSITION-SW-COMPONENT-TYPE" 
    SERVICE = "SERVICE-SW-COMPONENT-TYPE"
    SENSOR_ACTUATOR = "SENSOR-ACTUATOR-SW-COMPONENT-TYPE"
    COMPLEX_DEVICE_DRIVER = "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE"

class ComponentBehavior(str, Enum):
    """Component behavior types"""
    ATOMIC = "ATOMIC"
    COMPOSITE = "COMPOSITE"

@dataclass
class Component:
    """
    FIXED Component definition with complete dataclass fields
    """
    
    # Required fields
    short_name: str
    component_type: ComponentType
    
    # Optional fields with defaults
    desc: Optional[str] = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    package_path: Optional[str] = None
    behavior: ComponentBehavior = ComponentBehavior.ATOMIC
    
    # Port collections with proper defaults
    provided_ports: List['Port'] = field(default_factory=list)
    required_ports: List['Port'] = field(default_factory=list)
    
    # For composition components - sub-components
    components: List['Component'] = field(default_factory=list)
    
    # Connection information
    connections: List['Connection'] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Only generate UUID if not provided
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
            
        # Ensure component_type is proper enum
        if isinstance(self.component_type, str):
            try:
                self.component_type = ComponentType(self.component_type)
            except ValueError:
                self.component_type = ComponentType.APPLICATION
    
    @property
    def all_ports(self) -> List['Port']:
        """Get all ports (provided + required)"""
        return self.provided_ports + self.required_ports
    
    @property
    def is_composition(self) -> bool:
        """Check if component is a composition"""
        return self.component_type == ComponentType.COMPOSITION
    
    @property
    def port_count(self) -> int:
        """Get total port count"""
        return len(self.provided_ports) + len(self.required_ports)
    
    def get_port_by_name(self, name: str) -> Optional['Port']:
        """Find port by short name"""
        for port in self.all_ports:
            if hasattr(port, 'short_name') and port.short_name == name:
                return port
        return None
    
    def get_port_by_uuid(self, port_uuid: str) -> Optional['Port']:
        """Find port by UUID"""
        for port in self.all_ports:
            if hasattr(port, 'uuid') and port.uuid == port_uuid:
                return port
        return None
    
    def add_port(self, port: 'Port') -> None:
        """Add a port to the component"""
        try:
            # Set component reference
            if hasattr(port, 'component_uuid'):
                port.component_uuid = self.uuid
            
            # Add to appropriate list based on port type
            if hasattr(port, 'is_provided') and port.is_provided:
                if port not in self.provided_ports:
                    self.provided_ports.append(port)
            else:
                if port not in self.required_ports:
                    self.required_ports.append(port)
        except Exception:
            # Fallback - just add to required ports if we can't determine type
            if port not in self.required_ports:
                self.required_ports.append(port)
    
    def remove_port(self, port: 'Port') -> bool:
        """Remove a port from the component"""
        try:
            if port in self.provided_ports:
                self.provided_ports.remove(port)
                return True
            elif port in self.required_ports:
                self.required_ports.remove(port)
                return True
            return False
        except Exception:
            return False
    
    def add_sub_component(self, component: 'Component') -> None:
        """Add a sub-component (for compositions)"""
        if component not in self.components:
            self.components.append(component)
    
    def get_component_statistics(self) -> dict:
        """Get component statistics"""
        return {
            'name': self.short_name,
            'type': self.component_type.value,
            'port_count': self.port_count,
            'provided_ports': len(self.provided_ports),
            'required_ports': len(self.required_ports),
            'is_composition': self.is_composition,
            'sub_components': len(self.components) if self.is_composition else 0,
            'connections': len(self.connections) if self.connections else 0
        }
    
    def __str__(self) -> str:
        return f"Component({self.short_name}, {self.component_type.value})"
    
    def __repr__(self) -> str:
        return (f"Component(uuid='{self.uuid}', short_name='{self.short_name}', "
                f"type='{self.component_type.value}', ports={self.port_count})")
    
    def __eq__(self, other) -> bool:
        """Check equality based on UUID"""
        if not isinstance(other, Component):
            return False
        return self.uuid == other.uuid
    
    def __hash__(self) -> int:
        """Hash based on UUID"""
        return hash(self.uuid)

# Export classes
__all__ = ['Component', 'ComponentType', 'ComponentBehavior']