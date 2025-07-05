# src/arxml_viewer/parsers/arxml_parser.py (ENHANCED VERSION WITH CONNECTION PARSING)
"""
ARXML Parser - Enhanced with Day 5 Connection Parsing
Integration with interface parser and connection parsing capabilities
PRIORITY 1: CONNECTION VISUALIZATION - Complete Implementation
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
    
    def get_attribute(self, element: etree.Element, attr_name: str, default: str = "") -> str:
        """Get attribute value from element"""
        return element.get(attr_name, default)

class ARXMLParser:
    """
    Enhanced ARXML parser with Day 5 connection parsing capabilities
    PRIORITY 1: CONNECTION VISUALIZATION - Complete Implementation
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Parse statistics
        self.parse_stats = {
            'file_size': 0,
            'parse_time': 0,
            'components_parsed': 0,
            'ports_parsed': 0,
            'connections_parsed': 0,  # Enhanced for connections
            'packages_parsed': 0,
            'interfaces_parsed': 0
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
        
        # Day 5 - Connection parsing state
        self.parsed_connections: List[Connection] = []
        self.component_uuid_map: Dict[str, str] = {}  # component_path -> uuid
        self.port_uuid_map: Dict[str, str] = {}       # port_path -> uuid
    
    def parse_file(self, file_path: str) -> Tuple[List[Package], Dict[str, Any]]:
        """
        Parse ARXML file and return packages with components and connections
        Enhanced for Day 5 with connection parsing
        
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
        self.logger.info(f"Starting enhanced ARXML parsing with connections: {file_path} ({self.parse_stats['file_size']/1024/1024:.1f} MB)")
        
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
            
            # Clear connection parsing state
            self.parsed_connections.clear()
            self.component_uuid_map.clear()
            self.port_uuid_map.clear()
            
            # Parse main content with enhanced connection support
            packages = self._parse_packages_with_connections(root, xml_helper)
            
            # Calculate statistics
            self.parse_stats['parse_time'] = time.time() - start_time
            self._calculate_stats(packages)
            
            self.logger.info(f"Enhanced ARXML parsing completed in {self.parse_stats['parse_time']:.2f}s")
            self.logger.info(f"Parsed: {self.parse_stats['components_parsed']} components, "
                           f"{self.parse_stats['ports_parsed']} ports, "
                           f"{self.parse_stats['connections_parsed']} connections, "
                           f"{self.parse_stats['interfaces_parsed']} interfaces")
            
            # Build metadata with connection information
            metadata = {
                'file_path': str(file_path),
                'file_size': self.parse_stats['file_size'],
                'parse_time': self.parse_stats['parse_time'],
                'statistics': self.parse_stats.copy(),
                'namespaces': xml_helper.namespaces,
                'autosar_version': self._detect_autosar_version(root),
                'interfaces': self._get_interface_metadata(),
                'connections': self._get_connection_metadata()  # New for Day 5
            }
            
            return packages, metadata
            
        except etree.XMLSyntaxError as e:
            raise ARXMLParsingError(f"XML syntax error: {e}")
        except Exception as e:
            raise ARXMLParsingError(f"Parsing failed: {e}")
    
    def _parse_packages_with_connections(self, root: etree.Element, xml_helper: SimpleXMLHelper) -> List[Package]:
        """Parse AR-PACKAGES from XML root - Enhanced with connection parsing"""
        packages = []
        
        print("🔧 Enhanced package parsing with connection support...")
        
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
            
            # Day 5 - Parse connections after all components are loaded
            print("🔗 Starting connection parsing...")
            try:
                self._parse_connections_from_root(root, xml_helper)
                print(f"✅ Parsed {len(self.parsed_connections)} connections")
                self.parse_stats['connections_parsed'] = len(self.parsed_connections)
            except Exception as e:
                print(f"⚠️ Connection parsing failed: {e}")
                self.parsed_connections = []
            
            # Day 4 - Link interfaces to ports
            try:
                self._link_interfaces_to_ports(packages)
            except Exception as e:
                print(f"⚠️ Interface linking failed: {e}")
            
            # Day 5 - Add connections to packages/components
            try:
                self._add_connections_to_packages(packages)
            except Exception as e:
                print(f"⚠️ Connection integration failed: {e}")
            
            self.parse_stats['packages_parsed'] = len(packages)
            return packages
            
        except Exception as e:
            print(f"❌ Package parsing failed: {e}")
            raise ARXMLParsingError(f"Failed to parse packages: {e}")
    
    def _parse_connections_from_root(self, root: etree.Element, xml_helper: SimpleXMLHelper):
        """Parse connections from the entire XML document - NEW for Day 5"""
        try:
            print("🔗 Searching for connectors in XML...")
            
            # Find all CONNECTORS elements throughout the document
            connectors_elements = xml_helper.find_elements(root, "CONNECTORS")
            print(f"🔗 Found {len(connectors_elements)} CONNECTORS elements")
            
            for connectors_elem in connectors_elements:
                # Parse both assembly and delegation connectors
                self._parse_connectors_element(connectors_elem, xml_helper)
            
            print(f"🔗 Connection parsing completed: {len(self.parsed_connections)} connections")
            
        except Exception as e:
            print(f"❌ Connection parsing failed: {e}")
            raise
    
    def _parse_connectors_element(self, connectors_elem: etree.Element, xml_helper: SimpleXMLHelper):
        """Parse individual CONNECTORS element - NEW for Day 5"""
        try:
            # Parse ASSEMBLY-SW-CONNECTOR elements
            assembly_connectors = xml_helper.find_elements(connectors_elem, "ASSEMBLY-SW-CONNECTOR")
            print(f"🔗 Found {len(assembly_connectors)} assembly connectors")
            
            for conn_elem in assembly_connectors:
                connection = self._parse_assembly_connector(conn_elem, xml_helper)
                if connection:
                    self.parsed_connections.append(connection)
            
            # Parse DELEGATION-SW-CONNECTOR elements
            delegation_connectors = xml_helper.find_elements(connectors_elem, "DELEGATION-SW-CONNECTOR")
            print(f"🔗 Found {len(delegation_connectors)} delegation connectors")
            
            for conn_elem in delegation_connectors:
                connection = self._parse_delegation_connector(conn_elem, xml_helper)
                if connection:
                    self.parsed_connections.append(connection)
            
        except Exception as e:
            print(f"❌ Connectors element parsing failed: {e}")
    
    def _parse_assembly_connector(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[Connection]:
        """Parse ASSEMBLY-SW-CONNECTOR element - NEW for Day 5"""
        try:
            short_name = xml_helper.get_text(conn_elem, "SHORT-NAME")
            if not short_name:
                print("⚠️ Assembly connector without SHORT-NAME")
                return None
            
            print(f"🔗 Parsing assembly connector: {short_name}")
            
            # Get description
            desc = self._get_description(conn_elem, xml_helper)
            
            # Parse provider endpoint
            provider_endpoint = self._parse_provider_endpoint(conn_elem, xml_helper)
            if not provider_endpoint:
                print(f"⚠️ Assembly connector {short_name} missing provider endpoint")
                return None
            
            # Parse requester endpoint
            requester_endpoint = self._parse_requester_endpoint(conn_elem, xml_helper)
            if not requester_endpoint:
                print(f"⚠️ Assembly connector {short_name} missing requester endpoint")
                return None
            
            # Create connection
            connection = Connection(
                short_name=short_name,
                desc=desc,
                connection_type=ConnectionType.ASSEMBLY,
                provider_endpoint=provider_endpoint,
                requester_endpoint=requester_endpoint
            )
            
            print(f"✅ Created assembly connection: {short_name}")
            return connection
            
        except Exception as e:
            print(f"❌ Assembly connector parsing failed: {e}")
            return None
    
    def _parse_delegation_connector(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[Connection]:
        """Parse DELEGATION-SW-CONNECTOR element - NEW for Day 5"""
        try:
            short_name = xml_helper.get_text(conn_elem, "SHORT-NAME")
            if not short_name:
                print("⚠️ Delegation connector without SHORT-NAME")
                return None
            
            print(f"🔗 Parsing delegation connector: {short_name}")
            
            # Get description
            desc = self._get_description(conn_elem, xml_helper)
            
            # Parse inner port (acts as provider for delegation)
            inner_endpoint = self._parse_inner_port_endpoint(conn_elem, xml_helper)
            if not inner_endpoint:
                print(f"⚠️ Delegation connector {short_name} missing inner port")
                return None
            
            # Parse outer port (acts as requester for delegation)
            outer_endpoint = self._parse_outer_port_endpoint(conn_elem, xml_helper)
            if not outer_endpoint:
                print(f"⚠️ Delegation connector {short_name} missing outer port")
                return None
            
            # Create connection (inner = provider, outer = requester for delegation)
            connection = Connection(
                short_name=short_name,
                desc=desc,
                connection_type=ConnectionType.DELEGATION,
                provider_endpoint=inner_endpoint,
                requester_endpoint=outer_endpoint
            )
            
            print(f"✅ Created delegation connection: {short_name}")
            return connection
            
        except Exception as e:
            print(f"❌ Delegation connector parsing failed: {e}")
            return None
    
    def _parse_provider_endpoint(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[ConnectionEndpoint]:
        """Parse provider endpoint from assembly connector - NEW for Day 5"""
        try:
            # Look for PROVIDER-IREF
            provider_iref = xml_helper.find_element(conn_elem, "PROVIDER-IREF")
            if not provider_iref:
                return None
            
            # Get context component reference
            context_component_ref = xml_helper.get_text(provider_iref, "CONTEXT-COMPONENT-REF")
            # Get target port reference  
            target_port_ref = xml_helper.get_text(provider_iref, "TARGET-P-PORT-REF")
            
            if not context_component_ref or not target_port_ref:
                print("⚠️ Provider endpoint missing component or port reference")
                return None
            
            # Resolve to UUIDs
            component_uuid = self._resolve_component_reference(context_component_ref)
            port_uuid = self._resolve_port_reference(target_port_ref, component_uuid)
            
            if not component_uuid or not port_uuid:
                print(f"⚠️ Could not resolve provider endpoint: comp={component_uuid}, port={port_uuid}")
                return None
            
            return ConnectionEndpoint(
                component_uuid=component_uuid,
                port_uuid=port_uuid
            )
            
        except Exception as e:
            print(f"❌ Provider endpoint parsing failed: {e}")
            return None
    
    def _parse_requester_endpoint(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[ConnectionEndpoint]:
        """Parse requester endpoint from assembly connector - NEW for Day 5"""
        try:
            # Look for REQUESTER-IREF
            requester_iref = xml_helper.find_element(conn_elem, "REQUESTER-IREF")
            if not requester_iref:
                return None
            
            # Get context component reference
            context_component_ref = xml_helper.get_text(requester_iref, "CONTEXT-COMPONENT-REF")
            # Get target port reference
            target_port_ref = xml_helper.get_text(requester_iref, "TARGET-R-PORT-REF")
            
            if not context_component_ref or not target_port_ref:
                print("⚠️ Requester endpoint missing component or port reference")
                return None
            
            # Resolve to UUIDs
            component_uuid = self._resolve_component_reference(context_component_ref)
            port_uuid = self._resolve_port_reference(target_port_ref, component_uuid)
            
            if not component_uuid or not port_uuid:
                print(f"⚠️ Could not resolve requester endpoint: comp={component_uuid}, port={port_uuid}")
                return None
            
            return ConnectionEndpoint(
                component_uuid=component_uuid,
                port_uuid=port_uuid
            )
            
        except Exception as e:
            print(f"❌ Requester endpoint parsing failed: {e}")
            return None
    
    def _parse_inner_port_endpoint(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[ConnectionEndpoint]:
        """Parse inner port endpoint from delegation connector - NEW for Day 5"""
        try:
            # Look for INNER-PORT-IREF
            inner_iref = xml_helper.find_element(conn_elem, "INNER-PORT-IREF")
            if not inner_iref:
                return None
            
            # Get context component reference
            context_component_ref = xml_helper.get_text(inner_iref, "CONTEXT-COMPONENT-REF")
            # Get target port reference (could be P-PORT or R-PORT)
            target_port_ref = (xml_helper.get_text(inner_iref, "TARGET-P-PORT-REF") or 
                             xml_helper.get_text(inner_iref, "TARGET-R-PORT-REF"))
            
            if not context_component_ref or not target_port_ref:
                print("⚠️ Inner port endpoint missing component or port reference")
                return None
            
            # Resolve to UUIDs
            component_uuid = self._resolve_component_reference(context_component_ref)
            port_uuid = self._resolve_port_reference(target_port_ref, component_uuid)
            
            if not component_uuid or not port_uuid:
                print(f"⚠️ Could not resolve inner port endpoint: comp={component_uuid}, port={port_uuid}")
                return None
            
            return ConnectionEndpoint(
                component_uuid=component_uuid,
                port_uuid=port_uuid
            )
            
        except Exception as e:
            print(f"❌ Inner port endpoint parsing failed: {e}")
            return None
    
    def _parse_outer_port_endpoint(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[ConnectionEndpoint]:
        """Parse outer port endpoint from delegation connector - NEW for Day 5"""
        try:
            # Look for OUTER-PORT-REF (direct reference)
            outer_port_ref = xml_helper.get_text(conn_elem, "OUTER-PORT-REF")
            
            if not outer_port_ref:
                print("⚠️ Outer port endpoint missing port reference")
                return None
            
            # For outer ports, we need to find the composition component
            # This is a simplified approach - in real AUTOSAR, this would be more complex
            composition_uuid = self._find_composition_for_outer_port(outer_port_ref)
            port_uuid = self._resolve_port_reference(outer_port_ref, composition_uuid)
            
            if not composition_uuid or not port_uuid:
                print(f"⚠️ Could not resolve outer port endpoint: comp={composition_uuid}, port={port_uuid}")
                return None
            
            return ConnectionEndpoint(
                component_uuid=composition_uuid,
                port_uuid=port_uuid
            )
            
        except Exception as e:
            print(f"❌ Outer port endpoint parsing failed: {e}")
            return None
    
    def _resolve_component_reference(self, component_ref: str) -> Optional[str]:
        """Resolve component reference to UUID - NEW for Day 5"""
        try:
            # Simple implementation - could be enhanced with proper path resolution
            if component_ref in self.component_uuid_map:
                return self.component_uuid_map[component_ref]
            
            # Try to match by component name (fallback)
            component_name = component_ref.split('/')[-1] if '/' in component_ref else component_ref
            for ref_path, uuid in self.component_uuid_map.items():
                if ref_path.endswith(component_name):
                    return uuid
            
            print(f"⚠️ Could not resolve component reference: {component_ref}")
            return None
            
        except Exception as e:
            print(f"❌ Component reference resolution failed: {e}")
            return None
    
    def _resolve_port_reference(self, port_ref: str, component_uuid: str) -> Optional[str]:
        """Resolve port reference to UUID - NEW for Day 5"""
        try:
            # Create full port path
            full_port_path = f"{component_uuid}#{port_ref}"
            
            if full_port_path in self.port_uuid_map:
                return self.port_uuid_map[full_port_path]
            
            # Try to match by port name (fallback)
            port_name = port_ref.split('/')[-1] if '/' in port_ref else port_ref
            for ref_path, uuid in self.port_uuid_map.items():
                if ref_path.endswith(port_name) and component_uuid in ref_path:
                    return uuid
            
            print(f"⚠️ Could not resolve port reference: {port_ref} for component {component_uuid}")
            return None
            
        except Exception as e:
            print(f"❌ Port reference resolution failed: {e}")
            return None
    
    def _find_composition_for_outer_port(self, outer_port_ref: str) -> Optional[str]:
        """Find composition component that owns the outer port - NEW for Day 5"""
        try:
            # This is a simplified implementation
            # In a real system, you'd need to traverse the component hierarchy
            
            # For now, return the first composition component found
            for ref_path, uuid in self.component_uuid_map.items():
                if "composition" in ref_path.lower():
                    return uuid
            
            print(f"⚠️ Could not find composition for outer port: {outer_port_ref}")
            return None
            
        except Exception as e:
            print(f"❌ Composition lookup failed: {e}")
            return None
    
    def _add_connections_to_packages(self, packages: List[Package]):
        """Add parsed connections to packages/components - NEW for Day 5"""
        try:
            print(f"🔗 Integrating {len(self.parsed_connections)} connections into packages...")
            
            # For now, we'll store connections at the package level
            # In a more sophisticated implementation, you might want to store them
            # with the specific composition components that contain them
            
            if packages and self.parsed_connections:
                # Add all connections to the first package for simplicity
                # In reality, you'd want to determine which package owns each connection
                main_package = packages[0]
                
                # Add connection UUIDs to package
                connection_uuids = [conn.uuid for conn in self.parsed_connections]
                main_package.connections = getattr(main_package, 'connections', [])
                main_package.connections.extend(connection_uuids)
                
                print(f"✅ Added {len(connection_uuids)} connections to package {main_package.short_name}")
            
        except Exception as e:
            print(f"⚠️ Connection integration failed: {e}")
    
    # Enhanced mapping during component parsing
    def _parse_component(self, comp_elem: etree.Element, xml_helper: SimpleXMLHelper, 
                        component_type: ComponentType, package_path: str) -> Optional[Component]:
        """Parse individual component - Enhanced with UUID mapping for connections"""
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
            
            # Day 5 - Store component reference mapping for connection resolution
            component_ref = f"{package_path}/{short_name}"
            self.component_uuid_map[component_ref] = component.uuid
            self.component_uuid_map[short_name] = component.uuid  # Also store by name
            
            # Parse ports
            ports_elem = xml_helper.find_element(comp_elem, "PORTS")
            if ports_elem is not None:
                ports = self._parse_ports(ports_elem, xml_helper, component.uuid)
                component.provided_ports = [p for p in ports if p.is_provided]
                component.required_ports = [p for p in ports if p.is_required]
                self.parse_stats['ports_parsed'] += len(ports)
                
                # Day 5 - Store port reference mappings
                for port in ports:
                    port_ref = f"{component_ref}/{port.short_name}"
                    full_port_path = f"{component.uuid}#{port.short_name}"
                    self.port_uuid_map[port_ref] = port.uuid
                    self.port_uuid_map[full_port_path] = port.uuid
            
            return component
            
        except Exception as e:
            print(f"❌ Failed to parse component: {e}")
            return None
    
    # Existing methods remain the same...
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
    
    def _get_connection_metadata(self) -> Dict[str, Any]:
        """Get connection metadata for response - NEW for Day 5"""
        try:
            if self.parsed_connections:
                connection_metadata = {}
                
                for connection in self.parsed_connections:
                    connection_metadata[connection.uuid] = {
                        'short_name': connection.short_name,
                        'connection_type': connection.connection_type.value,
                        'provider_component': connection.provider_endpoint.component_uuid,
                        'provider_port': connection.provider_endpoint.port_uuid,
                        'requester_component': connection.requester_endpoint.component_uuid,
                        'requester_port': connection.requester_endpoint.port_uuid,
                        'description': connection.desc
                    }
                
                return {
                    'connections': connection_metadata,
                    'connection_count': len(self.parsed_connections),
                    'connection_types': self._get_connection_type_counts()
                }
            return {'connections': {}, 'connection_count': 0, 'connection_types': {}}
        except Exception as e:
            print(f"⚠️ Connection metadata generation failed: {e}")
            return {'connections': {}, 'connection_count': 0, 'connection_types': {}}
    
    def _get_connection_type_counts(self) -> Dict[str, int]:
        """Get count of connections by type - NEW for Day 5"""
        try:
            type_counts = {}
            for connection in self.parsed_connections:
                conn_type = connection.connection_type.value
                type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
            return type_counts
        except Exception:
            return {}
    
    # Day 5 - New public methods for connection access
    def get_parsed_connections(self) -> List[Connection]:
        """Get all parsed connections - NEW for Day 5"""
        return self.parsed_connections.copy()
    
    def get_connections_for_component(self, component_uuid: str) -> List[Connection]:
        """Get connections involving a specific component - NEW for Day 5"""
        try:
            connections = []
            for connection in self.parsed_connections:
                if connection.involves_component(component_uuid):
                    connections.append(connection)
            return connections
        except Exception as e:
            print(f"❌ Get connections for component failed: {e}")
            return []
    
    def get_connections_for_port(self, port_uuid: str) -> List[Connection]:
        """Get connections involving a specific port - NEW for Day 5"""
        try:
            connections = []
            for connection in self.parsed_connections:
                if connection.involves_port(port_uuid):
                    connections.append(connection)
            return connections
        except Exception as e:
            print(f"❌ Get connections for port failed: {e}")
            return []
    
    def get_connection_summary(self) -> Dict[str, Any]:
        """Get connection parsing summary - NEW for Day 5"""
        return {
            'total_connections': len(self.parsed_connections),
            'connection_types': self._get_connection_type_counts(),
            'parse_time': self.parse_stats.get('parse_time', 0),
            'component_mappings': len(self.component_uuid_map),
            'port_mappings': len(self.port_uuid_map)
        }
    
    # Day 4 - Existing interface support methods remain the same
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