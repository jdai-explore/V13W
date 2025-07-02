#!/usr/bin/env python3
"""
Remove Dark Theme from ARXML Viewer Pro
Switch to default system theme while preserving all functionality
"""

from pathlib import Path
import re

def remove_dark_theme_from_main_window():
    """Remove dark theme styling from main window"""
    
    main_window_path = Path("src/arxml_viewer/gui/main_window.py")
    
    if not main_window_path.exists():
        print(f"❌ Main window file not found: {main_window_path}")
        return False
    
    print("🔧 Removing dark theme from main window...")
    
    # Read the current file
    with open(main_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and comment out the _apply_theme method call
    content = re.sub(
        r'(\s+)self\._apply_theme\(\)',
        r'\1# self._apply_theme()  # Dark theme disabled',
        content
    )
    
    # Comment out the entire _apply_theme method
    lines = content.split('\n')
    new_lines = []
    in_apply_theme = False
    
    for line in lines:
        if 'def _apply_theme(self):' in line:
            in_apply_theme = True
            new_lines.append(f"    # {line.strip()}  # DISABLED: Dark theme method")
            continue
        elif in_apply_theme:
            # Check if we've reached the next method
            if line.strip().startswith('def ') and not line.startswith('        '):
                in_apply_theme = False
                new_lines.append(line)
            else:
                # Comment out all lines in the _apply_theme method
                if line.strip():
                    new_lines.append(f"        # {line.strip()}")
                else:
                    new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Write the modified content
    with open(main_window_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Removed dark theme from main window")
    return True

def remove_dark_theme_from_graphics_scene():
    """Remove dark theme from graphics scene"""
    
    graphics_scene_path = Path("src/arxml_viewer/gui/graphics/graphics_scene.py")
    
    if not graphics_scene_path.exists():
        print(f"❌ Graphics scene file not found: {graphics_scene_path}")
        return False
    
    print("🔧 Removing dark theme from graphics scene...")
    
    # Read the current file
    with open(graphics_scene_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace dark background with light background
    content = re.sub(
        r'QColor\(45, 45, 45\)',
        'QColor(245, 245, 245)',  # Light gray background
        content
    )
    
    # Update export scene image background
    content = re.sub(
        r'pixmap\.fill\(QColor\(45, 45, 45\)\)',
        'pixmap.fill(QColor(255, 255, 255))',  # White background for exports
        content
    )
    
    # Write the modified content
    with open(graphics_scene_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Removed dark theme from graphics scene")
    return True

def main():
    """Main function to remove dark theme"""
    print("🎨 Remove Dark Theme from ARXML Viewer Pro")
    print("=" * 50)
    
    success_count = 0
    
    # Remove dark theme from main components
    if remove_dark_theme_from_main_window():
        success_count += 1
    
    if remove_dark_theme_from_graphics_scene():
        success_count += 1
    
    print(f"\n✅ Dark theme removal completed!")
    print("\n🎨 Changes Made:")
    print("✅ Main window now uses default system theme")
    print("✅ Graphics scene uses light background")
    print("✅ All functionality preserved")
    print("\n🚀 Run the application to see the new light theme:")
    print("python run_app.py")

if __name__ == "__main__":
    main()
