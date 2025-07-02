# src/arxml_viewer/gui/layout/layout_manager.py
"""
Layout Manager - Panel layout and state management
Manages splitter states, panel visibility, and layout persistence
"""

from typing import Dict, List, Optional, Tuple, Any
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from PyQt5.QtWidgets import QSplitter, QWidget, QMainWindow

from ...utils.logger import get_logger
from ...utils.constants import UIConstants

class LayoutPreset:
    """Predefined layout presets"""
    
    # Standard three-panel layout
    STANDARD = {
        'name': 'Standard',
        'description': 'Balanced three-panel layout',
        'tree_width': 25,
        'diagram_width': 50, 
        'properties_width': 25,
        'tree_visible': True,
        'diagram_visible': True,
        'properties_visible': True
    }
    
    # Diagram-focused layout
    DIAGRAM_FOCUS = {
        'name': 'Diagram Focus',
        'description': 'Large diagram with minimal side panels',
        'tree_width': 15,
        'diagram_width': 70,
        'properties_width': 15,
        'tree_visible': True,
        'diagram_visible': True,
        'properties_visible': True
    }
    
    # Code/analysis layout
    ANALYSIS = {
        'name': 'Analysis',
        'description': 'Detailed properties with navigation',
        'tree_width': 30,
        'diagram_width': 35,
        'properties_width': 35,
        'tree_visible': True,
        'diagram_visible': True,
        'properties_visible': True
    }
    
    # Diagram only
    DIAGRAM_ONLY = {
        'name': 'Diagram Only',
        'description': 'Hide side panels, show only diagram',
        'tree_width': 0,
        'diagram_width': 100,
        'properties_width': 0,
        'tree_visible': False,
        'diagram_visible': True,
        'properties_visible': False
    }
    
    # Compact view
    COMPACT = {
        'name': 'Compact',
        'description': 'Compact layout for smaller screens',
        'tree_width': 20,
        'diagram_width': 60,
        'properties_width': 20,
        'tree_visible': True,
        'diagram_visible': True,
        'properties_visible': True
    }

