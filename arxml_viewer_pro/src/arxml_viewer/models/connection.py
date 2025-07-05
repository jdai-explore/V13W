# src/arxml_viewer/models/connection.py
"""
Connection Models - AUTOSAR connection definitions
Enhanced with Day 5 connection path tracking
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
    """AUTOSAR Connection definition - Enhanced for Day 5"""
    connection_type: ConnectionType
    
    # Connection endpoints
    provider_endpoint: ConnectionEndpoint
    requester_endpoint: ConnectionEndpoint
    
    # Additional endpoints for multi-point connections
    additional_endpoints: List[ConnectionEndpoint] = Field(default_factory=list)
    
    # Rendering properties
    path_points: List[tuple] = Field(default_factory=list)  # Routing path
    
    # Day 5 - Enhanced properties
    is_highlighted: bool = False
    is_selected: bool = False
    animation_phase: float = 0.0
    
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
    
    def get_connected_component_uuids(self) -> List[str]:
        """Day 5 - Get all connected component UUIDs"""
        return list(set(ep.component_uuid for ep in self.all_endpoints))
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Day 5 - Get connection information for display"""
        return {
            'uuid': self.uuid,
            'name': self.short_name or 'Unnamed Connection',
            'type': self.connection_type.value,
            'description': self.desc,
            'provider': {
                'component': self.provider_endpoint.component_uuid,
                'port': self.provider_endpoint.port_uuid
            },
            'requester': {
                'component': self.requester_endpoint.component_uuid,
                'port': self.requester_endpoint.port_uuid
            },
            'component_count': len(self.get_connected_component_uuids())
        }
    
    def __str__(self) -> str:
        return f"Connection({self.short_name}, {self.connection_type.value})"
    
    def __repr__(self) -> str:
        return (f"Connection(uuid='{self.uuid}', short_name='{self.short_name}', "
                f"type='{self.connection_type.value}')")