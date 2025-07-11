#!/usr/bin/env python3
"""
ARXML Viewer Pro - Dependency Installation Script
Installs required and optional dependencies for the application
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_package(package_name, description=""):
    """Install a single package"""
    try:
        print(f"📦 Installing {package_name}... {description}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name, "--upgrade"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def verify_installation(module_name, package_name):
    """Verify that a package was installed correctly"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name} verified")
        return True
    except ImportError:
        print(f"❌ {package_name} verification failed")
        return False

def main():
    """Main installation function"""
    print("🔧 ARXML Viewer Pro - Dependency Installer")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Required packages
    required_packages = [
        ("PyQt5>=5.15.0", "PyQt5", "GUI framework"),
        ("pydantic>=2.4.0", "pydantic", "Data validation"),
        ("lxml>=4.9.3", "lxml", "XML processing"),
    ]
    
    # Optional packages
    optional_packages = [
        ("loguru>=0.7.2", "loguru", "Enhanced logging"),
        ("pandas>=2.1.0", "pandas", "Data analysis"),
        ("matplotlib>=3.7.2", "matplotlib", "Plotting"),
        ("networkx>=3.1", "networkx", "Graph algorithms"),
        ("numpy>=1.24.0", "numpy", "Numerical computing"),
        ("Pillow>=10.0.0", "PIL", "Image processing"),
        ("reportlab>=4.0.4", "reportlab", "PDF generation"),
        ("click>=8.1.7", "click", "Command line interface"),
        ("numba>=0.58.0", "numba", "Performance optimization"),
    ]
    
    print("\n📦 Installing required packages...")
    required_success = True
    
    for package_spec, module_name, description in required_packages:
        if not install_package(package_spec, description):
            required_success = False
    
    print("\n🔍 Verifying required installations...")
    for package_spec, module_name, description in required_packages:
        if not verify_installation(module_name, package_spec.split(">=")[0]):
            required_success = False
    
    if not required_success:
        print("\n❌ Some required packages failed to install")
        print("Please install manually:")
        for package_spec, _, _ in required_packages:
            print(f"  pip install {package_spec}")
        return False
    
    print("\n✅ All required packages installed successfully!")
    
    # Ask about optional packages
    print(f"\n🔍 Optional packages can provide enhanced functionality.")
    choice = input("Install optional packages? (y/n): ").lower().strip()
    
    if choice == 'y':
        print("\n📦 Installing optional packages...")
        optional_success = 0
        
        for package_spec, module_name, description in optional_packages:
            if install_package(package_spec, description):
                if verify_installation(module_name, package_spec.split(">=")[0]):
                    optional_success += 1
        
        print(f"\n✅ {optional_success}/{len(optional_packages)} optional packages installed")
    
    print("\n🎉 Installation complete!")
    print("\nYou can now run the application with:")
    print("  python run_app.py")
    print("  or")
    print("  python -m arxml_viewer.main")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)