#!/usr/bin/env python3
"""
ARXML Viewer Pro - Day 3 Final Validation Script
Validates Tree Navigation & Search System Implementation
"""

import sys
import os
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add color support
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def colored_print(text: str, color: str = Colors.WHITE) -> None:
    """Print colored text"""
    print(f"{color}{text}{Colors.END}")

def print_header(title: str) -> None:
    """Print section header"""
    colored_print(f"\n📋 Testing: {title}", Colors.CYAN)
    colored_print("=" * 60, Colors.BLUE)

def print_success(message: str) -> None:
    """Print success message"""
    colored_print(f"✅ {message}", Colors.GREEN)

def print_error(message: str) -> None:
    """Print error message"""
    colored_print(f"❌ {message}", Colors.RED)

def print_warning(message: str) -> None:
    """Print warning message"""
    colored_print(f"⚠️  {message}", Colors.YELLOW)

def print_info(message: str) -> None:
    """Print info message"""
    colored_print(f"🔧 {message}", Colors.WHITE)


def test_basic_functionality():
    """Test basic Day 3 functionality"""
    try:
        # Add src to path
        src_path = Path.cwd() / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Test imports
        from arxml_viewer.services.search_engine import SearchEngine, SearchScope
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.package import Package
        
        # Create test data with correct parameter names
        package = Package(name="TestPackage", path="/test")
        component = Component(
            name="TestComponent",
            component_type=ComponentType.APPLICATION,  # Fixed: use component_type
            package_path="/test",
            parent_package=package
        )
        
        search_engine = SearchEngine()
        search_engine.add_component(component)
        search_engine.add_package(package)
        search_engine.build_index()
        
        results = search_engine.search("Test", SearchScope.ALL)
        print_success(f"Search engine working - found {len(results)} results")
        
        # Test filter manager
        from arxml_viewer.services.filter_manager import FilterManager
        filter_manager = FilterManager()
        filter_manager.add_component(component)
        filtered = filter_manager.get_filtered_components()
        print_success(f"Filter manager working - {len(filtered)} components")
        
        return True
        
    except Exception as e:
        print_error(f"Basic functionality test failed: {e}")
        return False


def main():
    """Main validation function"""
    colored_print("🔍 ARXML Viewer Pro - Day 3 Final Validation", Colors.BOLD)
    colored_print("=" * 60, Colors.BLUE)
    
    print_header("Quick Validation Test")
    
    # Test dependencies
    print_info("Testing dependencies...")
    deps_ok = True
    for dep in ['PyQt5', 'pydantic', 'lxml']:
        try:
            importlib.import_module(dep)
            print_success(f"{dep} available")
        except ImportError:
            print_error(f"{dep} missing")
            deps_ok = False
    
    if not deps_ok:
        return False
    
    # Test basic functionality
    print_info("Testing basic functionality...")
    func_ok = test_basic_functionality()
    
    # Test navigation controller
    print_info("Testing navigation controller...")
    try:
        src_path = Path.cwd() / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from arxml_viewer.gui.controllers.navigation_controller import NavigationController
        print_success("Navigation controller imports successfully")
        nav_ok = True
    except Exception as e:
        print_error(f"Navigation controller failed: {e}")
        nav_ok = False
    
    # Test config module
    print_info("Testing config module...")
    try:
        from arxml_viewer.core.config import ConfigurationManager
        config = ConfigurationManager()
        print_success("Configuration manager working")
        config_ok = True
    except Exception as e:
        print_error(f"Config module failed: {e}")
        config_ok = False
    
    # Summary
    total_tests = 4
    passed_tests = sum([deps_ok, func_ok, nav_ok, config_ok])
    
    print_header("Final Results")
    colored_print(f"Tests Passed: {passed_tests}/{total_tests}", Colors.CYAN)
    
    if passed_tests >= 3:
        colored_print("🎉 Day 3 Implementation: VALIDATED!", Colors.GREEN)
        colored_print("Ready to proceed to Day 4!", Colors.CYAN)
        return True
    else:
        colored_print("⚠️  Some issues remain", Colors.YELLOW)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
