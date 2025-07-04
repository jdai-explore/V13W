# src/arxml_viewer/parsers/arxml_parser.py (UPDATED for Day 4)
"""
ARXML Parser - Enhanced for Day 4 Interface Parsing
Integration with interface parser and enhanced port information
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
from ..parsers.interface_parser import InterfaceParser
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
        
        # Day 4 - Interface parser
        self.interface_parser: Optional[InterfaceParser] = None
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
            
            # Day 4 - Initialize interface parser
            self.interface_parser = InterfaceParser(xml_helper)
            
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
                'interfaces': {uuid: interface.get_interface_summary() 
                             for uuid, interface in self.parsed_interfaces.items()}
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
        
        # Day 4 - Parse interfaces first
        if self.interface_parser:
            print("🔧 Parsing interfaces...")
            self.parsed_interfaces = self.interface_parser.parse_interfaces_from_packages(all_package_elements)
            self.parse_stats['interfaces_parsed'] = len(self.parsed_interfaces)
            print(f"✅ Parsed {len(self.parsed_interfaces)} interfaces")
        
        # Parse packages with interface information
        for pkg_elem in all_package_elements:
            package = self._parse_package_enhanced(pkg_elem, xml_helper)
            if package:
                packages.append(package)
                print(f"✅ Parsed package: {package.short_name}")
        
        # Day 4 - Link interfaces to ports
        self._link_interfaces_to_ports(packages)
        
        self.parse_stats['packages_parsed'] = len(packages)
        return packages
    
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