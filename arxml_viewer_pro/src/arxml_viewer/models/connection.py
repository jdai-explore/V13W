# src/arxml_viewer/models/connection.py
"""
Connection Models - AUTOSAR connection definitions
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from .autosar import AutosarElement

class ConnectionType(str, Enum):
    """AUTOSAR connection types"""
    ASSEMBLY = "ASSEMBLY-SW-CONNECTOR"
    DELEGATION = "DELEGATION-SW-CONNECTOR"
    PASS_THROUGH = "PASS-THROUGH-SW-CONNECTOR"

class ConnectionEndpoint(BaseModel):
    """Connection endpoint definition"""
    component_uuid: str
    port_uuid: str
    
    def __str__(self) -> str:
        return f"Endpoint({self.component_uuid[:8]}:{self.port_uuid[:8]})"

class Connection(AutosarElement):
    """AUTOSAR Connection definition"""
    connection_type: ConnectionType
    
    # Connection endpoints
    provider_endpoint: ConnectionEndpoint
    requester_endpoint: ConnectionEndpoint
    
    # Additional endpoints for multi-point connections
    additional_endpoints: List[ConnectionEndpoint] = Field(default_factory=list)
    
    # Rendering properties
    path_points: List[tuple] = Field(default_factory=list)  # Routing path
    
    @validator('connection_type')
    def validate_connection_type(cls, v):
        """Validate connection type"""
        if isinstance(v, str):
            return ConnectionType(v)
        return v
    
    @property
    def all_endpoints(self) -> List[ConnectionEndpoint]:
        """Get all connection endpoints"""
        return [self.provider_endpoint, self.requester_endpoint] + self.additional_endpoints
    
    def involves_component(self, component_uuid: str) -> bool:
        """Check if connection involves a specific component"""
        return any(ep.component_uuid == component_uuid for ep in self.all_endpoints)
    
    def involves_port(self, port_uuid: str) -> bool:
        """Check if connection involves a specific port"""
        return any(ep.port_uuid == port_uuid for ep in self.all_endpoints)
    
    def __str__(self) -> str:
        return f"Connection({self.short_name}, {self.connection_type.value})"