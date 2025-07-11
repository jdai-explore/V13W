# src/arxml_viewer/services/filter_manager.py
"""
Filter Manager - SIMPLIFIED component filtering system
Basic filtering functionality for ARXML components
"""

from typing import List, Dict, Any, Optional, Callable
from enum import Enum

class FilterType(str, Enum):
    """Filter type options"""
    COMPONENT_TYPE = "component_type"
    PORT_TYPE = "port_type"
    PACKAGE = "package"
    INTERFACE = "interface"
    CUSTOM = "custom"

class FilterOperator(str, Enum):
    """Filter operator options"""
    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"

class Filter:
    """Individual filter definition"""
    
    def __init__(self, filter_type: FilterType, field: str, operator: FilterOperator, 
                 value: Any, active: bool = True):
        self.filter_type = filter_type
        self.field = field
        self.operator = operator
        self.value = value
        self.active = active
    
    def apply(self, item: Any) -> bool:
        """Apply filter to an item"""
        if not self.active:
            return True
        
        try:
            # Get field value from item
            if hasattr(item, self.field):
                item_value = getattr(item, self.field)
            else:
                return False
            
            # Convert to string for text operations
            item_str = str(item_value).lower() if item_value else ""
            value_str = str(self.value).lower()
            
            # Apply operator
            if self.operator == FilterOperator.EQUALS:
                return item_str == value_str
            elif self.operator == FilterOperator.CONTAINS:
                return value_str in item_str
            elif self.operator == FilterOperator.STARTS_WITH:
                return item_str.startswith(value_str)
            elif self.operator == FilterOperator.ENDS_WITH:
                return item_str.endswith(value_str)
            elif self.operator == FilterOperator.MATCHES:
                import re
                try:
                    return bool(re.search(value_str, item_str))
                except re.error:
                    return False
            
            return True
        
        except Exception:
            return True  # If error, don't filter out

