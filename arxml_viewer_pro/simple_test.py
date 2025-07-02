#!/usr/bin/env python3
"""
Simple ARXML Viewer Pro Test
Quick verification of core functionality
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path.cwd() / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def test_imports():
    """Test basic imports"""
    print("🔧 Testing imports...")
    
    try:
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.package import Package
        print("✅ Models import OK")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from arxml_viewer.services.search_engine import SearchEngine
        print("✅ SearchEngine import OK")
    except Exception as e:
        print(f"❌ SearchEngine import failed: {e}")
        return False
    
    return True

def test_functionality():
    """Test basic functionality"""
    print("\n🔧 Testing functionality...")
    
    try:
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.package import Package
        from arxml_viewer.services.search_engine import SearchEngine
        
        # Create test objects
        package = Package(short_name="TestPkg", full_path="/test")
        component = Component(
            short_name="TestComp", 
            component_type=ComponentType.APPLICATION,
            package_path="/test"
        )
        print("✅ Test objects created")
        
        # Test SearchEngine
        search_engine = SearchEngine()
        search_engine.build_index([package])
        print("✅ SearchEngine.build_index() works")
        
        results = search_engine.search("Test")
        print(f"✅ Search works - found {len(results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Main test"""
    print("🔍 ARXML Viewer Pro - Simple Test")
    print("=" * 40)
    
    if not test_imports():
        return False
    
    if not test_functionality():
        return False
    
    print("\n🎉 All tests passed!")
    print("✅ Day 3 implementation is working!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
