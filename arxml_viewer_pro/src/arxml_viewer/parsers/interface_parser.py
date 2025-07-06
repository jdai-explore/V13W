# src/arxml_viewer/parsers/interface_parser.py
"""
Interface Parser Extension - Day 4 Implementation
Extends existing ARXML parser to handle interface definitions
Built to work with existing SimpleXMLHelper from arxml_parser.py
"""

from typing import Dict, List, Optional, Tuple, Any
from lxml import etree

# Import interface models
from ..models.interface import (
    Interface, InterfaceType, InterfaceMethod, MethodArgument, 
    DataElement, DataType, DataTypeCategory, ArgumentDirection
)
from ..utils.logger import get_logger

class InterfaceParser:
    """
    Interface parser extension that works with existing ARXML parser
    Uses the same SimpleXMLHelper pattern for consistency
    """
    
    def __init__(self, xml_helper):
        self.logger = get_logger(__name__)
        self.xml_helper = xml_helper  # Use existing SimpleXMLHelper
        
        # Parsed interfaces cache
        self.interfaces: Dict[str, Interface] = {}
        self.interface_refs: Dict[str, str] = {}  # ref_path -> interface_uuid
        
        # Statistics
        self.parse_stats = {
            'interfaces_parsed': 0,
            'methods_parsed': 0,
            'data_elements_parsed': 0
        }
    
    def parse_interfaces_from_root(self, root_element: etree.Element) -> Dict[str, Interface]:
        """
        Parse interfaces from root element, working with existing parser structure
        This integrates with the existing package parsing approach
        """
        try:
            self.logger.info("Starting interface parsing...")
            
            # Find all AR-PACKAGES elements (same approach as existing parser)
            ar_packages_containers = self.xml_helper.find_elements(root_element, "AR-PACKAGES")
            
            for container in ar_packages_containers:
                pkg_elements = self.xml_helper.find_elements(container, "AR-PACKAGE")
                for pkg_elem in pkg_elements:
                    self._parse_package_interfaces_recursive(pkg_elem, "")
            
            self.logger.info(f"Interface parsing completed: {self.parse_stats}")
            return self.interfaces.copy()
            
        except Exception as e:
            self.logger.error(f"Interface parsing failed: {e}")
            return {}
    
    def parse_interfaces_from_packages(self, package_elements: List[etree.Element]) -> Dict[str, Interface]:
        """
        Parse interfaces from a list of package elements
        Alternative entry point for integration
        """
        try:
            self.logger.info("Starting interface parsing from package elements...")
            
            for pkg_elem in package_elements:
                self._parse_package_interfaces_recursive(pkg_elem, "")
            
            self.logger.info(f"Interface parsing completed: {self.parse_stats}")
            return self.interfaces.copy()
            
        except Exception as e:
            self.logger.error(f"Interface parsing failed: {e}")
            return {}
    
    def _parse_package_interfaces_recursive(self, pkg_elem: etree.Element, parent_path: str = ""):
        """Parse interfaces from package recursively - mirrors existing package parsing"""
        try:
            pkg_name = self.xml_helper.get_text(pkg_elem, "SHORT-NAME")
            if not pkg_name:
                return
            
            current_path = f"{parent_path}/{pkg_name}" if parent_path else pkg_name
            
            # Parse interfaces in ELEMENTS section
            elements_elem = self.xml_helper.find_element(pkg_elem, "ELEMENTS")
            if elements_elem is not None:
                self._parse_interface_elements(elements_elem, current_path)
            
            # Parse sub-packages recursively
            sub_packages_elem = self.xml_helper.find_element(pkg_elem, "SUB-PACKAGES")
            if sub_packages_elem is not None:
                sub_pkg_elements = self.xml_helper.find_elements(sub_packages_elem, "AR-PACKAGE")
                for sub_pkg_elem in sub_pkg_elements:
                    self._parse_package_interfaces_recursive(sub_pkg_elem, current_path)
                    
        except Exception as e:
            self.logger.error(f"Package interface parsing failed: {e}")
    
    def _parse_interface_elements(self, elements_elem: etree.Element, package_path: str):
        """Parse interface elements - simplified but comprehensive"""
        try:
            # Look for the most common interface types
            interface_types = [
                "SENDER-RECEIVER-INTERFACE",
                "CLIENT-SERVER-INTERFACE",
                "TRIGGER-INTERFACE",
                "MODE-SWITCH-INTERFACE",
                "NV-DATA-INTERFACE"
            ]
            
            for interface_type in interface_types:
                interface_elements = self.xml_helper.find_elements(elements_elem, interface_type)
                
                for interface_elem in interface_elements:
                    interface = self._parse_simple_interface(interface_elem, interface_type, package_path)
                    if interface:
                        self.interfaces[interface.uuid] = interface
                        # Create reference mapping
                        interface_ref = f"{package_path}/{interface.short_name}"
                        self.interface_refs[interface_ref] = interface.uuid
                        self.parse_stats['interfaces_parsed'] += 1
                        
        except Exception as e:
            self.logger.error(f"Interface elements parsing failed: {e}")
    
    def _parse_simple_interface(self, interface_elem: etree.Element, interface_type_name: str, package_path: str) -> Optional[Interface]:
        """Parse interface element - simplified implementation"""
        try:
            short_name = self.xml_helper.get_text(interface_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            self.logger.debug(f"Parsing interface: {short_name} ({interface_type_name})")
            
            # Map interface type
            interface_type = self._map_interface_type(interface_type_name)
            
            # Create basic interface - use existing AutosarElement pattern
            interface = Interface(
                short_name=short_name,
                interface_type=interface_type,
                desc=self._get_description(interface_elem),
                package_path=package_path
            )
            
            # Parse basic content based on type
            if interface_type == InterfaceType.SENDER_RECEIVER:
                self._parse_data_elements_simple(interface_elem, interface)
            elif interface_type == InterfaceType.CLIENT_SERVER:
                self._parse_methods_simple(interface_elem, interface)
            elif interface_type == InterfaceType.TRIGGER:
                self._parse_trigger_interface(interface_elem, interface)
            elif interface_type == InterfaceType.MODE_SWITCH:
                self._parse_mode_switch_interface(interface_elem, interface)
            elif interface_type == InterfaceType.NV_DATA:
                self._parse_nv_data_interface(interface_elem, interface)
            
            return interface
            
        except Exception as e:
            self.logger.error(f"Simple interface parsing failed: {e}")
            return None
    
    def _map_interface_type(self, interface_type_name: str) -> InterfaceType:
        """Map XML interface type name to enum"""
        type_mapping = {
            "SENDER-RECEIVER-INTERFACE": InterfaceType.SENDER_RECEIVER,
            "CLIENT-SERVER-INTERFACE": InterfaceType.CLIENT_SERVER,
            "TRIGGER-INTERFACE": InterfaceType.TRIGGER,
            "MODE-SWITCH-INTERFACE": InterfaceType.MODE_SWITCH,
            "NV-DATA-INTERFACE": InterfaceType.NV_DATA
        }
        return type_mapping.get(interface_type_name, InterfaceType.SENDER_RECEIVER)
    
    def _parse_data_elements_simple(self, interface_elem: etree.Element, interface: Interface):
        """Parse data elements - simplified implementation"""
        try:
            # Look for data elements
            data_elements_elem = self.xml_helper.find_element(interface_elem, "DATA-ELEMENTS")
            if data_elements_elem is not None:
                de_elements = self.xml_helper.find_elements(data_elements_elem, "VARIABLE-DATA-PROTOTYPE")
                
                for de_elem in de_elements:
                    name = self.xml_helper.get_text(de_elem, "SHORT-NAME")
                    if name:
                        # Create simple data element
                        data_type = self._parse_data_type(de_elem)
                        data_element = DataElement(
                            name=name,
                            data_type=data_type,
                            description=self._get_description(de_elem)
                        )
                        interface.data_elements.append(data_element)
                        self.parse_stats['data_elements_parsed'] += 1
                        
        except Exception as e:
            self.logger.error(f"Data elements parsing failed: {e}")
    
    def _parse_methods_simple(self, interface_elem: etree.Element, interface: Interface):
        """Parse methods - simplified implementation"""
        try:
            # Look for operations
            operations_elem = self.xml_helper.find_element(interface_elem, "OPERATIONS")
            if operations_elem is not None:
                op_elements = self.xml_helper.find_elements(operations_elem, "CLIENT-SERVER-OPERATION")
                
                for op_elem in op_elements:
                    name = self.xml_helper.get_text(op_elem, "SHORT-NAME")
                    if name:
                        # Create simple method
                        method = InterfaceMethod(
                            name=name,
                            description=self._get_description(op_elem),
                            arguments=self._parse_method_arguments(op_elem)
                        )
                        interface.methods.append(method)
                        self.parse_stats['methods_parsed'] += 1
                        
        except Exception as e:
            self.logger.error(f"Methods parsing failed: {e}")
    
    def _parse_method_arguments(self, operation_elem: etree.Element) -> List[MethodArgument]:
        """Parse method arguments"""
        arguments = []
        try:
            # Look for arguments
            arguments_elem = self.xml_helper.find_element(operation_elem, "ARGUMENTS")
            if arguments_elem is not None:
                arg_elements = self.xml_helper.find_elements(arguments_elem, "ARGUMENT-DATA-PROTOTYPE")
                
                for arg_elem in arg_elements:
                    name = self.xml_helper.get_text(arg_elem, "SHORT-NAME")
                    if name:
                        data_type = self._parse_data_type(arg_elem)
                        direction = self._parse_argument_direction(arg_elem)
                        
                        argument = MethodArgument(
                            name=name,
                            data_type=data_type,
                            direction=direction,
                            description=self._get_description(arg_elem)
                        )
                        arguments.append(argument)
        except Exception as e:
            self.logger.error(f"Method arguments parsing failed: {e}")
        
        return arguments
    
    def _parse_argument_direction(self, arg_elem: etree.Element) -> ArgumentDirection:
        """Parse argument direction"""
        try:
            direction_elem = self.xml_helper.find_element(arg_elem, "DIRECTION")
            if direction_elem is not None and direction_elem.text:
                direction_text = direction_elem.text.strip().upper()
                if direction_text == "IN":
                    return ArgumentDirection.IN
                elif direction_text == "OUT":
                    return ArgumentDirection.OUT
                elif direction_text == "INOUT":
                    return ArgumentDirection.INOUT
        except Exception:
            pass
        
        return ArgumentDirection.IN  # Default
    
    def _parse_data_type(self, elem: etree.Element) -> DataType:
        """Parse data type information"""
        try:
            # Look for type reference
            type_tref = self.xml_helper.get_text(elem, "TYPE-TREF")
            if type_tref:
                # Extract type name from reference
                type_name = type_tref.split('/')[-1] if '/' in type_tref else type_tref
                category = self._guess_data_type_category(type_name)
                return DataType(name=type_name, category=category, type_reference=type_tref)
            
            # Fallback - create basic type
            return DataType(name="Unknown", category=DataTypeCategory.PRIMITIVE)
            
        except Exception:
            return DataType(name="Unknown", category=DataTypeCategory.PRIMITIVE)
    
    def _guess_data_type_category(self, type_name: str) -> DataTypeCategory:
        """Guess data type category from name"""
        type_name_lower = type_name.lower()
        
        if any(primitive in type_name_lower for primitive in ['uint', 'int', 'bool', 'float', 'double']):
            return DataTypeCategory.PRIMITIVE
        elif 'array' in type_name_lower:
            return DataTypeCategory.ARRAY
        elif 'record' in type_name_lower or 'struct' in type_name_lower:
            return DataTypeCategory.RECORD
        else:
            return DataTypeCategory.PRIMITIVE
    
    def _parse_trigger_interface(self, interface_elem: etree.Element, interface: Interface):
        """Parse trigger interface specific elements"""
        try:
            # Trigger interfaces typically have trigger elements
            triggers_elem = self.xml_helper.find_element(interface_elem, "TRIGGERS")
            if triggers_elem is not None:
                trigger_elements = self.xml_helper.find_elements(triggers_elem, "TRIGGER")
                
                for trigger_elem in trigger_elements:
                    name = self.xml_helper.get_text(trigger_elem, "SHORT-NAME")
                    if name:
                        # Add as a simple method for now
                        method = InterfaceMethod(
                            name=name,
                            description=self._get_description(trigger_elem)
                        )
                        interface.methods.append(method)
                        self.parse_stats['methods_parsed'] += 1
        except Exception as e:
            self.logger.error(f"Trigger interface parsing failed: {e}")
    
    def _parse_mode_switch_interface(self, interface_elem: etree.Element, interface: Interface):
        """Parse mode switch interface specific elements"""
        try:
            # Mode switch interfaces have mode declaration groups
            mode_groups_elem = self.xml_helper.find_element(interface_elem, "MODE-DECLARATION-GROUPS")
            if mode_groups_elem is not None:
                group_elements = self.xml_helper.find_elements(mode_groups_elem, "MODE-DECLARATION-GROUP")
                
                for group_elem in group_elements:
                    name = self.xml_helper.get_text(group_elem, "SHORT-NAME")
                    if name:
                        # Add as data element for now
                        data_type = DataType(name="ModeType", category=DataTypeCategory.PRIMITIVE)
                        data_element = DataElement(
                            name=name,
                            data_type=data_type,
                            description=self._get_description(group_elem)
                        )
                        interface.data_elements.append(data_element)
                        self.parse_stats['data_elements_parsed'] += 1
        except Exception as e:
            self.logger.error(f"Mode switch interface parsing failed: {e}")
    
    def _parse_nv_data_interface(self, interface_elem: etree.Element, interface: Interface):
        """Parse NV data interface specific elements"""
        try:
            # NV data interfaces have NV data elements
            nv_datas_elem = self.xml_helper.find_element(interface_elem, "NV-DATAS")
            if nv_datas_elem is not None:
                nv_elements = self.xml_helper.find_elements(nv_datas_elem, "VARIABLE-DATA-PROTOTYPE")
                
                for nv_elem in nv_elements:
                    name = self.xml_helper.get_text(nv_elem, "SHORT-NAME")
                    if name:
                        data_type = self._parse_data_type(nv_elem)
                        data_element = DataElement(
                            name=name,
                            data_type=data_type,
                            description=self._get_description(nv_elem)
                        )
                        interface.data_elements.append(data_element)
                        self.parse_stats['data_elements_parsed'] += 1
        except Exception as e:
            self.logger.error(f"NV data interface parsing failed: {e}")
    
    def _get_description(self, elem: etree.Element) -> Optional[str]:
        """Get description - mirrors existing parser approach"""
        try:
            # Use same approach as existing parser
            desc_elem = self.xml_helper.find_element(elem, "DESC")
            if desc_elem is not None:
                l2_elem = self.xml_helper.find_element(desc_elem, "L-2")
                if l2_elem is not None and l2_elem.text:
                    return l2_elem.text.strip()
        except Exception:
            pass
        return None
    
    def get_interface_by_reference(self, interface_ref: str) -> Optional[Interface]:
        """Get interface by reference path"""
        try:
            # Direct lookup
            if interface_ref in self.interface_refs:
                interface_uuid = self.interface_refs[interface_ref]
                return self.interfaces.get(interface_uuid)
            
            # Partial matching - look for interface name at end of path
            interface_name = interface_ref.split('/')[-1] if '/' in interface_ref else interface_ref
            
            for ref_path, uuid in self.interface_refs.items():
                if ref_path.endswith(interface_name):
                    return self.interfaces.get(uuid)
            
            # Name-based lookup
            for interface in self.interfaces.values():
                if interface.short_name == interface_name:
                    return interface
            
            return None
            
        except Exception as e:
            self.logger.error(f"Interface reference lookup failed: {e}")
            return None
    
    def get_parsing_statistics(self) -> Dict[str, int]:
        """Get interface parsing statistics"""
        return self.parse_stats.copy()
    
    def get_all_interfaces(self) -> Dict[str, Interface]:
        """Get all parsed interfaces"""
        return self.interfaces.copy()
    
    def get_interfaces_by_type(self, interface_type: InterfaceType) -> List[Interface]:
        """Get interfaces of specific type"""
        return [
            interface for interface in self.interfaces.values()
            if interface.interface_type == interface_type
        ]
    
    def clear_cache(self):
        """Clear parsed interfaces cache"""
        self.interfaces.clear()
        self.interface_refs.clear()
        self.parse_stats = {
            'interfaces_parsed': 0,
            'methods_parsed': 0,
            'data_elements_parsed': 0
        }