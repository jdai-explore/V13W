#!/bin/bash
# fix_application_pyqt5.sh - Fix the core application.py for PyQt5

echo "🔧 Fixing core/application.py for PyQt5..."

# Backup the original file
if [ -f "src/arxml_viewer/core/application.py" ]; then
    cp "src/arxml_viewer/core/application.py" "src/arxml_viewer/core/application_pyqt6_backup.py"
    echo "✅ Backed up original application.py"
fi

# Update PyQt6 to PyQt5 imports in application.py
sed -i '' 's/from PyQt6\./from PyQt5\./g' src/arxml_viewer/core/application.py

if [ $? -eq 0 ]; then
    echo "✅ Updated PyQt6 imports to PyQt5 in application.py"
    
    # Verify the changes
    echo "🔍 Verifying changes:"
    grep -n "from PyQt" src/arxml_viewer/core/application.py | head -5
    
    echo "✅ application.py is now PyQt5 compatible!"
else
    echo "❌ Failed to update application.py"
    exit 1
fi