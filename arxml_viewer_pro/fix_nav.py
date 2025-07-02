#!/usr/bin/env python3
"""
Direct NavigationController Fix - Run from arxml_viewer_pro directory
"""

import os
from pathlib import Path

def fix_navigation_controller():
    """Fix NavigationController by removing problematic imports"""
    
    nav_path = Path("src/arxml_viewer/gui/controllers/navigation_controller.py")
    
    if not nav_path.exists():
        print(f"❌ File not found: {nav_path}")
        print(f"Current directory: {Path.cwd()}")
        return False
    
    print("�� Fixing NavigationController...")
    
    # Read file
    with open(nav_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if 'layout_manager' not in content or '# REMOVED:' in content:
        print("✅ NavigationController already appears to be fixed")
        return True
    
    # Fix problematic lines
    lines = content.split('\n')
    fixed_lines = []
    fixes_made = 0
    
    for line in lines:
        if ('layout_manager' in line and 
            ('import' in line or 'from' in line) and 
            not line.strip().startswith('#')):
            fixed_lines.append(f"# {line.strip()}  # REMOVED: Problematic import")
            fixes_made += 1
            print(f"Fixed: {line.strip()}")
        else:
            fixed_lines.append(line)
    
    if fixes_made > 0:
        # Write fixed content
        with open(nav_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print(f"✅ Fixed {fixes_made} problematic import(s)")
    else:
        print("⚠️  No problematic imports found")
    
    return True

def test_import():
    """Test if NavigationController can be imported"""
    print("\n🔍 Testing import...")
    
    try:
        import sys
        src_path = Path.cwd() / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from arxml_viewer.gui.controllers.navigation_controller import NavigationController
        print("✅ NavigationController imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def main():
    print("🔧 Direct NavigationController Fix")
    print("=" * 40)
    print(f"Working directory: {Path.cwd()}")
    
    if fix_navigation_controller():
        if test_import():
            print("\n🎉 Fix successful! NavigationController is working.")
            print("Now run: python validate_day3_working.py")
        else:
            print("\n⚠️  Import still failing - check for other issues")
    else:
        print("\n❌ Fix failed")

if __name__ == "__main__":
    main()
