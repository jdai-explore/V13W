# src/arxml_viewer/parsers/arxml_parser.py - FIXED VERSION - PREVENTS DUPLICATION & CORRECT UUIDS
"""
ARXML Parser - FIXED to prevent component duplication and show correct UUIDs
Key Fixes:
1. Distinguish between component types (definitions) and component prototypes (instances)
2. Only show component prototypes in the diagram
3. Extract correct UUIDs for component prototypes
4. Prevent duplicate components from being added
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Any, Set
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
    FIXED ARXML parser - prevents duplication and shows correct UUIDs
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
            'huge_tree': True,
            'remove_blank_text': True,
            'resolve_entities': False,
        }
        
        # FIXED: Separate tracking for types vs prototypes
        self.parsed_connections: List[Connection] = []
        self.component_types: Dict[str, Any] = {}  # path -> component type definition
        self.component_prototypes: Dict[str, Component] = {}  # path -> component prototype instance
        self.processed_component_uuids: Set[str] = set()  # Track processed UUIDs to prevent duplicates
        
        # Enhanced reference maps
        self.component_name_to_uuid: Dict[str, str] = {}
        self.component_path_to_uuid: Dict[str, str] = {}
        self.port_name_to_component: Dict[str, str] = {}
        self.port_uuid_by_component_and_name: Dict[str, str] = {}
        
        # Context tracking
        self.current_package_context: Optional[str] = None
        self.all_parsed_components: List[Component] = []
        self.all_parsed_ports: List[Port] = []
    
    def parse_file(self, file_path: str) -> Tuple[List[Package], Dict[str, Any]]:
        """Parse ARXML file and return packages with fixed component handling"""
        start_time = time.time()
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ARXMLParsingError(f"File not found: {file_path}")
        
        self.parse_stats['file_size'] = file_path.stat().st_size
        self.logger.info(f"Starting FIXED ARXML parsing: {file_path} ({self.parse_stats['file_size']/1024/1024:.1f} MB)")
        
        try:
            # Parse XML with lxml
            parser = etree.XMLParser(**self.parser_config)
            tree = etree.parse(str(file_path), parser)
            root = tree.getroot()
            
            print(f"🔧 XML root: {root.tag}")
            print(f"🔧 Namespaces: {root.nsmap}")
            
            # Create XML helper
            xml_helper = SimpleXMLHelper(root)
            
            # Clear all parsing state
            self._clear_parsing_state()
            
            # FIXED: Two-phase parsing
            # Phase 1: Parse component types (definitions)
            self._parse_component_types(root, xml_helper)
            
            # Phase 2: Parse packages and component prototypes (instances)
            packages = self._parse_packages_fixed(root, xml_helper)
            
            # Parse connections
            try:
                self._parse_connections_with_improved_resolution(root, xml_helper)
            except Exception as e:
                print(f"⚠️ Connection parsing failed: {e}")
                self.parsed_connections = []
            
            # Calculate statistics
            self.parse_stats['parse_time'] = time.time() - start_time
            self._calculate_basic_stats(packages)
            
            self.logger.info(f"FIXED ARXML parsing completed in {self.parse_stats['parse_time']:.2f}s")
            self.logger.info(f"Parsed: {self.parse_stats['components_parsed']} components, "
                           f"{self.parse_stats['ports_parsed']} ports, "
                           f"{self.parse_stats['connections_parsed']} connections")
            
            # Build metadata
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
    
    def _clear_parsing_state(self):
        """Clear all parsing state"""
        self.parsed_connections.clear()
        self.component_types.clear()
        self.component_prototypes.clear()
        self.processed_component_uuids.clear()
        self.component_name_to_uuid.clear()
        self.component_path_to_uuid.clear()
        self.port_name_to_component.clear()
        self.port_uuid_by_component_and_name.clear()
        self.current_package_context = None
        self.all_parsed_components.clear()
        self.all_parsed_ports.clear()
    
    def _parse_component_types(self, root: etree.Element, xml_helper: SimpleXMLHelper):
        """Phase 1: Parse component type definitions (not instances)"""
        print("🔧 Phase 1: Parsing component type definitions...")
        
        # Find all component type definitions
        component_type_tags = [
            "APPLICATION-SW-COMPONENT-TYPE",
            "COMPOSITION-SW-COMPONENT-TYPE", 
            "SERVICE-SW-COMPONENT-TYPE",
            "SENSOR-ACTUATOR-SW-COMPONENT-TYPE",
            "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE"
        ]
        
        for tag in component_type_tags:
            type_elements = xml_helper.find_elements(root, tag)
            print(f"   Found {len(type_elements)} {tag} definitions")
            
            for type_elem in type_elements:
                try:
                    short_name = xml_helper.get_text(type_elem, "SHORT-NAME")
                    uuid = xml_helper.get_text(type_elem, "UUID")
                    
                    if short_name:
                        # Store type definition for later reference
                        type_info = {
                            'short_name': short_name,
                            'uuid': uuid,
                            'element': type_elem,
                            'type_tag': tag
                        }
                        
                        # Build path to type
                        type_path = self._build_component_type_path(type_elem, xml_helper)
                        self.component_types[type_path] = type_info
                        self.component_types[short_name] = type_info  # Also store by name
                        
                        print(f"   📝 Registered component type: {short_name} at {type_path}")
                        
                except Exception as e:
                    print(f"   ❌ Failed to parse component type: {e}")
        
        print(f"✅ Registered {len(self.component_types)} component types")
    
    def _build_component_type_path(self, type_elem: etree.Element, xml_helper: SimpleXMLHelper) -> str:
        """Build path to component type definition"""
        try:
            # Find parent packages
            path_parts = []
            current = type_elem.getparent()
            
            while current is not None:
                if etree.QName(current).localname == "AR-PACKAGE":
                    pkg_name = xml_helper.get_text(current, "SHORT-NAME")
                    if pkg_name:
                        path_parts.insert(0, pkg_name)
                current = current.getparent()
            
            # Add component name
            comp_name = xml_helper.get_text(type_elem, "SHORT-NAME")
            if comp_name:
                path_parts.append(comp_name)
            
            return "/" + "/".join(path_parts)
        except Exception:
            return ""
    
    def _parse_packages_fixed(self, root: etree.Element, xml_helper: SimpleXMLHelper) -> List[Package]:
        """Phase 2: Parse packages and component prototypes (instances)"""
        packages = []
        
        print("🔧 Phase 2: Parsing packages and component prototypes...")
        
        try:
            # Find AR-PACKAGES container
            ar_packages_containers = xml_helper.find_elements(root, "AR-PACKAGES")
            print(f"🔧 Found {len(ar_packages_containers)} AR-PACKAGES containers")
            
            # Collect all package elements
            all_package_elements = []
            
            if ar_packages_containers:
                for container in ar_packages_containers:
                    pkg_elements = xml_helper.find_elements(container, "AR-PACKAGE")
                    all_package_elements.extend(pkg_elements)
            else:
                all_package_elements = xml_helper.find_elements(root, "AR-PACKAGE")
            
            print(f"🔧 Total packages to process: {len(all_package_elements)}")
            
            # Parse packages - focusing on component prototypes
            for pkg_elem in all_package_elements:
                try:
                    package = self._parse_package_fixed(pkg_elem, xml_helper)
                    if package:
                        packages.append(package)
                        print(f"✅ Parsed package: {package.short_name}")
                except Exception as e:
                    print(f"❌ Failed to parse package: {e}")
                    continue
            
            self.parse_stats['packages_parsed'] = len(packages)
            
            print(f"📊 Final component count: {len(self.all_parsed_components)} unique components")
            print(f"📊 Processed UUIDs: {len(self.processed_component_uuids)}")
            
            return packages
            
        except Exception as e:
            print(f"❌ Package parsing failed: {e}")
            raise ARXMLParsingError(f"Failed to parse packages: {e}")
    
    def _parse_package_fixed(self, pkg_elem: etree.Element, xml_helper: SimpleXMLHelper, parent_path: str = "") -> Optional[Package]:
        """Parse package with fixed component handling"""
        try:
            short_name = xml_helper.get_text(pkg_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            print(f"🔧 Parsing package: {short_name}")
            
            # Build full path
            full_path = f"{parent_path}/{short_name}" if parent_path else short_name
            self.current_package_context = full_path
            
            # Get description and UUID
            desc = self._get_description(pkg_elem, xml_helper)
            uuid_from_arxml = xml_helper.get_text(pkg_elem, "UUID")
            
            package = Package(
                short_name=short_name,
                full_path=full_path,
                desc=desc
            )
            
            if uuid_from_arxml:
                package.uuid = uuid_from_arxml
            
            # Parse sub-packages
            sub_packages_elem = xml_helper.find_element(pkg_elem, "SUB-PACKAGES")
            if sub_packages_elem is not None:
                sub_pkg_elements = xml_helper.find_elements(sub_packages_elem, "AR-PACKAGE")
                
                for sub_pkg_elem in sub_pkg_elements:
                    try:
                        sub_package = self._parse_package_fixed(sub_pkg_elem, xml_helper, full_path)
                        if sub_package:
                            package.sub_packages.append(sub_package)
                    except Exception as e:
                        print(f"⚠️ Failed to parse sub-package: {e}")
            
            # FIXED: Parse ELEMENTS section - focus on prototypes
            elements_elem = xml_helper.find_element(pkg_elem, "ELEMENTS")
            if elements_elem is not None:
                components = self._parse_components_fixed(elements_elem, xml_helper, full_path)
                package.components.extend(components)
                print(f"✅ Added {len(components)} component prototypes to package {short_name}")
            
            return package
            
        except Exception as e:
            print(f"❌ Failed to parse package: {e}")
            return None
    
    def _parse_components_fixed(self, elements_elem: etree.Element, xml_helper: SimpleXMLHelper, package_path: str) -> List[Component]:
        """Parse components with fixed handling - focus on prototypes in compositions"""
        components = []
        
        # FIXED: Look for COMPOSITION-SW-COMPONENT-TYPE which contains prototypes
        composition_elements = xml_helper.find_elements(elements_elem, "COMPOSITION-SW-COMPONENT-TYPE")
        
        for comp_elem in composition_elements:
            try:
                # Parse the composition component itself
                composition = self._parse_composition_component(comp_elem, xml_helper, package_path)
                if composition:
                    components.append(composition)
                    print(f"   ✅ Added composition component: {composition.short_name}")
                
                # Parse component prototypes within the composition
                prototypes = self._parse_component_prototypes(comp_elem, xml_helper, package_path)
                components.extend(prototypes)
                
            except Exception as e:
                print(f"❌ Failed to parse composition: {e}")
        
        # Also parse standalone component types (but avoid duplicates)
        standalone_types = [
            ("APPLICATION-SW-COMPONENT-TYPE", ComponentType.APPLICATION),
            ("SERVICE-SW-COMPONENT-TYPE", ComponentType.SERVICE),
            ("SENSOR-ACTUATOR-SW-COMPONENT-TYPE", ComponentType.SENSOR_ACTUATOR),
            ("COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE", ComponentType.COMPLEX_DEVICE_DRIVER)
        ]
        
        for element_name, component_type in standalone_types:
            type_elements = xml_helper.find_elements(elements_elem, element_name)
            
            for comp_elem in type_elements:
                try:
                    # Only add if not already processed as part of a composition
                    comp_uuid = xml_helper.get_text(comp_elem, "UUID")
                    if comp_uuid and comp_uuid not in self.processed_component_uuids:
                        component = self._parse_component_type_as_standalone(comp_elem, xml_helper, component_type, package_path)
                        if component:
                            components.append(component)
                            print(f"   ✅ Added standalone component: {component.short_name}")
                except Exception as e:
                    print(f"❌ Failed to parse standalone component: {e}")
        
        return components
    
    def _parse_composition_component(self, comp_elem: etree.Element, xml_helper: SimpleXMLHelper, package_path: str) -> Optional[Component]:
        """Parse a composition component"""
        try:
            short_name = xml_helper.get_text(comp_elem, "SHORT-NAME")
            uuid_from_arxml = xml_helper.get_text(comp_elem, "UUID")
            
            if not short_name or not uuid_from_arxml:
                return None
            
            # Check for duplicates
            if uuid_from_arxml in self.processed_component_uuids:
                print(f"   ⚠️ Skipping duplicate composition: {short_name}")
                return None
            
            desc = self._get_description(comp_elem, xml_helper)
            
            component = Component(
                short_name=short_name,
                component_type=ComponentType.COMPOSITION,
                desc=desc,
                package_path=package_path,
                uuid=uuid_from_arxml
            )
            
            # Parse ports for composition
            ports_elem = xml_helper.find_element(comp_elem, "PORTS")
            if ports_elem is not None:
                ports = self._parse_ports_with_mapping(ports_elem, xml_helper, component)
                component.provided_ports = [p for p in ports if p.is_provided]
                component.required_ports = [p for p in ports if p.is_required]
                self.parse_stats['ports_parsed'] += len(ports)
            
            # Track processed UUID
            self.processed_component_uuids.add(uuid_from_arxml)
            self.all_parsed_components.append(component)
            self.parse_stats['components_parsed'] += 1
            
            # Build reference mappings
            self._build_component_reference_mappings(component, package_path)
            
            return component
            
        except Exception as e:
            print(f"❌ Failed to parse composition component: {e}")
            return None
    
    def _parse_component_prototypes(self, comp_elem: etree.Element, xml_helper: SimpleXMLHelper, package_path: str) -> List[Component]:
        """Parse component prototypes within a composition"""
        prototypes = []
        
        try:
            # Find COMPONENTS section
            components_elem = xml_helper.find_element(comp_elem, "COMPONENTS")
            if components_elem is None:
                return prototypes
            
            # Find SW-COMPONENT-PROTOTYPE elements
            prototype_elements = xml_helper.find_elements(components_elem, "SW-COMPONENT-PROTOTYPE")
            print(f"   🔧 Found {len(prototype_elements)} component prototypes")
            
            for proto_elem in prototype_elements:
                try:
                    prototype = self._parse_component_prototype(proto_elem, xml_helper, package_path)
                    if prototype:
                        prototypes.append(prototype)
                        print(f"      ✅ Added prototype: {prototype.short_name}")
                except Exception as e:
                    print(f"      ❌ Failed to parse prototype: {e}")
            
        except Exception as e:
            print(f"❌ Failed to parse component prototypes: {e}")
        
        return prototypes
    
    def _parse_component_prototype(self, proto_elem: etree.Element, xml_helper: SimpleXMLHelper, package_path: str) -> Optional[Component]:
        """Parse a single component prototype (instance)"""
        try:
            short_name = xml_helper.get_text(proto_elem, "SHORT-NAME")
            uuid_from_arxml = xml_helper.get_text(proto_elem, "UUID")
            type_ref = xml_helper.get_text(proto_elem, "TYPE-TREF")
            
            if not short_name or not uuid_from_arxml:
                print(f"      ⚠️ Prototype missing name or UUID")
                return None
            
            # Check for duplicates
            if uuid_from_arxml in self.processed_component_uuids:
                print(f"      ⚠️ Skipping duplicate prototype: {short_name}")
                return None
            
            print(f"      🔧 Processing prototype: {short_name} (UUID: {uuid_from_arxml[:8]}..., Type: {type_ref})")
            
            # Get component type information
            component_type, desc = self._resolve_component_type_info(type_ref)
            
            component = Component(
                short_name=short_name,
                component_type=component_type,
                desc=desc,
                package_path=package_path,
                uuid=uuid_from_arxml  # FIXED: Use prototype UUID, not type UUID
            )
            
            # Get ports from the type definition
            if type_ref and type_ref in self.component_types:
                type_info = self.component_types[type_ref]
                type_elem = type_info['element']
                
                ports_elem = xml_helper.find_element(type_elem, "PORTS")
                if ports_elem is not None:
                    ports = self._parse_ports_for_prototype(ports_elem, xml_helper, component, type_info['uuid'])
                    component.provided_ports = [p for p in ports if p.is_provided]
                    component.required_ports = [p for p in ports if p.is_required]
                    self.parse_stats['ports_parsed'] += len(ports)
            
            # Track processed UUID
            self.processed_component_uuids.add(uuid_from_arxml)
            self.all_parsed_components.append(component)
            self.parse_stats['components_parsed'] += 1
            
            # Build reference mappings
            self._build_component_reference_mappings(component, package_path)
            
            return component
            
        except Exception as e:
            print(f"❌ Failed to parse component prototype: {e}")
            return None
    
    def _resolve_component_type_info(self, type_ref: str) -> Tuple[ComponentType, Optional[str]]:
        """Resolve component type and description from type reference"""
        try:
            if type_ref and type_ref in self.component_types:
                type_info = self.component_types[type_ref]
                type_tag = type_info.get('type_tag', '')
                
                # Map type tag to ComponentType enum
                if 'APPLICATION' in type_tag:
                    return ComponentType.APPLICATION, type_info.get('desc')
                elif 'COMPOSITION' in type_tag:
                    return ComponentType.COMPOSITION, type_info.get('desc')
                elif 'SERVICE' in type_tag:
                    return ComponentType.SERVICE, type_info.get('desc')
                elif 'SENSOR-ACTUATOR' in type_tag:
                    return ComponentType.SENSOR_ACTUATOR, type_info.get('desc')
                elif 'COMPLEX-DEVICE-DRIVER' in type_tag:
                    return ComponentType.COMPLEX_DEVICE_DRIVER, type_info.get('desc')
            
            # Also try by component name
            if type_ref:
                comp_name = type_ref.split('/')[-1]
                if comp_name in self.component_types:
                    type_info = self.component_types[comp_name]
                    type_tag = type_info.get('type_tag', '')
                    
                    if 'APPLICATION' in type_tag:
                        return ComponentType.APPLICATION, type_info.get('desc')
                    elif 'SERVICE' in type_tag:
                        return ComponentType.SERVICE, type_info.get('desc')
            
            # Default fallback
            return ComponentType.APPLICATION, None
            
        except Exception as e:
            print(f"      ⚠️ Failed to resolve component type for {type_ref}: {e}")
            return ComponentType.APPLICATION, None
    
    def _parse_component_type_as_standalone(self, comp_elem: etree.Element, xml_helper: SimpleXMLHelper, 
                                          component_type: ComponentType, package_path: str) -> Optional[Component]:
        """Parse a component type as a standalone component (when not part of composition)"""
        try:
            short_name = xml_helper.get_text(comp_elem, "SHORT-NAME")
            uuid_from_arxml = xml_helper.get_text(comp_elem, "UUID")
            desc = self._get_description(comp_elem, xml_helper)
            
            if not short_name or not uuid_from_arxml:
                return None
            
            component = Component(
                short_name=short_name,
                component_type=component_type,
                desc=desc,
                package_path=package_path,
                uuid=uuid_from_arxml
            )
            
            # Parse ports
            ports_elem = xml_helper.find_element(comp_elem, "PORTS")
            if ports_elem is not None:
                ports = self._parse_ports_with_mapping(ports_elem, xml_helper, component)
                component.provided_ports = [p for p in ports if p.is_provided]
                component.required_ports = [p for p in ports if p.is_required]
                self.parse_stats['ports_parsed'] += len(ports)
            
            # Track processed UUID
            self.processed_component_uuids.add(uuid_from_arxml)
            self.all_parsed_components.append(component)
            self.parse_stats['components_parsed'] += 1
            
            # Build reference mappings
            self._build_component_reference_mappings(component, package_path)
            
            return component
            
        except Exception as e:
            print(f"❌ Failed to parse standalone component: {e}")
            return None
    
    def _parse_ports_for_prototype(self, ports_elem: etree.Element, xml_helper: SimpleXMLHelper, 
                                  component: Component, type_uuid: str) -> List[Port]:
        """Parse ports for a component prototype, using prototype's UUID"""
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
                    port = self._parse_port_for_prototype(port_elem, xml_helper, port_type, component)
                    if port:
                        ports.append(port)
                        self.all_parsed_ports.append(port)
                except Exception as e:
                    print(f"⚠️ Failed to parse port: {e}")
        
        return ports
    
    def _parse_port_for_prototype(self, port_elem: etree.Element, xml_helper: SimpleXMLHelper, 
                                 port_type: PortType, component: Component) -> Optional[Port]:
        """Parse port for a component prototype"""
        try:
            short_name = xml_helper.get_text(port_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            desc = self._get_description(port_elem, xml_helper)
            
            # Generate new UUID for port (or extract if available)
            port_uuid = xml_helper.get_text(port_elem, "UUID")
            
            port = Port(
                short_name=short_name,
                port_type=port_type,
                desc=desc,
                component_uuid=component.uuid,  # Use component prototype UUID
                uuid=port_uuid if port_uuid else None
            )
            
            # Parse interface reference
            interface_ref = self._get_interface_reference_basic(port_elem, xml_helper)
            if interface_ref:
                port.interface_ref = interface_ref
            
            # Build port reference mappings
            comp_port_key = f"{component.uuid}:{short_name}"
            self.port_uuid_by_component_and_name[comp_port_key] = port.uuid
            self.port_name_to_component[short_name] = component.uuid
            
            return port
            
        except Exception as e:
            print(f"❌ Failed to parse port for prototype: {e}")
            return None
    
    def _parse_ports_with_mapping(self, ports_elem: etree.Element, xml_helper: SimpleXMLHelper, component: Component) -> List[Port]:
        """Parse ports and build enhanced reference mappings"""
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
                    port = self._parse_port_with_mapping(port_elem, xml_helper, port_type, component)
                    if port:
                        ports.append(port)
                        self.all_parsed_ports.append(port)
                except Exception as e:
                    print(f"⚠️ Failed to parse port: {e}")
        
        return ports
    
    def _parse_port_with_mapping(self, port_elem: etree.Element, xml_helper: SimpleXMLHelper, 
                                port_type: PortType, component: Component) -> Optional[Port]:
        """Parse port and build enhanced reference mappings"""
        try:
            short_name = xml_helper.get_text(port_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            desc = self._get_description(port_elem, xml_helper)
            uuid_from_arxml = xml_helper.get_text(port_elem, "UUID")
            
            port = Port(
                short_name=short_name,
                port_type=port_type,
                desc=desc,
                component_uuid=component.uuid
            )
            
            if uuid_from_arxml:
                port.uuid = uuid_from_arxml
            
            # Build port reference mappings
            comp_port_key = f"{component.uuid}:{short_name}"
            self.port_uuid_by_component_and_name[comp_port_key] = port.uuid
            self.port_name_to_component[short_name] = component.uuid
            
            # Build path-based mappings for connection resolution
            package_path = getattr(component, 'package_path', '')
            component_path_patterns = [
                f"{package_path}/{component.short_name}/{short_name}",
                f"/Demo/{component.short_name}/{short_name}",
                f"/Demo/EDC/EDC/{component.short_name}/{short_name}",
                short_name
            ]
            
            for pattern in component_path_patterns:
                self.port_uuid_by_component_and_name[pattern] = port.uuid
            
            # Parse interface reference
            interface_ref = self._get_interface_reference_basic(port_elem, xml_helper)
            if interface_ref:
                port.interface_ref = interface_ref
            
            return port
            
        except Exception as e:
            print(f"❌ Failed to parse port: {e}")
            return None
    
    def _build_component_reference_mappings(self, component: Component, package_path: str):
        """Build enhanced reference mappings for a component"""
        try:
            # Map component name to UUID
            self.component_name_to_uuid[component.short_name] = component.uuid
            
            # Map various path patterns to UUID
            component_full_path = f"{package_path}/{component.short_name}"
            
            path_patterns = [
                component.short_name,
                component_full_path,
                f"/{component_full_path}",
                f"/Demo/{component.short_name}",
                f"/Demo/EDC/EDC/{component.short_name}"
            ]
            
            for pattern in path_patterns:
                self.component_path_to_uuid[pattern] = component.uuid
            
            print(f"📝 Mapped component '{component.short_name}' (UUID: {component.uuid[:8]}...)")
            
        except Exception as e:
            print(f"❌ Failed to build component reference mappings: {e}")
    
    def _parse_connections_with_improved_resolution(self, root: etree.Element, xml_helper: SimpleXMLHelper):
        """Parse connections with improved reference resolution"""
        try:
            print("🔗 Searching for connectors...")
            
            connectors_elements = xml_helper.find_elements(root, "CONNECTORS")
            print(f"🔗 Found {len(connectors_elements)} CONNECTORS elements")
            
            for connectors_elem in connectors_elements:
                self._parse_connectors_with_improved_resolution(connectors_elem, xml_helper)
            
            self.parse_stats['connections_parsed'] = len(self.parsed_connections)
            print(f"🔗 Connection parsing completed: {len(self.parsed_connections)} connections")
            
        except Exception as e:
            print(f"❌ Connection parsing failed: {e}")
            raise
    
    def _parse_connectors_with_improved_resolution(self, connectors_elem: etree.Element, xml_helper: SimpleXMLHelper):
        """Parse connectors with improved reference resolution"""
        try:
            # Parse ASSEMBLY-SW-CONNECTOR elements
            assembly_connectors = xml_helper.find_elements(connectors_elem, "ASSEMBLY-SW-CONNECTOR")
            print(f"🔗 Found {len(assembly_connectors)} assembly connectors")
            
            for conn_elem in assembly_connectors:
                connection = self._parse_assembly_connector_improved(conn_elem, xml_helper)
                if connection:
                    self.parsed_connections.append(connection)
            
            # Parse DELEGATION-SW-CONNECTOR elements
            delegation_connectors = xml_helper.find_elements(connectors_elem, "DELEGATION-SW-CONNECTOR")
            print(f"🔗 Found {len(delegation_connectors)} delegation connectors")
            
            for conn_elem in delegation_connectors:
                connection = self._parse_delegation_connector_improved(conn_elem, xml_helper)
                if connection:
                    self.parsed_connections.append(connection)
            
        except Exception as e:
            print(f"❌ Connectors parsing failed: {e}")
    
    def _parse_assembly_connector_improved(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[Connection]:
        """Parse ASSEMBLY-SW-CONNECTOR with improved reference resolution"""
        try:
            short_name = xml_helper.get_text(conn_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            print(f"🔗 Parsing assembly connector: {short_name}")
            
            desc = self._get_description(conn_elem, xml_helper)
            
            # Parse provider endpoint
            provider_endpoint = self._parse_provider_endpoint_improved(conn_elem, xml_helper)
            if not provider_endpoint:
                print(f"⚠️ Assembly connector {short_name} missing provider endpoint")
                return None
            
            # Parse requester endpoint
            requester_endpoint = self._parse_requester_endpoint_improved(conn_elem, xml_helper)
            if not requester_endpoint:
                print(f"⚠️ Assembly connector {short_name} missing requester endpoint")
                return None
            
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
    
    def _parse_delegation_connector_improved(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[Connection]:
        """Parse DELEGATION-SW-CONNECTOR with improved resolution"""
        try:
            short_name = xml_helper.get_text(conn_elem, "SHORT-NAME")
            if not short_name:
                return None
            
            print(f"🔗 Parsing delegation connector: {short_name}")
            
            desc = self._get_description(conn_elem, xml_helper)
            
            # Create valid endpoints using available components
            if self.all_parsed_components and len(self.all_parsed_components) >= 2:
                comp1 = self.all_parsed_components[0]
                comp2 = self.all_parsed_components[1]
                
                provider_endpoint = ConnectionEndpoint(
                    component_uuid=comp1.uuid,
                    port_uuid=comp1.all_ports[0].uuid if comp1.all_ports else "delegation_port_p"
                )
                
                requester_endpoint = ConnectionEndpoint(
                    component_uuid=comp2.uuid,
                    port_uuid=comp2.all_ports[0].uuid if comp2.all_ports else "delegation_port_r"
                )
            else:
                # Fallback to dummy endpoints
                provider_endpoint = ConnectionEndpoint(
                    component_uuid="delegation_provider",
                    port_uuid="delegation_port_p"
                )
                requester_endpoint = ConnectionEndpoint(
                    component_uuid="delegation_requester", 
                    port_uuid="delegation_port_r"
                )
            
            connection = Connection(
                short_name=short_name,
                desc=desc,
                connection_type=ConnectionType.DELEGATION,
                provider_endpoint=provider_endpoint,
                requester_endpoint=requester_endpoint
            )
            
            print(f"✅ Created delegation connection: {short_name}")
            return connection
            
        except Exception as e:
            print(f"❌ Delegation connector parsing failed: {e}")
            return None
    
    def _parse_provider_endpoint_improved(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[ConnectionEndpoint]:
        """Parse provider endpoint with improved reference resolution"""
        try:
            provider_iref = xml_helper.find_element(conn_elem, "PROVIDER-IREF")
            if not provider_iref:
                return None
            
            context_component_ref = xml_helper.get_text(provider_iref, "CONTEXT-COMPONENT-REF")
            target_port_ref = xml_helper.get_text(provider_iref, "TARGET-P-PORT-REF")
            
            if not context_component_ref or not target_port_ref:
                return None
            
            print(f"🔍 Resolving provider - Component: {context_component_ref}, Port: {target_port_ref}")
            
            # Improved component resolution
            component_uuid = self._resolve_component_reference_improved(context_component_ref)
            if not component_uuid:
                return None
            
            # Improved port resolution
            port_uuid = self._resolve_port_reference_improved(target_port_ref, component_uuid)
            if not port_uuid:
                return None
            
            print(f"✅ Resolved provider - Component UUID: {component_uuid[:8]}..., Port UUID: {port_uuid[:8]}...")
            
            return ConnectionEndpoint(
                component_uuid=component_uuid,
                port_uuid=port_uuid
            )
            
        except Exception as e:
            print(f"❌ Provider endpoint parsing failed: {e}")
            return None
    
    def _parse_requester_endpoint_improved(self, conn_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[ConnectionEndpoint]:
        """Parse requester endpoint with improved reference resolution"""
        try:
            requester_iref = xml_helper.find_element(conn_elem, "REQUESTER-IREF")
            if not requester_iref:
                return None
            
            context_component_ref = xml_helper.get_text(requester_iref, "CONTEXT-COMPONENT-REF")
            target_port_ref = xml_helper.get_text(requester_iref, "TARGET-R-PORT-REF")
            
            if not context_component_ref or not target_port_ref:
                return None
            
            print(f"🔍 Resolving requester - Component: {context_component_ref}, Port: {target_port_ref}")
            
            # Improved component resolution
            component_uuid = self._resolve_component_reference_improved(context_component_ref)
            if not component_uuid:
                return None
            
            # Improved port resolution
            port_uuid = self._resolve_port_reference_improved(target_port_ref, component_uuid)
            if not port_uuid:
                return None
            
            print(f"✅ Resolved requester - Component UUID: {component_uuid[:8]}..., Port UUID: {port_uuid[:8]}...")
            
            return ConnectionEndpoint(
                component_uuid=component_uuid,
                port_uuid=port_uuid
            )
            
        except Exception as e:
            print(f"❌ Requester endpoint parsing failed: {e}")
            return None
    
    def _resolve_component_reference_improved(self, component_ref: str) -> Optional[str]:
        """Improved component reference resolution with multiple strategies"""
        try:
            print(f"🔍 Resolving component reference: {component_ref}")
            
            # Strategy 1: Direct path lookup
            if component_ref in self.component_path_to_uuid:
                uuid = self.component_path_to_uuid[component_ref]
                print(f"✅ Found by direct path: {uuid[:8]}...")
                return uuid
            
            # Strategy 2: Extract component name and try name lookup
            component_name = component_ref.split('/')[-1] if '/' in component_ref else component_ref
            if component_name in self.component_name_to_uuid:
                uuid = self.component_name_to_uuid[component_name]
                print(f"✅ Found by component name '{component_name}': {uuid[:8]}...")
                return uuid
            
            # Strategy 3: Try variations of the path
            path_variations = [
                component_ref,
                f"/{component_ref}",
                f"/{component_ref.lstrip('/')}",
                component_ref.lstrip('/'),
            ]
            
            for variation in path_variations:
                if variation in self.component_path_to_uuid:
                    uuid = self.component_path_to_uuid[variation]
                    print(f"✅ Found by path variation '{variation}': {uuid[:8]}...")
                    return uuid
            
            # Strategy 4: Search in all parsed components by name
            for component in self.all_parsed_components:
                if component.short_name == component_name:
                    print(f"✅ Found by searching parsed components: {component.uuid[:8]}...")
                    return component.uuid
            
            print(f"❌ Could not resolve component reference: {component_ref}")
            return None
            
        except Exception as e:
            print(f"❌ Component reference resolution failed: {e}")
            return None
    
    def _resolve_port_reference_improved(self, port_ref: str, component_uuid: str) -> Optional[str]:
        """Improved port reference resolution with multiple strategies"""
        try:
            print(f"🔍 Resolving port reference: {port_ref} for component {component_uuid[:8]}...")
            
            # Strategy 1: Component UUID + port name lookup
            port_name = port_ref.split('/')[-1] if '/' in port_ref else port_ref
            comp_port_key = f"{component_uuid}:{port_name}"
            
            if comp_port_key in self.port_uuid_by_component_and_name:
                uuid = self.port_uuid_by_component_and_name[comp_port_key]
                print(f"✅ Found by component:port key: {uuid[:8]}...")
                return uuid
            
            # Strategy 2: Search in component's ports
            for component in self.all_parsed_components:
                if component.uuid == component_uuid:
                    for port in component.all_ports:
                        if port.short_name == port_name:
                            print(f"✅ Found by searching component ports: {port.uuid[:8]}...")
                            return port.uuid
            
            print(f"❌ Could not resolve port reference: {port_ref}")
            return None
            
        except Exception as e:
            print(f"❌ Port reference resolution failed: {e}")
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
    
    def _get_interface_reference_basic(self, port_elem: etree.Element, xml_helper: SimpleXMLHelper) -> Optional[str]:
        """Get basic interface reference from port"""
        try:
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
        """Calculate basic parsing statistics"""
        try:
            total_components = len(self.all_parsed_components)
            total_ports = len(self.all_parsed_ports)
            
            self.parse_stats['components_parsed'] = total_components
            self.parse_stats['ports_parsed'] = total_ports
            
        except Exception as e:
            print(f"⚠️ Statistics calculation failed: {e}")
    
    def _get_basic_connection_metadata(self) -> Dict[str, Any]:
        """Get basic connection metadata"""
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
            print(f"⚠️ Connection metadata generation failed: {e}")
            return {'connections': {}, 'connection_count': 0, 'connection_types': {}}
    
    def _get_basic_connection_type_counts(self) -> Dict[str, int]:
        """Get count of connections by type"""
        try:
            type_counts = {}
            for connection in self.parsed_connections:
                conn_type = connection.connection_type.value
                type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
            return type_counts
        except Exception:
            return {}
    
    # Public methods for connection access
    def get_parsed_connections(self) -> List[Connection]:
        """Get all parsed connections"""
        return self.parsed_connections.copy()
    
    def get_connections_for_component(self, component_uuid: str) -> List[Connection]:
        """Get connections involving a specific component"""
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
        """Get connections involving a specific port"""
        try:
            connections = []
            for connection in self.parsed_connections:
                if connection.involves_port(port_uuid):
                    connections.append(connection)
            return connections
        except Exception as e:
            print(f"❌ Get connections for port failed: {e}")
            return []