class LayoutManager(QObject):
    """
    Manages application layout state and persistence
    Handles splitter states, panel visibility, and responsive behavior
    """
    
    # Signals
    layout_changed = pyqtSignal(str)  # layout_name
    panel_visibility_changed = pyqtSignal(str, bool)  # panel_name, visible
    splitter_moved = pyqtSignal(list)  # sizes
    
    def __init__(self, main_window: QMainWindow = None):
        super().__init__()
        
        self.logger = get_logger(__name__)
        self.main_window = main_window
        
        # Layout state
        self.current_layout_name = "Standard"
        self.panel_sizes: Dict[str, int] = {}
        self.panel_visibility: Dict[str, bool] = {
            'tree': True,
            'diagram': True,
            'properties': True
        }
        
        # UI components
        self.main_splitter: Optional[QSplitter] = None
        self.tree_panel: Optional[QWidget] = None
        self.diagram_panel: Optional[QWidget] = None
        self.properties_panel: Optional[QWidget] = None
        
        # Layout presets
        self.presets = {
            'Standard': LayoutPreset.STANDARD,
            'Diagram Focus': LayoutPreset.DIAGRAM_FOCUS,
            'Analysis': LayoutPreset.ANALYSIS,
            'Diagram Only': LayoutPreset.DIAGRAM_ONLY,
            'Compact': LayoutPreset.COMPACT
        }
        
        # Custom layouts saved by user
        self.custom_layouts: Dict[str, Dict[str, Any]] = {}
        
        # Settings for persistence
        self.settings = QSettings()
        
        # Responsive breakpoints (window width in pixels)
        self.responsive_breakpoints = {
            'small': 800,
            'medium': 1200,
            'large': 1600
        }
        
        # Load saved state
        self._load_state()
    
    def setup_ui_components(self, 
                          main_splitter: QSplitter,
                          tree_panel: QWidget,
                          diagram_panel: QWidget,
                          properties_panel: QWidget):
        """Setup UI components for layout management"""
        self.main_splitter = main_splitter
        self.tree_panel = tree_panel
        self.diagram_panel = diagram_panel
        self.properties_panel = properties_panel
        
        # Connect splitter signals
        if self.main_splitter:
            self.main_splitter.splitterMoved.connect(self._on_splitter_moved)
        
        # Apply current layout
        self.apply_layout(self.current_layout_name)
        
        self.logger.debug("Layout manager UI components setup complete")
    
    def apply_layout(self, layout_name: str):
        """Apply a layout preset or custom layout"""
        layout = None
        
        # Check presets first
        if layout_name in self.presets:
            layout = self.presets[layout_name]
        # Check custom layouts
        elif layout_name in self.custom_layouts:
            layout = self.custom_layouts[layout_name]
        
        if not layout:
            self.logger.warning(f"Layout '{layout_name}' not found")
            return
        
        self.current_layout_name = layout_name
        
        # Apply panel visibility
        self.set_panel_visibility('tree', layout['tree_visible'])
        self.set_panel_visibility('diagram', layout['diagram_visible'])
        self.set_panel_visibility('properties', layout['properties_visible'])
        
        # Apply splitter sizes if splitter is available
        if self.main_splitter and any([layout['tree_visible'], layout['diagram_visible'], layout['properties_visible']]):
            self._apply_splitter_sizes(layout)
        
        # Emit signal
        self.layout_changed.emit(layout_name)
        
        self.logger.debug(f"Applied layout: {layout_name}")
    
    def _apply_splitter_sizes(self, layout: Dict[str, Any]):
        """Apply splitter sizes based on layout"""
        if not self.main_splitter:
            return
        
        # Calculate total window width
        total_width = self.main_window.width() if self.main_window else 1400
        
        # Get visible panels and their proportions
        visible_panels = []
        proportions = []
        
        if layout['tree_visible']:
            visible_panels.append('tree')
            proportions.append(layout['tree_width'])
        
        if layout['diagram_visible']:
            visible_panels.append('diagram')
            proportions.append(layout['diagram_width'])
        
        if layout['properties_visible']:
            visible_panels.append('properties')
            proportions.append(layout['properties_width'])
        
        if not visible_panels:
            return
        
        # Normalize proportions to sum to 100
        total_proportion = sum(proportions)
        if total_proportion > 0:
            proportions = [(p / total_proportion) * 100 for p in proportions]
        
        # Calculate pixel sizes
        sizes = [int(total_width * (prop / 100)) for prop in proportions]
        
        # Ensure minimum sizes
        min_size = 50
        for i, size in enumerate(sizes):
            if size < min_size:
                sizes[i] = min_size
        
        # Apply sizes to splitter
        self.main_splitter.setSizes(sizes)
        
        # Store current sizes
        for i, panel in enumerate(visible_panels):
            if i < len(sizes):
                self.panel_sizes[panel] = sizes[i]
    
    def set_panel_visibility(self, panel_name: str, visible: bool):
        """Set visibility of a specific panel"""
        if panel_name not in self.panel_visibility:
            return
        
        old_visibility = self.panel_visibility[panel_name]
        self.panel_visibility[panel_name] = visible
        
        # Apply to UI
        panel_widget = self._get_panel_widget(panel_name)
        if panel_widget:
            panel_widget.setVisible(visible)
        
        # Emit signal if changed
        if old_visibility != visible:
            self.panel_visibility_changed.emit(panel_name, visible)
            self.logger.debug(f"Panel '{panel_name}' visibility: {visible}")
    
    def toggle_panel_visibility(self, panel_name: str):
        """Toggle visibility of a specific panel"""
        current_visibility = self.panel_visibility.get(panel_name, True)
        self.set_panel_visibility(panel_name, not current_visibility)
    
    def _get_panel_widget(self, panel_name: str) -> Optional[QWidget]:
        """Get widget for panel name"""
        if panel_name == 'tree':
            return self.tree_panel
        elif panel_name == 'diagram':
            return self.diagram_panel
        elif panel_name == 'properties':
            return self.properties_panel
        return None
    
    def _on_splitter_moved(self, pos: int, index: int):
        """Handle splitter movement"""
        if self.main_splitter:
            sizes = self.main_splitter.sizes()
            
            # Update stored sizes
            visible_panels = []
            if self.panel_visibility.get('tree', True):
                visible_panels.append('tree')
            if self.panel_visibility.get('diagram', True):
                visible_panels.append('diagram')
            if self.panel_visibility.get('properties', True):
                visible_panels.append('properties')
            
            for i, panel in enumerate(visible_panels):
                if i < len(sizes):
                    self.panel_sizes[panel] = sizes[i]
            
            # Emit signal
            self.splitter_moved.emit(sizes)
    
    def save_current_as_custom_layout(self, name: str, description: str = ""):
        """Save current layout as custom layout"""
        if not self.main_splitter:
            return
        
        # Calculate proportions from current splitter sizes
        sizes = self.main_splitter.sizes()
        total_size = sum(sizes) if sizes else 1
        
        visible_panels = []
        if self.panel_visibility.get('tree', True):
            visible_panels.append('tree')
        if self.panel_visibility.get('diagram', True):
            visible_panels.append('diagram')
        if self.panel_visibility.get('properties', True):
            visible_panels.append('properties')
        
        # Default proportions
        tree_width = 25
        diagram_width = 50
        properties_width = 25
        
        # Calculate actual proportions if we have sizes
        if len(sizes) == len(visible_panels) and total_size > 0:
            proportions = [(size / total_size) * 100 for size in sizes]
            
            prop_index = 0
            if self.panel_visibility.get('tree', True):
                tree_width = proportions[prop_index]
                prop_index += 1
            else:
                tree_width = 0
            
            if self.panel_visibility.get('diagram', True):
                diagram_width = proportions[prop_index]
                prop_index += 1
            else:
                diagram_width = 0
            
            if self.panel_visibility.get('properties', True):
                properties_width = proportions[prop_index]
            else:
                properties_width = 0
        
        # Create custom layout
        custom_layout = {
            'name': name,
            'description': description,
            'tree_width': tree_width,
            'diagram_width': diagram_width,
            'properties_width': properties_width,
            'tree_visible': self.panel_visibility.get('tree', True),
            'diagram_visible': self.panel_visibility.get('diagram', True),
            'properties_visible': self.panel_visibility.get('properties', True)
        }
        
        self.custom_layouts[name] = custom_layout
        self.logger.debug(f"Saved custom layout: {name}")
    
    def delete_custom_layout(self, name: str):
        """Delete a custom layout"""
        if name in self.custom_layouts:
            del self.custom_layouts[name]
            self.logger.debug(f"Deleted custom layout: {name}")
    
    def get_available_layouts(self) -> List[str]:
        """Get list of all available layout names"""
        layouts = list(self.presets.keys()) + list(self.custom_layouts.keys())
        return sorted(layouts)
    
    def get_layout_info(self, layout_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific layout"""
        if layout_name in self.presets:
            return self.presets[layout_name].copy()
        elif layout_name in self.custom_layouts:
            return self.custom_layouts[layout_name].copy()
        return None
    
    def apply_responsive_layout(self, window_width: int):
        """Apply responsive layout based on window width"""
        if window_width <= self.responsive_breakpoints['small']:
            # Small screen - use compact layout
            self.apply_layout('Compact')
        elif window_width <= self.responsive_breakpoints['medium']:
            # Medium screen - use standard layout
            self.apply_layout('Standard')
        else:
            # Large screen - use current layout or diagram focus
            if self.current_layout_name not in self.get_available_layouts():
                self.apply_layout('Standard')
        
        self.logger.debug(f"Applied responsive layout for width: {window_width}")
    
    def handle_window_resize(self, new_size):
        """Handle main window resize event"""
        if self.main_window:
            window_width = new_size.width()
            
            # Apply responsive behavior if enabled
            # For now, just log the resize
            self.logger.debug(f"Window resized to: {window_width}x{new_size.height()}")
            
            # Could implement automatic responsive layout switching here
            # self.apply_responsive_layout(window_width)
    
    def reset_to_default_layout(self):
        """Reset to default standard layout"""
        self.apply_layout('Standard')
    
    def _save_state(self):
        """Save current layout state to settings"""
        self.settings.setValue("layout/current_layout", self.current_layout_name)
        self.settings.setValue("layout/panel_visibility", self.panel_visibility)
        self.settings.setValue("layout/panel_sizes", self.panel_sizes)
        
        # Save custom layouts
        for name, layout in self.custom_layouts.items():
            self.settings.setValue(f"layout/custom/{name}", layout)
        
        # Save splitter state
        if self.main_splitter:
            self.settings.setValue("layout/splitter_state", self.main_splitter.saveState())
    
    def _load_state(self):
        """Load layout state from settings"""
        # Load current layout
        saved_layout = self.settings.value("layout/current_layout", "Standard")
        if isinstance(saved_layout, str):
            self.current_layout_name = saved_layout
        
        # Load panel visibility
        saved_visibility = self.settings.value("layout/panel_visibility", self.panel_visibility)
        if isinstance(saved_visibility, dict):
            self.panel_visibility.update(saved_visibility)
        
        # Load panel sizes
        saved_sizes = self.settings.value("layout/panel_sizes", {})
        if isinstance(saved_sizes, dict):
            self.panel_sizes.update(saved_sizes)
        
        # Load custom layouts
        self.settings.beginGroup("layout/custom")
        for key in self.settings.childKeys():
            layout_data = self.settings.value(key)
            if isinstance(layout_data, dict):
                self.custom_layouts[key] = layout_data
        self.settings.endGroup()
    
    def save_state_on_exit(self):
        """Save state when application exits"""
        self._save_state()
        self.logger.debug("Layout state saved")
    
    def restore_splitter_state(self):
        """Restore splitter state from settings"""
        if self.main_splitter:
            splitter_state = self.settings.value("layout/splitter_state")
            if splitter_state:
                self.main_splitter.restoreState(splitter_state)
    
    def get_current_layout_name(self) -> str:
        """Get name of currently active layout"""
        return self.current_layout_name
    
    def is_panel_visible(self, panel_name: str) -> bool:
        """Check if panel is currently visible"""
        return self.panel_visibility.get(panel_name, True)
    
    def get_panel_sizes(self) -> Dict[str, int]:
        """Get current panel sizes"""
        return self.panel_sizes.copy()
    
    def minimize_panel(self, panel_name: str):
        """Minimize a panel to minimal size"""
        if not self.main_splitter:
            return
        
        panel_widget = self._get_panel_widget(panel_name)
        if panel_widget:
            # Set minimum size
            sizes = self.main_splitter.sizes()
            panel_index = self._get_panel_index(panel_name)
            
            if 0 <= panel_index < len(sizes):
                # Store current size for restoration
                self.panel_sizes[f"{panel_name}_before_minimize"] = sizes[panel_index]
                
                # Set to minimal size
                sizes[panel_index] = 50  # Minimal size
                self.main_splitter.setSizes(sizes)
    
    def restore_panel(self, panel_name: str):
        """Restore panel from minimized state"""
        if not self.main_splitter:
            return
        
        stored_size_key = f"{panel_name}_before_minimize"
        if stored_size_key in self.panel_sizes:
            sizes = self.main_splitter.sizes()
            panel_index = self._get_panel_index(panel_name)
            
            if 0 <= panel_index < len(sizes):
                # Restore previous size
                sizes[panel_index] = self.panel_sizes[stored_size_key]
                self.main_splitter.setSizes(sizes)
                
                # Clean up stored size
                del self.panel_sizes[stored_size_key]
    
    def _get_panel_index(self, panel_name: str) -> int:
        """Get index of panel in splitter"""
        visible_panels = []
        if self.panel_visibility.get('tree', True):
            visible_panels.append('tree')
        if self.panel_visibility.get('diagram', True):
            visible_panels.append('diagram')
        if self.panel_visibility.get('properties', True):
            visible_panels.append('properties')
        
        try:
            return visible_panels.index(panel_name)
        except ValueError:
            return -1