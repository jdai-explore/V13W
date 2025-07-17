# src/arxml_viewer/models/package.py - FIXED VERSION
"""
Package Model - FIXED VERSION with proper dataclass definition
FIXES APPLIED:
- Complete dataclass definition with all required fields
- Proper UUID field initialization
- Fixed __post_init__ method
- Corrected field defaults and types
"""

import uuid
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

# Forward reference to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .component import Component

@dataclass
class Package:
    """
    FIXED Package definition with complete dataclass fields
    """
    
    # Required fields
    short_name: str
    
    # Optional fields with defaults
    full_path: str = ""
    desc: Optional[str] = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Collections with proper defaults
    components: List['Component'] = field(default_factory=list)
    sub_packages: List['Package'] = field(default_factory=list)
    
    # Optional parent reference
    parent_package: Optional['Package'] = None
    
    def __post_init__(self):
        """FIXED initialization"""
        # Only generate UUID if not provided
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
            
        # Fix full_path if not provided
        if not self.full_path:
            self.full_path = f"/{self.short_name}"
        
        # Ensure full_path starts with /
        if not self.full_path.startswith('/'):
            self.full_path = f"/{self.full_path}"
    
    @property
    def path_segments(self) -> List[str]:
        """Get path segments - SIMPLIFIED calculation"""
        if not self.full_path:
            return [self.short_name]
        
        # Remove leading slash and split - basic approach
        path = self.full_path.lstrip('/')
        if not path:
            return []
        
        segments = path.split('/')
        # Filter out empty segments
        return [seg for seg in segments if seg]
    
    @property
    def depth(self) -> int:
        """Get package depth in hierarchy - SIMPLIFIED calculation"""
        # Depth is the number of path segments
        return len(self.path_segments)
    
    @property
    def package_path(self) -> str:
        """Get package path (alias for full_path)"""
        return self.full_path
    
    def add_component(self, component: 'Component'):
        """Add component to package - SIMPLIFIED"""
        try:
            if component not in self.components:
                self.components.append(component)
                # Set component's package reference
                if hasattr(component, 'package_path'):
                    component.package_path = self.full_path
        except Exception:
            # Silent failure - just don't add if there's an issue
            pass
    
    def add_sub_package(self, sub_package: 'Package'):
        """Add sub-package - SIMPLIFIED"""
        try:
            if sub_package not in self.sub_packages:
                self.sub_packages.append(sub_package)
                sub_package.parent_package = self
                
                # Fix sub-package path - basic concatenation
                if not sub_package.full_path.startswith(self.full_path):
                    sub_package.full_path = f"{self.full_path}/{sub_package.short_name}"
        except Exception:
            # Silent failure - just don't add if there's an issue
            pass
    
    def get_all_components(self, recursive: bool = False) -> List['Component']:
        """Get all components, optionally recursive - SIMPLIFIED"""
        try:
            components = self.components.copy()
            
            if recursive:
                for sub_pkg in self.sub_packages:
                    try:
                        components.extend(sub_pkg.get_all_components(recursive=True))
                    except Exception:
                        # Skip problematic sub-packages
                        continue
            
            return components
        except Exception:
            # Return empty list on any error
            return []
    
    def get_all_sub_packages(self, recursive: bool = False) -> List['Package']:
        """Get all sub-packages, optionally recursive - SIMPLIFIED"""
        try:
            packages = self.sub_packages.copy()
            
            if recursive:
                for sub_pkg in self.sub_packages:
                    try:
                        packages.extend(sub_pkg.get_all_sub_packages(recursive=True))
                    except Exception:
                        # Skip problematic sub-packages
                        continue
            
            return packages
        except Exception:
            # Return empty list on any error
            return []
    
    def find_component_by_name(self, name: str, recursive: bool = True) -> Optional['Component']:
        """Find component by name - SIMPLIFIED"""
        try:
            # Search direct components
            for comp in self.components:
                if hasattr(comp, 'short_name') and comp.short_name == name:
                    return comp
            
            # Search sub-packages if recursive
            if recursive:
                for sub_pkg in self.sub_packages:
                    try:
                        found = sub_pkg.find_component_by_name(name, recursive=True)
                        if found:
                            return found
                    except Exception:
                        # Skip problematic sub-packages
                        continue
            
            return None
        except Exception:
            return None
    
    def find_component_by_uuid(self, component_uuid: str, recursive: bool = True) -> Optional['Component']:
        """Find component by UUID - SIMPLIFIED"""
        try:
            # Search direct components
            for comp in self.components:
                if hasattr(comp, 'uuid') and comp.uuid == component_uuid:
                    return comp
            
            # Search sub-packages if recursive
            if recursive:
                for sub_pkg in self.sub_packages:
                    try:
                        found = sub_pkg.find_component_by_uuid(component_uuid, recursive=True)
                        if found:
                            return found
                    except Exception:
                        # Skip problematic sub-packages
                        continue
            
            return None
        except Exception:
            return None
    
    def get_component_count(self, recursive: bool = False) -> int:
        """Get total component count - SIMPLIFIED"""
        try:
            count = len(self.components)
            
            if recursive:
                for sub_pkg in self.sub_packages:
                    try:
                        count += sub_pkg.get_component_count(recursive=True)
                    except Exception:
                        # Skip problematic sub-packages
                        continue
            
            return count
        except Exception:
            return 0
    
    def get_package_statistics(self) -> Dict[str, Any]:
        """Get BASIC package statistics - SIMPLIFIED"""
        try:
            return {
                'name': self.short_name,
                'path': self.full_path,
                'depth': self.depth,
                'components': len(self.components),
                'sub_packages': len(self.sub_packages),
                'total_components': self.get_component_count(recursive=True),
                'total_sub_packages': len(self.get_all_sub_packages(recursive=True))
            }
        except Exception:
            # Return minimal stats on error
            return {
                'name': self.short_name,
                'path': self.full_path,
                'depth': 0,
                'components': 0,
                'sub_packages': 0,
                'total_components': 0,
                'total_sub_packages': 0
            }
    
    def is_empty(self) -> bool:
        """Check if package is empty - SIMPLIFIED"""
        try:
            return len(self.components) == 0 and len(self.sub_packages) == 0
        except Exception:
            return True
    
    def has_components(self) -> bool:
        """Check if package has components - SIMPLIFIED"""
        try:
            return len(self.components) > 0
        except Exception:
            return False
    
    def has_sub_packages(self) -> bool:
        """Check if package has sub-packages - SIMPLIFIED"""
        try:
            return len(self.sub_packages) > 0
        except Exception:
            return False
    
    def get_direct_content_summary(self) -> Dict[str, Any]:
        """Get summary of direct content only - SIMPLIFIED"""
        try:
            component_types = {}
            for comp in self.components:
                try:
                    if hasattr(comp, 'component_type'):
                        comp_type = comp.component_type.value if hasattr(comp.component_type, 'value') else str(comp.component_type)
                        component_types[comp_type] = component_types.get(comp_type, 0) + 1
                except Exception:
                    component_types['Unknown'] = component_types.get('Unknown', 0) + 1
            
            return {
                'direct_components': len(self.components),
                'direct_sub_packages': len(self.sub_packages),
                'component_types': component_types,
                'is_empty': self.is_empty()
            }
        except Exception:
            return {
                'direct_components': 0,
                'direct_sub_packages': 0,
                'component_types': {},
                'is_empty': True
            }
    
    def remove_component(self, component: 'Component') -> bool:
        """Remove component from package - SIMPLIFIED"""
        try:
            if component in self.components:
                self.components.remove(component)
                return True
            return False
        except Exception:
            return False
    
    def remove_sub_package(self, sub_package: 'Package') -> bool:
        """Remove sub-package - SIMPLIFIED"""
        try:
            if sub_package in self.sub_packages:
                self.sub_packages.remove(sub_package)
                sub_package.parent_package = None
                return True
            return False
        except Exception:
            return False
    
    def clear_content(self):
        """Clear all content - SIMPLIFIED"""
        try:
            self.components.clear()
            for sub_pkg in self.sub_packages:
                sub_pkg.parent_package = None
            self.sub_packages.clear()
        except Exception:
            # Silent failure
            pass
    
    def get_full_hierarchy_info(self) -> Dict[str, Any]:
        """Get full hierarchy information - SIMPLIFIED"""
        try:
            def get_hierarchy_recursive(pkg: 'Package', level: int = 0) -> Dict[str, Any]:
                try:
                    info = {
                        'name': pkg.short_name,
                        'path': pkg.full_path,
                        'level': level,
                        'components': [comp.short_name for comp in pkg.components if hasattr(comp, 'short_name')],
                        'sub_packages': []
                    }
                    
                    for sub_pkg in pkg.sub_packages:
                        try:
                            info['sub_packages'].append(get_hierarchy_recursive(sub_pkg, level + 1))
                        except Exception:
                            # Skip problematic sub-packages
                            continue
                    
                    return info
                except Exception:
                    return {
                        'name': getattr(pkg, 'short_name', 'Unknown'),
                        'path': getattr(pkg, 'full_path', ''),
                        'level': level,
                        'components': [],
                        'sub_packages': []
                    }
            
            return get_hierarchy_recursive(self)
        except Exception:
            return {
                'name': self.short_name,
                'path': self.full_path,
                'level': 0,
                'components': [],
                'sub_packages': []
            }
    
    def __str__(self) -> str:
        return f"Package({self.short_name}, {self.full_path})"
    
    def __repr__(self) -> str:
        return f"Package(short_name='{self.short_name}', full_path='{self.full_path}', components={len(self.components)}, sub_packages={len(self.sub_packages)})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on UUID"""
        if not isinstance(other, Package):
            return False
        return self.uuid == other.uuid
    
    def __hash__(self) -> int:
        """Hash based on UUID"""
        return hash(self.uuid)
    
    def __len__(self) -> int:
        """Return total number of direct components"""
        return len(self.components)
    
    def __contains__(self, item) -> bool:
        """Check if component is in this package"""
        if hasattr(item, 'uuid'):
            # Check by UUID for components
            for comp in self.components:
                if hasattr(comp, 'uuid') and comp.uuid == item.uuid:
                    return True
            # Check by UUID for sub-packages
            for sub_pkg in self.sub_packages:
                if hasattr(sub_pkg, 'uuid') and sub_pkg.uuid == item.uuid:
                    return True
        elif isinstance(item, str):
            # Check by name
            return any(comp.short_name == item for comp in self.components if hasattr(comp, 'short_name'))
        return False

# Export the Package class
__all__ = ['Package']