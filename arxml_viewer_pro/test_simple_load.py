#!/usr/bin/env python3
# test_simple_load.py - Updated test script

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_simple_arxml_load():
    """Test simple ARXML loading with better test file"""
    print("🔧 Testing Simple ARXML Loading")
    print("=" * 50)
    
    # Test parser directly
    try:
        from arxml_viewer.parsers.arxml_parser import ARXMLParser
        
        parser = ARXMLParser()
        print("✅ Parser created")
        
        # Create better test ARXML with proper namespace
        test_arxml = '''<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>TestPackage</SHORT-NAME>
      <DESC>
        <L-2>Test package for ARXML viewer</L-2>
      </DESC>
      <ELEMENTS>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>TestApplicationComponent</SHORT-NAME>
          <DESC>
            <L-2>Test application component</L-2>
          </DESC>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>ProvidedPort1</SHORT-NAME>
              <DESC>
                <L-2>Test provided port</L-2>
              </DESC>
            </P-PORT-PROTOTYPE>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>RequiredPort1</SHORT-NAME>
              <DESC>
                <L-2>Test required port</L-2>
              </DESC>
            </R-PORT-PROTOTYPE>
          </PORTS>
        </APPLICATION-SW-COMPONENT-TYPE>
        
        <COMPOSITION-SW-COMPONENT-TYPE>
          <SHORT-NAME>TestComposition</SHORT-NAME>
          <DESC>
            <L-2>Test composition component</L-2>
          </DESC>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>CompositionProvidedPort</SHORT-NAME>
            </P-PORT-PROTOTYPE>
          </PORTS>
        </COMPOSITION-SW-COMPONENT-TYPE>
        
        <SERVICE-SW-COMPONENT-TYPE>
          <SHORT-NAME>TestService</SHORT-NAME>
          <DESC>
            <L-2>Test service component</L-2>
          </DESC>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>ServicePort</SHORT-NAME>
            </P-PORT-PROTOTYPE>
          </PORTS>
        </SERVICE-SW-COMPONENT-TYPE>
      </ELEMENTS>
      
      <SUB-PACKAGES>
        <AR-PACKAGE>
          <SHORT-NAME>SubPackage1</SHORT-NAME>
          <DESC>
            <L-2>Test sub-package</L-2>
          </DESC>
          <ELEMENTS>
            <APPLICATION-SW-COMPONENT-TYPE>
              <SHORT-NAME>SubComponent</SHORT-NAME>
              <PORTS>
                <R-PORT-PROTOTYPE>
                  <SHORT-NAME>SubRequiredPort</SHORT-NAME>
                </R-PORT-PROTOTYPE>
              </PORTS>
            </APPLICATION-SW-COMPONENT-TYPE>
          </ELEMENTS>
        </AR-PACKAGE>
      </SUB-PACKAGES>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>'''
        
        # Save test file
        test_file = Path("test_better.arxml")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_arxml)
        
        print(f"✅ Created test file: {test_file}")
        
        # Test parsing
        packages, metadata = parser.parse_file(str(test_file))
        print(f"✅ Parsed {len(packages)} packages")
        
        # Display results
        for pkg in packages:
            print(f"\nPackage: {pkg.short_name}")
            print(f"  Full Path: {pkg.full_path}")
            print(f"  Components: {len(pkg.components)}")
            print(f"  Sub-packages: {len(pkg.sub_packages)}")
            
            for comp in pkg.components:
                print(f"    Component: {comp.short_name} ({comp.component_type.name})")
                for port in comp.all_ports:
                    port_type = "PROVIDED" if port.is_provided else "REQUIRED"
                    print(f"      Port: {port.short_name} ({port_type})")
            
            # Show sub-packages
            for sub_pkg in pkg.sub_packages:
                print(f"    Sub-package: {sub_pkg.short_name}")
                for comp in sub_pkg.components:
                    print(f"      Component: {comp.short_name} ({comp.component_type.name})")
                    for port in comp.all_ports:
                        port_type = "PROVIDED" if port.is_provided else "REQUIRED"
                        print(f"        Port: {port.short_name} ({port_type})")
        
        # Display statistics
        print(f"\nParsing Statistics:")
        print(f"  Parse time: {metadata['statistics']['parse_time']:.3f}s")
        print(f"  Components: {metadata['statistics']['components_parsed']}")
        print(f"  Ports: {metadata['statistics']['ports_parsed']}")
        print(f"  Packages: {metadata['statistics']['packages_parsed']}")
        
        # Clean up
        test_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_startup():
    """Test GUI startup"""
    print("\n🔧 Testing GUI Startup")
    print("=" * 30)
    
    try:
        # Test imports first
        print("Testing imports...")
        
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 imported")
        
        import sys
        if len(sys.argv) == 1:
            sys.argv.append("--test")  # Prevent GUI from actually starting
        
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        from arxml_viewer.core.application import ARXMLViewerApplication
        from arxml_viewer.config import ConfigManager
        print("✅ Core modules imported")
        
        config_manager = ConfigManager()
        print("✅ Config manager created")
        
        # Don't actually show the GUI in test mode
        print("✅ GUI components ready")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 ARXML Viewer Pro - Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test 1: Parser
    if not test_simple_arxml_load():
        success = False
    
    # Test 2: GUI startup
    if not test_gui_startup():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Run: python debug_run.py")
        print("2. File → Open → Select the test ARXML file")
        print("3. Check tree panel and graphics panel")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Check the error messages above and fix the issues.")
    
    return success

if __name__ == "__main__":
    main()