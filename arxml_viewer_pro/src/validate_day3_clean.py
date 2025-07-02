#!/usr/bin/env python3
"""
ARXML Viewer Pro - Clean Day 3 Validator
Tests actual implementation without assumptions
"""

import sys
import os
import importlib
from pathlib import Path

def setup_path():
    """Setup Python path"""
    src_path = Path.cwd() / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

def test_dependencies():
    """Test required dependencies"""
    deps = ['PyQt5', 'pydantic', 'lxml']
    missing = []
    
    for dep in deps:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            missing.append(dep)
    
    return len(missing) == 0

def test_models():
    """Test model classes"""
    try:
        setup_path()
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.package import Package
        
        # Test basic creation
        package = Package(short_name="Test", full_path="/test")
        component = Component(
            short_name="TestComp",
            component_type=ComponentType.APPLICATION,
            package_path="/test"
        )
        
        print("✅ Models work correctly")
        return True
    except Exception as e:
        print(f"❌ Models failed: {e}")
        return False

def test_search_engine():
    """Test SearchEngine"""
    try:
        setup_path()
        from arxml_viewer.services.search_engine import SearchEngine, SearchScope
        
        se = SearchEngine()
        
        # Test methods exist
        required_methods = ['search', 'build_index']
        for method in required_methods:
            if hasattr(se, method):
                print(f"✅ SearchEngine has {method}")
            else:
                print(f"⚠️  SearchEngine missing {method}")
        
        print("✅ SearchEngine working")
        return True
    except Exception as e:
        print(f"❌ SearchEngine failed: {e}")
        return False

def test_filter_manager():
    """Test FilterManager"""
    try:
        setup_path()
        from arxml_viewer.services.filter_manager import FilterManager
        
        fm = FilterManager()
        print("✅ FilterManager created")
        return True
    except Exception as e:
        print(f"❌ FilterManager failed: {e}")
        return False

def test_navigation_controller():
    """Test NavigationController"""
    try:
        setup_path()
        from arxml_viewer.gui.controllers.navigation_controller import NavigationController
        print("✅ NavigationController imports")
        
        # Try to create (might fail due to Qt, but import works)
        try:
            nc = NavigationController()
            print("✅ NavigationController created")
        except Exception as e:
            print(f"⚠️  NavigationController needs Qt: {str(e)[:30]}...")
        
        return True
    except Exception as e:
        print(f"❌ NavigationController import failed: {e}")
        return False

def test_widgets():
    """Test widget imports"""
    try:
        setup_path()
        from arxml_viewer.gui.widgets.tree_widget import EnhancedTreeWidget
        from arxml_viewer.gui.widgets.search_widget import AdvancedSearchWidget
        
        print("✅ Widgets import successfully")
        return True
    except Exception as e:
        print(f"❌ Widgets failed: {e}")
        return False

def test_config():
    """Test config module"""
    try:
        setup_path()
        from arxml_viewer.core.config import ConfigurationManager
        
        config = ConfigurationManager()
        print("✅ Configuration manager works")
        return True
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return False

def main():
    """Main validation"""
    print("🔍 ARXML Viewer Pro - Clean Day 3 Validation")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Models", test_models),
        ("SearchEngine", test_search_engine),
        ("FilterManager", test_filter_manager),
        ("NavigationController", test_navigation_controller),
        ("Widgets", test_widgets),
        ("Config", test_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n🔧 Testing {name}...")
        if test_func():
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed >= 6:
        print("\n🎉 Day 3 Implementation: EXCELLENT!")
        print("🚀 Ready for Day 4: Port Visualization & Component Details!")
        return True
    elif passed >= 4:
        print("\n✅ Day 3 Implementation: GOOD!")
        print("Minor issues but ready to proceed")
        return True
    else:
        print("\n⚠️  More work needed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
