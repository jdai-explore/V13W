#!/usr/bin/env python3
"""
Run ARXML Viewer Pro Application
Handles Python path setup and launches the application
"""

import sys
import os
from pathlib import Path

def setup_python_path():
    """Setup Python path for the application"""
    # Get the project root directory
    project_root = Path.cwd()
    src_path = project_root / "src"
    
    if not src_path.exists():
        print(f"❌ Source directory not found: {src_path}")
        print(f"Current directory: {project_root}")
        print("Make sure you're running from the arxml_viewer_pro directory")
        return False
    
    # Add src to Python path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        print(f"✅ Added to Python path: {src_path}")
    
    return True

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    deps = ['PyQt5', 'pydantic', 'lxml']
    missing = []
    
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            missing.append(dep)
    
    if missing:
        print(f"\n❌ Missing dependencies: {missing}")
        print("Install them with: pip install PyQt5 pydantic lxml")
        return False
    
    return True

def run_application():
    """Run the ARXML Viewer Pro application"""
    print("\n🚀 Starting ARXML Viewer Pro...")
    
    try:
        # Import the main module
        from arxml_viewer.main import main
        
        print("✅ Application module imported successfully")
        
        # Run the application
        print("🖥️  Launching GUI application...")
        return main()
        
    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        return False
    except Exception as e:
        print(f"❌ Application failed to start: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🔧 ARXML Viewer Pro Launcher")
    print("=" * 40)
    
    # Check we're in the right directory
    if not Path("src").exists():
        print("❌ Please run this script from the arxml_viewer_pro directory")
        print("Current directory:", Path.cwd())
        return False
    
    # Setup Python path
    if not setup_python_path():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Run the application
    success = run_application()
    
    if success:
        print("\n✅ Application closed successfully")
    else:
        print("\n❌ Application encountered errors")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
