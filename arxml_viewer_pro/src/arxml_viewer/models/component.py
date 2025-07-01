# src/arxml_viewer/models/component.py
"""
Component Models - AUTOSAR software component definitions
"""

from typing import Optional, List, Dict, Set
from enum import Enum
from pydantic import BaseModel, Field, validator
from .autosar import AutosarElement
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

class Component(AutosarElement):
    """AUTOSAR Software Component model"""
    component_type: ComponentType
    behavior: ComponentBehavior = ComponentBehavior.ATOMIC
    
    # Ports
    provided_ports: List[Port] = Field(default_factory=list)
    required_ports: List[Port] = Field(default_factory=list)
    
    # Composition-specific
    components: List['Component'] = Field(default_factory=list)  # Sub-components
    connections: List[str] = Field(default_factory=list)  # Connection UUIDs
    
    # Metadata
    package_path: Optional[str] = None
    xml_path: Optional[str] = None  # XPath in original XML
    
    # Rendering properties
    position: Optional[tuple] = None  # (x, y) position for layout
    size: Optional[tuple] = None      # (width, height) for rendering
    
    @validator('component_type')
    def validate_component_type(cls, v):
        """Validate component type"""
        if isinstance(v, str):
            return ComponentType(v)
        return v
    
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
    
    def add_port(self, port: Port) -> None:
        """Add a port to the component"""
        if port.port_type.is_provided():
            self.provided_ports.append(port)
        else:
            self.required_ports.append(port)
    
    def __str__(self) -> str:
        return f"Component({self.short_name}, {self.component_type.value})"
    
    def __repr__(self) -> str:
        return (f"Component(uuid='{self.uuid}', short_name='{self.short_name}', "
                f"type='{self.component_type.value}', ports={self.port_count})")