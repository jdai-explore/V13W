#!/bin/bash
# find_pyqt6_imports.sh - Find any remaining PyQt6 imports

echo "🔍 Searching for PyQt6 imports in the codebase..."
echo "=" * 50

# Search for PyQt6 imports in Python files
echo "Looking for 'PyQt6' in .py files:"
grep -r "PyQt6" src/ --include="*.py" || echo "No PyQt6 imports found in src/"

echo ""
echo "Looking for 'from PyQt6' in .py files:"
grep -r "from PyQt6" src/ --include="*.py" || echo "No 'from PyQt6' imports found"

echo ""
echo "Looking for 'import PyQt6' in .py files:"
grep -r "import PyQt6" src/ --include="*.py" || echo "No 'import PyQt6' statements found"

echo ""
echo "🔍 Checking specific files that might have imports..."
echo "-" * 30

# Check key files
files_to_check=(
    "src/arxml_viewer/main.py"
    "src/arxml_viewer/core/application.py"
    "src/arxml_viewer/gui/main_window.py"
    "src/arxml_viewer/gui/graphics/graphics_scene.py"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "Checking $file:"
        grep -n "PyQt" "$file" | head -5 || echo "  No PyQt imports found"
    else
        echo "$file: File not found"
    fi
    echo ""
done

echo "🔍 Summary: If any PyQt6 imports are found above, they need to be changed to PyQt5"