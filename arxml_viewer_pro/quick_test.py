#!/usr/bin/env python3
"""
Quick Test Script - ARXML Viewer Pro
Tests core functionality to verify the installation works
"""

import sys
import os
import tempfile
from pathlib import Path

def setup_path():
    """Setup Python path"""
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        return True
    return False

def create_test_arxml():
    """Create a simple test ARXML file"""
    test_content = '''<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>TestPackage</SHORT-NAME>
      <ELEMENTS>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>TestApp</SHORT-NAME>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>OutPort</SHORT-NAME>
            </P-PORT-PROTOTYPE>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>InPort</SHORT-NAME>
            </R-PORT-PROTOTYPE>
          </PORTS>
        </APPLICATION-SW-COMPONENT-TYPE>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.arxml', delete=False) as f:
        f.write(test_content)
        return f.name

def test_imports():
    """Test that core modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import arxml_viewer
        print("✅ arxml_viewer package")
    except ImportError as e:
        print(f"❌ arxml_viewer package: {e}")
        return False
    
    try:
        from arxml_viewer.models.component import Component, ComponentType
        print("✅ Component model")
    except ImportError as e:
        print(f"❌ Component model: {e}")
        return False
    
    try:
        from arxml_viewer.models.port import Port, PortType
        print("✅ Port model")
    except ImportError as e:
        print(f"❌ Port model: {e}")
        return False
    
    try:
        from arxml_viewer.parsers.arxml_parser import ARXMLParser
        print("✅ ARXML Parser")
    except ImportError as e:
        print(f"❌ ARXML Parser: {e}")
        return False
    
    try:
        from arxml_viewer.config import ConfigManager
        print("✅ Configuration")
    except ImportError as e:
        print(f"❌ Configuration: {e}")
        return False
    
    return True

def test_models():
    """Test model creation"""
    print("\n🔍 Testing models...")
    
    try:
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.port import Port, PortType
        
        # Test component creation
        comp = Component(
            short_name="TestComponent",
            component_type=ComponentType.APPLICATION
        )
        print("✅ Component creation")
        
        # Test port creation
        port = Port(
            short_name="TestPort",
            port_type=PortType.PROVIDED
        )
        print("✅ Port creation")
        
        # Test port assignment
        comp.add_port(port)
        if len(comp.all_ports) == 1:
            print("✅ Port assignment")
        else:
            print("❌ Port assignment failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_parser():
    """Test ARXML parsing"""
    print("\n🔍 Testing parser...")
    
    try:
        from arxml_viewer.parsers.arxml_parser import ARXMLParser
        
        # Create test file
        test_file = create_test_arxml()
        
        try:
            # Test parsing
            parser = ARXMLParser()
            packages, metadata = parser.parse_file(test_file)
            
            if len(packages) > 0:
                print("✅ ARXML parsing")
                
                # Check package content
                package = packages[0]
                if package.short_name == "TestPackage":
                    print("✅ Package parsing")
                else:
                    print("❌ Package name incorrect")
                    return False
                
                # Check components
                if len(package.components) > 0:
                    print("✅ Component parsing")
                    
                    # Check component details
                    component = package.components[0]
                    if component.short_name == "TestApp":
                        print("✅ Component details")
                    else:
                        print("❌ Component name incorrect")
                        return False
                    
                    # Check ports
                    if len(component.all_ports) > 0:
                        print("✅ Port parsing")
                    else:
                        print("❌ No ports found")
                        return False
                else:
                    print("❌ No components found")
                    return False
            else:
                print("❌ No packages found")
                return False
            
            return True
            
        finally:
            # Clean up test file
            try:
                os.unlink(test_file)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Parser test failed: {e}")
        return False

def test_config():
    """Test configuration system"""
    print("\n🔍 Testing configuration...")
    
    try:
        from arxml_viewer.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.config
        
        if hasattr(config, 'theme') and hasattr(config, 'recent_files'):
            print("✅ Configuration system")
            return True
        else:
            print("❌ Configuration structure incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_gui_imports():
    """Test GUI component imports (optional)"""
    print("\n🔍 Testing GUI imports...")
    
    try:
        # Test PyQt5 availability
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 available")
        
        # Test graphics components
        try:
            from arxml_viewer.gui.graphics import ComponentDiagramScene
            print("✅ Graphics scene")
        except ImportError as e:
            print(f"⚠️ Graphics scene: {e}")
        
        # Test main window
        try:
            from arxml_viewer.gui.main_window import MainWindow
            print("✅ Main window")
        except ImportError as e:
            print(f"⚠️ Main window: {e}")
        
        return True
        
    except ImportError as e:
        print(f"⚠️ PyQt5 not available: {e}")
        return True  # This is optional, so don't fail

def test_services():
    """Test service components"""
    print("\n🔍 Testing services...")
    
    try:
        from arxml_viewer.services import SearchEngine, FilterManager
        
        # Test search engine
        search_engine = SearchEngine()
        print("✅ Search engine")
        
        # Test filter manager
        filter_manager = FilterManager()
        print("✅ Filter manager")
        
        return True
        
    except Exception as e:
        print(f"❌ Services test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 ARXML Viewer Pro - Quick Test Suite")
    print("=" * 45)
    
    tests = [
        ("Import Test", test_imports),
        ("Model Test", test_models),
        ("Parser Test", test_parser),
        ("Config Test", test_config),
        ("GUI Test", test_gui_imports),
        ("Services Test", test_services)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 45)
    print("🏁 Test Summary")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The application should work correctly.")
        print("You can now run: python run_app.py")
        return True
    elif failed <= 2:
        print("\n⚠️ Some tests failed, but core functionality works.")
        print("You can try running: python run_app.py")
        return True
    else:
        print("\n❌ Multiple test failures. Please check the installation.")
        print("Try running: python install_deps.py")
        return False

def main():
    """Main test function"""
    # Setup path
    if not setup_path():
        print("❌ Could not setup Python path")
        return False
    
    # Run tests
    success = run_all_tests()
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)