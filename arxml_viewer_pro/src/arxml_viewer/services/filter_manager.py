# src/arxml_viewer/services/filter_manager.py
"""
Filter Manager Service - FIXED VERSION with Safe Cleanup
Manages filtering of components, ports, and packages based on various criteria
"""

from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json

from ..models.component import Component, ComponentType
from ..models.port import Port, PortType
from ..models.package import Package
from ..utils.logger import get_logger

class FilterOperator(Enum):
    """Filter operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"

@dataclass
class FilterCriteria:
    """Individual filter criteria"""
    field_name: str
    operator: FilterOperator
    value: Any
    case_sensitive: bool = False
    enabled: bool = True

@dataclass
class FilterSet:
    """Collection of filter criteria"""
    name: str
    description: str
    criteria: List[FilterCriteria]
    combine_with_and: bool = True  # True for AND, False for OR
    enabled: bool = True

class QuickFilter:
    """Quick filter presets"""
    
    # Component type filters
    APPLICATION_COMPONENTS = FilterSet(
        name="Application Components",
        description="Show only application software components",
        criteria=[FilterCriteria("component_type", FilterOperator.EQUALS, ComponentType.APPLICATION)],
        combine_with_and=True
    )
    
    COMPOSITION_COMPONENTS = FilterSet(
        name="Composition Components", 
        description="Show only composition components",
        criteria=[FilterCriteria("component_type", FilterOperator.EQUALS, ComponentType.COMPOSITION)],
        combine_with_and=True
    )
    
    SERVICE_COMPONENTS = FilterSet(
        name="Service Components",
        description="Show only service components", 
        criteria=[FilterCriteria("component_type", FilterOperator.EQUALS, ComponentType.SERVICE)],
        combine_with_and=True
    )
    
    # Port filters
    PROVIDED_PORTS = FilterSet(
        name="Provided Ports",
        description="Show only provided ports",
        criteria=[FilterCriteria("port_type", FilterOperator.EQUALS, PortType.PROVIDED)],
        combine_with_and=True
    )
    
    REQUIRED_PORTS = FilterSet(
        name="Required Ports", 
        description="Show only required ports",
        criteria=[FilterCriteria("port_type", FilterOperator.EQUALS, PortType.REQUIRED)],
        combine_with_and=True
    )
    
    # Complex filters
    COMPONENTS_WITH_PORTS = FilterSet(
        name="Components with Ports",
        description="Show components that have at least one port",
        criteria=[FilterCriteria("port_count", FilterOperator.NOT_EQUALS, 0)],
        combine_with_and=True
    )
    
    EMPTY_COMPONENTS = FilterSet(
        name="Empty Components",
        description="Show components without ports",
        criteria=[FilterCriteria("port_count", FilterOperator.EQUALS, 0)],
        combine_with_and=True
    )

class FilterManager:
    """Main filter manager for ARXML components - FIXED VERSION with Safe Cleanup"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Filter sets
        self.active_filters: List[FilterSet] = []
        self.saved_filter_sets: Dict[str, FilterSet] = {}
        
        # Quick filters
        self.quick_filters = {
            "application": QuickFilter.APPLICATION_COMPONENTS,
            "composition": QuickFilter.COMPOSITION_COMPONENTS, 
            "service": QuickFilter.SERVICE_COMPONENTS,
            "provided_ports": QuickFilter.PROVIDED_PORTS,
            "required_ports": QuickFilter.REQUIRED_PORTS,
            "with_ports": QuickFilter.COMPONENTS_WITH_PORTS,
            "empty": QuickFilter.EMPTY_COMPONENTS
        }
        
        # Field extractors for different object types
        self.field_extractors = {
            Component: self._extract_component_fields,
            Port: self._extract_port_fields,
            Package: self._extract_package_fields
        }
        
        # FIXED: Track UI items safely
        self.tracked_ui_items: Set = set()
    
    def add_filter(self, filter_set: FilterSet):
        """Add a filter set to active filters"""
        if filter_set.enabled:
            self.active_filters.append(filter_set)
            self.logger.debug(f"Added filter: {filter_set.name}")
    
    def remove_filter(self, filter_name: str):
        """Remove a filter set by name"""
        self.active_filters = [f for f in self.active_filters if f.name != filter_name]
        self.logger.debug(f"Removed filter: {filter_name}")
    
    def clear_filters(self):
        """Clear all active filters - FIXED with safe cleanup"""
        try:
            # Clear active filters safely
            self.active_filters.clear()
            
            # Clear tracked UI items safely
            items_to_remove = list(self.tracked_ui_items)
            for item in items_to_remove:
                try:
                    # Check if the Qt object is still valid before accessing
                    if hasattr(item, 'isValid') and not item.isValid():
                        continue
                    if hasattr(item, 'setHidden'):
                        item.setHidden(False)
                except RuntimeError:
                    # Qt object has been deleted - skip it
                    continue
                except Exception as e:
                    # Log other exceptions but continue
                    print(f"❌ Clear filter failed: {e}")
                    continue
            
            # Clear the tracking set
            self.tracked_ui_items.clear()
            
            self.logger.debug("Cleared all filters safely")
            
        except Exception as e:
            print(f"❌ Filter clearing failed: {e}")
            self.logger.error(f"Filter clearing failed: {e}")
    
    def track_ui_item(self, item):
        """Track a UI item for safe cleanup - NEW METHOD"""
        try:
            if item is not None:
                self.tracked_ui_items.add(item)
        except Exception:
            # Ignore tracking errors
            pass
    
    def apply_quick_filter(self, filter_key: str):
        """Apply a quick filter preset"""
        if filter_key in self.quick_filters:
            quick_filter = self.quick_filters[filter_key]
            self.add_filter(quick_filter)
            self.logger.debug(f"Applied quick filter: {quick_filter.name}")
    
    def filter_components(self, components: List[Component]) -> List[Component]:
        """Filter list of components"""
        if not self.active_filters:
            return components
        
        filtered_components = []
        
        for component in components:
            if self._passes_filters(component):
                filtered_components.append(component)
        
        self.logger.debug(f"Filtered components: {len(components)} -> {len(filtered_components)}")
        return filtered_components
    
    def filter_ports(self, ports: List[Port]) -> List[Port]:
        """Filter list of ports"""
        if not self.active_filters:
            return ports
        
        filtered_ports = []
        
        for port in ports:
            if self._passes_filters(port):
                filtered_ports.append(port)
        
        self.logger.debug(f"Filtered ports: {len(ports)} -> {len(filtered_ports)}")
        return filtered_ports
    
    def filter_packages(self, packages: List[Package]) -> List[Package]:
        """Filter list of packages"""
        if not self.active_filters:
            return packages
        
        filtered_packages = []
        
        for package in packages:
            if self._passes_filters(package):
                filtered_packages.append(package)
        
        self.logger.debug(f"Filtered packages: {len(packages)} -> {len(filtered_packages)}")
        return filtered_packages
    
    def _passes_filters(self, obj: Any) -> bool:
        """Check if object passes all active filters"""
        for filter_set in self.active_filters:
            if not filter_set.enabled:
                continue
                
            if not self._passes_filter_set(obj, filter_set):
                return False
        
        return True
    
    def _passes_filter_set(self, obj: Any, filter_set: FilterSet) -> bool:
        """Check if object passes a specific filter set"""
        if not filter_set.criteria:
            return True
        
        results = []
        
        for criteria in filter_set.criteria:
            if not criteria.enabled:
                continue
                
            result = self._evaluate_criteria(obj, criteria)
            results.append(result)
        
        if not results:
            return True
        
        # Combine results based on filter set logic
        if filter_set.combine_with_and:
            return all(results)
        else:
            return any(results)
    
    def _evaluate_criteria(self, obj: Any, criteria: FilterCriteria) -> bool:
        """Evaluate single filter criteria against object"""
        # Extract field value from object
        field_value = self._extract_field_value(obj, criteria.field_name)
        
        if field_value is None:
            return False
        
        # Convert to string for text operations if needed
        if isinstance(field_value, (ComponentType, PortType)):
            field_value = field_value.value
        
        filter_value = criteria.value
        if isinstance(filter_value, (ComponentType, PortType)):
            filter_value = filter_value.value
        
        # Apply case sensitivity
        if isinstance(field_value, str) and isinstance(filter_value, str):
            if not criteria.case_sensitive:
                field_value = field_value.lower()
                filter_value = filter_value.lower()
        
        # Evaluate based on operator
        operator = criteria.operator
        
        if operator == FilterOperator.EQUALS:
            return field_value == filter_value
        elif operator == FilterOperator.NOT_EQUALS:
            return field_value != filter_value
        elif operator == FilterOperator.CONTAINS:
            return str(filter_value) in str(field_value)
        elif operator == FilterOperator.NOT_CONTAINS:
            return str(filter_value) not in str(field_value)
        elif operator == FilterOperator.STARTS_WITH:
            return str(field_value).startswith(str(filter_value))
        elif operator == FilterOperator.ENDS_WITH:
            return str(field_value).endswith(str(filter_value))
        elif operator == FilterOperator.IN:
            return field_value in filter_value if hasattr(filter_value, '__contains__') else False
        elif operator == FilterOperator.NOT_IN:
            return field_value not in filter_value if hasattr(filter_value, '__contains__') else True
        
        return False
    
    def _extract_field_value(self, obj: Any, field_name: str) -> Any:
        """Extract field value from object"""
        obj_type = type(obj)
        
        if obj_type in self.field_extractors:
            fields = self.field_extractors[obj_type](obj)
            return fields.get(field_name)
        
        # Fallback to direct attribute access
        return getattr(obj, field_name, None)
    
    def _extract_component_fields(self, component: Component) -> Dict[str, Any]:
        """Extract searchable fields from component"""
        return {
            'short_name': component.short_name,
            'desc': component.desc,
            'component_type': component.component_type,
            'behavior': component.behavior,
            'package_path': component.package_path,
            'port_count': component.port_count,
            'provided_port_count': len(component.provided_ports),
            'required_port_count': len(component.required_ports),
            'is_composition': component.is_composition,
            'xml_path': component.xml_path
        }
    
    def _extract_port_fields(self, port: Port) -> Dict[str, Any]:
        """Extract searchable fields from port"""
        return {
            'short_name': port.short_name,
            'desc': port.desc,
            'port_type': port.port_type,
            'interface_ref': port.interface_ref,
            'is_provided': port.is_provided,
            'is_required': port.is_required,
            'component_uuid': port.component_uuid
        }
    
    def _extract_package_fields(self, package: Package) -> Dict[str, Any]:
        """Extract searchable fields from package"""
        return {
            'short_name': package.short_name,
            'desc': package.desc,
            'full_path': package.full_path,
            'depth': package.depth,
            'component_count': len(package.components),
            'subpackage_count': len(package.sub_packages),
            'total_components': len(package.get_all_components(recursive=True))
        }
    
    def create_custom_filter(self, 
                           name: str,
                           description: str = "",
                           criteria: List[FilterCriteria] = None,
                           combine_with_and: bool = True) -> FilterSet:
        """Create a custom filter set"""
        filter_set = FilterSet(
            name=name,
            description=description,
            criteria=criteria or [],
            combine_with_and=combine_with_and
        )
        
        return filter_set
    
    def save_filter_set(self, filter_set: FilterSet):
        """Save a filter set for later use"""
        self.saved_filter_sets[filter_set.name] = filter_set
        self.logger.debug(f"Saved filter set: {filter_set.name}")
    
    def load_filter_set(self, name: str) -> Optional[FilterSet]:
        """Load a saved filter set"""
        return self.saved_filter_sets.get(name)
    
    def get_saved_filter_names(self) -> List[str]:
        """Get names of all saved filter sets"""
        return list(self.saved_filter_sets.keys())
    
    def delete_saved_filter(self, name: str):
        """Delete a saved filter set"""
        if name in self.saved_filter_sets:
            del self.saved_filter_sets[name]
            self.logger.debug(f"Deleted saved filter: {name}")
    
    def export_filters_to_json(self) -> str:
        """Export all saved filters to JSON string"""
        export_data = {}
        
        for name, filter_set in self.saved_filter_sets.items():
            export_data[name] = {
                'name': filter_set.name,
                'description': filter_set.description,
                'combine_with_and': filter_set.combine_with_and,
                'enabled': filter_set.enabled,
                'criteria': []
            }
            
            for criteria in filter_set.criteria:
                criteria_data = {
                    'field_name': criteria.field_name,
                    'operator': criteria.operator.value,
                    'value': criteria.value,
                    'case_sensitive': criteria.case_sensitive,
                    'enabled': criteria.enabled
                }
                export_data[name]['criteria'].append(criteria_data)
        
        return json.dumps(export_data, indent=2)
    
    def import_filters_from_json(self, json_str: str):
        """Import filters from JSON string"""
        try:
            import_data = json.loads(json_str)
            
            for name, filter_data in import_data.items():
                criteria = []
                
                for criteria_data in filter_data.get('criteria', []):
                    criteria.append(FilterCriteria(
                        field_name=criteria_data['field_name'],
                        operator=FilterOperator(criteria_data['operator']),
                        value=criteria_data['value'],
                        case_sensitive=criteria_data.get('case_sensitive', False),
                        enabled=criteria_data.get('enabled', True)
                    ))
                
                filter_set = FilterSet(
                    name=filter_data['name'],
                    description=filter_data.get('description', ''),
                    criteria=criteria,
                    combine_with_and=filter_data.get('combine_with_and', True),
                    enabled=filter_data.get('enabled', True)
                )
                
                self.saved_filter_sets[name] = filter_set
            
            self.logger.info(f"Imported {len(import_data)} filter sets")
            
        except Exception as e:
            self.logger.error(f"Failed to import filters: {e}")
    
    def get_active_filter_summary(self) -> str:
        """Get summary of currently active filters"""
        if not self.active_filters:
            return "No filters active"
        
        enabled_filters = [f for f in self.active_filters if f.enabled]
        if not enabled_filters:
            return "No filters enabled"
        
        summary_parts = []
        for filter_set in enabled_filters:
            enabled_criteria = [c for c in filter_set.criteria if c.enabled]
            if enabled_criteria:
                summary_parts.append(f"{filter_set.name} ({len(enabled_criteria)} criteria)")
        
        return f"Active filters: {', '.join(summary_parts)}"
    
    def get_filter_statistics(self, components: List[Component] = None, 
                            ports: List[Port] = None,
                            packages: List[Package] = None) -> Dict[str, Any]:
        """Get statistics about filtering results"""
        stats = {
            'active_filters': len([f for f in self.active_filters if f.enabled]),
            'saved_filters': len(self.saved_filter_sets)
        }
        
        if components is not None:
            filtered_components = self.filter_components(components)
            stats['components'] = {
                'total': len(components),
                'filtered': len(filtered_components),
                'filtered_percentage': (len(filtered_components) / len(components) * 100) if components else 0
            }
        
        if ports is not None:
            filtered_ports = self.filter_ports(ports)
            stats['ports'] = {
                'total': len(ports),
                'filtered': len(filtered_ports),
                'filtered_percentage': (len(filtered_ports) / len(ports) * 100) if ports else 0
            }
        
        if packages is not None:
            filtered_packages = self.filter_packages(packages)
            stats['packages'] = {
                'total': len(packages),
                'filtered': len(filtered_packages),
                'filtered_percentage': (len(filtered_packages) / len(packages) * 100) if packages else 0
            }
        
        return stats
    
    def get_available_fields(self, object_type: str) -> List[str]:
        """Get list of available fields for filtering by object type"""
        if object_type.lower() == 'component':
            return list(self._extract_component_fields(Component(
                short_name="dummy", component_type=ComponentType.APPLICATION
            )).keys())
        elif object_type.lower() == 'port':
            return list(self._extract_port_fields(Port(
                short_name="dummy", port_type=PortType.PROVIDED
            )).keys())
        elif object_type.lower() == 'package':
            return list(self._extract_package_fields(Package(
                short_name="dummy"
            )).keys())
        
        return []
    
    def suggest_filter_values(self, field_name: str, 
                            components: List[Component] = None,
                            ports: List[Port] = None,
                            packages: List[Package] = None) -> List[Any]:
        """Suggest possible values for a filter field"""
        values = set()
        
        # Collect values from components
        if components:
            for component in components:
                fields = self._extract_component_fields(component)
                if field_name in fields and fields[field_name] is not None:
                    values.add(fields[field_name])
        
        # Collect values from ports
        if ports:
            for port in ports:
                fields = self._extract_port_fields(port)
                if field_name in fields and fields[field_name] is not None:
                    values.add(fields[field_name])
        
        # Collect values from packages
        if packages:
            for package in packages:
                fields = self._extract_package_fields(package)
                if field_name in fields and fields[field_name] is not None:
                    values.add(fields[field_name])
        
        # Convert to sorted list
        values_list = list(values)
        try:
            return sorted(values_list)
        except TypeError:
            # Handle mixed types that can't be sorted
            return values_list