class FilterManager:
    """
    SIMPLIFIED filter manager for ARXML components
    Basic filtering with predefined and custom filters
    """
    
    def __init__(self):
        self.active_filters: Dict[str, Filter] = {}
        self.quick_filters: Dict[str, str] = {}
        self.custom_filter_functions: Dict[str, Callable] = {}
    
    def add_filter(self, name: str, filter_obj: Filter) -> None:
        """Add a new filter"""
        self.active_filters[name] = filter_obj
    
    def remove_filter(self, name: str) -> bool:
        """Remove a filter"""
        if name in self.active_filters:
            del self.active_filters[name]
            return True
        return False
    
    def toggle_filter(self, name: str) -> bool:
        """Toggle filter active state"""
        if name in self.active_filters:
            self.active_filters[name].active = not self.active_filters[name].active
            return self.active_filters[name].active
        return False
    
    def clear_filters(self) -> None:
        """Clear all filters"""
        self.active_filters.clear()
        self.quick_filters.clear()
    
    def apply_quick_filter(self, filter_type: str) -> None:
        """Apply predefined quick filter"""
        # Clear existing quick filters
        keys_to_remove = [k for k in self.active_filters.keys() if k.startswith('quick_')]
        for key in keys_to_remove:
            del self.active_filters[key]
        
        # Apply new quick filter
        self.quick_filters['current'] = filter_type
        
        if filter_type == "application":
            self.add_filter('quick_application', Filter(
                FilterType.COMPONENT_TYPE, 'component_type', FilterOperator.CONTAINS, 'APPLICATION'
            ))
        elif filter_type == "service":
            self.add_filter('quick_service', Filter(
                FilterType.COMPONENT_TYPE, 'component_type', FilterOperator.CONTAINS, 'SERVICE'
            ))
        elif filter_type == "composition":
            self.add_filter('quick_composition', Filter(
                FilterType.COMPONENT_TYPE, 'component_type', FilterOperator.CONTAINS, 'COMPOSITION'
            ))
        elif filter_type == "provided_ports":
            self.add_filter('quick_provided', Filter(
                FilterType.PORT_TYPE, 'is_provided', FilterOperator.EQUALS, True
            ))
        elif filter_type == "required_ports":
            self.add_filter('quick_required', Filter(
                FilterType.PORT_TYPE, 'is_required', FilterOperator.EQUALS, True
            ))
    
    def filter_components(self, components: List[Any]) -> List[Any]:
        """Filter list of components"""
        if not self.active_filters:
            return components
        
        filtered = []
        for component in components:
            if self._passes_all_filters(component):
                filtered.append(component)
        
        return filtered
    
    def filter_ports(self, ports: List[Any]) -> List[Any]:
        """Filter list of ports"""
        if not self.active_filters:
            return ports
        
        filtered = []
        for port in ports:
            if self._passes_all_filters(port):
                filtered.append(port)
        
        return filtered
    
    def filter_packages(self, packages: List[Any]) -> List[Any]:
        """Filter list of packages"""
        if not self.active_filters:
            return packages
        
        filtered = []
        for package in packages:
            if self._passes_all_filters(package):
                filtered.append(package)
        
        return filtered
    
    def _passes_all_filters(self, item: Any) -> bool:
        """Check if item passes all active filters"""
        try:
            for filter_obj in self.active_filters.values():
                if not filter_obj.apply(item):
                    return False
            
            # Check custom filter functions
            for func in self.custom_filter_functions.values():
                try:
                    if not func(item):
                        return False
                except Exception:
                    continue
            
            return True
        except Exception:
            return True  # If error, don't filter out
    
    def add_custom_filter(self, name: str, filter_function: Callable[[Any], bool]) -> None:
        """Add custom filter function"""
        self.custom_filter_functions[name] = filter_function
    
    def remove_custom_filter(self, name: str) -> bool:
        """Remove custom filter function"""
        if name in self.custom_filter_functions:
            del self.custom_filter_functions[name]
            return True
        return False
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """Get summary of active filters"""
        try:
            active_count = sum(1 for f in self.active_filters.values() if f.active)
            
            filter_types = {}
            for filter_obj in self.active_filters.values():
                if filter_obj.active:
                    filter_type = filter_obj.filter_type.value
                    filter_types[filter_type] = filter_types.get(filter_type, 0) + 1
            
            return {
                'total_filters': len(self.active_filters),
                'active_filters': active_count,
                'filter_types': filter_types,
                'quick_filters': self.quick_filters.copy(),
                'custom_filters': len(self.custom_filter_functions)
            }
        except Exception:
            return {
                'total_filters': 0,
                'active_filters': 0,
                'filter_types': {},
                'quick_filters': {},
                'custom_filters': 0
            }
    
    def get_active_filter_names(self) -> List[str]:
        """Get names of all active filters"""
        return [name for name, filter_obj in self.active_filters.items() if filter_obj.active]
    
    def create_component_type_filter(self, component_type: str) -> Filter:
        """Create filter for specific component type"""
        return Filter(
            FilterType.COMPONENT_TYPE,
            'component_type',
            FilterOperator.CONTAINS,
            component_type.upper()
        )
    
    def create_port_type_filter(self, is_provided: bool) -> Filter:
        """Create filter for port type (provided/required)"""
        field = 'is_provided' if is_provided else 'is_required'
        return Filter(
            FilterType.PORT_TYPE,
            field,
            FilterOperator.EQUALS,
            True
        )
    
    def create_name_filter(self, name_pattern: str, operator: FilterOperator = FilterOperator.CONTAINS) -> Filter:
        """Create filter for name matching"""
        return Filter(
            FilterType.CUSTOM,
            'short_name',
            operator,
            name_pattern
        )
    
    def create_package_filter(self, package_path: str) -> Filter:
        """Create filter for package path"""
        return Filter(
            FilterType.PACKAGE,
            'package_path',
            FilterOperator.CONTAINS,
            package_path
        )
    
    def apply_text_filter(self, text: str, field: str = 'short_name') -> None:
        """Apply simple text filter to specified field"""
        if text.strip():
            self.add_filter('text_filter', Filter(
                FilterType.CUSTOM,
                field,
                FilterOperator.CONTAINS,
                text.strip()
            ))
        else:
            self.remove_filter('text_filter')
    
    def get_filtered_statistics(self, original_items: List[Any], filtered_items: List[Any]) -> Dict[str, Any]:
        """Get statistics about filtering results"""
        try:
            original_count = len(original_items)
            filtered_count = len(filtered_items)
            
            filter_efficiency = 0.0
            if original_count > 0:
                filter_efficiency = (original_count - filtered_count) / original_count
            
            return {
                'original_count': original_count,
                'filtered_count': filtered_count,
                'items_removed': original_count - filtered_count,
                'filter_efficiency': filter_efficiency,
                'percentage_remaining': (filtered_count / original_count * 100) if original_count > 0 else 0
            }
        except Exception:
            return {
                'original_count': 0,
                'filtered_count': 0,
                'items_removed': 0,
                'filter_efficiency': 0.0,
                'percentage_remaining': 0.0
            }

# Utility functions for common filter operations
def create_component_type_filters() -> Dict[str, Filter]:
    """Create filters for all component types"""
    return {
        'application': Filter(FilterType.COMPONENT_TYPE, 'component_type', FilterOperator.CONTAINS, 'APPLICATION'),
        'service': Filter(FilterType.COMPONENT_TYPE, 'component_type', FilterOperator.CONTAINS, 'SERVICE'),
        'composition': Filter(FilterType.COMPONENT_TYPE, 'component_type', FilterOperator.CONTAINS, 'COMPOSITION'),
        'sensor_actuator': Filter(FilterType.COMPONENT_TYPE, 'component_type', FilterOperator.CONTAINS, 'SENSOR_ACTUATOR'),
        'complex_driver': Filter(FilterType.COMPONENT_TYPE, 'component_type', FilterOperator.CONTAINS, 'COMPLEX_DEVICE_DRIVER')
    }

def create_port_type_filters() -> Dict[str, Filter]:
    """Create filters for port types"""
    return {
        'provided': Filter(FilterType.PORT_TYPE, 'is_provided', FilterOperator.EQUALS, True),
        'required': Filter(FilterType.PORT_TYPE, 'is_required', FilterOperator.EQUALS, True),
        'bidirectional': Filter(FilterType.PORT_TYPE, 'is_bidirectional', FilterOperator.EQUALS, True)
    }

# Export classes and functions
__all__ = [
    'FilterManager', 'Filter', 'FilterType', 'FilterOperator',
    'create_component_type_filters', 'create_port_type_filters'
]