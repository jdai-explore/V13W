#!/bin/bash
# Complete Controllers Directory Fix
# This will fix all import issues in the controllers directory

echo "🔧 Complete Controllers Directory Fix"
echo "====================================="

# Step 1: Check and fix controllers __init__.py
echo "🔍 Checking controllers __init__.py..."

CONTROLLERS_INIT="src/arxml_viewer/gui/controllers/__init__.py"

if [ -f "$CONTROLLERS_INIT" ]; then
    echo "Found controllers __init__.py, checking content..."
    cat "$CONTROLLERS_INIT"
    
    # Check if it imports layout_manager
    if grep -q "layout_manager" "$CONTROLLERS_INIT"; then
        echo "❌ Found layout_manager import in __init__.py"
        echo "🔧 Fixing __init__.py..."
        
        # Create clean __init__.py
        cat > "$CONTROLLERS_INIT" << 'INITEOF'
# src/arxml_viewer/gui/controllers/__init__.py
"""
GUI Controllers - Navigation and interaction controllers
"""

from .navigation_controller import NavigationController

__all__ = ['NavigationController']
INITEOF
        echo "✅ Fixed controllers __init__.py"
    else
        echo "✅ No layout_manager imports in __init__.py"
    fi
else
    echo "Creating controllers __init__.py..."
    cat > "$CONTROLLERS_INIT" << 'INITEOF'
# src/arxml_viewer/gui/controllers/__init__.py
"""
GUI Controllers - Navigation and interaction controllers
"""

from .navigation_controller import NavigationController

__all__ = ['NavigationController']
INITEOF
    echo "✅ Created clean controllers __init__.py"
fi

# Step 2: Remove any layout_manager.py files if they exist
echo ""
echo "🔍 Checking for layout_manager files..."

LAYOUT_MANAGER_FILE="src/arxml_viewer/gui/controllers/layout_manager.py"
if [ -f "$LAYOUT_MANAGER_FILE" ]; then
    echo "❌ Found layout_manager.py - removing it"
    rm "$LAYOUT_MANAGER_FILE"
    echo "✅ Removed layout_manager.py"
else
    echo "✅ No layout_manager.py file found"
fi

# Step 3: Clean Python cache
echo ""
echo "🔧 Cleaning Python cache..."

find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

echo "✅ Cleaned Python cache"

# Step 4: Test the import
echo ""
echo "🔍 Testing NavigationController import..."

python3 << 'PYEOF'
import sys
from pathlib import Path

# Add src to path
src_path = Path.cwd() / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Clear any cached imports
modules_to_clear = [
    'arxml_viewer.gui.controllers.navigation_controller',
    'arxml_viewer.gui.controllers',
    'arxml_viewer.gui',
    'arxml_viewer'
]
for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]

try:
    from arxml_viewer.gui.controllers.navigation_controller import NavigationController
    print("✅ NavigationController imports successfully")
    
    # Try to create instance
    nav_controller = NavigationController()
    print("✅ NavigationController created successfully")
    print("🎉 Fix successful!")
    
except Exception as e:
    print(f"❌ Still failing: {e}")
    import traceback
    traceback.print_exc()
PYEOF

echo ""
echo "🔧 Running final validation..."
python3 validate_day3_working.py
