# src/arxml_viewer/models/package.py
"""
Package Models - AUTOSAR package hierarchy
"""

from typing import Optional, List, Dict, Set
from pydantic import BaseModel, Field, validator
from .autosar import AutosarElement
from .component import Component

class Package(AutosarElement):
    """AUTOSAR Package definition"""
    # Hierarchy
    parent_package: Optional['Package'] = None
    sub_packages: List['Package'] = Field(default_factory=list)
    
    # Contents
    components: List[Component] = Field(default_factory=list)
    interfaces: List[str] = Field(default_factory=list)  # Interface UUIDs
    
    # Metadata
    full_path: Optional[str] = None  # Full package path
    
    @property
    def path_segments(self) -> List[str]:
        """Get package path as segments"""
        if self.full_path:
            return self.full_path.split('/')
        return []
    
    @property
    def depth(self) -> int:
        """Get package depth in hierarchy"""
        return len(self.path_segments)
    
    def add_component(self, component: Component) -> None:
        """Add a component to this package"""
        component.package_path = self.full_path
        self.components.append(component)
    
    def get_all_components(self, recursive: bool = False) -> List[Component]:
        """Get all components in package"""
        components = self.components.copy()
        if recursive:
            for sub_pkg in self.sub_packages:
                components.extend(sub_pkg.get_all_components(recursive=True))
        return components
    
    def find_component_by_name(self, name: str, recursive: bool = False) -> Optional[Component]:
        """Find component by short name"""
        for component in self.components:
            if component.short_name == name:
                return component
        
        if recursive:
            for sub_pkg in self.sub_packages:
                result = sub_pkg.find_component_by_name(name, recursive=True)
                if result:
                    return result
        return None
    
    def __str__(self) -> str:
        return f"Package({self.short_name})"

# Update forward references
Component.model_rebuild()
Package.model_rebuild()