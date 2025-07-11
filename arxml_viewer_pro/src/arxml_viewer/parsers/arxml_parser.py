# src/arxml_viewer/parsers/arxml_parser.py - SIMPLIFIED VERSION
"""
ARXML Parser - SIMPLIFIED with interface_parser integration removed
MODERATE SIMPLIFICATION: Removed interface_parser, simplified connections, basic parsing
FIXES APPLIED:
- Remove interface_parser integration completely
- Remove complex connection parsing (keep basic connections only)
- Remove UUID mapping systems for connections
- Simplify XML parsing - use basic lxml approach only
- Remove complex statistics tracking
- Remove interface linking functionality
- Simplify to: Parse packages → Parse components → Parse ports → Basic connections
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from lxml import etree

from ..models.component import Component, ComponentType
from ..models.port import Port, PortType
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
    SIMPLIFIED ARXML parser - interface_parser integration removed
    MODERATE SIMPLIFICATION as per guide requirements
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # SIMPLIFIED parse statistics
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
        
        # SIMPLIFIED connection parsing state - basic only
        self.parsed_connections: List[Connection] = []
        self.component_uuid_map: Dict[str, str] = {}  # component_path -> uuid
        self.port_uuid_map: Dict[str, str] = {}       # port_path -> uuid
    
    def parse_file(self, file_path: str) -> Tuple[List[Package], Dict[str, Any]]:
        """
        Parse ARXML file and return packages with basic connections
        SIMPLIFIED - removed interface_parser integration
        
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
        self.logger.info(f"Starting SIMPLIFIED ARXML parsing: {file_path} ({self.parse_stats['file_size']/1024/1024:.1f} MB)")
        
        try:
            # Parse XML with lxml - basic approach
            parser = etree.XMLParser(**self.parser_config)
            tree = etree.parse(str(file_path), parser)
            root = tree.getroot()
            
            print(f"🔧 XML root: {root.tag}")
            print(f"🔧 Namespaces: {root.nsmap}")
            
            # Create XML helper
            xml_helper = SimpleXMLHelper(root)
            
            # Clear connection parsing state
            self.parsed_connections.clear()
            self.component_uuid_map.clear()
            self.port_uuid_map.clear()
            
            # SIMPLIFIED parsing - no interface parser
            packages = self._parse_packages_simplified(root, xml_helper)
            
            # SIMPLIFIED connection parsing - basic only
            try:
                self._parse_basic_connections(root, xml_helper)
            except Exception as e:
                print(f"⚠️ Basic connection parsing failed: {e}")
                self.parsed_connections = []
            
            # Calculate statistics
            self.parse_stats['parse_time'] = time.time() - start_time
            self._calculate_basic_stats(packages)
            
            self.logger.info(f"SIMPLIFIED ARXML parsing completed in {self.parse_stats['parse_time']:.2f}s")
            self.logger.info(f"Parsed: {self.parse_stats['components_parsed']} components, "
                           f"{self.parse_stats['ports_parsed']} ports, "
                           f"{self.parse_stats['connections_parsed']} basic connections")
            
            # Build SIMPLIFIED metadata
            metadata = {
                'file_path': str(file_path),
                'file_size': self.parse_stats['file_size'],
                'parse_time': self.parse_stats['parse_time'],
                'statistics': self.parse_stats.copy(),
                'namespaces': xml_helper.namespaces,
                'autosar_version': self._detect_autosar_version(root),
                'connections': self._get_basic_connection_metadata()
            }
            
            return packages, metadata
            
        except etree.XMLSyntaxError as e:
            raise ARXMLParsingError(f"XML syntax error: {e}")
        except Exception as e:
            raise ARXMLParsingError(f"Parsing failed: {e}")
    
    def _parse_packages_simplified(self, root: etree.Element, xml_helper: SimpleXMLHelper) -> List[Package]:
        """Parse AR-PACKAGES from XML root - SIMPLIFIED without interface parsing"""
        packages = []
        
        print("🔧 SIMPLIFIED package parsing...")
        
        try:
            # Find AR-PACKAGES container first
            ar_packages_containers = xml_helper.find_elements(root, "AR-PACKAGES")
            print(f"🔧 Found {len(ar_packages_containers)} AR-PACKAGES containers")
            
            # Collect all package elements
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
            
            # Parse packages WITHOUT interface information
            for pkg_elem in all_package_elements:
                try:
                    package = self._parse_package_simplified(pkg_elem, xml_helper)
                    if package:
                        packages.append(package)
                        print(f"✅ Parsed package: {package.short_name}")
                except Exception as e:
                    print(f"❌ Failed to parse package: {e}")
                    continue
            
            self.parse_stats['packages_parsed'] = len(packages)
            return packages
            
        except Exception as e:
            print(f"❌ Package parsing failed: {e}")
            raise ARXMLParsingError(f"Failed to parse packages: {e}")
    
    def _parse_package_simplified(self, pkg_elem: etree.Element, xml_helper: SimpleXMLHelper, parent_path: str = "") -> Optional[Package]:
        """Parse individual AR-PACKAGE element - SIMPLIFIED"""
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
                        sub_package = self._parse_package_simplified(sub_pkg_elem, xml_helper, full_path)
                        if sub_package:
                            package.sub_packages.append(sub_package)
                    except Exception as e:
                        print(f"⚠️ Failed to parse sub-package: {e}")
            
            # Parse components in ELEMENTS section
            elements_elem = xml_helper.find_element(pkg_elem, "ELEMENTS")
            if elements_elem is not None:
                components = self._parse_components_simplified(elements_elem, xml_helper, full_path)
                package.components.extend(components)
                print(f"✅ Parsed {len(components)} components in package {short_name}")
            
            return package
            
        except Exception as e:
            print(f"❌ Failed to parse package: {e}")
            return None
    
    def _parse_components_simplified(self, elements_elem: etree.Element, xml_helper: SimpleXMLHelper, package_path: str) -> List[Component]:
        """Parse components from ELEMENTS section - SIMPLIFIED"""
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
                    component = self._parse_component_simplified(comp_elem, xml_helper, component_type, package_path)
                    if component:
                        components.append(component)
                        self.parse_stats['components_parsed'] += 1
                except Exception as e:
                    print(f"⚠️ Failed to parse component: {e}")
        
        return components
    
    def _parse_component_simplified(self, comp_elem: etree.Element, xml_helper: SimpleXMLHelper, 
                                   component_type: ComponentType, package_path: str) -> Optional[Component]:
        """Parse individual component - SIMPLIFIED without interface linking"""
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
            
            # Store component reference mapping for basic connection resolution
            component_ref = f"{package_path}/{short_name}"
            self.component_uuid_map[component_ref] = component.uuid
            self.component_uuid_map[short_name] = component.uuid  # Also store by name
            
            # Parse ports - SIMPLIFIED without interface linking
            ports_elem = xml_helper.find_element(comp_elem, "PORTS")
            if ports_elem is not None:
                ports = self._parse_ports_simplified(ports_elem, xml_helper, component.uuid)
                component.provided_ports = [p for p in ports if p.is_provided]
                component.required_ports = [p for p in ports if p.is_required]
                self.parse_stats['ports_parsed'] += len(ports)
                
                # Store port reference mappings for basic connection resolution
                for port in ports:
                    port_ref = f"{component_ref}/{port.short_name}"
                    full_port_path = f"{component.uuid}#{port.short_name}"
                    self.port_uuid_map[port_ref] = port.uuid
                    self.port_uuid_map[full_port_path] = port.uuid
            
            return component
            
        except Exception as e:
            print(f"❌ Failed to parse component: {e}")
            return None
    
    def _parse_ports_simplified(self, ports_elem: etree.Element, xml_helper: SimpleXMLHelper, component_uuid: str) -> List[Port]:
        """Parse ports from PORTS section - SIMPLIFIED without interface linking"""
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
                    port = self._parse_port_simplified(port_elem, xml_helper, port_type, component_uuid)
                    if port:
                        ports.append(port)
                except Exception as e:
                    print(f"⚠️ Failed to parse port: {e}")
        
        return ports
    
    def _parse_port_simplified(self, port_elem: etree.Element, xml_helper: SimpleXMLHelper, 
                              port_type: PortType, component_uuid: str) -> Optional[Port]:
        """Parse individual port - SIMPLIFIED without interface resolution"""
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
            
            # Parse basic interface reference - store as string only
            interface_ref = self._get_interface_reference_basic(port_elem, xml_helper)
            if interface_ref:
                port.interface_ref = interface_ref
            
            return port
            
        except Exception as e:
            print(f"❌ Failed to parse port: {e}")
            return None
    
    def _parse_basic_connections(self, root: etree.Element, xml_helper: SimpleXMLHelper):
        """Parse basic connections - SIMPLIFIED without complex UUID mapping"""
        try:
            print("🔗 Searching for basic connectors in XML...")
            
            # Find all CONNECTORS elements throughout the document
            connectors_elements = xml_helper.find_elements(root, "CONNECTORS")
            print(f"🔗 Found {len(connectors_elements)} CONNECTORS elements")
            
            for connectors_elem in connectors_elements:
                # Parse basic assembly and delegation connectors
                self._parse_basic_connectors_element(connectors_elem, xml_helper)
            
            self.parse_stats['connections_parsed'] = len(self.parsed_connections)
            print(f"🔗 Basic connection parsing completed: {len(self.parsed_connections)} connections")
            
        except Exception as e:
            print(f"❌ Basic connection parsing failed: {e}")
            raise
    
    def _parse_basic_connectors_element(self, connectors_elem: etree.Element, xml_helper: SimpleXMLHelper):
        """Parse individual CONNECTORS element - SIMPLIFIED"""
        try:
            # Parse ASSEMBLY-SW-CONNECTOR elements
            assembly_connectors = xml_helper.find_elements(connectors_elem, "ASSEMBLY-SW-CONNECTOR")
            print(f"🔗 Found {len(assembly_connectors)} assembly connectors")
            
            for conn_elem in assembly_connectors:
                connection = self._parse_basic_assembly_connector(conn_elem, xml_helper)
                if connection:
                    self.parsed_connections.append(connection)
            
            # Parse DELEGATION-SW-CONNECTOR elements
            delegation_connectors = xml_helper.find_elements(connectors_elem, "DELEGATION-SW-CONNECTOR")
            print(f"🔗 Found {len(delegation_connectors)} delegation connectors")
            
            for conn_elem in delegation_connectors:
                connection = self._parse_basic_delegation_connector(conn_elem, xml_helper)
                if connection:
                    self.parsed_connections.append(connection)
            
        except Exception as e:
            print(f"❌ Basic connectors element parsing failed: {e}")
    
    def _parse_basic_assembly_connector(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[Connection]:
        """Parse ASSEMBLY-SW-CONNECTOR element - SIMPLIFIED"""
        try:
            short_name = xml_helper.get_text(conn_elem, "SHORT-NAME")
            if not short_name:
                print("⚠️ Assembly connector without SHORT-NAME")
                return None
            
            print(f"🔗 Parsing basic assembly connector: {short_name}")
            
            # Get description
            desc = self._get_description(conn_elem, xml_helper)
            
            # Parse basic provider endpoint
            provider_endpoint = self._parse_basic_provider_endpoint(conn_elem, xml_helper)
            if not provider_endpoint:
                print(f"⚠️ Assembly connector {short_name} missing provider endpoint")
                return None
            
            # Parse basic requester endpoint
            requester_endpoint = self._parse_basic_requester_endpoint(conn_elem, xml_helper)
            if not requester_endpoint:
                print(f"⚠️ Assembly connector {short_name} missing requester endpoint")
                return None
            
            # Create basic connection
            connection = Connection(
                short_name=short_name,
                desc=desc,
                connection_type=ConnectionType.ASSEMBLY,
                provider_endpoint=provider_endpoint,
                requester_endpoint=requester_endpoint
            )
            
            print(f"✅ Created basic assembly connection: {short_name}")
            return connection
            
        except Exception as e:
            print(f"❌ Basic assembly connector parsing failed: {e}")
            return None
    
    def _parse_basic_delegation_connector(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[Connection]:
        """Parse DELEGATION-SW-CONNECTOR element - SIMPLIFIED"""
        try:
            short_name = xml_helper.get_text(conn_elem, "SHORT-NAME")
            if not short_name:
                print("⚠️ Delegation connector without SHORT-NAME")
                return None
            
            print(f"🔗 Parsing basic delegation connector: {short_name}")
            
            # Get description
            desc = self._get_description(conn_elem, xml_helper)
            
            # For basic delegation, create dummy endpoints
            # In a full implementation, you'd parse INNER-PORT-IREF and OUTER-PORT-REF
            dummy_provider = ConnectionEndpoint(component_uuid="delegation_provider", port_uuid="delegation_port_p")
            dummy_requester = ConnectionEndpoint(component_uuid="delegation_requester", port_uuid="delegation_port_r")
            
            # Create basic connection
            connection = Connection(
                short_name=short_name,
                desc=desc,
                connection_type=ConnectionType.DELEGATION,
                provider_endpoint=dummy_provider,
                requester_endpoint=dummy_requester
            )
            
            print(f"✅ Created basic delegation connection: {short_name}")
            return connection
            
        except Exception as e:
            print(f"❌ Basic delegation connector parsing failed: {e}")
            return None
    
    def _parse_basic_provider_endpoint(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[ConnectionEndpoint]:
        """Parse basic provider endpoint - SIMPLIFIED"""
        try:
            # Look for PROVIDER-IREF
            provider_iref = xml_helper.find_element(conn_elem, "PROVIDER-IREF")
            if not provider_iref:
                return None
            
            # Get basic component and port references
            context_component_ref = xml_helper.get_text(provider_iref, "CONTEXT-COMPONENT-REF")
            target_port_ref = xml_helper.get_text(provider_iref, "TARGET-P-PORT-REF")
            
            if not context_component_ref or not target_port_ref:
                print("⚠️ Provider endpoint missing component or port reference")
                return None
            
            # Basic resolution - use reference strings as UUIDs for now
            component_uuid = self._resolve_basic_component_reference(context_component_ref)
            port_uuid = self._resolve_basic_port_reference(target_port_ref, component_uuid)
            
            if not component_uuid or not port_uuid:
                # Fallback to using references directly
                component_uuid = context_component_ref
                port_uuid = target_port_ref
            
            return ConnectionEndpoint(
                component_uuid=component_uuid,
                port_uuid=port_uuid
            )
            
        except Exception as e:
            print(f"❌ Basic provider endpoint parsing failed: {e}")
            return None
    
    def _parse_basic_requester_endpoint(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[ConnectionEndpoint]:
        """Parse basic requester endpoint - SIMPLIFIED"""
        try:
            # Look for REQUESTER-IREF
            requester_iref = xml_helper.find_element(conn_elem, "REQUESTER-IREF")
            if not requester_iref:
                return None
            
            # Get basic component and port references
            context_component_ref = xml_helper.get_text(requester_iref, "CONTEXT-COMPONENT-REF")
            target_port_ref = xml_helper.get_text(requester_iref, "TARGET-R-PORT-REF")
            
            if not context_component_ref or not target_port_ref:
                print("⚠️ Requester endpoint missing component or port reference")
                return None
            
            # Basic resolution - use reference strings as UUIDs for now
            component_uuid = self._resolve_basic_component_reference(context_component_ref)
            port_uuid = self._resolve_basic_port_reference(target_port_ref, component_uuid)
            
            if not component_uuid or not port_uuid:
                # Fallback to using references directly
                component_uuid = context_component_ref
                port_uuid = target_port_ref
            
            return ConnectionEndpoint(
                component_uuid=component_uuid,
                port_uuid=port_uuid
            )
            
        except Exception as e:
            print(f"❌ Basic requester endpoint parsing failed: {e}")
            return None
    
    def _resolve_basic_component_reference(self, component_ref: str) -> Optional[str]:
        """Resolve basic component reference - SIMPLIFIED"""
        try:
            # Simple implementation
            if component_ref in self.component_uuid_map:
                return self.component_uuid_map[component_ref]
            
            # Try to match by component name (fallback)
            component_name = component_ref.split('/')[-1] if '/' in component_ref else component_ref
            for ref_path, uuid in self.component_uuid_map.items():
                if ref_path.endswith(component_name):
                    return uuid
            
            print(f"⚠️ Could not resolve basic component reference: {component_ref}")
            return component_ref  # Use reference as UUID fallback
            
        except Exception as e:
            print(f"❌ Basic component reference resolution failed: {e}")
            return component_ref
    
    def _resolve_basic_port_reference(self, port_ref: str, component_uuid: str) -> Optional[str]:
        """Resolve basic port reference - SIMPLIFIED"""
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
            
            print(f"⚠️ Could not resolve basic port reference: {port_ref}")
            return port_ref  # Use reference as UUID fallback
            
        except Exception as e:
            print(f"❌ Basic port reference resolution failed: {e}")
            return port_ref
    
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
    
    def _get_interface_reference_basic(self, port_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[str]:
        """Get basic interface reference from port - SIMPLIFIED"""
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
    
    def _calculate_basic_stats(self, packages: List[Package]):
        """Calculate basic parsing statistics - SIMPLIFIED"""
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
            print(f"⚠️ Basic statistics calculation failed: {e}")
    
    def _get_basic_connection_metadata(self) -> Dict[str, Any]:
        """Get basic connection metadata - SIMPLIFIED"""
        try:
            if self.parsed_connections:
                connection_metadata = {}
                
                for connection in self.parsed_connections:
                    connection_metadata[connection.uuid] = {
                        'short_name': connection.short_name,
                        'connection_type': connection.connection_type.value,
                        'description': connection.desc
                    }
                
                return {
                    'connections': connection_metadata,
                    'connection_count': len(self.parsed_connections),
                    'connection_types': self._get_basic_connection_type_counts()
                }
            return {'connections': {}, 'connection_count': 0, 'connection_types': {}}
        except Exception as e:
            print(f"⚠️ Basic connection metadata generation failed: {e}")
            return {'connections': {}, 'connection_count': 0, 'connection_types': {}}
    
    def _get_basic_connection_type_counts(self) -> Dict[str, int]:
        """Get count of connections by type - SIMPLIFIED"""
        try:
            type_counts = {}
            for connection in self.parsed_connections:
                conn_type = connection.connection_type.value
                type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
            return type_counts
        except Exception:
            return {}
    
    # SIMPLIFIED public methods for connection access
    def get_parsed_connections(self) -> List[Connection]:
        """Get all parsed connections - SIMPLIFIED"""
        return self.parsed_connections.copy()
    
    def get_connections_for_component(self, component_uuid: str) -> List[Connection]:
        """Get connections involving a specific component - SIMPLIFIED"""
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
        """Get connections involving a specific port - SIMPLIFIED"""
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
        """Get basic connection parsing summary - SIMPLIFIED"""
        return {
            'total_connections': len(self.parsed_connections),
            'connection_types': self._get_basic_connection_type_counts(),
            'parse_time': self.parse_stats.get('parse_time', 0),
            'component_mappings': len(self.component_uuid_map),
            'port_mappings': len(self.port_uuid_map)
        }
    
    def get_parser_statistics(self) -> Dict[str, Any]:
        """Get parser statistics - SIMPLIFIED"""
        return {
            'total_packages': self.parse_stats.get('packages_parsed', 0),
            'total_components': self.parse_stats.get('components_parsed', 0),
            'total_ports': self.parse_stats.get('ports_parsed', 0),
            'total_connections': self.parse_stats.get('connections_parsed', 0),
            'parse_time': self.parse_stats.get('parse_time', 0),
            'file_size': self.parse_stats.get('file_size', 0)
        }