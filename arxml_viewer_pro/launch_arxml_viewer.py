#!/usr/bin/env python
"""
ARXML Viewer Pro Launcher
Simple launcher script that adds src to path and runs the main application
Save as: launch_arxml_viewer.py
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))
    print(f"✅ Added to Python path: {src_path}")
else:
    print(f"❌ Source directory not found: {src_path}")
    sys.exit(1)

# Import and run the main application
try:
    from arxml_viewer.main import main
    print("🚀 Launching ARXML Viewer Pro...")
    sys.exit(main())
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all source files are in src/arxml_viewer/")
    sys.exit(1)
except Exception as e:
    print(f"❌ Failed to launch: {e}")
    sys.exit(1)