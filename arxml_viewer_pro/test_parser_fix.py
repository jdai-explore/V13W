#!/usr/bin/env python3
"""
Test Script for ARXML Parser Fixes
Tests the enhanced parser with comprehensive component extraction
"""

import sys
import os
from pathlib import Path

def setup_path():
    """Setup Python path"""
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        return True
    return False

def test_enhanced_parser():
    """Test the enhanced ARXML parser"""
    print("🧪 Testing Enhanced ARXML Parser")
    print("=" * 50)
    
    try:
        # Import the enhanced parser
        from arxml_viewer.parsers.arxml_parser import ARXMLParser
        
        # Create parser instance
        parser = ARXMLParser()
        print("✅ Enhanced parser created successfully")
        
        # Test file path (adjust as needed)
        test_file = Path("C:/Users/jayad/Downloads/EcuExtract.arxml")
        
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            print("   Please update the test_file path in the script")
            return False
        
        print(f"📁 Testing with file: {test_file.name}")
        print(f"📊 File size: {test_file.stat().st_size / 1024:.1f} KB")
        
        # Parse the file
        print("\n🔧 Starting enhanced parsing...")
        packages, metadata = parser.parse_file(str(test_file))
        
        # Print results
        print(f"\n📊 PARSING RESULTS:")
        print(f"   Packages found: {len(packages)}")
        print(f"   Parse time: {metadata.get('parse_time', 0):.2f} seconds")
        
        # Show statistics
        stats = metadata.get('statistics', {})
        print(f"\n📈 STATISTICS:")
        print(f"   Components parsed: {stats.get('components_parsed', 0)}")
        print(f"   Ports parsed: {stats.get('ports_parsed', 0)}")
        print(f"   Connections parsed: {stats.get('connections_parsed', 0)}")
        
        # Show debug info
        debug_info = metadata.get('debug_info', {})
        print(f"\n🔍 DEBUG INFO:")
        print(f"   Compositions found: {debug_info.get('composition_found', 0)}")
        print(f"   Prototypes attempted: {debug_info.get('prototypes_attempted', 0)}")
        print(f"   Prototypes successful: {debug_info.get('prototypes_successful', 0)}")
        print(f"   Standalone components: {debug_info.get('standalone_components', 0)}")
        
        # Show package details
        print(f"\n📦 PACKAGE DETAILS:")
        for i, package in enumerate(packages):
            print(f"   Package {i+1}: {package.short_name}")
            print(f"      Path: {package.full_path}")
            print(f"      Components: {len(package.components)}")
            
            # Show component details
            for j, component in enumerate(package.components):
                print(f"        Component {j+1}: {component.short_name}")
                print(f"           Type: {component.component_type.value}")
                print(f"           UUID: {component.uuid[:8]}...")
                print(f"           Ports: {len(component.all_ports)}")
                
                # Show first few ports
                for k, port in enumerate(component.all_ports[:3]):
                    port_type = "PROVIDED" if port.is_provided else "REQUIRED"
                    print(f"             Port {k+1}: {port.short_name} ({port_type})")
                
                if len(component.all_ports) > 3:
                    print(f"             ... and {len(component.all_ports) - 3} more ports")
            
            if package.sub_packages:
                print(f"      Sub-packages: {len(package.sub_packages)}")
        
        # Test connections
        connections = parser.get_parsed_connections()
        print(f"\n🔗 CONNECTIONS:")
        print(f"   Total connections: {len(connections)}")
        
        for i, connection in enumerate(connections[:5]):  # Show first 5
            print(f"   Connection {i+1}: {connection.short_name}")
            print(f"      Type: {connection.connection_type.value}")
            
        if len(connections) > 5:
            print(f"   ... and {len(connections) - 5} more connections")
        
        # Success check
        total_components = sum(len(pkg.components) for pkg in packages)
        if total_components > 0:
            print(f"\n✅ SUCCESS: Found {total_components} components!")
            print("   The enhanced parser is working correctly.")
            return True
        else:
            print(f"\n⚠️ WARNING: No components found")
            print("   This may indicate an issue with the ARXML file or parser")
            return False
        
    except Exception as e:
        print(f"\n❌ PARSER TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models():
    """Test the model classes"""
    print("\n🧪 Testing Model Classes")
    print("=" * 30)
    
    try:
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.port import Port, PortType
        from arxml_viewer.models.connection import Connection, ConnectionType, ConnectionEndpoint
        from arxml_viewer.models.package import Package
        
        # Test component creation
        component = Component(
            short_name="TestComponent",
            component_type=ComponentType.APPLICATION
        )
        print(f"✅ Component created: {component.short_name}")
        
        # Test port creation
        port = Port(
            short_name="TestPort",
            port_type=PortType.PROVIDED
        )
        print(f"✅ Port created: {port.short_name}")
        
        # Test port assignment
        component.add_port(port)
        print(f"✅ Port assigned to component: {len(component.all_ports)} ports")
        
        # Test package creation
        package = Package(short_name="TestPackage")
        package.add_component(component)
        print(f"✅ Package created with component: {len(package.components)} components")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🔬 ARXML Viewer Pro - Parser Fix Test Suite")
    print("=" * 60)
    
    # Setup path
    if not setup_path():
        print("❌ Could not setup Python path")
        return False
    
    # Test models first
    models_ok = test_models()
    
    # Test enhanced parser
    parser_ok = test_enhanced_parser()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print(f"   Models test: {'✅ PASSED' if models_ok else '❌ FAILED'}")
    print(f"   Parser test: {'✅ PASSED' if parser_ok else '❌ FAILED'}")
    
    if models_ok and parser_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("   The enhanced parser should work correctly.")
        print("   You can now run: python run_app.py")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("   Please check the error messages above.")
        return False

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