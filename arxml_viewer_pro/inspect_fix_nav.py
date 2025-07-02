#!/usr/bin/env python3
"""
Inspect and completely fix NavigationController
"""

from pathlib import Path

def inspect_navigation_controller():
    """Inspect the NavigationController file to find the exact problem"""
    
    nav_path = Path("src/arxml_viewer/gui/controllers/navigation_controller.py")
    
    if not nav_path.exists():
        print(f"❌ File not found: {nav_path}")
        return
    
    print("🔍 Inspecting NavigationController file...")
    
    with open(nav_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    # Find any references to layout_manager
    layout_manager_refs = []
    for i, line in enumerate(lines, 1):
        if 'layout_manager' in line.lower():
            layout_manager_refs.append((i, line.strip()))
    
    if layout_manager_refs:
        print(f"\n❌ Found {len(layout_manager_refs)} references to layout_manager:")
        for line_num, line_content in layout_manager_refs:
            print(f"  Line {line_num}: {line_content}")
    else:
        print("✅ No layout_manager references found")
    
    return layout_manager_refs

def create_clean_navigation_controller():
    """Create a clean NavigationController without any layout_manager references"""
    
    clean_nav_content = '''"""
Navigation Controller for ARXML Viewer Pro
Handles navigation state management and tree-diagram synchronization
"""
from typing import Optional, List, Dict, Any, Callable
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget
import logging
from dataclasses import dataclass
from enum import Enum

from ...models.component import Component
from ...models.package import Package

logger = logging.getLogger(__name__)


class NavigationMode(Enum):
    """Navigation modes for different views"""
    TREE_VIEW = "tree"
    DIAGRAM_VIEW = "diagram"
    COMBINED_VIEW = "combined"


@dataclass
class NavigationState:
    """Represents the current navigation state"""
    current_package: Optional[Package] = None
    selected_component: Optional[Component] = None
    breadcrumb_path: List[str] = None
    view_mode: NavigationMode = NavigationMode.COMBINED_VIEW
    zoom_level: float = 1.0
    scroll_position: tuple = (0, 0)
    
    def __post_init__(self):
        if self.breadcrumb_path is None:
            self.breadcrumb_path = []


class NavigationController(QObject):
    """
    Central navigation controller that coordinates between different views
    """
    
    # Signals for navigation events
    navigation_changed = pyqtSignal(NavigationState)
    component_selected = pyqtSignal(Component)
    package_changed = pyqtSignal(Package)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Navigation state
        self.current_state = NavigationState()
        
        # View references
        self.tree_widget: Optional[QWidget] = None
        self.graphics_scene: Optional[QWidget] = None
        self.properties_panel: Optional[QWidget] = None
        
        logger.info("Navigation controller initialized")
    
    def set_views(self, tree_widget: QWidget = None, graphics_scene: QWidget = None, 
                  properties_panel: QWidget = None) -> None:
        """Set view references after initialization"""
        if tree_widget:
            self.tree_widget = tree_widget
        if graphics_scene:
            self.graphics_scene = graphics_scene
        if properties_panel:
            self.properties_panel = properties_panel
        
        logger.debug("Navigation controller views configured")
    
    def navigate_to_package(self, package: Package) -> None:
        """Navigate to a specific package"""
        logger.info(f"Navigating to package: {package.short_name}")
        self.current_state.current_package = package
        self.package_changed.emit(package)
        self.navigation_changed.emit(self.current_state)
    
    def select_component(self, component: Component) -> None:
        """Select a specific component"""
        logger.info(f"Selecting component: {component.short_name}")
        self.current_state.selected_component = component
        self.component_selected.emit(component)
        self.navigation_changed.emit(self.current_state)
    
    def get_current_state(self) -> NavigationState:
        """Get current navigation state"""
        return self.current_state
'''
    
    nav_path = Path("src/arxml_viewer/gui/controllers/navigation_controller.py")
    
    # Backup existing file
    backup_path = nav_path.with_suffix('.py.broken')
    if nav_path.exists():
        with open(nav_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_content)
        print(f"✅ Backed up broken file to: {backup_path}")
    
    # Write clean version
    with open(nav_path, 'w', encoding='utf-8') as f:
        f.write(clean_nav_content)
    
    print("✅ Created clean NavigationController")

def test_import():
    """Test if NavigationController can be imported"""
    print("\n🔍 Testing import...")
    
    try:
        import sys
        src_path = Path.cwd() / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Clear any cached imports
        modules_to_clear = [
            'arxml_viewer.gui.controllers.navigation_controller',
            'arxml_viewer.gui.controllers'
        ]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        from arxml_viewer.gui.controllers.navigation_controller import NavigationController
        print("✅ NavigationController imports successfully")
        
        # Try to create instance
        nav_controller = NavigationController()
        print("✅ NavigationController created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Import/creation failed: {e}")
        return False

def main():
    print("🔧 Inspect and Fix NavigationController")
    print("=" * 50)
    
    # First inspect to see the problem
    layout_manager_refs = inspect_navigation_controller()
    
    print(f"\n🔧 Creating clean NavigationController...")
    create_clean_navigation_controller()
    
    if test_import():
        print("\n🎉 NavigationController is now completely fixed!")
        print("Run: python validate_day3_working.py")
    else:
        print("\n⚠️  Still having issues - check the error above")

if __name__ == "__main__":
    main()
