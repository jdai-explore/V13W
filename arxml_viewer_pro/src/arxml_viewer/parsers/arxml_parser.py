# src/arxml_viewer/parsers/arxml_parser.py (COMPLETE FIXED VERSION)
"""
ARXML Parser - Enhanced for Day 4 Interface Parsing
Integration with interface parser and enhanced port information
FIXED: Complete implementation with proper try/except blocks
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
    Enhanced ARXML parser with Day 4 interface parsing capabilities
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
            'packages_parsed': 0,
            'interfaces_parsed': 0  # New for Day 4
        }
        
        # XML parsing configuration
        self.parser_config = {
            'huge_tree': True,          # Handle large files
            'remove_blank_text': True,  # Clean up whitespace
            'resolve_entities': False,  # Security - don't resolve external entities
        }
        
        # Day 4 - Interface parser (will be initialized later)
        self.interface_parser = None
        self.parsed_interfaces: Dict[str, Interface] = {}
    
    def parse_file(self, file_path: str) -> Tuple[List[Package], Dict[str, Any]]:
        """
        Parse ARXML file and return packages with components - Enhanced for Day 4
        
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
        self.logger.info(f"Starting enhanced ARXML parsing: {file_path} ({self.parse_stats['file_size']/1024/1024:.1f} MB)")
        
        try:
            # Parse XML with lxml
            parser = etree.XMLParser(**self.parser_config)
            tree = etree.parse(str(file_path), parser)
            root = tree.getroot()
            
            print(f"🔧 XML root: {root.tag}")
            print(f"🔧 Namespaces: {root.nsmap}")
            
            # Create XML helper
            xml_helper = SimpleXMLHelper(root)
            
            # Day 4 - Initialize interface parser (safe fallback if not available)
            try:
                from .interface_parser import InterfaceParser
                self.interface_parser = InterfaceParser(xml_helper)
                print("✅ Interface parser initialized")
            except ImportError:
                print("⚠️ Interface parser not available - continuing without interface parsing")
                self.interface_parser = None
            
            # Parse main content with enhanced interface support
            packages = self._parse_packages_enhanced(root, xml_helper)
            
            # Calculate statistics
            self.parse_stats['parse_time'] = time.time() - start_time
            self._calculate_stats(packages)
            
            self.logger.info(f"Enhanced ARXML parsing completed in {self.parse_stats['parse_time']:.2f}s")
            self.logger.info(f"Parsed: {self.parse_stats['components_parsed']} components, "
                           f"{self.parse_stats['ports_parsed']} ports, "
                           f"{self.parse_stats['interfaces_parsed']} interfaces")
            
            # Build metadata with interface information
            metadata = {
                'file_path': str(file_path),
                'file_size': self.parse_stats['file_size'],
                'parse_time': self.parse_stats['parse_time'],
                'statistics': self.parse_stats.copy(),
                'namespaces': xml_helper.namespaces,
                'autosar_version': self._detect_autosar_version(root),
                'interfaces': self._get_interface_metadata()
            }
            
            return packages, metadata
            
        except etree.XMLSyntaxError as e:
            raise ARXMLParsingError(f"XML syntax error: {e}")
        except Exception as e:
            raise ARXMLParsingError(f"Parsing failed: {e}")
    
    def _parse_packages_enhanced(self, root: etree.Element, xml_helper: SimpleXMLHelper) -> List[Package]:
        """Parse AR-PACKAGES from XML root - Enhanced with interface parsing"""
        packages = []
        
        print("🔧 Enhanced package parsing with interface support...")
        
        try:
            # Find AR-PACKAGES container first
            ar_packages_containers = xml_helper.find_elements(root, "AR-PACKAGES")
            print(f"🔧 Found {len(ar_packages_containers)} AR-PACKAGES containers")
            
            # Collect all package elements for interface parsing
            all_package_elements = []
            
            if ar_packages_containers:
                for container in ar_packages_containers:
                    pkg_elements = xml_helper.find_elements(container, "AR-PACKAGE")
                    all_package_elements.extend(pkg_elements)
                    print(f"🔧 Found {len(pkg_elements)} packages in container")
            else:
                # Try direct search
                all_package_elements = xml_helper.find_elements(root, "AR-PACKAGE")
                print(f"🔧 Found {len(all_package_elements)} packages via direct search")
            
            print(f"🔧 Total packages to process: {len(all_package_elements)}")
            
            # Day 4 - Parse interfaces first (if interface parser available)
            if self.interface_parser:
                try:
                    print("🔧 Parsing interfaces...")
                    self.parsed_interfaces = self.interface_parser.parse_interfaces_from_root(root)
                    self.parse_stats['interfaces_parsed'] = len(self.parsed_interfaces)
                    print(f"✅ Parsed {len(self.parsed_interfaces)} interfaces")
                except Exception as e:
                    print(f"⚠️ Interface parsing failed: {e}")
                    self.parsed_interfaces = {}
            
            # Parse packages with interface information
            for pkg_elem in all_package_elements:
                try:
                    package = self._parse_package_enhanced(pkg_elem, xml_helper)
                    if package:
                        packages.append(package)
                        print(f"✅ Parsed package: {package.short_name}")
                except Exception as e:
                    print(f"❌ Failed to parse package: {e}")
                    continue
            
            # Day 4 - Link interfaces to ports
            try:
                self._link_interfaces_to_ports(packages)
            except Exception as e:
                print(f"⚠️ Interface linking failed: {e}")
            
            self.parse_stats['packages_parsed'] = len(packages)
            return packages
            
        except Exception as e:
            print(f"❌ Package parsing failed: {e}")
            raise ARXMLParsingError(f"Failed to parse packages: {e}")
    
    def _parse_package_enhanced(self, pkg_elem: etree.Element, xml_helper: SimpleXMLHelper, parent_path: str = "") -> Optional[Package]:
        """Parse individual AR-PACKAGE element - Enhanced for Day 4"""
        try:
            short_name = xml_helper.get_text(pkg_elem, "SHORT-NAME")
            if not short_name:
                print("⚠️ Package without SHORT-NAME")
                return None
            
            print(f"🔧 Parsing package: {short_name}")
            
            # Build full path
            full_path = f"{parent_path}/{short_name}" if parent_path else short_name
            
            # Get description
            desc = self._get_description(pkg_elem, xml_helper)
            
            package = Package(
                short_name=short_name,
                full_path=full_path,
                desc=desc
            )
            
            # Parse sub-packages
            sub_packages_elem = xml_helper.find_element(pkg_elem, "SUB-PACKAGES")
            if sub_packages_elem is not None:
                sub_pkg_elements = xml_helper.find_elements(sub_packages_elem, "AR-PACKAGE")
                print(f"🔧 Found {len(sub_pkg_elements)} sub-packages")
                
                for sub_pkg_elem in sub_pkg_elements:
                    try:
                        sub_package = self._parse_package_enhanced(sub_pkg_elem, xml_helper, full_path)
                        if sub_package:
                            package.sub_packages.append(sub_package)
                    except Exception as e:
                        print(f"⚠️ Failed to parse sub-package: {e}")
            
            # Parse components in ELEMENTS section
            elements_elem = xml_helper.find_element(pkg_elem, "ELEMENTS")
            if elements_elem is not None:
                components = self._parse_components(elements_elem, xml_helper, full_path)
                package.components.extend(components)
                print(f"✅ Parsed {len(components)} components in package {short_name}")
            
            return package
            
        except Exception as e:
            print(f"❌ Failed to parse package: {e}")
            return None
    
    def _parse_components(self, elements_elem: etree.Element, xml_helper: SimpleXMLHelper, package_path: str) -> List[Component]:
        """Parse components from ELEMENTS section"""
        components = []
        
        component_types = [
            ("APPLICATION-SW-COMPONENT-TYPE", ComponentType.APPLICATION),
            ("COMPOSITION-SW-COMPONENT-TYPE", ComponentType.COMPOSITION),
            ("SERVICE-SW-COMPONENT-TYPE", ComponentType.SERVICE),
            ("SENSOR-ACTUATOR-SW-COMPONENT-TYPE", ComponentType.SENSOR_ACTUATOR),
            ("COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE", ComponentType.COMPLEX_DEVICE_DRIVER)
        ]
        
        for element_name, component_type in component_types:
            component_elements = xml_helper.find_elements(elements_elem, element_name)
            
            for comp_elem in component_elements:
                try:
                    component = self._parse_component(comp_elem, xml_helper, component_type, package_path)
                    if component:
                        components.append(component)
                        self.parse_stats['components_parsed'] += 1
                except Exception as e:
                    print(f"⚠️ Failed to parse component: {e}")
        
        return components
    
    def _parse_component(self, comp_elem: etree.Element, xml_helper: SimpleXMLHelper, 
                        component_type: ComponentType, package_path: str) -> Optional[Component]:
        """Parse individual component"""
        try:
            short_name = xml_helper.get_text(comp_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            desc = self._get_description(comp_elem, xml_helper)
            
            component = Component(
                short_name=short_name,
                component_type=component_type,
                desc=desc,
                package_path=package_path
            )
            
            # Parse ports
            ports_elem = xml_helper.find_element(comp_elem, "PORTS")
            if ports_elem is not None:
                ports = self._parse_ports(ports_elem, xml_helper, component.uuid)
                component.provided_ports = [p for p in ports if p.is_provided]
                component.required_ports = [p for p in ports if p.is_required]
                self.parse_stats['ports_parsed'] += len(ports)
            
            return component
            
        except Exception as e:
            print(f"❌ Failed to parse component: {e}")
            return None
    
    def _parse_ports(self, ports_elem: etree.Element, xml_helper: SimpleXMLHelper, component_uuid: str) -> List[Port]:
        """Parse ports from PORTS section"""
        ports = []
        
        port_types = [
            ("P-PORT-PROTOTYPE", PortType.PROVIDED),
            ("R-PORT-PROTOTYPE", PortType.REQUIRED),
            ("PR-PORT-PROTOTYPE", PortType.PROVIDED_REQUIRED)
        ]
        
        for element_name, port_type in port_types:
            port_elements = xml_helper.find_elements(ports_elem, element_name)
            
            for port_elem in port_elements:
                try:
                    port = self._parse_port(port_elem, xml_helper, port_type, component_uuid)
                    if port:
                        ports.append(port)
                except Exception as e:
                    print(f"⚠️ Failed to parse port: {e}")
        
        return ports
    
    def _parse_port(self, port_elem: etree.Element, xml_helper: SimpleXMLHelper, 
                   port_type: PortType, component_uuid: str) -> Optional[Port]:
        """Parse individual port"""
        try:
            short_name = xml_helper.get_text(port_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            desc = self._get_description(port_elem, xml_helper)
            
            port = Port(
                short_name=short_name,
                port_type=port_type,
                desc=desc,
                component_uuid=component_uuid
            )
            
            # Parse interface reference
            interface_ref = self._get_interface_reference(port_elem, xml_helper)
            if interface_ref:
                port.interface_ref = interface_ref
            
            return port
            
        except Exception as e:
            print(f"❌ Failed to parse port: {e}")
            return None
    
    def _get_description(self, elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[str]:
        """Get description from DESC/L-2 element"""
        try:
            desc_elem = xml_helper.find_element(elem, "DESC")
            if desc_elem is not None:
                l2_elem = xml_helper.find_element(desc_elem, "L-2")
                if l2_elem is not None and l2_elem.text:
                    return l2_elem.text.strip()
        except Exception:
            pass
        return None
    
    def _get_interface_reference(self, port_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[str]:
        """Get interface reference from port"""
        try:
            # Look for PROVIDED-INTERFACE-TREF or REQUIRED-INTERFACE-TREF
            ref_elements = [
                "PROVIDED-INTERFACE-TREF",
                "REQUIRED-INTERFACE-TREF",
                "PROVIDED-COM-SPECS",
                "REQUIRED-COM-SPECS"
            ]
            
            for ref_elem_name in ref_elements:
                ref_elem = xml_helper.find_element(port_elem, ref_elem_name)
                if ref_elem is not None and ref_elem.text:
                    return ref_elem.text.strip()
            
        except Exception:
            pass
        return None
    
    def _detect_autosar_version(self, root: etree.Element) -> str:
        """Detect AUTOSAR version from XML"""
        try:
            # Check namespace for version info
            for ns_uri in root.nsmap.values():
                if ns_uri and 'autosar.org' in ns_uri:
                    if 'r4.0' in ns_uri:
                        return "4.0"
                    elif 'r4.1' in ns_uri:
                        return "4.1"
                    elif 'r4.2' in ns_uri:
                        return "4.2"
                    elif 'r4.3' in ns_uri:
                        return "4.3"
            
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def _calculate_stats(self, packages: List[Package]):
        """Calculate parsing statistics"""
        try:
            total_components = 0
            total_ports = 0
            
            for package in packages:
                all_components = package.get_all_components(recursive=True)
                total_components += len(all_components)
                
                for component in all_components:
                    total_ports += len(component.all_ports)
            
            # Update stats
            self.parse_stats['components_parsed'] = total_components
            self.parse_stats['ports_parsed'] = total_ports
            
        except Exception as e:
            print(f"⚠️ Statistics calculation failed: {e}")
    
    def _link_interfaces_to_ports(self, packages: List[Package]):
        """Link parsed interfaces to ports - Day 4 feature"""
        if not self.interface_parser or not self.parsed_interfaces:
            return
        
        try:
            linked_count = 0
            
            for package in packages:
                all_components = package.get_all_components(recursive=True)
                
                for component in all_components:
                    for port in component.all_ports:
                        if port.interface_ref:
                            # Try to find matching interface
                            interface = self.interface_parser.get_interface_by_reference(port.interface_ref)
                            if interface:
                                port.interface = interface
                                linked_count += 1
            
            print(f"✅ Linked {linked_count} ports to interfaces")
            
        except Exception as e:
            print(f"⚠️ Interface linking failed: {e}")
    
    def _get_interface_metadata(self) -> Dict[str, Any]:
        """Get interface metadata for response"""
        try:
            if self.parsed_interfaces:
                return {
                    uuid: {
                        'short_name': interface.short_name,
                        'interface_type': interface.interface_type.value,
                        'methods_count': len(interface.methods),
                        'data_elements_count': len(interface.data_elements)
                    }
                    for uuid, interface in self.parsed_interfaces.items()
                }
            return {}
        except Exception:
            return {}
    
    # Day 4 - New methods for interface support
    def get_parsed_interfaces(self) -> Dict[str, Interface]:
        """Get all parsed interfaces"""
        return self.parsed_interfaces.copy()
    
    def get_interface_summary(self) -> Dict[str, Any]:
        """Get interface parsing summary"""
        return {
            'total_interfaces': len(self.parsed_interfaces),
            'interface_types': self._get_interface_type_counts(),
            'parse_time': self.parse_stats.get('parse_time', 0)
        }
    
    def _get_interface_type_counts(self) -> Dict[str, int]:
        """Get count of interfaces by type"""
        try:
            type_counts = {}
            for interface in self.parsed_interfaces.values():
                interface_type = interface.interface_type.value
                type_counts[interface_type] = type_counts.get(interface_type, 0) + 1
            return type_counts
        except Exception:
            return {}