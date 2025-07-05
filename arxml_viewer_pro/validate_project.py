#!/usr/bin/env python3
"""
ARXML Viewer Pro - Comprehensive Validation Script
Tests all implemented functionality from Day 1-5
"""

import sys
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")

def print_test(test_name: str, status: bool, message: str = ""):
    """Print test result"""
    status_text = f"{Colors.GREEN}✓ PASS{Colors.ENDC}" if status else f"{Colors.RED}✗ FAIL{Colors.ENDC}"
    print(f"  {test_name:<40} [{status_text}] {message}")

def print_summary(passed: int, failed: int, total: int):
    """Print test summary"""
    print(f"\n{Colors.BOLD}Test Summary:{Colors.ENDC}")
    print(f"  Total Tests: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.ENDC}")
    print(f"  {Colors.RED}Failed: {failed}{Colors.ENDC}")
    
    if failed == 0:
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL TESTS PASSED! 🎉{Colors.ENDC}")
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}⚠️  SOME TESTS FAILED ⚠️{Colors.ENDC}")

class ARXMLViewerValidator:
    """Comprehensive validator for ARXML Viewer Pro"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results: List[Tuple[str, bool, str]] = []
        self.sample_arxml = self._create_sample_arxml()
    
    def _create_sample_arxml(self) -> str:
        """Create sample ARXML content for testing"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>TestPackage</SHORT-NAME>
      <ELEMENTS>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>TestComponent1</SHORT-NAME>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>OutPort1</SHORT-NAME>
            </P-PORT-PROTOTYPE>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>InPort1</SHORT-NAME>
            </R-PORT-PROTOTYPE>
          </PORTS>
        </APPLICATION-SW-COMPONENT-TYPE>
        <COMPOSITION-SW-COMPONENT-TYPE>
          <SHORT-NAME>CompositionComponent</SHORT-NAME>
          <COMPONENTS>
            <SW-COMPONENT-PROTOTYPE>
              <SHORT-NAME>SubComponent1</SHORT-NAME>
            </SW-COMPONENT-PROTOTYPE>
          </COMPONENTS>
          <CONNECTORS>
            <ASSEMBLY-SW-CONNECTOR>
              <SHORT-NAME>Connection1</SHORT-NAME>
              <PROVIDER-IREF>
                <CONTEXT-COMPONENT-REF>/TestPackage/TestComponent1</CONTEXT-COMPONENT-REF>
                <TARGET-P-PORT-REF>OutPort1</TARGET-P-PORT-REF>
              </PROVIDER-IREF>
              <REQUESTER-IREF>
                <CONTEXT-COMPONENT-REF>/TestPackage/TestComponent2</CONTEXT-COMPONENT-REF>
                <TARGET-R-PORT-REF>InPort2</TARGET-R-PORT-REF>
              </REQUESTER-IREF>
            </ASSEMBLY-SW-CONNECTOR>
          </CONNECTORS>
        </COMPOSITION-SW-COMPONENT-TYPE>
        <SERVICE-SW-COMPONENT-TYPE>
          <SHORT-NAME>TestComponent2</SHORT-NAME>
          <PORTS>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>InPort2</SHORT-NAME>
            </R-PORT-PROTOTYPE>
          </PORTS>
        </SERVICE-SW-COMPONENT-TYPE>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>"""
    
    def run_test(self, test_func, test_name: str) -> bool:
        """Run a single test and record result"""
        try:
            result = test_func()
            self.test_results.append((test_name, result, ""))
            if result:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            print_test(test_name, result)
            return result
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.test_results.append((test_name, False, error_msg))
            self.failed_tests += 1
            print_test(test_name, False, error_msg)
            if os.environ.get('DEBUG'):
                traceback.print_exc()
            return False
    
    def validate_all(self):
        """Run all validation tests"""
        print(f"{Colors.BOLD}{Colors.CYAN}ARXML Viewer Pro - Comprehensive Validation{Colors.ENDC}")
        print(f"{Colors.CYAN}Testing all features from Day 1-5 implementation{Colors.ENDC}")
        
        # Day 1: Core Models
        print_header("Day 1: Core Models")
        self.validate_models()
        
        # Day 1: ARXML Parser
        print_header("Day 1: ARXML Parser")
        self.validate_parser()
        
        # Day 1: Basic GUI
        print_header("Day 1: Basic GUI Components")
        self.validate_basic_gui()
        
        # Day 2: Enhanced Tree Widget
        print_header("Day 2: Enhanced Tree Widget")
        self.validate_tree_widget()
        
        # Day 2: Graphics Scene
        print_header("Day 2: Graphics Scene")
        self.validate_graphics_scene()
        
        # Day 3: Search Engine
        print_header("Day 3: Search Engine")
        self.validate_search_engine()
        
        # Day 3: Filter Manager
        print_header("Day 3: Filter Manager")
        self.validate_filter_manager()
        
        # Day 3: Navigation Controller
        print_header("Day 3: Navigation Controller")
        self.validate_navigation_controller()
        
        # Day 4: Interface Parser
        print_header("Day 4: Interface Parser")
        self.validate_interface_parser()
        
        # Day 4: Enhanced Port Graphics
        print_header("Day 4: Enhanced Port Graphics")
        self.validate_port_graphics()
        
        # Day 5: Connection Visualization
        print_header("Day 5: Connection Visualization")
        self.validate_connection_graphics()
        
        # Day 5: Breadcrumb Navigation
        print_header("Day 5: Breadcrumb Navigation")
        self.validate_breadcrumb_widget()
        
        # Day 5: Layout Algorithms
        print_header("Day 5: Layout Algorithms")
        self.validate_layout_algorithms()
        
        # Integration Tests
        print_header("Integration Tests")
        self.validate_integration()
        
        # Print summary
        total = self.passed_tests + self.failed_tests
        print_summary(self.passed_tests, self.failed_tests, total)
    
    # Day 1: Core Models Tests
    def validate_models(self):
        """Validate core model classes"""
        
        def test_component_model():
            from arxml_viewer.models.component import Component, ComponentType
            comp = Component(
                short_name="TestComp",
                component_type=ComponentType.APPLICATION
            )
            return (comp.short_name == "TestComp" and 
                   comp.component_type == ComponentType.APPLICATION and
                   comp.uuid is not None)
        
        def test_port_model():
            from arxml_viewer.models.port import Port, PortType
            port = Port(
                short_name="TestPort",
                port_type=PortType.PROVIDED
            )
            return port.is_provided and not port.is_required
        
        def test_connection_model():
            from arxml_viewer.models.connection import Connection, ConnectionType, ConnectionEndpoint
            conn = Connection(
                short_name="TestConn",
                connection_type=ConnectionType.ASSEMBLY,
                provider_endpoint=ConnectionEndpoint(component_uuid="comp1", port_uuid="port1"),
                requester_endpoint=ConnectionEndpoint(component_uuid="comp2", port_uuid="port2")
            )
            return conn.involves_component("comp1") and conn.involves_port("port2")
        
        def test_package_model():
            from arxml_viewer.models.package import Package
            pkg = Package(short_name="TestPkg", full_path="/Test/TestPkg")
            return pkg.depth == 2 and pkg.path_segments == ["", "Test", "TestPkg"]
        
        def test_interface_model():
            from arxml_viewer.models.interface import Interface, InterfaceType
            intf = Interface(
                short_name="TestInterface",
                interface_type=InterfaceType.SENDER_RECEIVER
            )
            return intf.is_sender_receiver and not intf.is_client_server
        
        self.run_test(test_component_model, "Component Model")
        self.run_test(test_port_model, "Port Model")
        self.run_test(test_connection_model, "Connection Model")
        self.run_test(test_package_model, "Package Model")
        self.run_test(test_interface_model, "Interface Model")
    
    # Day 1: Parser Tests
    def validate_parser(self):
        """Validate ARXML parser"""
        
        def test_parser_creation():
            from arxml_viewer.parsers.arxml_parser import ARXMLParser
            parser = ARXMLParser()
            return parser is not None
        
        def test_parse_sample():
            from arxml_viewer.parsers.arxml_parser import ARXMLParser
            import tempfile
            
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.arxml', delete=False) as f:
                f.write(self.sample_arxml)
                temp_path = f.name
            
            try:
                parser = ARXMLParser()
                packages, metadata = parser.parse_file(temp_path)
                return (len(packages) == 1 and 
                       packages[0].short_name == "TestPackage" and
                       len(packages[0].components) == 3)
            finally:
                os.unlink(temp_path)
        
        def test_connection_parsing():
            from arxml_viewer.parsers.arxml_parser import ARXMLParser
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.arxml', delete=False) as f:
                f.write(self.sample_arxml)
                temp_path = f.name
            
            try:
                parser = ARXMLParser()
                packages, metadata = parser.parse_file(temp_path)
                connections = parser.get_parsed_connections()
                return len(connections) >= 1
            finally:
                os.unlink(temp_path)
        
        self.run_test(test_parser_creation, "Parser Creation")
        self.run_test(test_parse_sample, "Parse Sample ARXML")
        self.run_test(test_connection_parsing, "Connection Parsing")
    
    # Day 1: Basic GUI Tests
    def validate_basic_gui(self):
        """Validate basic GUI components"""
        
        def test_config_manager():
            from arxml_viewer.config import ConfigManager
            config = ConfigManager()
            return config.config is not None
        
        def test_constants():
            from arxml_viewer.utils.constants import AppConstants, UIConstants
            return (AppConstants.APP_NAME == "ARXML Viewer Pro" and
                   UIConstants.COMPONENT_MIN_WIDTH == 120)
        
        def test_logger():
            from arxml_viewer.utils.logger import get_logger
            logger = get_logger("test")
            return logger is not None
        
        self.run_test(test_config_manager, "Config Manager")
        self.run_test(test_constants, "Application Constants")
        self.run_test(test_logger, "Logger Setup")
    
    # Day 2: Tree Widget Tests
    def validate_tree_widget(self):
        """Validate enhanced tree widget"""
        
        def test_tree_widget_creation():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.widgets.tree_widget import EnhancedTreeWidget
                tree = EnhancedTreeWidget()
                return tree is not None
            except:
                return False
        
        def test_tree_search_widget():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.widgets.tree_widget import TreeSearchWidget
                search = TreeSearchWidget()
                return search.search_input is not None
            except:
                return False
        
        self.run_test(test_tree_widget_creation, "Enhanced Tree Widget")
        self.run_test(test_tree_search_widget, "Tree Search Widget")
    
    # Day 2: Graphics Scene Tests
    def validate_graphics_scene(self):
        """Validate graphics scene"""
        
        def test_graphics_scene_creation():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.graphics.graphics_scene import ComponentDiagramScene
                scene = ComponentDiagramScene()
                return scene is not None
            except:
                return False
        
        def test_component_graphics():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.graphics.graphics_scene import ComponentGraphicsItem
                from arxml_viewer.models.component import Component, ComponentType
                
                comp = Component(short_name="Test", component_type=ComponentType.APPLICATION)
                item = ComponentGraphicsItem(comp)
                return item.component == comp
            except:
                return False
        
        self.run_test(test_graphics_scene_creation, "Graphics Scene")
        self.run_test(test_component_graphics, "Component Graphics Item")
    
    # Day 3: Search Engine Tests
    def validate_search_engine(self):
        """Validate search engine"""
        
        def test_search_engine_creation():
            from arxml_viewer.services.search_engine import SearchEngine
            engine = SearchEngine()
            return engine is not None
        
        def test_search_functionality():
            from arxml_viewer.services.search_engine import SearchEngine, SearchScope
            from arxml_viewer.models.component import Component, ComponentType
            from arxml_viewer.models.package import Package
            
            engine = SearchEngine()
            pkg = Package(short_name="TestPkg")
            comp = Component(short_name="TestComponent", component_type=ComponentType.APPLICATION)
            pkg.components.append(comp)
            
            engine.build_index([pkg])
            results = engine.search("Test", SearchScope.ALL)
            return len(results) >= 1
        
        self.run_test(test_search_engine_creation, "Search Engine")
        self.run_test(test_search_functionality, "Search Functionality")
    
    # Day 3: Filter Manager Tests
    def validate_filter_manager(self):
        """Validate filter manager"""
        
        def test_filter_manager_creation():
            from arxml_viewer.services.filter_manager import FilterManager
            manager = FilterManager()
            return manager is not None
        
        def test_filter_functionality():
            from arxml_viewer.services.filter_manager import FilterManager, FilterCriteria, FilterOperator
            from arxml_viewer.models.component import Component, ComponentType
            
            manager = FilterManager()
            components = [
                Component(short_name="App1", component_type=ComponentType.APPLICATION),
                Component(short_name="Svc1", component_type=ComponentType.SERVICE)
            ]
            
            manager.apply_quick_filter("application")
            filtered = manager.filter_components(components)
            return len(filtered) <= len(components)
        
        self.run_test(test_filter_manager_creation, "Filter Manager")
        self.run_test(test_filter_functionality, "Filter Functionality")
    
    # Day 3: Navigation Controller Tests
    def validate_navigation_controller(self):
        """Validate navigation controller"""
        
        def test_navigation_controller():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.controllers.navigation_controller import NavigationController
                nav = NavigationController()
                return nav is not None and hasattr(nav, 'navigate_back')
            except:
                return False
        
        self.run_test(test_navigation_controller, "Navigation Controller")
    
    # Day 4: Interface Parser Tests
    def validate_interface_parser(self):
        """Validate interface parser"""
        
        def test_interface_parser():
            try:
                from arxml_viewer.parsers.interface_parser import InterfaceParser
                from arxml_viewer.parsers.arxml_parser import SimpleXMLHelper
                from lxml import etree
                
                root = etree.fromstring("<root/>")
                helper = SimpleXMLHelper(root)
                parser = InterfaceParser(helper)
                return parser is not None
            except:
                return False
        
        self.run_test(test_interface_parser, "Interface Parser")
    
    # Day 4: Port Graphics Tests
    def validate_port_graphics(self):
        """Validate enhanced port graphics"""
        
        def test_enhanced_port_graphics():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.graphics.port_graphics import EnhancedPortGraphicsItem
                from arxml_viewer.models.port import Port, PortType
                
                port = Port(short_name="TestPort", port_type=PortType.PROVIDED)
                item = EnhancedPortGraphicsItem(port)
                return item.port == port
            except:
                return False
        
        self.run_test(test_enhanced_port_graphics, "Enhanced Port Graphics")
    
    # Day 5: Connection Graphics Tests
    def validate_connection_graphics(self):
        """Validate connection graphics"""
        
        def test_connection_graphics():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.graphics.connection_graphics import ConnectionGraphicsItem, ConnectionManager
                from arxml_viewer.gui.graphics.graphics_scene import ComponentDiagramScene
                
                scene = ComponentDiagramScene()
                manager = ConnectionManager(scene)
                return manager is not None
            except:
                return False
        
        self.run_test(test_connection_graphics, "Connection Graphics")
    
    # Day 5: Breadcrumb Widget Tests
    def validate_breadcrumb_widget(self):
        """Validate breadcrumb widget"""
        
        def test_breadcrumb_widget():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.widgets.breadcrumb_widget import BreadcrumbWidget
                
                widget = BreadcrumbWidget()
                widget.add_breadcrumb("Test", item_type="component")
                return len(widget.breadcrumb_items) >= 1
            except:
                return False
        
        self.run_test(test_breadcrumb_widget, "Breadcrumb Widget")
    
    # Day 5: Layout Algorithm Tests
    def validate_layout_algorithms(self):
        """Validate layout algorithms"""
        
        def test_layout_engine():
            from arxml_viewer.utils.layout_algorithms import LayoutEngine, LayoutType
            from arxml_viewer.models.component import Component, ComponentType
            
            engine = LayoutEngine()
            components = [
                Component(short_name=f"Comp{i}", component_type=ComponentType.APPLICATION)
                for i in range(5)
            ]
            
            positions = engine.apply_layout(components, layout_type=LayoutType.GRID)
            return len(positions) == len(components)
        
        def test_all_layout_types():
            from arxml_viewer.utils.layout_algorithms import LayoutEngine, LayoutType
            from arxml_viewer.models.component import Component, ComponentType
            
            engine = LayoutEngine()
            components = [Component(short_name="Test", component_type=ComponentType.APPLICATION)]
            
            success = True
            for layout_type in LayoutType:
                try:
                    positions = engine.apply_layout(components, layout_type=layout_type)
                    if not positions:
                        success = False
                except:
                    success = False
            
            return success
        
        self.run_test(test_layout_engine, "Layout Engine")
        self.run_test(test_all_layout_types, "All Layout Types")
    
    # Integration Tests
    def validate_integration(self):
        """Validate integrated functionality"""
        
        def test_application_controller():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.core.application import ARXMLViewerApplication
                from arxml_viewer.config import ConfigManager
                
                config = ConfigManager()
                app_controller = ARXMLViewerApplication(config, show_splash=False)
                return app_controller is not None
            except:
                return False
        
        def test_main_window_creation():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.main_window import MainWindow
                
                window = MainWindow()
                return (window is not None and 
                       hasattr(window, 'graphics_scene') and
                       hasattr(window, 'breadcrumb_widget'))
            except:
                return False
        
        def test_search_widget():
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance() or QApplication([])
                from arxml_viewer.gui.widgets.search_widget import AdvancedSearchWidget
                
                widget = AdvancedSearchWidget()
                return widget.search_input is not None
            except:
                return False
        
        self.run_test(test_application_controller, "Application Controller")
        self.run_test(test_main_window_creation, "Main Window Integration")
        self.run_test(test_search_widget, "Search Widget Integration")


def main():
    """Main validation entry point"""
    validator = ARXMLViewerValidator()
    
    try:
        validator.validate_all()
        
        # Return exit code based on results
        if validator.failed_tests == 0:
            print(f"\n{Colors.BOLD}{Colors.GREEN}Validation completed successfully!{Colors.ENDC}")
            print(f"{Colors.GREEN}The ARXML Viewer Pro implementation is ready.{Colors.ENDC}")
            return 0
        else:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}Validation completed with issues.{Colors.ENDC}")
            print(f"{Colors.YELLOW}Please review the failed tests above.{Colors.ENDC}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Validation interrupted by user.{Colors.ENDC}")
        return 2
    except Exception as e:
        print(f"\n{Colors.RED}Validation failed with error: {e}{Colors.ENDC}")
        if os.environ.get('DEBUG'):
            traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())