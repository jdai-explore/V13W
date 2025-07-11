#!/usr/bin/env python3
"""
Run ARXML Viewer Pro Application - FIXED VERSION
Handles Python path setup and launches the application with better error handling
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
    
    required_deps = ['PyQt5', 'pydantic', 'lxml']
    optional_deps = ['loguru', 'pandas', 'matplotlib', 'networkx']
    
    missing_required = []
    missing_optional = []
    
    # Check required dependencies
    for dep in required_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING (REQUIRED)")
            missing_required.append(dep)
    
    # Check optional dependencies
    for dep in optional_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"⚠️ {dep} - MISSING (OPTIONAL)")
            missing_optional.append(dep)
    
    if missing_required:
        print(f"\n❌ Missing required dependencies: {missing_required}")
        print("Install them with: pip install PyQt5 pydantic lxml")
        return False
    
    if missing_optional:
        print(f"\n⚠️ Missing optional dependencies: {missing_optional}")
        print("Application will run with reduced functionality.")
        print("Install with: pip install loguru pandas matplotlib networkx")
    
    return True

def install_missing_dependencies():
    """Try to install missing dependencies"""
    print("\n🔧 Attempting to install missing dependencies...")
    
    try:
        import subprocess
        
        # Install basic required packages
        packages = ["PyQt5>=5.15.0", "pydantic>=2.4.0", "lxml>=4.9.3"]
        
        for package in packages:
            try:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installed")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Auto-installation failed: {e}")
        return False

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
        
        # Check if it's a missing dependency issue
        if "loguru" in str(e):
            print("\n💡 This appears to be a loguru dependency issue.")
            print("The application should work with the fallback logger.")
            print("Try installing loguru: pip install loguru")
        
        return False
    except Exception as e:
        print(f"❌ Application failed to start: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🔧 ARXML Viewer Pro Launcher - FIXED VERSION")
    print("=" * 50)
    
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
        print("\n🔧 Required dependencies are missing.")
        choice = input("Would you like to try auto-installing them? (y/n): ").lower().strip()
        
        if choice == 'y':
            if install_missing_dependencies():
                print("✅ Dependencies installed. Restarting dependency check...")
                if not check_dependencies():
                    print("❌ Dependency installation incomplete. Please install manually.")
                    return False
            else:
                print("❌ Auto-installation failed. Please install manually:")
                print("pip install PyQt5 pydantic lxml")
                return False
        else:
            print("❌ Cannot continue without required dependencies.")
            return False
    
    # Run the application
    success = run_application()
    
    if success:
        print("\n✅ Application closed successfully")
    else:
        print("\n❌ Application encountered errors")
        print("\n🔍 Troubleshooting tips:")
        print("1. Make sure you're in the arxml_viewer_pro directory")
        print("2. Install missing dependencies: pip install PyQt5 pydantic lxml loguru")
        print("3. Try running: python -m arxml_viewer.main")
        print("4. Check if PyQt5 is properly installed: python -c 'import PyQt5; print(\"PyQt5 OK\")'")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)