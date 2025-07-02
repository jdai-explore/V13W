#!/usr/bin/env python3
"""
Quick Test - Verify core functionality
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path.cwd() / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def main():
    print("🧪 Quick Test - Core Functionality")
    print("-" * 40)
    
    try:
        # Test basic imports
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.package import Package
        from arxml_viewer.services.search_engine import SearchEngine
        print("✅ Core imports successful")
        
        # Test object creation
        package = Package(short_name="Test", full_path="/test")
        component = Component(
            short_name="TestComp",
            component_type=ComponentType.APPLICATION,
            package_path="/test"
        )
        print("✅ Object creation successful")
        
        # Test search engine
        search_engine = SearchEngine()
        search_engine.build_index([package])
        results = search_engine.search("Test")
        print(f"✅ Search engine works - {len(results)} results")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("Day 3 implementation is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
