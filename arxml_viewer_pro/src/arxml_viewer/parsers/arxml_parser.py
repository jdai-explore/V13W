# src/arxml_viewer/parsers/arxml_parser.py
"""
ARXML Parser - Main parser for AUTOSAR XML files
SIMPLIFIED VERSION - Fixed namespace issues
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
from ..utils.logger import get_logger

class ARXMLParsingError(Exception):
    """Custom exception for ARXML parsing errors"""
    pass

class SimpleXMLHelper:
    """Simplified XML helper without complex namespace handling"""
    
    def __init__(self, root: etree.Element):
        self.root = root
        self.namespaces = root.nsmap or {}
        
        # Set up default namespace
        self.default_ns = None
        for prefix, uri in self.namespaces.items():
            if prefix is None:
                self.default_ns = uri
                break
    
    def find_elements(self, parent: etree.Element, tag_name: str) -> List[etree.Element]:
        """Find elements by tag name, handling namespaces simply"""
        results = []
        
        # Try different approaches
        try:
            # Method 1: Direct tag search
            for elem in parent.iter():
                local_name = etree.QName(elem).localname
                if local_name == tag_name:
                    results.append(elem)
        except Exception:
            pass
        
        return results
    
    def find_element(self, parent: etree.Element, tag_name: str) -> Optional[etree.Element]:
        """Find first element by tag name"""
        elements = self.find_elements(parent, tag_name)
        return elements[0] if elements else None
    
    def get_text(self, parent: etree.Element, tag_name: str, default: str = "") -> str:
        """Get text content of child element"""
        element = self.find_element(parent, tag_name)
        if element is not None and element.text:
            return element.text.strip()
        return default

class ARXMLParser:
    """
    Simplified ARXML parser with better error handling
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Parse statistics
        self.parse_stats = {
            'file_size': 0,
            'parse_time': 0,
            'components_parsed': 0,
            'ports_parsed': 0,
            'connections_parsed': 0,
            'packages_parsed': 0
        }
        
        # XML parsing configuration
        self.parser_config = {
            'huge_tree': True,          # Handle large files
            'remove_blank_text': True,  # Clean up whitespace
            'resolve_entities': False,  # Security - don't resolve external entities
        }
    
    def parse_file(self, file_path: str) -> Tuple[List[Package], Dict[str, Any]]:
        """
        Parse ARXML file and return packages with components - SIMPLIFIED
        
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
            
            print(f"🔧 XML root: {root.tag}")
            print(f"🔧 Namespaces: {root.nsmap}")
            
            # Create XML helper
            xml_helper = SimpleXMLHelper(root)
            
            # Parse main content
            packages = self._parse_packages(root, xml_helper)
            
            # Calculate statistics
            self.parse_stats['parse_time'] = time.time() - start_time
            self._calculate_stats(packages)
            
            self.logger.info(f"ARXML parsing completed in {self.parse_stats['parse_time']:.2f}s")
            self.logger.info(f"Parsed: {self.parse_stats['components_parsed']} components, "
                           f"{self.parse_stats['ports_parsed']} ports")
            
            # Build metadata
            metadata = {
                'file_path': str(file_path),
                'file_size': self.parse_stats['file_size'],
                'parse_time': self.parse_stats['parse_time'],
                'statistics': self.parse_stats.copy(),
                'namespaces': xml_helper.namespaces,
                'autosar_version': self._detect_autosar_version(root)
            }
            
            return packages, metadata
            
        except etree.XMLSyntaxError as e:
            raise ARXMLParsingError(f"XML syntax error: {e}")
        except Exception as e:
            raise ARXMLParsingError(f"Parsing failed: {e}")
    
    def _parse_packages(self, root: etree.Element, xml_helper: SimpleXMLHelper) -> List[Package]:
        """Parse AR-PACKAGES from XML root - SIMPLIFIED"""
        packages = []
        
        print("🔧 Looking for AR-PACKAGE elements...")
        
        # Find AR-PACKAGES container first
        ar_packages_containers = xml_helper.find_elements(root, "AR-PACKAGES")
        print(f"🔧 Found {len(ar_packages_containers)} AR-PACKAGES containers")
        
        # Find all AR-PACKAGE elements
        package_elements = []
        
        if ar_packages_containers:
            for container in ar_packages_containers:
                pkg_elements = xml_helper.find_elements(container, "AR-PACKAGE")
                package_elements.extend(pkg_elements)
                print(f"🔧 Found {len(pkg_elements)} packages in container")
        else:
            # Try direct search
            package_elements = xml_helper.find_elements(root, "AR-PACKAGE")
            print(f"🔧 Found {len(package_elements)} packages via direct search")
        
        print(f"🔧 Total packages to process: {len(package_elements)}")
        
        for pkg_elem in package_elements:
            package = self._parse_package(pkg_elem, xml_helper)
            if package:
                packages.append(package)
                print(f"✅ Parsed package: {package.short_name}")
        
        self.parse_stats['packages_parsed'] = len(packages)
        return packages
    
    def _parse_package(self, pkg_elem: etree.Element, xml_helper: SimpleXMLHelper, parent_path: str = "") -> Optional[Package]:
        """Parse individual AR-PACKAGE element - SIMPLIFIED"""
        try:
            short_name = xml_helper.get_text(pkg_elem, "SHORT-NAME")
            if not short_name:
                print("⚠️ Package without SHORT-NAME")
                return None
            
            print(f"🔧 Parsing package: {short_name}")
            
            # Build full path
            full_path = f"{parent_path}/{short_name}" if parent_path else short_name
            
            package = Package(
                short_name=short_name,
                full_path=full_path,
                desc=xml_helper.get_text(pkg_elem, "DESC")
            )
            
            # Parse sub-packages
            sub_packages_elem = xml_helper.find_element(pkg_elem, "SUB-PACKAGES")
            if sub_packages_elem is not None:
                sub_pkg_elements = xml_helper.find_elements(sub_packages_elem, "AR-PACKAGE")
                print(f"🔧 Found {len(sub_pkg_elements)} sub-packages")
                for sub_pkg_elem in sub_pkg_elements:
                    sub_package = self._parse_package(sub_pkg_elem, xml_helper, full_path)
                    if sub_package:
                        sub_package.parent_package = package
                        package.sub_packages.append(sub_package)
            
            # Parse elements in package
            elements_elem = xml_helper.find_element(pkg_elem, "ELEMENTS")
            if elements_elem is not None:
                self._parse_package_elements(elements_elem, package, xml_helper)
            
            return package
            
        except Exception as e:
            print(f"❌ Failed to parse package: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_package_elements(self, elements_elem: etree.Element, package: Package, xml_helper: SimpleXMLHelper):
        """Parse ELEMENTS section of package - SIMPLIFIED"""
        # Look for component types
        component_types = [
            "APPLICATION-SW-COMPONENT-TYPE",
            "COMPOSITION-SW-COMPONENT-TYPE", 
            "SERVICE-SW-COMPONENT-TYPE",
            "SENSOR-ACTUATOR-SW-COMPONENT-TYPE",
            "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE"
        ]
        
        for comp_type in component_types:
            comp_elements = xml_helper.find_elements(elements_elem, comp_type)
            print(f"🔧 Found {len(comp_elements)} {comp_type} components")
            
            for comp_elem in comp_elements:
                component = self._parse_component(comp_elem, package, xml_helper, comp_type)
                if component:
                    package.add_component(component)
                    print(f"✅ Added component: {component.short_name}")
    
    def _parse_component(self, comp_elem: etree.Element, package: Package, xml_helper: SimpleXMLHelper, comp_type_name: str) -> Optional[Component]:
        """Parse software component element - SIMPLIFIED"""
        try:
            short_name = xml_helper.get_text(comp_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            print(f"🔧 Parsing component: {short_name} ({comp_type_name})")
            
            # Map component type
            component_type = self._map_component_type(comp_type_name)
            
            component = Component(
                short_name=short_name,
                component_type=component_type,
                desc=xml_helper.get_text(comp_elem, "DESC"),
                package_path=package.full_path
            )
            
            # Parse ports
            ports_elem = xml_helper.find_element(comp_elem, "PORTS")
            if ports_elem is not None:
                self._parse_component_ports(ports_elem, component, xml_helper)
                print(f"🔧 Component {short_name} has {component.port_count} ports")
            
            self.parse_stats['components_parsed'] += 1
            return component
            
        except Exception as e:
            print(f"❌ Failed to parse component: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_component_ports(self, ports_elem: etree.Element, component: Component, xml_helper: SimpleXMLHelper):
        """Parse component ports - SIMPLIFIED"""
        port_types = ["P-PORT-PROTOTYPE", "R-PORT-PROTOTYPE", "PR-PORT-PROTOTYPE"]
        
        for port_type_name in port_types:
            port_elements = xml_helper.find_elements(ports_elem, port_type_name)
            print(f"🔧 Found {len(port_elements)} {port_type_name} ports")
            
            for port_elem in port_elements:
                port = self._parse_port(port_elem, component, xml_helper, port_type_name)
                if port:
                    component.add_port(port)
    
    def _parse_port(self, port_elem: etree.Element, component: Component, xml_helper: SimpleXMLHelper, port_type_name: str) -> Optional[Port]:
        """Parse port element - SIMPLIFIED"""
        try:
            short_name = xml_helper.get_text(port_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            # Map port type
            port_type = self._map_port_type(port_type_name)
            
            port = Port(
                short_name=short_name,
                port_type=port_type,
                component_uuid=component.uuid,
                desc=xml_helper.get_text(port_elem, "DESC")
            )
            
            self.parse_stats['ports_parsed'] += 1
            return port
            
        except Exception as e:
            print(f"❌ Failed to parse port: {e}")
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
    
    def _calculate_stats(self, packages: List[Package]):
        """Calculate parsing statistics"""
        total_components = sum(len(pkg.get_all_components(recursive=True)) for pkg in packages)
        self.parse_stats['components_parsed'] = total_components
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        return self.parse_stats.copy()