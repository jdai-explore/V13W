#!/usr/bin/env python3
"""
Fix Syntax Error in Main Window
Fix the indentation issue caused by theme removal
"""

from pathlib import Path

def fix_main_window_syntax():
    """Fix syntax error in main window by adding missing pass statements"""
    
    main_window_path = Path("src/arxml_viewer/gui/main_window.py")
    
    if not main_window_path.exists():
        print(f"❌ Main window file not found: {main_window_path}")
        return False
    
    print("🔧 Fixing syntax error in main window...")
    
    # Read the current file
    with open(main_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix common syntax issues by adding pass statements where needed
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        fixed_lines.append(line)
        
        # If line ends with colon and next line is not indented properly
        if line.strip().endswith(':') and ('if ' in line or 'elif ' in line or 'else:' in line):
            # Check next line
            if i + 1 < len(lines):
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                
                # If next line is empty, a comment, or not properly indented
                if (not next_line.strip() or 
                    next_line.strip().startswith('#') or
                    next_line.strip().startswith('def ') or
                    next_line.strip().startswith('class ') or
                    (next_line.strip() and len(next_line) - len(next_line.lstrip()) <= len(line) - len(line.lstrip()))):
                    
                    # Add pass statement
                    indent = len(line) - len(line.lstrip()) + 4
                    fixed_lines.append(' ' * indent + 'pass')
    
    # Write the fixed content
    with open(main_window_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed syntax error in main window")
    return True

def main():
    """Main fix function"""
    print("🔧 Fix Syntax Error in Main Window")
    print("=" * 40)
    
    if fix_main_window_syntax():
        print("\n🎉 Syntax error fixed!")
        print("Run: python run_app.py")
    else:
        print("\n❌ Fix failed")

if __name__ == "__main__":
    main()
