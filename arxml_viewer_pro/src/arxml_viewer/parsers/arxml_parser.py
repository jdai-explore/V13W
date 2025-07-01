# src/arxml_viewer/parsers/arxml_parser.py
"""
ARXML Parser - Main parser for AUTOSAR XML files
Handles efficient parsing of large ARXML files with proper error handling
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Set, Any
from pathlib import Path
from lxml import etree
from loguru import logger

from ..models.component import Component, ComponentType
from ..models.port import Port, PortType, Interface, InterfaceType
from ..models.connection import Connection, ConnectionType, ConnectionEndpoint
from ..models.package import Package
from ..utils.xml_utils import XMLNamespaceHandler
from ..utils.logger import get_logger

class ARXMLParsingError(Exception):
    """Custom exception for ARXML parsing errors"""
    pass

class ARXMLParser:
    """
    Professional ARXML parser with performance optimization and error handling
    Supports large files (100MB+) with efficient memory usage
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.namespace_handler = XMLNamespaceHandler()
        
        # Parse statistics
        self.parse_stats = {
            'file_size': 0,
            'parse_time': 0,
            'components_parsed': 0,
            'ports_parsed': 0,
            'connections_parsed': 0,
            'packages_parsed': 0
        }
        
        # Caches for performance
        self._component_cache: Dict[str, Component] = {}
        self._port_cache: Dict[str, Port] = {}
        self._interface_cache: Dict[str, Interface] = {}
        self._package_cache: Dict[str, Package] = {}
        
        # XML parsing configuration
        self.parser_config = {
            'huge_tree': True,          # Handle large files
            'remove_blank_text': True,  # Clean up whitespace
            'resolve_entities': False,  # Security - don't resolve external entities
        }
    
    def parse_file(self, file_path: str) -> Tuple[List[Package], Dict[str, Any]]:
        """
        Parse ARXML file and return packages with components
        
        Args:
            file_path: Path to ARXML file
            
        Returns:
            Tuple of (packages, metadata)
            
        Raises:
            ARXMLParsingError: If parsing fails
        """
        start_time = time.time()
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ARXMLParsingError(f"File not found: {file_path}")
        
        self.parse_stats['file_size'] = file_path.stat().st_size
        self.logger.info(f"Starting ARXML parsing: {file_path} ({self.parse_stats['file_size']/1024/1024:.1f} MB)")
        
        try:
            # Parse XML with lxml
            parser = etree.XMLParser(**self.parser_config)
            tree = etree.parse(str(file_path), parser)
            root = tree.getroot()
            
            # Extract and register namespaces
            self.namespace_handler.extract_namespaces(root)
            
            # Parse main content
            packages = self._parse_packages(root)
            
            # Post-processing: resolve references and build relationships
            self._resolve_references()
            
            # Calculate statistics
            self.parse_stats['parse_time'] = time.time() - start_time
            self._calculate_stats(packages)
            
            self.logger.info(f"ARXML parsing completed in {self.parse_stats['parse_time']:.2f}s")
            self.logger.info(f"Parsed: {self.parse_stats['components_parsed']} components, "
                           f"{self.parse_stats['ports_parsed']} ports, "
                           f"{self.parse_stats['connections_parsed']} connections")
            
            # Build metadata
            metadata = {
                'file_path': str(file_path),
                'file_size': self.parse_stats['file_size'],
                'parse_time': self.parse_stats['parse_time'],
                'statistics': self.parse_stats.copy(),
                'namespaces': self.namespace_handler.namespaces,
                'autosar_version': self._detect_autosar_version(root)
            }
            
            return packages, metadata
            
        except etree.XMLSyntaxError as e:
            raise ARXMLParsingError(f"XML syntax error: {e}")
        except Exception as e:
            raise ARXMLParsingError(f"Parsing failed: {e}")
    
    def _parse_packages(self, root: etree.Element) -> List[Package]:
        """Parse AR-PACKAGES from XML root"""
        packages = []
        
        # Find all AR-PACKAGE elements
        package_elements = self.namespace_handler.find_elements(root, ".//AR-PACKAGE")
        
        for pkg_elem in package_elements:
            package = self._parse_package(pkg_elem)
            if package:
                packages.append(package)
                self._package_cache[package.uuid] = package
        
        self.parse_stats['packages_parsed'] = len(packages)
        return packages
    
    def _parse_package(self, pkg_elem: etree.Element, parent_path: str = "") -> Optional[Package]:
        """Parse individual AR-PACKAGE element"""
        try:
            short_name = self.namespace_handler.get_text(pkg_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            # Build full path
            full_path = f"{parent_path}/{short_name}" if parent_path else short_name
            
            package = Package(
                short_name=short_name,
                full_path=full_path,
                desc=self.namespace_handler.get_text(pkg_elem, "DESC/L-2"),
                xml_path=self._get_element_xpath(pkg_elem)
            )
            
            # Parse sub-packages
            sub_packages_elem = self.namespace_handler.find_element(pkg_elem, "SUB-PACKAGES")
            if sub_packages_elem is not None:
                for sub_pkg_elem in self.namespace_handler.find_elements(sub_packages_elem, "AR-PACKAGE"):
                    sub_package = self._parse_package(sub_pkg_elem, full_path)
                    if sub_package:
                        sub_package.parent_package = package
                        package.sub_packages.append(sub_package)
            
            # Parse elements in package
            elements_elem = self.namespace_handler.find_element(pkg_elem, "ELEMENTS")
            if elements_elem is not None:
                self._parse_package_elements(elements_elem, package)
            
            return package
            
        except Exception as e:
            self.logger.warning(f"Failed to parse package: {e}")
            return None
    
    def _parse_package_elements(self, elements_elem: etree.Element, package: Package):
        """Parse ELEMENTS section of package"""
        # Parse software components
        for comp_elem in self.namespace_handler.find_elements(elements_elem, "*[contains(local-name(), 'SW-COMPONENT-TYPE')]"):
            component = self._parse_component(comp_elem, package)
            if component:
                package.add_component(component)
                self._component_cache[component.uuid] = component
        
        # Parse interfaces
        for intf_elem in self.namespace_handler.find_elements(elements_elem, "*[contains(local-name(), 'INTERFACE')]"):
            interface = self._parse_interface(intf_elem)
            if interface:
                package.interfaces.append(interface.uuid)
                self._interface_cache[interface.uuid] = interface
    
    def _parse_component(self, comp_elem: etree.Element, package: Package) -> Optional[Component]:
        """Parse software component element"""
        try:
            short_name = self.namespace_handler.get_text(comp_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            # Determine component type from element tag
            tag_name = etree.QName(comp_elem).localname
            component_type = self._map_component_type(tag_name)
            
            component = Component(
                short_name=short_name,
                component_type=component_type,
                desc=self.namespace_handler.get_text(comp_elem, "DESC/L-2"),
                package_path=package.full_path,
                xml_path=self._get_element_xpath(comp_elem)
            )
            
            # Parse ports
            ports_elem = self.namespace_handler.find_element(comp_elem, "PORTS")
            if ports_elem is not None:
                self._parse_component_ports(ports_elem, component)
            
            # Parse internal behavior for compositions
            if component_type == ComponentType.COMPOSITION:
                self._parse_composition_internals(comp_elem, component)
            
            self.parse_stats['components_parsed'] += 1
            return component
            
        except Exception as e:
            self.logger.warning(f"Failed to parse component: {e}")
            return None
    
    def _parse_component_ports(self, ports_elem: etree.Element, component: Component):
        """Parse component ports"""
        for port_elem in self.namespace_handler.find_elements(ports_elem, "*[contains(local-name(), 'PORT-PROTOTYPE')]"):
            port = self._parse_port(port_elem, component)
            if port:
                component.add_port(port)
                self._port_cache[port.uuid] = port
    
    def _parse_port(self, port_elem: etree.Element, component: Component) -> Optional[Port]:
        """Parse port element"""
        try:
            short_name = self.namespace_handler.get_text(port_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            # Determine port type from element tag
            tag_name = etree.QName(port_elem).localname
            port_type = self._map_port_type(tag_name)
            
            # Get interface reference
            interface_ref = None
            interface_tref_elem = self.namespace_handler.find_element(port_elem, ".//INTERFACE-TREF")
            if interface_tref_elem is not None:
                interface_ref = interface_tref_elem.text
            
            port = Port(
                short_name=short_name,
                port_type=port_type,
                interface_ref=interface_ref,
                component_uuid=component.uuid,
                desc=self.namespace_handler.get_text(port_elem, "DESC/L-2")
            )
            
            self.parse_stats['ports_parsed'] += 1
            return port
            
        except Exception as e:
            self.logger.warning(f"Failed to parse port: {e}")
            return None
    
    def _parse_interface(self, intf_elem: etree.Element) -> Optional[Interface]:
        """Parse interface element"""
        try:
            short_name = self.namespace_handler.get_text(intf_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            # Determine interface type from element tag
            tag_name = etree.QName(intf_elem).localname
            interface_type = self._map_interface_type(tag_name)
            
            interface = Interface(
                short_name=short_name,
                interface_type=interface_type,
                desc=self.namespace_handler.get_text(intf_elem, "DESC/L-2")
            )
            
            # Parse methods and data elements based on interface type
            if interface_type == InterfaceType.CLIENT_SERVER:
                self._parse_cs_interface_methods(intf_elem, interface)
            elif interface_type == InterfaceType.SENDER_RECEIVER:
                self._parse_sr_interface_data_elements(intf_elem, interface)
            
            return interface
            
        except Exception as e:
            self.logger.warning(f"Failed to parse interface: {e}")
            return None
    
    def _parse_composition_internals(self, comp_elem: etree.Element, component: Component):
        """Parse composition internal structure"""
        # This will be expanded in Day 5 for connection parsing
        # For now, just mark as composition
        component.behavior = "COMPOSITE"
    
    def _resolve_references(self):
        """Resolve interface references and build relationships"""
        # Resolve port interface references
        for port in self._port_cache.values():
            if port.interface_ref:
                # Try to find interface by reference path
                interface = self._find_interface_by_ref(port.interface_ref)
                if interface:
                    port.interface = interface
    
    def _find_interface_by_ref(self, interface_ref: str) -> Optional[Interface]:
        """Find interface by reference path"""
        # Simple implementation - find by short name in path
        if '/' in interface_ref:
            short_name = interface_ref.split('/')[-1]
        else:
            short_name = interface_ref
        
        for interface in self._interface_cache.values():
            if interface.short_name == short_name:
                return interface
        return None
    
    def _map_component_type(self, tag_name: str) -> ComponentType:
        """Map XML tag name to ComponentType enum"""
        mapping = {
            'APPLICATION-SW-COMPONENT-TYPE': ComponentType.APPLICATION,
            'COMPOSITION-SW-COMPONENT-TYPE': ComponentType.COMPOSITION,
            'SERVICE-SW-COMPONENT-TYPE': ComponentType.SERVICE,
            'SENSOR-ACTUATOR-SW-COMPONENT-TYPE': ComponentType.SENSOR_ACTUATOR,
            'COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE': ComponentType.COMPLEX_DEVICE_DRIVER,
        }
        return mapping.get(tag_name, ComponentType.APPLICATION)
    
    def _map_port_type(self, tag_name: str) -> PortType:
        """Map XML tag name to PortType enum"""
        mapping = {
            'P-PORT-PROTOTYPE': PortType.PROVIDED,
            'R-PORT-PROTOTYPE': PortType.REQUIRED,
            'PR-PORT-PROTOTYPE': PortType.PROVIDED_REQUIRED,
        }
        return mapping.get(tag_name, PortType.REQUIRED)
    
    def _map_interface_type(self, tag_name: str) -> InterfaceType:
        """Map XML tag name to InterfaceType enum"""
        mapping = {
            'SENDER-RECEIVER-INTERFACE': InterfaceType.SENDER_RECEIVER,
            'CLIENT-SERVER-INTERFACE': InterfaceType.CLIENT_SERVER,
            'TRIGGER-INTERFACE': InterfaceType.TRIGGER,
            'MODE-SWITCH-INTERFACE': InterfaceType.MODE_SWITCH,
            'NV-DATA-INTERFACE': InterfaceType.NV_DATA,
        }
        return mapping.get(tag_name, InterfaceType.SENDER_RECEIVER)
    
    def _parse_cs_interface_methods(self, intf_elem: etree.Element, interface: Interface):
        """Parse client-server interface methods"""
        operations_elem = self.namespace_handler.find_element(intf_elem, "OPERATIONS")
        if operations_elem is not None:
            for op_elem in self.namespace_handler.find_elements(operations_elem, "CLIENT-SERVER-OPERATION"):
                method_name = self.namespace_handler.get_text(op_elem, "SHORT-NAME")
                if method_name:
                    interface.methods.append(method_name)
    
    def _parse_sr_interface_data_elements(self, intf_elem: etree.Element, interface: Interface):
        """Parse sender-receiver interface data elements"""
        data_elements_elem = self.namespace_handler.find_element(intf_elem, "DATA-ELEMENTS")
        if data_elements_elem is not None:
            for de_elem in self.namespace_handler.find_elements(data_elements_elem, "VARIABLE-DATA-PROTOTYPE"):
                element_name = self.namespace_handler.get_text(de_elem, "SHORT-NAME")
                if element_name:
                    interface.data_elements.append(element_name)
    
    def _detect_autosar_version(self, root: etree.Element) -> str:
        """Detect AUTOSAR version from XML"""
        # Check schema location or root attributes
        schema_location = root.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', '')
        if 'AUTOSAR_4-3-0' in schema_location:
            return '4.3.0'
        elif 'AUTOSAR_4-2-2' in schema_location:
            return '4.2.2'
        elif 'AUTOSAR_4-4-0' in schema_location:
            return '4.4.0'
        else:
            return 'Unknown'
    
    def _get_element_xpath(self, element: etree.Element) -> str:
        """Get XPath for element"""
        tree = element.getroottree()
        return tree.getpath(element)
    
    def _calculate_stats(self, packages: List[Package]):
        """Calculate parsing statistics"""
        total_components = sum(len(pkg.get_all_components(recursive=True)) for pkg in packages)
        self.parse_stats['components_parsed'] = total_components
    
    def clear_cache(self):
        """Clear internal caches"""
        self._component_cache.clear()
        self._port_cache.clear()
        self._interface_cache.clear()
        self._package_cache.clear()
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        return self.parse_stats.copy()