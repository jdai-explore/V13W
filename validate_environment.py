#!/usr/bin/env python3
"""
Environment Validation Script - Standalone checker for ARXML Viewer Pro
This script validates your Python environment before running the main application
"""

import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    print("🔍 ARXML Viewer Pro - Environment Validation")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 50)

def check_python_version():
    """Check Python version"""
    print("\n📋 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3:
        print(f"❌ Python 3 required, found Python {version.major}")
        return False
    elif version.major == 3 and version.minor < 9:
        print(f"❌ Python 3.9+ required, found Python {version.major}.{version.minor}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True

def check_pip():
    """Check pip installation"""
    print("\n📋 Checking pip...")
    
    try:
        import pip
        print(f"✅ pip available - version {pip.__version__}")
        return True
    except ImportError:
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ pip available via module")
                return True
            else:
                print("❌ pip not available")
                return False
        except:
            print("❌ pip not available")
            return False

def check_required_packages():
    """Check if required packages are installed"""
    print("\n📋 Checking required packages...")
    
    required_packages = [
        ('lxml', 'XML processing library'),
        ('PyQt6', 'GUI framework'),
        ('pydantic', 'Data validation'),
        ('pandas', 'Data processing'),
        ('numpy', 'Numerical computing'),
        ('matplotlib', 'Plotting library'),
        ('pytest', 'Testing framework'),
        ('black', 'Code formatter'),
        ('mypy', 'Type checker')
    ]
    
    installed = []
    missing = []
    
    for package_name, description in required_packages:
        try:
            __import__(package_name)
            installed.append((package_name, description))
            print(f"✅ {package_name} - {description}")
        except ImportError:
            missing.append((package_name, description))
            print(f"❌ {package_name} - {description} (missing)")
    
    print(f"\n📊 Summary: {len(installed)}/{len(required_packages)} packages available")
    
    if missing:
        print("\n⚠️  Missing packages:")
        for package, desc in missing:
            print(f"   • {package} - {desc}")
        print("\nTo install missing packages:")
        print("pip install " + " ".join([pkg for pkg, _ in missing]))
        return False
    
    return True

def check_conda_environment():
    """Check if we're in a conda environment"""
    print("\n📋 Checking environment type...")
    
    # Check for conda
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print(f"✅ Conda environment: {conda_env}")
        
        # Check conda command
        try:
            result = subprocess.run(['conda', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                conda_version = result.stdout.strip()
                print(f"✅ {conda_version}")
            else:
                print("⚠️  Conda command not available")
        except FileNotFoundError:
            print("⚠️  Conda command not found in PATH")
        
        return True
    
    # Check for virtual environment
    elif hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        venv_path = sys.prefix
        print(f"✅ Virtual environment: {venv_path}")
        return True
    
    else:
        print("⚠️  No virtual environment detected")
        print("   Recommendation: Use conda or venv for isolation")
        return False

def check_project_structure():
    """Check basic project structure"""
    print("\n📋 Checking project structure...")
    
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Check for key project indicators
    project_files = [
        'setup.py',
        'requirements.txt',
        'README.md',
        '.gitignore'
    ]
    
    project_dirs = [
        'src',
        'tests',
        'scripts'
    ]
    
    found_files = []
    found_dirs = []
    
    for file_name in project_files:
        if (current_dir / file_name).exists():
            found_files.append(file_name)
            print(f"✅ {file_name}")
        else:
            print(f"⚠️  {file_name} (not found)")
    
    for dir_name in project_dirs:
        if (current_dir / dir_name).is_dir():
            found_dirs.append(dir_name)
            print(f"✅ {dir_name}/")
        else:
            print(f"⚠️  {dir_name}/ (not found)")
    
    if len(found_files) >= 2 or len(found_dirs) >= 1:
        print("✅ Project structure detected")
        return True
    else:
        print("⚠️  Project structure not found")
        print("   You may need to run the setup script first")
        return False

def check_display():
    """Check display capabilities for GUI"""
    print("\n📋 Checking display capabilities...")
    
    if platform.system() == "Darwin":  # macOS
        print("✅ macOS - GUI should work")
        return True
    elif platform.system() == "Windows":
        print("✅ Windows - GUI should work")
        return True
    elif platform.system() == "Linux":
        display = os.environ.get('DISPLAY')
        if display:
            print(f"✅ Linux with display: {display}")
            return True
        else:
            print("⚠️  Linux without display - GUI may not work")
            print("   Set DISPLAY environment variable or use X11 forwarding")
            return False
    else:
        print(f"⚠️  Unknown platform: {platform.system()}")
        return False

def test_basic_functionality():
    """Test basic Python functionality"""
    print("\n📋 Testing basic functionality...")
    
    try:
        # Test file operations
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
            f.write("test")
        print("✅ File operations")
        
        # Test JSON
        import json
        test_data = {"test": "value"}
        json_str = json.dumps(test_data)
        parsed = json.loads(json_str)
        assert parsed["test"] == "value"
        print("✅ JSON operations")
        
        # Test datetime
        import datetime
        now = datetime.datetime.now()
        print("✅ Datetime operations")
        
        # Test pathlib
        from pathlib import Path
        current = Path.cwd()
        print("✅ Path operations")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def provide_recommendations(results):
    """Provide recommendations based on test results"""
    print("\n" + "=" * 50)
    print("📋 RECOMMENDATIONS")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    if passed_tests == total_tests:
        print("🎉 EXCELLENT! Your environment is fully ready!")
        print("✅ You can proceed with ARXML Viewer Pro development")
        print("\nNext steps:")
        print("1. Run the main application: python -m arxml_viewer.main")
        print("2. Start implementing Day 2: PyQt6 GUI components")
        print("3. Use VS Code for development: code .")
        
    elif passed_tests >= total_tests - 2:
        print("✅ GOOD! Your environment is mostly ready")
        print("⚠️  Some minor issues detected - see above")
        print("\nYou can proceed with development, but consider:")
        print("1. Installing missing packages")
        print("2. Setting up virtual environment")
        print("3. Running the project setup script")
        
    else:
        print("❌ ISSUES DETECTED! Please address the following:")
        
        if not results.get('python_version'):
            print("• Upgrade to Python 3.9 or higher")
        
        if not results.get('packages'):
            print("• Install required packages:")
            print("  pip install PyQt6 lxml pydantic pandas pytest black mypy")
        
        if not results.get('environment'):
            print("• Set up virtual environment:")
            print("  python -m venv venv")
            print("  source venv/bin/activate  # or conda activate your-env")
        
        if not results.get('display'):
            print("• Fix display issues for GUI development")
        
        print("\nRecommendation: Run the project setup script")

def main():
    """Main validation function"""
    print_header()
    
    # Import os here to avoid issues
    import os
    globals()['os'] = os
    
    # Run all checks
    results = {}
    
    results['python_version'] = check_python_version()
    results['pip'] = check_pip()
    results['packages'] = check_required_packages()
    results['environment'] = check_conda_environment()
    results['structure'] = check_project_structure()
    results['display'] = check_display()
    results['functionality'] = test_basic_functionality()
    
    # Summary
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n🎯 VALIDATION SUMMARY: {passed}/{total} checks passed")
    
    # Provide recommendations
    provide_recommendations(results)
    
    return passed >= total - 2  # Allow 1-2 failures

if __name__ == "__main__":
    success = main()
    print(f"\nValidation {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)