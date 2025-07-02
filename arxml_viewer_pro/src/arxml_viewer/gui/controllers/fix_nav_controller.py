#!/usr/bin/env python3
"""
Fix Navigation Controller - Remove Circular Import
This script updates the navigation controller to remove the circular import issue
"""

import os
from pathlib import Path

def fix_navigation_controller():
    """Fix the navigation controller file"""
    
    project_root = Path.cwd()
    nav_controller_path = project_root / "src" / "arxml_viewer" / "gui" / "controllers" / "navigation_controller.py"
    
    if not nav_controller_path.exists():
        print(f"❌ Navigation controller not found at: {nav_controller_path}")
        return False
    
    # Read the fixed navigation controller content
    fixed_content = '''"""
Navigation Controller for ARXML Viewer Pro
Fixed version without circular imports
"""
from typing import Optional, List, Dict, Any, Callable
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget
import logging
from dataclasses import dataclass
from enum import Enum

from arxml_viewer.models.component import Component
from arxml_viewer.models.package import Package

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


class NavigationHistory:
    """Manages navigation history with undo/redo functionality"""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history: List[NavigationState] = []
        self.current_index = -1
    
    def push_state(self, state: NavigationState) -> None:
        """Add a new state to history"""
        # Remove any forward history when pushing new state
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Add new state
        self.history.append(state)
        self.current_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
        
        logger.debug(f"Navigation state pushed: {len(self.history)} states")
    
    def can_go_back(self) -> bool:
        """Check if we can navigate back"""
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        """Check if we can navigate forward"""
        return self.current_index < len(self.history) - 1
    
    def go_back(self) -> Optional[NavigationState]:
        """Navigate to previous state"""
        if self.can_go_back():
            self.current_index -= 1
            return self.history[self.current_index]
        return None
    
    def go_forward(self) -> Optional[NavigationState]:
        """Navigate to next state"""
        if self.can_go_forward():
            self.current_index += 1
            return self.history[self.current_index]
        return None
    
    def get_current_state(self) -> Optional[NavigationState]:
        """Get current navigation state"""
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None


class NavigationController(QObject):
    """
    Central navigation controller that coordinates between different views
    and manages navigation state across the application
    """
    
    # Signals for navigation events
    navigation_changed = pyqtSignal(NavigationState)
    component_selected = pyqtSignal(Component)
    package_changed = pyqtSignal(Package)
    breadcrumb_updated = pyqtSignal(list)
    view_mode_changed = pyqtSignal(NavigationMode)
    history_changed = pyqtSignal(bool, bool)  # can_go_back, can_go_forward
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Navigation state
        self.current_state = NavigationState()
        self.history = NavigationHistory()
        
        # View references (set later to avoid circular imports)
        self.tree_widget: Optional[QWidget] = None
        self.graphics_scene: Optional[QWidget] = None
        self.properties_panel: Optional[QWidget] = None
        
        # Event handlers
        self.selection_handlers: List[Callable] = []
        self.navigation_handlers: List[Callable] = []
        
        logger.info("Navigation controller initialized")
    
    def set_views(self, tree_widget: QWidget = None, graphics_scene: QWidget = None, 
                  properties_panel: QWidget = None) -> None:
        """Set view references after initialization to avoid circular imports"""
        if tree_widget:
            self.tree_widget = tree_widget
        if graphics_scene:
            self.graphics_scene = graphics_scene
        if properties_panel:
            self.properties_panel = properties_panel
        
        logger.debug("Navigation controller views configured")
    
    def navigate_to_package(self, package: Package, add_to_history: bool = True) -> None:
        """Navigate to a specific package"""
        logger.info(f"Navigating to package: {package.name}")
        
        # Update current state
        old_state = self.current_state
        self.current_state = NavigationState(
            current_package=package,
            selected_component=None,
            breadcrumb_path=self._build_breadcrumb_path(package),
            view_mode=old_state.view_mode,
            zoom_level=1.0,  # Reset zoom when changing package
            scroll_position=(0, 0)
        )
        
        # Add to history
        if add_to_history:
            self.history.push_state(self.current_state)
            self._emit_history_signals()
        
        # Emit signals
        self.package_changed.emit(package)
        self.breadcrumb_updated.emit(self.current_state.breadcrumb_path)
        self.navigation_changed.emit(self.current_state)
        
        # Update views
        self._update_views()
    
    def select_component(self, component: Component, add_to_history: bool = True) -> None:
        """Select a specific component"""
        logger.info(f"Selecting component: {component.name}")
        
        # Update current state
        old_state = self.current_state
        self.current_state = NavigationState(
            current_package=old_state.current_package,
            selected_component=component,
            breadcrumb_path=old_state.breadcrumb_path,
            view_mode=old_state.view_mode,
            zoom_level=old_state.zoom_level,
            scroll_position=old_state.scroll_position
        )
        
        # Add to history
        if add_to_history:
            self.history.push_state(self.current_state)
            self._emit_history_signals()
        
        # Emit signals
        self.component_selected.emit(component)
        self.navigation_changed.emit(self.current_state)
        
        # Update views
        self._update_views()
    
    def set_view_mode(self, mode: NavigationMode) -> None:
        """Change the view mode"""
        logger.info(f"Changing view mode to: {mode.value}")
        
        old_state = self.current_state
        self.current_state = NavigationState(
            current_package=old_state.current_package,
            selected_component=old_state.selected_component,
            breadcrumb_path=old_state.breadcrumb_path,
            view_mode=mode,
            zoom_level=old_state.zoom_level,
            scroll_position=old_state.scroll_position
        )
        
        self.view_mode_changed.emit(mode)
        self.navigation_changed.emit(self.current_state)
    
    def update_view_state(self, zoom_level: float = None, 
                         scroll_position: tuple = None) -> None:
        """Update view-specific state (zoom, scroll)"""
        old_state = self.current_state
        self.current_state = NavigationState(
            current_package=old_state.current_package,
            selected_component=old_state.selected_component,
            breadcrumb_path=old_state.breadcrumb_path,
            view_mode=old_state.view_mode,
            zoom_level=zoom_level if zoom_level is not None else old_state.zoom_level,
            scroll_position=scroll_position if scroll_position is not None else old_state.scroll_position
        )
    
    def go_back(self) -> bool:
        """Navigate to previous state"""
        if not self.history.can_go_back():
            return False
        
        previous_state = self.history.go_back()
        if previous_state:
            self.current_state = previous_state
            self._emit_history_signals()
            self.navigation_changed.emit(self.current_state)
            self._update_views()
            logger.info("Navigated back in history")
            return True
        return False
    
    def go_forward(self) -> bool:
        """Navigate to next state"""
        if not self.history.can_go_forward():
            return False
        
        next_state = self.history.go_forward()
        if next_state:
            self.current_state = next_state
            self._emit_history_signals()
            self.navigation_changed.emit(self.current_state)
            self._update_views()
            logger.info("Navigated forward in history")
            return True
        return False
    
    def navigate_to_breadcrumb(self, index: int) -> None:
        """Navigate to a specific breadcrumb level"""
        if 0 <= index < len(self.current_state.breadcrumb_path):
            # This would require package hierarchy navigation
            # Implementation depends on your package structure
            logger.info(f"Navigating to breadcrumb index: {index}")
            # TODO: Implement breadcrumb navigation
    
    def get_current_state(self) -> NavigationState:
        """Get current navigation state"""
        return self.current_state
    
    def get_current_package(self) -> Optional[Package]:
        """Get currently selected package"""
        return self.current_state.current_package
    
    def get_current_component(self) -> Optional[Component]:
        """Get currently selected component"""
        return self.current_state.selected_component
    
    def can_go_back(self) -> bool:
        """Check if back navigation is possible"""
        return self.history.can_go_back()
    
    def can_go_forward(self) -> bool:
        """Check if forward navigation is possible"""
        return self.history.can_go_forward()
    
    def add_selection_handler(self, handler: Callable[[Component], None]) -> None:
        """Add a selection change handler"""
        self.selection_handlers.append(handler)
    
    def add_navigation_handler(self, handler: Callable[[NavigationState], None]) -> None:
        """Add a navigation change handler"""
        self.navigation_handlers.append(handler)
    
    def _build_breadcrumb_path(self, package: Package) -> List[str]:
        """Build breadcrumb path for a package"""
        path = []
        current = package
        
        while current:
            path.insert(0, current.name)
            current = current.parent
        
        return path
    
    def _emit_history_signals(self) -> None:
        """Emit history-related signals"""
        self.history_changed.emit(
            self.history.can_go_back(),
            self.history.can_go_forward()
        )
    
    def _update_views(self) -> None:
        """Update all connected views with current state"""
        # Call custom handlers
        for handler in self.navigation_handlers:
            try:
                handler(self.current_state)
            except Exception as e:
                logger.error(f"Error in navigation handler: {e}")
        
        # Update specific views if available
        if self.tree_widget and hasattr(self.tree_widget, 'update_from_navigation'):
            try:
                self.tree_widget.update_from_navigation(self.current_state)
            except Exception as e:
                logger.error(f"Error updating tree widget: {e}")
        
        if self.graphics_scene and hasattr(self.graphics_scene, 'update_from_navigation'):
            try:
                self.graphics_scene.update_from_navigation(self.current_state)
            except Exception as e:
                logger.error(f"Error updating graphics scene: {e}")
        
        if self.properties_panel and hasattr(self.properties_panel, 'update_from_navigation'):
            try:
                self.properties_panel.update_from_navigation(self.current_state)
            except Exception as e:
                logger.error(f"Error updating properties panel: {e}")


class NavigationSync:
    """
    Utility class for synchronizing navigation between different views
    """
    
    def __init__(self, controller: NavigationController):
        self.controller = controller
        self.synchronized_views: List[QWidget] = []
    
    def add_synchronized_view(self, view: QWidget) -> None:
        """Add a view to be synchronized"""
        self.synchronized_views.append(view)
    
    def sync_selection(self, source_view: QWidget, selected_item: Any) -> None:
        """Synchronize selection across views"""
        for view in self.synchronized_views:
            if view != source_view and hasattr(view, 'sync_selection'):
                try:
                    view.sync_selection(selected_item)
                except Exception as e:
                    logger.error(f"Error syncing selection to view: {e}")
    
    def sync_navigation(self, source_view: QWidget, navigation_target: Any) -> None:
        """Synchronize navigation across views"""
        for view in self.synchronized_views:
            if view != source_view and hasattr(view, 'sync_navigation'):
                try:
                    view.sync_navigation(navigation_target)
                except Exception as e:
                    logger.error(f"Error syncing navigation to view: {e}")
'''
    
    try:
        # Write the fixed content
        with open(nav_controller_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Fixed navigation controller: {nav_controller_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing navigation controller: {e}")
        return False


def main():
    """Main function"""
    print("🔧 Fixing Navigation Controller...")
    print("=" * 50)
    
    success = fix_navigation_controller()
    
    if success:
        print("\n✅ Navigation controller fixed successfully!")
        print("🚀 You can now run the improved validation script.")
        print("\nNext steps:")
        print("1. Save the improved validation script as 'validate_day3_improved.py'")
        print("2. Run: python validate_day3_improved.py")
        print("3. If all tests pass, you're ready for Day 4!")
    else:
        print("\n❌ Failed to fix navigation controller.")
        print("Please check the file path and try again.")
    
    return success


if __name__ == "__main__":
    main()