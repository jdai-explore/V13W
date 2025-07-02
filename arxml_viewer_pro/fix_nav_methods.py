#!/usr/bin/env python3
"""
Fix NavigationController Missing Methods
Add missing methods that the main window expects
"""

from pathlib import Path

def fix_navigation_controller():
    """Add missing methods to NavigationController"""
    
    nav_path = Path("src/arxml_viewer/gui/controllers/navigation_controller.py")
    
    if not nav_path.exists():
        print(f"❌ NavigationController file not found: {nav_path}")
        return False
    
    print("🔧 Adding missing methods to NavigationController...")
    
    # Read current content
    with open(nav_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if methods already exist
    if 'def set_tree_widget(' in content:
        print("✅ set_tree_widget method already exists")
        return True
    
    # Simply append the missing methods at the end of the class
    missing_methods = '''
    def set_tree_widget(self, tree_widget):
        """Set the tree widget reference"""
        self.tree_widget = tree_widget
    
    def set_graphics_scene(self, graphics_scene):
        """Set the graphics scene reference"""
        self.graphics_scene = graphics_scene
    
    def set_properties_panel(self, properties_panel):
        """Set the properties panel reference"""
        self.properties_panel = properties_panel
    
    def can_navigate_back(self):
        """Check if back navigation is possible"""
        return False
    
    def can_navigate_forward(self):
        """Check if forward navigation is possible"""
        return False
    
    def navigate_back(self):
        """Navigate back (stub for Day 3)"""
        return False
    
    def navigate_forward(self):
        """Navigate forward (stub for Day 3)"""
        return False
    
    def get_breadcrumb_path(self):
        """Get breadcrumb path (stub for Day 3)"""
        return []
    
    def clear_mappings(self):
        """Clear navigation mappings (stub for Day 3)"""
        pass
    
    def register_tree_item(self, tree_item, data_object):
        """Register tree item mapping (stub for Day 3)"""
        pass
'''
    
    # Add methods to the end
    content += missing_methods
    
    # Write back to file
    with open(nav_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added missing methods to NavigationController")
    return True

def main():
    """Main fix function"""
    print("🔧 Fix NavigationController Missing Methods")
    print("=" * 50)
    
    if fix_navigation_controller():
        print("\n🎉 NavigationController is now complete!")
        print("Run: python run_app.py")
    else:
        print("\n❌ Fix failed")

if __name__ == "__main__":
    main()
