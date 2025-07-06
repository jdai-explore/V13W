# src/arxml_viewer/services/filter_manager.py - FIXED VERSION
"""
Filter Manager - FIXED VERSION with proper filter handling
Manages component filtering and search result filtering
"""

from typing import List, Dict, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..models.component import Component, ComponentType
from ..models.port import Port, PortType
from ..models.package import Package
from ..utils.logger import get_logger

class FilterScope(Enum):
    """Filter scope enumeration"""
    COMPONENTS = "components"
    PORTS = "ports"
    PACKAGES = "packages"
    ALL = "all"

class FilterOperator(Enum):
    """Filter operator enumeration"""
    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"

@dataclass
class FilterCriteria:
    """Filter criteria definition - FIXED VERSION"""
    name: str
    scope: FilterScope
    field: str
    operator: FilterOperator
    value: str
    enabled: bool = True  # FIXED: Added enabled attribute
    description: str = ""
    case_sensitive: bool = False

class FilterManager:
    """
    Manages filtering for ARXML components - FIXED VERSION
    Provides advanced filtering capabilities with multiple criteria
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Filter state
        self.active_filters: List[FilterCriteria] = []
        self.quick_filters: Dict[str, FilterCriteria] = {}
        
        # Filter history
        self.filter_history: List[str] = []
        
        # Performance tracking
        self.last_filter_time = 0.0
        
        # Initialize predefined quick filters
        self._setup_quick_filters()
    
    def _setup_quick_filters(self):
        """Setup predefined quick filters - FIXED VERSION"""
        try:
            # Component type filters
            self.quick_filters["application"] = FilterCriteria(
                name="Application Components",
                scope=FilterScope.COMPONENTS,
                field="component_type",
                operator=FilterOperator.EQUALS,
                value="APPLICATION",
                description="Show only application components"
            )
            
            self.quick_filters["service"] = FilterCriteria(
                name="Service Components", 
                scope=FilterScope.COMPONENTS,
                field="component_type",
                operator=FilterOperator.EQUALS,
                value="SERVICE",
                description="Show only service components"
            )
            
            self.quick_filters["composition"] = FilterCriteria(
                name="Composition Components",
                scope=FilterScope.COMPONENTS, 
                field="component_type",
                operator=FilterOperator.EQUALS,
                value="COMPOSITION",
                description="Show only composition components"
            )
            
            # Port type filters
            self.quick_filters["provided_ports"] = FilterCriteria(
                name="Provided Ports",
                scope=FilterScope.PORTS,
                field="port_type", 
                operator=FilterOperator.EQUALS,
                value="PROVIDED",
                description="Show only provided ports"
            )
            
            self.quick_filters["required_ports"] = FilterCriteria(
                name="Required Ports",
                scope=FilterScope.PORTS,
                field="port_type",
                operator=FilterOperator.EQUALS, 
                value="REQUIRED",
                description="Show only required ports"
            )
            
            self.logger.debug(f"Setup {len(self.quick_filters)} quick filters")
            
        except Exception as e:
            self.logger.error(f"Quick filter setup failed: {e}")
    
    def add_filter(self, filter_criteria: FilterCriteria):
        """Add a new filter criteria - FIXED VERSION"""
        try:
            # Check if filter with same name already exists
            existing = self.get_filter_by_name(filter_criteria.name)
            if existing:
                self.logger.warning(f"Filter '{filter_criteria.name}' already exists, replacing")
                self.remove_filter(filter_criteria.name)
            
            self.active_filters.append(filter_criteria)
            self.logger.debug(f"Added filter: {filter_criteria.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to add filter: {e}")
    
    def add_quick_filter(self, name: str) -> bool:
        """Add a predefined quick filter - FIXED VERSION"""
        try:
            if name.lower() in self.quick_filters:
                quick_filter = self.quick_filters[name.lower()]
                
                # Create a copy for active filters
                active_filter = FilterCriteria(
                    name=quick_filter.name,
                    scope=quick_filter.scope,
                    field=quick_filter.field,
                    operator=quick_filter.operator,
                    value=quick_filter.value,
                    enabled=True,  # FIXED: Ensure enabled is set
                    description=quick_filter.description,
                    case_sensitive=quick_filter.case_sensitive
                )
                
                self.add_filter(active_filter)
                return True
            else:
                self.logger.warning(f"Quick filter '{name}' not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to add quick filter '{name}': {e}")
            return False
    
    def apply_quick_filter(self, filter_name: str):
        """Apply a quick filter by name - FIXED VERSION"""
        try:
            # Clear existing filters first
            self.clear_filters()
            
            # Add the quick filter
            success = self.add_quick_filter(filter_name.lower())
            if success:
                self.logger.debug(f"Applied quick filter: {filter_name}")
            else:
                self.logger.warning(f"Failed to apply quick filter: {filter_name}")
                
        except Exception as e:
            self.logger.error(f"Quick filter application failed: {e}")
    
    def remove_filter(self, filter_name: str) -> bool:
        """Remove filter by name"""
        try:
            initial_count = len(self.active_filters)
            self.active_filters = [f for f in self.active_filters if f.name != filter_name]
            
            removed = initial_count > len(self.active_filters)
            if removed:
                self.logger.debug(f"Removed filter: {filter_name}")
            
            return removed
            
        except Exception as e:
            self.logger.error(f"Failed to remove filter: {e}")
            return False
    
    def clear_filters(self):
        """Clear all active filters"""
        try:
            self.active_filters.clear()
            self.logger.debug("Cleared all filters")
        except Exception as e:
            self.logger.error(f"Failed to clear filters: {e}")
    
    def enable_filter(self, filter_name: str, enabled: bool = True):
        """Enable or disable a filter - FIXED VERSION"""
        try:
            filter_criteria = self.get_filter_by_name(filter_name)
            if filter_criteria:
                filter_criteria.enabled = enabled
                self.logger.debug(f"Filter '{filter_name}' enabled: {enabled}")
            else:
                self.logger.warning(f"Filter '{filter_name}' not found")
                
        except Exception as e:
            self.logger.error(f"Failed to enable/disable filter: {e}")
    
    def get_filter_by_name(self, filter_name: str) -> Optional[FilterCriteria]:
        """Get filter by name"""
        try:
            for filter_criteria in self.active_filters:
                if filter_criteria.name == filter_name:
                    return filter_criteria
            return None
        except Exception as e:
            self.logger.error(f"Failed to get filter by name: {e}")
            return None
    
    def filter_components(self, components: List[Component]) -> List[Component]:
        """Filter components based on active criteria - FIXED VERSION"""
        try:
            if not self.active_filters:
                return components
            
            filtered = components.copy()
            
            for filter_criteria in self.active_filters:
                if not filter_criteria.enabled:  # FIXED: Check enabled attribute
                    continue
                    
                if filter_criteria.scope in [FilterScope.COMPONENTS, FilterScope.ALL]:
                    filtered = self._apply_component_filter(filtered, filter_criteria)
            
            self.logger.debug(f"Filtered components: {len(components)} -> {len(filtered)}")
            return filtered
            
        except Exception as e:
            self.logger.error(f"Component filtering failed: {e}")
            return components
    
    def filter_ports(self, ports: List[Port]) -> List[Port]:
        """Filter ports based on active criteria"""
        try:
            if not self.active_filters:
                return ports
            
            filtered = ports.copy()
            
            for filter_criteria in self.active_filters:
                if not filter_criteria.enabled:
                    continue
                    
                if filter_criteria.scope in [FilterScope.PORTS, FilterScope.ALL]:
                    filtered = self._apply_port_filter(filtered, filter_criteria)
            
            self.logger.debug(f"Filtered ports: {len(ports)} -> {len(filtered)}")
            return filtered
            
        except Exception as e:
            self.logger.error(f"Port filtering failed: {e}")
            return ports
    
    def filter_packages(self, packages: List[Package]) -> List[Package]:
        """Filter packages based on active criteria"""
        try:
            if not self.active_filters:
                return packages
            
            filtered = packages.copy()
            
            for filter_criteria in self.active_filters:
                if not filter_criteria.enabled:
                    continue
                    
                if filter_criteria.scope in [FilterScope.PACKAGES, FilterScope.ALL]:
                    filtered = self._apply_package_filter(filtered, filter_criteria)
            
            self.logger.debug(f"Filtered packages: {len(packages)} -> {len(filtered)}")
            return filtered
            
        except Exception as e:
            self.logger.error(f"Package filtering failed: {e}")
            return packages
    
    def _apply_component_filter(self, components: List[Component], filter_criteria: FilterCriteria) -> List[Component]:
        """Apply filter to components - FIXED VERSION"""
        try:
            result = []
            
            for component in components:
                if self._matches_component_filter(component, filter_criteria):
                    result.append(component)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Component filter application failed: {e}")
            return components
    
    def _matches_component_filter(self, component: Component, filter_criteria: FilterCriteria) -> bool:
        """Check if component matches filter criteria - FIXED VERSION"""
        try:
            # Get field value
            if filter_criteria.field == "component_type":
                field_value = component.component_type.name  # FIXED: Use .name instead of .value
            elif filter_criteria.field == "short_name":
                field_value = component.short_name or ""
            elif filter_criteria.field == "desc":
                field_value = component.desc or ""
            else:
                return False
            
            # Apply operator
            return self._apply_filter_operator(field_value, filter_criteria)
            
        except Exception as e:
            self.logger.error(f"Component filter matching failed: {e}")
            return False
    
    def _apply_port_filter(self, ports: List[Port], filter_criteria: FilterCriteria) -> List[Port]:
        """Apply filter to ports"""
        try:
            result = []
            
            for port in ports:
                if self._matches_port_filter(port, filter_criteria):
                    result.append(port)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Port filter application failed: {e}")
            return ports
    
    def _matches_port_filter(self, port: Port, filter_criteria: FilterCriteria) -> bool:
        """Check if port matches filter criteria"""
        try:
            # Get field value
            if filter_criteria.field == "port_type":
                field_value = port.port_type.name
            elif filter_criteria.field == "short_name":
                field_value = port.short_name or ""
            elif filter_criteria.field == "desc":
                field_value = port.desc or ""
            else:
                return False
            
            # Apply operator
            return self._apply_filter_operator(field_value, filter_criteria)
            
        except Exception as e:
            self.logger.error(f"Port filter matching failed: {e}")
            return False
    
    def _apply_package_filter(self, packages: List[Package], filter_criteria: FilterCriteria) -> List[Package]:
        """Apply filter to packages"""
        try:
            result = []
            
            for package in packages:
                if self._matches_package_filter(package, filter_criteria):
                    result.append(package)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Package filter application failed: {e}")
            return packages
    
    def _matches_package_filter(self, package: Package, filter_criteria: FilterCriteria) -> bool:
        """Check if package matches filter criteria"""
        try:
            # Get field value
            if filter_criteria.field == "short_name":
                field_value = package.short_name or ""
            elif filter_criteria.field == "desc":
                field_value = package.desc or ""
            elif filter_criteria.field == "full_path":
                field_value = package.full_path or ""
            else:
                return False
            
            # Apply operator
            return self._apply_filter_operator(field_value, filter_criteria)
            
        except Exception as e:
            self.logger.error(f"Package filter matching failed: {e}")
            return False
    
    def _apply_filter_operator(self, field_value: str, filter_criteria: FilterCriteria) -> bool:
        """Apply filter operator to field value - FIXED VERSION"""
        try:
            # Normalize case if needed
            if not filter_criteria.case_sensitive:
                field_value = field_value.lower()
                filter_value = filter_criteria.value.lower()
            else:
                filter_value = filter_criteria.value
            
            # Apply operator
            if filter_criteria.operator == FilterOperator.EQUALS:
                return field_value == filter_value
            elif filter_criteria.operator == FilterOperator.CONTAINS:
                return filter_value in field_value
            elif filter_criteria.operator == FilterOperator.STARTS_WITH:
                return field_value.startswith(filter_value)
            elif filter_criteria.operator == FilterOperator.ENDS_WITH:
                return field_value.endswith(filter_value)
            elif filter_criteria.operator == FilterOperator.REGEX:
                import re
                pattern = re.compile(filter_value, re.IGNORECASE if not filter_criteria.case_sensitive else 0)
                return bool(pattern.search(field_value))
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Filter operator application failed: {e}")
            return False
    
    def get_active_filters(self) -> List[FilterCriteria]:
        """Get list of active filters"""
        return [f for f in self.active_filters if f.enabled]
    
    def get_filter_statistics(self) -> Dict[str, Any]:
        """Get filter statistics"""
        try:
            active_count = len(self.get_active_filters())
            
            return {
                'total_filters': len(self.active_filters),
                'active_filters': active_count,
                'quick_filters_available': len(self.quick_filters),
                'has_active_filters': active_count > 0
            }
        except Exception as e:
            self.logger.error(f"Filter statistics failed: {e}")
            return {}
    
    def export_filters(self) -> Dict[str, Any]:
        """Export current filter configuration"""
        try:
            return {
                'active_filters': [
                    {
                        'name': f.name,
                        'scope': f.scope.value,
                        'field': f.field,
                        'operator': f.operator.value,
                        'value': f.value,
                        'enabled': f.enabled,
                        'description': f.description,
                        'case_sensitive': f.case_sensitive
                    }
                    for f in self.active_filters
                ]
            }
        except Exception as e:
            self.logger.error(f"Filter export failed: {e}")
            return {}
    
    def import_filters(self, filter_config: Dict[str, Any]):
        """Import filter configuration"""
        try:
            self.clear_filters()
            
            for filter_data in filter_config.get('active_filters', []):
                filter_criteria = FilterCriteria(
                    name=filter_data['name'],
                    scope=FilterScope(filter_data['scope']),
                    field=filter_data['field'],
                    operator=FilterOperator(filter_data['operator']),
                    value=filter_data['value'],
                    enabled=filter_data.get('enabled', True),
                    description=filter_data.get('description', ''),
                    case_sensitive=filter_data.get('case_sensitive', False)
                )
                self.add_filter(filter_criteria)
            
            self.logger.debug(f"Imported {len(filter_config.get('active_filters', []))} filters")
            
        except Exception as e:
            self.logger.error(f"Filter import failed: {e}")

# Export main classes
__all__ = ['FilterManager', 'FilterCriteria', 'FilterScope', 'FilterOperator']