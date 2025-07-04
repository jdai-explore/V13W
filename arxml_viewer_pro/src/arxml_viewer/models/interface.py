# src/arxml_viewer/parsers/interface_parser.py
"""
Interface Parser Extension - Day 4 Implementation
Extends existing ARXML parser to handle interface definitions
Built to work with existing SimpleXMLHelper from arxml_parser.py
"""

from typing import Dict, List, Optional, Tuple, Any
from lxml import etree

# Import existing interface models
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
                "CLIENT-SERVER-INTERFACE"
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
            interface_type = InterfaceType.SENDER_RECEIVER if "SENDER-RECEIVER" in interface_type_name else InterfaceType.CLIENT_SERVER
            
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
            
            return interface
            
        except Exception as e:
            self.logger.error(f"Simple interface parsing failed: {e}")
            return None
    
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
                        data_type = DataType(name="Unknown", category=DataTypeCategory.PRIMITIVE)
                        data_element = DataElement(name=name, data_type=data_type)
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
                            description=self._get_description(op_elem)
                        )
                        interface.methods.append(method)
                        self.parse_stats['methods_parsed'] += 1
                        
        except Exception as e:
            self.logger.error(f"Methods parsing failed: {e}")
    
    def _get_description(self, elem: etree.Element) -> Optional[str]:
        """Get description - mirrors existing parser approach"""
        # Use same approach as existing parser
        desc_elem = self.xml_helper.find_element(elem, "DESC")
        if desc_elem is not None:
            l2_elem = self.xml_helper.find_element(desc_elem, "L-2")
            if l2_elem is not None and l2_elem.text:
                return l2_elem.text.strip()
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