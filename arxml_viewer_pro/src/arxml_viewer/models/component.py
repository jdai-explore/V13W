# src/arxml_viewer/models/component.py - FIXED VERSION
"""
Component Models - AUTOSAR software component definitions
FIXED: Removed autosar.py base class, replaced Pydantic with dataclass
Simplified validation and removed rendering properties from data model
"""

from typing import Optional, List
from enum import Enum
from dataclasses import dataclass, field
import uuid

# Import Port from same package (will be fixed too)
from .port import Port

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
    FIXED AUTOSAR Software Component model - SIMPLIFIED
    Removed AutosarElement inheritance, using basic dataclass
    Removed Pydantic validation complexity
    Removed rendering properties (position, size) - handle in graphics layer
    """
    
    # Essential properties only
    short_name: str
    component_type: ComponentType
    behavior: ComponentBehavior = ComponentBehavior.ATOMIC
    desc: Optional[str] = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Ports - simplified port management (basic lists only)
    provided_ports: List[Port] = field(default_factory=list)
    required_ports: List[Port] = field(default_factory=list)
    
    # Composition-specific - simplified
    components: List['Component'] = field(default_factory=list)  # Sub-components
    connections: List[str] = field(default_factory=list)  # Connection UUIDs
    
    # Metadata - keep essential only
    package_path: Optional[str] = None
    xml_path: Optional[str] = None  # XPath in original XML
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure component_type is proper enum
        if isinstance(self.component_type, str):
            try:
                self.component_type = ComponentType(self.component_type)
            except ValueError:
                # Fallback to APPLICATION if unknown type
                self.component_type = ComponentType.APPLICATION
    
    @property
    def all_ports(self) -> List[Port]:
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
    
    def get_port_by_name(self, name: str) -> Optional[Port]:
        """Find port by short name"""
        for port in self.all_ports:
            if port.short_name == name:
                return port
        return None
    
    def get_port_by_uuid(self, port_uuid: str) -> Optional[Port]:
        """Find port by UUID"""
        for port in self.all_ports:
            if port.uuid == port_uuid:
                return port
        return None
    
    def add_port(self, port: Port) -> None:
        """Add a port to the component"""
        try:
            # Set component reference
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
    
    def remove_port(self, port: Port) -> bool:
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