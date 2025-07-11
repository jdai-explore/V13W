# src/arxml_viewer/models/connection.py - FIXED VERSION
"""
Connection Models - AUTOSAR connection definitions
FIXED: Removed AutosarElement inheritance, replaced Pydantic with dataclass
Removed Day 5 properties (animation, highlighting), simplified validation
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
import uuid

class ConnectionType(str, Enum):
    """AUTOSAR connection types"""
    ASSEMBLY = "ASSEMBLY-SW-CONNECTOR"
    DELEGATION = "DELEGATION-SW-CONNECTOR"
    PASS_THROUGH = "PASS-THROUGH-SW-CONNECTOR"

@dataclass
class ConnectionEndpoint:
    """
    SIMPLIFIED Connection endpoint definition
    Removed complex validation and helper methods
    Just component_uuid and port_uuid
    """
    component_uuid: str
    port_uuid: str
    
    def __str__(self) -> str:
        return f"Endpoint({self.component_uuid[:8]}:{self.port_uuid[:8]})"
    
    def __repr__(self) -> str:
        return f"ConnectionEndpoint(component='{self.component_uuid}', port='{self.port_uuid}')"
    
    def __eq__(self, other) -> bool:
        """Check equality"""
        if not isinstance(other, ConnectionEndpoint):
            return False
        return (self.component_uuid == other.component_uuid and 
                self.port_uuid == other.port_uuid)
    
    def __hash__(self) -> int:
        """Hash for use in sets/dicts"""
        return hash((self.component_uuid, self.port_uuid))

@dataclass
class Connection:
    """
    FIXED AUTOSAR Connection definition - SIMPLIFIED
    Removed AutosarElement inheritance, using basic dataclass
    Replaced Pydantic with dataclass
    Removed Day 5 properties: is_highlighted, is_selected, animation_phase
    Simplified ConnectionEndpoint - just component_uuid and port_uuid
    Removed complex validation and helper methods
    """
    
    # Essential properties
    short_name: str
    connection_type: ConnectionType
    desc: Optional[str] = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Connection endpoints - simplified
    provider_endpoint: ConnectionEndpoint
    requester_endpoint: ConnectionEndpoint
    
    # Additional endpoints for multi-point connections (simplified)
    additional_endpoints: List[ConnectionEndpoint] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure connection_type is proper enum
        if isinstance(self.connection_type, str):
            try:
                self.connection_type = ConnectionType(self.connection_type)
            except ValueError:
                # Fallback to ASSEMBLY if unknown type
                self.connection_type = ConnectionType.ASSEMBLY
        
        # Ensure endpoints are proper objects
        if isinstance(self.provider_endpoint, dict):
            self.provider_endpoint = ConnectionEndpoint(**self.provider_endpoint)
        if isinstance(self.requester_endpoint, dict):
            self.requester_endpoint = ConnectionEndpoint(**self.requester_endpoint)
    
    @property
    def all_endpoints(self) -> List[ConnectionEndpoint]:
        """Get all connection endpoints"""
        return [self.provider_endpoint, self.requester_endpoint] + self.additional_endpoints
    
    def involves_component(self, component_uuid: str) -> bool:
        """Check if connection involves a specific component"""
        try:
            return any(ep.component_uuid == component_uuid for ep in self.all_endpoints)
        except Exception:
            return False
    
    def involves_port(self, port_uuid: str) -> bool:
        """Check if connection involves a specific port"""
        try:
            return any(ep.port_uuid == port_uuid for ep in self.all_endpoints)
        except Exception:
            return False
    
    def get_connected_component_uuids(self) -> List[str]:
        """Get all connected component UUIDs"""
        try:
            return list(set(ep.component_uuid for ep in self.all_endpoints))
        except Exception:
            return []
    
    def get_connected_port_uuids(self) -> List[str]:
        """Get all connected port UUIDs"""
        try:
            return list(set(ep.port_uuid for ep in self.all_endpoints))
        except Exception:
            return []
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for display"""
        try:
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
                'component_count': len(self.get_connected_component_uuids()),
                'port_count': len(self.get_connected_port_uuids()),
                'additional_endpoints': len(self.additional_endpoints)
            }
        except Exception:
            return {
                'uuid': self.uuid,
                'name': self.short_name or 'Unnamed Connection',
                'type': self.connection_type.value if hasattr(self.connection_type, 'value') else str(self.connection_type),
                'description': self.desc,
                'error': 'Failed to get connection details'
            }
    
    def is_valid(self) -> bool:
        """Check if connection is valid (has required endpoints)"""
        try:
            return (self.provider_endpoint is not None and 
                   self.requester_endpoint is not None and
                   self.provider_endpoint.component_uuid and
                   self.provider_endpoint.port_uuid and
                   self.requester_endpoint.component_uuid and
                   self.requester_endpoint.port_uuid)
        except Exception:
            return False
    
    def is_self_connection(self) -> bool:
        """Check if connection is within the same component"""
        try:
            return (self.provider_endpoint.component_uuid == 
                   self.requester_endpoint.component_uuid)
        except Exception:
            return False
    
    def get_connection_direction(self) -> str:
        """Get connection direction description"""
        try:
            provider_comp = self.provider_endpoint.component_uuid[:8]
            requester_comp = self.requester_endpoint.component_uuid[:8]
            
            if self.is_self_connection():
                return f"Internal ({provider_comp})"
            else:
                return f"{provider_comp} → {requester_comp}"
        except Exception:
            return "Unknown direction"
    
    def add_endpoint(self, endpoint: ConnectionEndpoint) -> None:
        """Add additional endpoint to connection"""
        if endpoint not in self.additional_endpoints:
            self.additional_endpoints.append(endpoint)
    
    def remove_endpoint(self, endpoint: ConnectionEndpoint) -> bool:
        """Remove additional endpoint from connection"""
        try:
            if endpoint in self.additional_endpoints:
                self.additional_endpoints.remove(endpoint)
                return True
            return False
        except Exception:
            return False
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            'type': self.connection_type.value,
            'endpoint_count': len(self.all_endpoints),
            'component_count': len(self.get_connected_component_uuids()),
            'port_count': len(self.get_connected_port_uuids()),
            'is_valid': self.is_valid(),
            'is_self_connection': self.is_self_connection(),
            'direction': self.get_connection_direction()
        }
    
    def __str__(self) -> str:
        return f"Connection({self.short_name}, {self.connection_type.value})"
    
    def __repr__(self) -> str:
        return (f"Connection(uuid='{self.uuid}', short_name='{self.short_name}', "
                f"type='{self.connection_type.value}')")
    
    def __eq__(self, other) -> bool:
        """Check equality based on UUID"""
        if not isinstance(other, Connection):
            return False
        return self.uuid == other.uuid
    
    def __hash__(self) -> int:
        """Hash based on UUID"""
        return hash(self.uuid)

# Export all classes
__all__ = ['Connection', 'ConnectionType', 'ConnectionEndpoint']