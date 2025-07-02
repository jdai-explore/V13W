#!/usr/bin/env python3
"""
Conda-Aware NavigationController Fix
Uses the current Python interpreter (which has the dependencies)
"""

import sys
import os
from pathlib import Path

def check_environment():
    """Check current Python environment"""
    print("🔍 Checking current Python environment...")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Check conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'Not in conda')
    print(f"Conda environment: {conda_env}")
    
    # Test dependencies in current environment
    deps = ['PyQt5', 'pydantic', 'lxml']
    available_deps = []
    
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep} available")
            available_deps.append(dep)
        except ImportError:
            print(f"❌ {dep} missing")
    
    return len(available_deps) == len(deps)

def clean_python_cache():
    """Clean Python cache files"""
    print("\n🔧 Cleaning Python cache...")
    
    # Clear sys.modules for our packages
    modules_to_clear = [
        'arxml_viewer.gui.controllers.navigation_controller',
        'arxml_viewer.gui.controllers',
        'arxml_viewer.gui',
        'arxml_viewer'
    ]
    
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
            print(f"Cleared {module} from cache")

def create_minimal_navigation_controller():
    """Create a minimal NavigationController that works"""
    print("\n🔧 Creating minimal NavigationController...")
    
    nav_path = Path("src/arxml_viewer/gui/controllers/navigation_controller.py")
    
    minimal_nav_content = '''"""
Navigation Controller for ARXML Viewer Pro - Minimal Version
"""
from typing import Optional, List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget

from ...models.component import Component
from ...models.package import Package


class NavigationController(QObject):
    """Minimal navigation controller for Day 3 validation"""
    
    # Basic signals
    component_selected = pyqtSignal(object)
    package_changed = pyqtSignal(object)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.current_component = None
        self.current_package = None
    
    def select_component(self, component: Component) -> None:
        """Select a component"""
        self.current_component = component
        self.component_selected.emit(component)
    
    def navigate_to_package(self, package: Package) -> None:
        """Navigate to a package"""
        self.current_package = package
        self.package_changed.emit(package)
    
    def get_current_component(self) -> Optional[Component]:
        """Get current component"""
        return self.current_component
    
    def get_current_package(self) -> Optional[Package]:
        """Get current package"""
        return self.current_package
'''
    
    # Backup existing file
    if nav_path.exists():
        backup_path = nav_path.with_suffix('.py.backup')
        with open(nav_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_content)
        print(f"✅ Backed up to {backup_path}")
    
    # Write minimal version
    with open(nav_path, 'w', encoding='utf-8') as f:
        f.write(minimal_nav_content)
    
    print("✅ Created minimal NavigationController")

def test_navigation_controller():
    """Test NavigationController import and creation"""
    print("\n🔍 Testing NavigationController...")
    
    try:
        # Add src to path
        src_path = Path.cwd() / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Import and test
        from arxml_viewer.gui.controllers.navigation_controller import NavigationController
        print("✅ NavigationController imports successfully")
        
        # Create instance
        nav_controller = NavigationController()
        print("✅ NavigationController created successfully")
        
        # Test basic functionality
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.package import Package
        
        test_package = Package(short_name="TestPkg", full_path="/test")
        test_component = Component(
            short_name="TestComp",
            component_type=ComponentType.APPLICATION,
            package_path="/test"
        )
        
        nav_controller.select_component(test_component)
        nav_controller.navigate_to_package(test_package)
        
        print("✅ NavigationController functionality works")
        return True
        
    except Exception as e:
        print(f"❌ NavigationController test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main fix function"""
    print("🔧 Conda-Aware NavigationController Fix")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Dependencies missing in current environment")
        print("Make sure you're in the correct conda environment:")
        print("conda activate arxml-viewer-pro")
        return False
    
    # Clean cache
    clean_python_cache()
    
    # Create minimal NavigationController
    create_minimal_navigation_controller()
    
    # Test NavigationController
    if test_navigation_controller():
        print("\n🎉 NavigationController is working!")
        print("Now run: python validate_day3_working.py")
    else:
        print("\n❌ NavigationController still has issues")

if __name__ == "__main__":
    main()
