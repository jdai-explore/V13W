#!/usr/bin/env python3
"""
Fix EnhancedTreeWidget Missing Method
Add the missing _setup_context_menu method
"""

from pathlib import Path

def fix_enhanced_tree_widget():
    """Fix the EnhancedTreeWidget by adding missing methods"""
    
    tree_widget_path = Path("src/arxml_viewer/gui/widgets/tree_widget.py")
    
    if not tree_widget_path.exists():
        print(f"❌ Tree widget file not found: {tree_widget_path}")
        return False
    
    print("🔧 Fixing EnhancedTreeWidget...")
    
    # Read the current file
    with open(tree_widget_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file is incomplete (ends abruptly)
    if not content.strip().endswith('"""'):
        # The file appears to be cut off, let's complete it
        print("🔧 Completing incomplete EnhancedTreeWidget...")
        
        # Add the missing methods at the end
        missing_methods = '''
    def _setup_context_menu(self):
        """Setup context menu for tree items"""
        pass
    
    def _connect_signals(self):
        """Connect tree widget signals"""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemActivated.connect(self._on_item_activated)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _on_selection_changed(self):
        """Handle selection changes"""
        selected_items = self.selectedItems()
        if selected_items:
            item = selected_items[0]
            if hasattr(item, 'data_object') and item.data_object:
                self.item_selected.emit(item.data_object)
    
    def _on_item_activated(self, item, column):
        """Handle item activation (double-click)"""
        if hasattr(item, 'data_object') and item.data_object:
            self.item_activated.emit(item.data_object)
    
    def _show_context_menu(self, position):
        """Show context menu at position"""
        pass
    
    def load_packages(self, packages):
        """Load packages into tree widget"""
        self.clear()
        self.all_items.clear()
        
        for package in packages:
            self._add_package_to_tree(package)
    
    def _add_package_to_tree(self, package, parent_item=None):
        """Add package to tree"""
        try:
            item = EnhancedTreeWidgetItem(parent_item, TreeItemType.PACKAGE)
            item.set_data_object(package)
            
            if parent_item is None:
                self.addTopLevelItem(item)
            
            # Add components
            for component in package.components:
                comp_item = EnhancedTreeWidgetItem(item, TreeItemType.COMPONENT)
                comp_item.set_data_object(component)
                
                # Add ports
                for port in component.all_ports:
                    port_item = EnhancedTreeWidgetItem(comp_item, TreeItemType.PORT)
                    port_item.set_data_object(port)
            
            # Add sub-packages
            for sub_package in package.sub_packages:
                self._add_package_to_tree(sub_package, item)
            
            self.all_items.append(item)
            
        except Exception as e:
            print(f"Error adding package to tree: {e}")
    
    def apply_search(self, search_text):
        """Apply search filter"""
        if not search_text:
            self.clear_search_and_filter()
            return
        
        self.current_search_terms = [search_text.lower()]
        
        for item in self.all_items:
            if hasattr(item, 'data_object') and item.data_object:
                obj = item.data_object
                match = False
                
                search_fields = [
                    getattr(obj, 'short_name', ''),
                    getattr(obj, 'desc', ''),
                ]
                
                for field in search_fields:
                    if search_text.lower() in field.lower():
                        match = True
                        break
                
                item.setHidden(not match)
    
    def apply_filter(self, filter_text):
        """Apply type filter"""
        if filter_text == "All Items":
            self.clear_search_and_filter()
            return
        
        for item in self.all_items:
            if hasattr(item, 'item_type'):
                show = True
                if filter_text == "Components Only" and item.item_type != TreeItemType.COMPONENT:
                    show = False
                elif filter_text == "Ports Only" and item.item_type != TreeItemType.PORT:
                    show = False
                elif filter_text == "Packages Only" and item.item_type != TreeItemType.PACKAGE:
                    show = False
                
                item.setHidden(not show)
    
    def clear_search_and_filter(self):
        """Clear search and filter"""
        self.current_search_terms.clear()
        for item in self.all_items:
            item.setHidden(False)
    
    def select_object_by_uuid(self, uuid):
        """Select object by UUID"""
        for item in self.all_items:
            if (hasattr(item, 'data_object') and 
                item.data_object and 
                hasattr(item.data_object, 'uuid') and 
                item.data_object.uuid == uuid):
                self.setCurrentItem(item)
                return True
        return False
    
    def get_statistics(self):
        """Get tree statistics"""
        return {
            'total_items': len(self.all_items),
            'visible_items': len([item for item in self.all_items if not item.isHidden()])
        }
'''
        
        # Add the missing methods to complete the class
        content += missing_methods
        
        # Write the fixed content
        with open(tree_widget_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Completed EnhancedTreeWidget with missing methods")
        return True
    
    elif '_setup_context_menu' not in content:
        print("⚠️  Method missing but file seems complete - needs manual inspection")
        return False
    else:
        print("✅ _setup_context_menu method already exists")
        return True

def main():
    """Main fix function"""
    print("🔧 Fix EnhancedTreeWidget Missing Method")
    print("=" * 50)
    
    if fix_enhanced_tree_widget():
        print("\n🎉 EnhancedTreeWidget is now fixed!")
        print("Run: python run_app.py")
    else:
        print("\n❌ Fix failed")

if __name__ == "__main__":
    main()
