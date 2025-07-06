# src/arxml_viewer/models/package.py - FIXED VERSION
"""
Package Model - FIXED VERSION with correct path calculation
Represents an AUTOSAR package with proper path handling
"""

import uuid
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from .component import Component
from ..utils.logger import get_logger

@dataclass
class Package:
    """
    AUTOSAR Package representation - FIXED VERSION
    Contains components and sub-packages with proper path calculation
    """
    
    short_name: str
    full_path: str = ""
    desc: Optional[str] = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Content
    components: List[Component] = field(default_factory=list)
    sub_packages: List['Package'] = field(default_factory=list)
    
    # Parent reference
    parent_package: Optional['Package'] = None
    
    def __post_init__(self):
        """Initialize package after creation"""
        self.logger = get_logger(__name__)
        
        # Fix full_path if not provided
        if not self.full_path:
            self.full_path = f"/{self.short_name}"
        
        # Ensure full_path starts with /
        if not self.full_path.startswith('/'):
            self.full_path = f"/{self.full_path}"
    
    @property
    def path_segments(self) -> List[str]:
        """Get path segments - FIXED calculation"""
        if not self.full_path:
            return [self.short_name]
        
        # Remove leading slash and split
        path = self.full_path.lstrip('/')
        if not path:
            return []
        
        segments = path.split('/')
        # Filter out empty segments
        return [seg for seg in segments if seg]
    
    @property
    def depth(self) -> int:
        """Get package depth in hierarchy - FIXED calculation"""
        # Depth is the number of path segments
        return len(self.path_segments)
    
    @property
    def package_path(self) -> str:
        """Get package path (alias for full_path)"""
        return self.full_path
    
    def add_component(self, component: Component):
        """Add component to package"""
        try:
            if component not in self.components:
                self.components.append(component)
                # Set component's package reference
                component.package_path = self.full_path
                self.logger.debug(f"Added component {component.short_name} to package {self.short_name}")
        except Exception as e:
            self.logger.error(f"Failed to add component: {e}")
    
    def add_sub_package(self, sub_package: 'Package'):
        """Add sub-package"""
        try:
            if sub_package not in self.sub_packages:
                self.sub_packages.append(sub_package)
                sub_package.parent_package = self
                
                # Fix sub-package path
                if not sub_package.full_path.startswith(self.full_path):
                    sub_package.full_path = f"{self.full_path}/{sub_package.short_name}"
                
                self.logger.debug(f"Added sub-package {sub_package.short_name} to {self.short_name}")
        except Exception as e:
            self.logger.error(f"Failed to add sub-package: {e}")
    
    def get_all_components(self, recursive: bool = False) -> List[Component]:
        """Get all components, optionally recursive"""
        components = self.components.copy()
        
        if recursive:
            for sub_pkg in self.sub_packages:
                components.extend(sub_pkg.get_all_components(recursive=True))
        
        return components
    
    def get_all_sub_packages(self, recursive: bool = False) -> List['Package']:
        """Get all sub-packages, optionally recursive"""
        packages = self.sub_packages.copy()
        
        if recursive:
            for sub_pkg in self.sub_packages:
                packages.extend(sub_pkg.get_all_sub_packages(recursive=True))
        
        return packages
    
    def find_component_by_name(self, name: str, recursive: bool = True) -> Optional[Component]:
        """Find component by name"""
        # Search direct components
        for comp in self.components:
            if comp.short_name == name:
                return comp
        
        # Search sub-packages if recursive
        if recursive:
            for sub_pkg in self.sub_packages:
                found = sub_pkg.find_component_by_name(name, recursive=True)
                if found:
                    return found
        
        return None
    
    def find_component_by_uuid(self, component_uuid: str, recursive: bool = True) -> Optional[Component]:
        """Find component by UUID"""
        # Search direct components
        for comp in self.components:
            if comp.uuid == component_uuid:
                return comp
        
        # Search sub-packages if recursive
        if recursive:
            for sub_pkg in self.sub_packages:
                found = sub_pkg.find_component_by_uuid(component_uuid, recursive=True)
                if found:
                    return found
        
        return None
    
    def get_component_count(self, recursive: bool = False) -> int:
        """Get total component count"""
        count = len(self.components)
        
        if recursive:
            for sub_pkg in self.sub_packages:
                count += sub_pkg.get_component_count(recursive=True)
        
        return count
    
    def get_package_statistics(self) -> Dict[str, Any]:
        """Get package statistics"""
        return {
            'name': self.short_name,
            'path': self.full_path,
            'depth': self.depth,
            'components': len(self.components),
            'sub_packages': len(self.sub_packages),
            'total_components': self.get_component_count(recursive=True),
            'total_sub_packages': len(self.get_all_sub_packages(recursive=True))
        }
    
    def __str__(self) -> str:
        return f"Package({self.short_name}, {self.full_path})"
    
    def __repr__(self) -> str:
        return f"Package(short_name='{self.short_name}', full_path='{self.full_path}', components={len(self.components)}, sub_packages={len(self.sub_packages)})"